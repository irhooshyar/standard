from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By

from extract import driver, page_size, base_url


def get_page(page):
    if page == 1 :
        page_num_select_box = driver.find_element(By.ID,'PageNumber')
        page_num_select = Select(page_num_select_box)
        page_num_select.select_by_index(0)
    else:
        page_num_select_box = driver.find_element(By.ID,'PageNumber')
        page_num_select = Select(page_num_select_box)
        page_num_select.select_by_value(str(page))
    return driver.page_source


# print(get_page(1))
