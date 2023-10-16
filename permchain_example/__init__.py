import os
from dotenv import load_dotenv
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_dir = os.path.abspath(os.path.join(current_dir, '..'))
dotenv_path = os.path.join(dotenv_dir, '.env')
load_dotenv(dotenv_path=dotenv_path, verbose=True)

# 设置代理
os.environ["http_proxy"]="http://172.27.9.200:15672"
os.environ["HTTP_PROXY"]="http://172.27.9.200:15672"
os.environ["https_proxy"]="http://172.27.9.200:15672"
os.environ["HTTPS_PROXY"]="http://172.27.9.200:15672"
