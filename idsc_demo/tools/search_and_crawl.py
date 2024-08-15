from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from typing_extensions import Annotated

# Helper functions
def not_blacklisted(blacklist):
    def link_not_blacklisted(link):
        is_not_in_blacklist = [word not in link for word in blacklist]
        return all(is_not_in_blacklist)
    return link_not_blacklisted

def google_search(
    query: Annotated[str, 'query to search for'],
    driver,
    blacklist=['google','youtu'], 
    n=3
):
    driver.maximize_window()
    driver.get("https://www.google.com/search?q="+query)

    links = list(map(lambda x : x.get_attribute("href"), driver.find_elements(By.XPATH, "//a[@href]"))) 
    links = list(dict.fromkeys(filter(not_blacklisted(blacklist),links)))
    
    return links[0:n]

def read_webpage(url, driver):
        driver.get(url)
        driver.implicitly_wait(10)
        txt_arr = []
        try:
            txt_elements = driver.find_elements(by=By.TAG_NAME, value="p")
            for txt_element in txt_elements:
                txt_arr.append(txt_element.text)
            res = " ".join(txt_arr)
            return res
        except:
            return ""



# Tool that searches a query on Google and extracts content in the top 3 sites. 
def search_and_crawl(
    query: Annotated[str, 'query to search for'],
    n=1,
    blacklist=['google','youtu'], 
    ):
    driver = webdriver.Firefox()
    urls = google_search(query, driver, blacklist, n)
    driver.find_element
    extracts = []
    for url in urls:
        extract = read_webpage(url, driver)
        extracts.append(extract)
    
    #for url, extract in zip(urls,extracts):
        #print(f"Extracted from ${url}:")
        #print(extract + "\n")
    return "#Search results: " + "\n".join(extracts)    