"""
mac Sonoma系统的safaridriver有问题: self.assert_process_still_running()报错
firefox的geckodriver可以用: https://github.com/mozilla/geckodriver/releases
"""
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from webdriver_manager.firefox import GeckoDriverManager


# driver = webdriver.Safari()
# driver.get("https://webkit.org/status/")
# time.sleep(2)
# search_box = driver.find_element(By.XPATH, '//input[@type="search"]') # //*[@id="menu-main-menu"]/li[7]/form/input
# print(search_box)
# driver.quit()
# from selenium import webdriver
options = FirefoxOptions()
# print("CFG.selenium_web_browser: ", CFG.selenium_web_browser)
user_agent= "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
options.add_argument(f"user-agent={user_agent}")
options.add_argument('--headless') # headless不打开浏览器
options.add_argument("--enable-javascript")
# driver = webdriver.Firefox()
service = Service(executable_path="/usr/local/bin/geckodriver")#GeckoDriverManager().install())
driver = webdriver.Firefox(
    service=service, options=options
)
driver.get("https://dev.to")


# driver.find_element(By.ID, "nav-search").send_keys("Selenium")

