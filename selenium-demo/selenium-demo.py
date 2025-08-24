"""
Docker command to build SeleniumGrid server:
```shell
docker run -it -d \
  --platform linux/amd64 \
  --name selenium-dev \
  -p 14444:4444 \
  -p 15900:5900 \
  -p 17900:7900 \
  -v /dev/shm:/dev/shm \
  -e SE_NODE_OVERRIDE_MAX_SESSIONS=true \
  -e SE_NODE_MAX_SESSIONS=5 \
  -e JAVA_OPTS=-XX:ActiveProcessorCount=5 \
  selenium/standalone-chrome:130.0-20250505
```
"""

import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1080,720")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-insecure-localhost")
# chrome_options.add_argument("--headless")

driver = webdriver.Remote(
    # command_executor="https://standalone-chrome-46372.asia-east1.run.app/wd/hub",
    command_executor="http://127.0.0.1:14444/wd/hub",
    options=chrome_options,
)

url = "https://www.ptt.cc/bbs/index.html"

driver.get(url)
time.sleep(10)

driver.find_element(by=By.PARTIAL_LINK_TEXT, value="Gossiping").click()
time.sleep(10)

driver.find_element(by=By.CLASS_NAME, value="btn-big").click()
time.sleep(10)

cookie = driver.get_cookies()
time.sleep(1000)

driver.quit()

ss = requests.session()

# Extract cookies
for c in cookie:
    ss.cookies.set(c["name"], c["value"])

res = ss.get("https://www.ptt.cc/bbs/Gossiping/index.html")
soup = BeautifulSoup(res.text, "html.parser")
print(soup.prettify())