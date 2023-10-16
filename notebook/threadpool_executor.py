import sys
sys.path.append("/Users/jarvixwang/Documents/Project/gpt-researcher/")

from fastapi import WebSocket
import asyncio
from concurrent.futures import ThreadPoolExecutor
from actions.web_scrape import scrape_text_with_selenium, add_header
import processing.text as summary

async def async_browse(url: str, question: str) -> str:
    print("进入async_browse")
    loop = asyncio.get_event_loop()
    # 定义了8线程的线程池
    executor = ThreadPoolExecutor(max_workers=8)
    print("已创建loop和executor")

    print(f"Scraping url {url} with question {question}")
    # scrape_text_with_selenium(url)
    # 它会将 func(*args) 函数添加到线程池(executor)中，并返回一个协程对象。
    # 协程对象可以使用 await 关键字等待函数执行完成，并返回函数的结果（driver, text）
    driver, text = await loop.run_in_executor(executor, scrape_text_with_selenium, url)
    # 将add_header(driver)加入线程池: add_header(driver)是对正在分析的网页加一个遮罩层
    await loop.run_in_executor(executor, add_header, driver)
    # 将summary.summarize_text(url, text, question, driver)加入到线程池, 等待处理
    summary_text = await loop.run_in_executor(executor, summary.summarize_text, url, text, question, driver)
    return summary_text

import asyncio

async def main():
    print("进入main函数")
    url = "https://cn.nytimes.com/world/20231016/hamas-israel-mood-distrust/"
    question = "目前巴以冲突战况如何"
    url = "https://en.wikipedia.org/wiki/Large_language_model"
    question = "what large language model aims for?"
    rsp = await async_browse(url, question=question) # add await here
    print(rsp)

if __name__ == '__main__':
    asyncio.run(main())
