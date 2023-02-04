from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


base_url = "https://qavanin.ir/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}


page_size = 1000


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')


# Choose Chrome Browser
driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

driver.get(base_url)
page_size_select_box = driver.find_element(By.ID,'PageSize')
page_size_select = Select(page_size_select_box)
page_size_select.select_by_value(str(page_size))
