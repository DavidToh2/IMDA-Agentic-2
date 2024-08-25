from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

from typing_extensions import Annotated

from langchain_core.tools import tool

class WebSearcher:
    def __init__(self, blacklist=['google', 'youtu', 'linkedin', 'forbes']):
        self.driver = webdriver.Firefox()
        self.blacklist = set(blacklist)

    def link_not_blacklisted(self, link):
        is_not_in_blacklist = [word not in link for word in self.blacklist]
        return all(is_not_in_blacklist)

    def google_search(
        self,
        query: Annotated[str, 'query to search for'],
        n=3
    ):
        self.driver.maximize_window()
        self.driver.get("https://www.google.com/search?q="+query)

        links = list(dict.fromkeys(map(lambda x : x.get_attribute("href"), self.driver.find_elements(By.XPATH, "//a[@href][./h3]")))) 
        links = [link for link in links if self.link_not_blacklisted(link)]
        return links[0:n]
    
    def search_and_crawl(
            self,
            query,
            n=3
        ):
        urls = self.google_search(query, n)
        extracts = []
        for url in urls:
            print(f"---- Crawling url {url} ----")
            extract = self.read_webpage(url)
            l = max(len(extract), 4000)
            extracts.append(extract[:l])
        
        #for url, extract in zip(urls,extracts):
            #print(f"Extracted from ${url}:")
            #print(extract + "\n")
        res = "SEARCH RESULTS: " + "\n".join(extracts)  
        print(f"---- External search complete ----")
        return res

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
            res = re.sub(r"\[[0-9]+\]", '', " ".join(txt_arr))
            return res
        except:
            return ""

    def close(self):
        self.driver.close()

@tool
def search_and_crawl(online_search_query: Annotated[str, 'Query to search for'], num_pages: Annotated[int, 'Number of search results'] = 2):
    """Search the web for information on the query.
    """
    web_searcher = WebSearcher()
    res = web_searcher.search_and_crawl(online_search_query, num_pages)
    web_searcher.close()
    return res

def search_and_crawl_autogen(external_search_query: Annotated[str, 'Query to search for'], num_pages: Annotated[int, 'Number of search results'] = 2):
    """Search the web for information on the query.
    """
    web_searcher = WebSearcher()
    res = web_searcher.search_and_crawl(external_search_query, num_pages)
    web_searcher.close()
    return res

# c = WebSearcher()
# print(c.google_search("Dario Amodei"))