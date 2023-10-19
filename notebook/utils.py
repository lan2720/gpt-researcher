import re
import os
from md2pdf.core import md2pdf
from sec_api import ExtractorApi, XbrlApi, QueryApi
from langchain.document_loaders import UnstructuredFileLoader
import requests

# https://sec-api.io/profile
EXTRACTOR_API_KEY = "01c9ecf0d0e82f4c0c284cf56761fad0ecade92f6ec63a3e13a828dbfc6a96d4"
default_headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit'}


project_dir = "/Users/jarvixwang/Documents/Project/gpt-researcher"
# output_dir = os.path.join(project_dir, "notebook/raw_pdfs")
# os.makedirs(output_dir, exist_ok=True)


def parse_data_from_filing_url(filing_url, add_hyphen=True):
    """
    :param filing_url:
    :param add_hyphen: 默认是True, 会将accessionNo=000195004723003734转化成"0001950047-23-003734", 如果是False则不转化
    :return:
    """
    """
    全部都以: https://www.sec.gov/Archives/edgar/data/ 开头, 后面紧接着的字段是cik=1318605,7位数字, accessionNo=000195004723003734要转化成"0001950047-23-003734"
    https://www.sec.gov/Archives/edgar/data/1754581/000110465922129506/tm2231949d5_6k.htm
    # edger/data/后面只有3个段
    https://www.sec.gov/Archives/edgar/data/1045810/000195004723003455/xsl144X01/primary_doc.xml
    下面这种edgar/data/后面有4个段
    
    :param filing_url:
    :return: 返回dict, 包括{"cik": str, "accessionNo": "0001950047-23-003734"}
    """
    data_pattern = re.compile(r"(?<=www.sec.gov/Archives/edgar/data/)(?P<cik>\d+)/(?P<accession_no>\d+)/")
    shot = data_pattern.search(filing_url)
    if shot:
        data = shot.groupdict()
        # accession_no再次进行分割
        if add_hyphen:
            data["accession_no"] = data["accession_no"][:-8] + "-" + data["accession_no"][-8:-6] + "-" + data["accession_no"][-6:]
        data["filename"] = os.path.splitext(os.path.basename(filing_url))[0]
        return data
    else:
        return {}


def download_htm(cik, accession_no, filename, 
                  save_filepath):
    url = f"https://archive.sec-api.io/{cik}/{accession_no}/{filename}.htm?token={EXTRACTOR_API_KEY}"
    # url = "https://archive.sec-api.io/815094/000156459021006205/abmd-8k_20210211.htm?token=01c9ecf0d0e82f4c0c284cf56761fad0ecade92f6ec63a3e13a828dbfc6a96d4"
    print(f"拼接url_data得到url: {url}")
    # url = "https://archive.sec-api.io"
    headers = default_headers.copy()
    headers["Authorization"] = EXTRACTOR_API_KEY
    rsp = requests.get(url, headers=headers)
    html = rsp.text
    with open(save_filepath, "w") as f:
        f.write(html)

def sec_htm_to_file(url, save_filepath):
    # form_url = "https://www.sec.gov/Archives/edgar/data/1754581/000110465923061118/tm2315930d1_ex99-1.htm"
    url_data = parse_data_from_filing_url(url, add_hyphen=False)
    print(f"从SEC url={url}:\n解析到url_data={url_data}")
    try:
        download_htm(**url_data, save_filepath=save_filepath)
        print(f"成功保存SEC url文件到本地: {save_filepath}")
    except Exception as e:
        print("保存SEC url文件到本地失败")


def get_formatted_query(url_data, form_type):
    """
    https://sec-api.io/docs/query-api
    :param url_data: dict, 包含2个key: cik(表示公司个股), accessionNo(标识文件)
    :param form_type: str, 通过以下链接查询: https://sec-api.io/list-of-sec-filing-types
    :return:
    """
    cik = url_data.get("cik", None)
    accession_no = url_data.get("accession_no", None)
    assert cik and accession_no, "url_data内需要包含cik和accessionNo字段"
    return {
        "query": {
            "query_string": {
                "query": f"cik:\"{cik}\" AND accessionNo: \"{accession_no}\" AND formType:\"{form_type}\""
            }
        },
        "from": "0",
        "size": "20",
        "sort": [{ "filedAt": { "order": "desc" } }]
    }

