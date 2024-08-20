from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from typing_extensions import Annotated

import pickle

class WebpageCrawler:
    def __init__(self, blacklist=['google', 'youtu']):
        self.driver = webdriver.Firefox()

    def screenshot_webpage(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        self.driver.get_full_page_screenshot_as_file("test.png")
            
    def read_webpage(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        txt_arr = []
        try:
            # b = self.driver.find_element(by=By.TAG_NAME, value="body")
            # res = b.text
            txt_elements = self.driver.find_elements(by=By.TAG_NAME, value="p")
            for txt_element in txt_elements:
                txt_arr.append(txt_element.text)
            res = " ".join(txt_arr)
            return res
        except:
            return ""