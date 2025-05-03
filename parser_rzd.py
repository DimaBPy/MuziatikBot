import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from directions import *


def get_parse():
    flights = {}
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    with webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                          # options=options
                          ) as driver:
        driver.get(klngrd_spb)
        time.sleep(3)
        train_number = driver.find_elements(
            By.XPATH, '//div[@class="fade-out__content"]/h3')
        local_price = driver.find_elements(
            By.XPATH, '//div[@class="col body__classes"]')
        duration = driver.find_elements(
            By.XPATH, '//div[@class="card-route__duration"]')
        for i in range(len(duration)):
            dur = BeautifulSoup(duration[i].text, 'lxml')
            type_price = BeautifulSoup(local_price[i].text, 'lxml')
            format_type_ = type_price.get_text()
            first_index = format_type_.find('Купе')
            last_index = format_type_.rfind('₽') + 1
            format_type_ = format_type_[first_index:last_index]
            flights[str(train_number[i].text)] = (
                dur.text, format_type_.replace('\n', ' '))
    return flights


if __name__ == '__main__':
    print(get_parse())