class InsiderTradingDataAPI:
    """SEC in form 3, 4 and 5.
    https://sec-api.io/docs/insider-ownership-trading-api
    QueryApi: https://gitlab.futunn.com/algo_explore/notice_summarization/-/blob/main/src/trading/title_generate.py#L102
    """
    # form_types查询: https://sec-api.io/list-of-sec-filing-types
    supported_form_types = ["3", "4", "5"]

    @classmethod
    def dump_text_by_filing_url(cls, url, form_type, save_filepath=None):
        """
        :param url: 美股公告链接
        :param form_type: 所有form类型前往https://sec-api.io/list-of-sec-filing-types查询
        :param save_path: 可以是目录或文件路径
        :return:
        """
        assert form_type in cls.supported_form_types, f"form_type={form_type}不在支持的form_type列表内: {cls.supported_form_types}"
        try:
            url_data = parse_data_from_filing_url(url)#"https://www.sec.gov/Archives/edgar/data/2488/000195004723003927/xsl144X01/primary_doc.xml")
        except Exception as e:
            print(f"从url: {url}解析关键字段报错")#, exc_info=True)
            return
        query = get_formatted_query(url_data, form_type=form_type)
        query_api = QueryApi(EXTRACTOR_API_KEY)
        try:
            rsp = query_api.get_filings(query=query)
        except Exception as e:
            print(f"QueryApi.get_filings()报错: query: {query}")#, exc_info=True)
            return
        if len(rsp["filings"]) > 0:
            filing_info = rsp["filings"][0]
            print(f"filing_info: {filing_info}")
            txt_url = filing_info["linkToTxt"]
            print(f"获取到link_to_txt: {txt_url}")
            # logger.debug(f'获取到link_to_html: {filing_info["linkToHtml"]}') # linkToHtml没用
            # 下载txt到指定目录
        #     try:
        #         content = get_content_from_url(txt_url)
        #     except Exception as e:
        #         logger.error(f"获取url内容报错, url: {txt_url}", exc_info=True)
        #         return
        #     # 如果没有给出save_path则直接返回内容字符串
        #     if not save_path:
        #         return content
        #     if os.path.isfile(save_path):
        #         save_dir = os.path.dirname(save_path)
        #     elif os.path.isdir(save_path):
        #         save_dir = save_path
        #     os.makedirs(save_dir, exist_ok=True)
        #     if os.path.isdir(save_path):
        #         # 从url中提取文件名
        #         url_filename = os.path.splitext(os.path.basename(url))[0]
        #         save_path = os.path.join(save_dir, f"{url_filename}.txt")
        #     # 给了save_path则保存content到文件
        #     with open(save_path, "w") as f:
        #         f.write(content)
        #         logger.info(f"成功获取url: {url}链接的内容, 保存到save_path: {save_path}")
        # else:
        #     logger.error(f"QueryApi未查询到任何相关文件, url: {url}, url_data: {url_data}, form_type={form_type}, 因此无法现在该链接的文本到save_path={save_path}")
        #     return None


def make_doc_clean(doc_text):
    # print(docs[0].page_content)
    doc_text = re.sub("\n+",  "\n", doc_text)
    doc_text = re.sub(" +",  " ", doc_text)
    return doc_text

def load_pdf_text(pdf_filepath):
    loader = UnstructuredFileLoader(
        pdf_filepath#"../data/tslaletter.htm - Generated by SEC Publisher for SEC Filing.pdf"
    )
    docs = loader.load()
    doc_text = docs[0].page_content
    return make_doc_clean(doc_text)

def load_llm():
    from langchain import hub
    from langchain.chat_models import AzureChatOpenAI

    AZURE_ENDPOINT = "https://futu-002-caeast-001.openai.azure.com/"
    AZURE_API_KEY = "5d050ffec2b94f5eb43c54c80149561e"
    AZURE_API_VERSION = "2023-07-01-preview"

    llm =  AzureChatOpenAI(
                temperature=0.0,
                deployment_name='gpt-4',
                openai_api_key=AZURE_API_KEY,
                openai_api_base=AZURE_ENDPOINT,
                openai_api_type="azure",
                openai_api_version=AZURE_API_VERSION,
            )
    return llm


def markdown_to_pdf(markdown_text, output_dir, filename):
    try:
        md2pdf(os.path.join(output_dir, f"{filename}.pdf"),
            md_content=markdown_text,
            md_file_path=None,
            css_file_path=None,
            base_url=None)
        print("markdown写入pdf成功")
    except Exception as e:
        print("markdown写入pdf失败")


if __name__ == '__main__':
    pass