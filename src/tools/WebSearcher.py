from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from typing_extensions import Annotated

from tools.WebpageCrawler import WebpageCrawler

class WebSearcher:
    def __init__(self, blacklist=['google', 'youtu']):
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

        links = list(map(lambda x : x.get_attribute("href"), self.driver.find_elements(By.XPATH, "//a[@href]"))) 
        links = [link for link in links if self.link_not_blacklisted(link)]
        return links[0:n]
    
    def search_and_crawl(
            self,
            query,
            n=3
        ):
        web_crawler = WebpageCrawler()
        urls = self.google_search(query, n)
        extracts = []
        for url in urls:
            extract = web_crawler.read_webpage(url)
            extracts.append(extract)
        
        #for url, extract in zip(urls,extracts):
            #print(f"Extracted from ${url}:")
            #print(extract + "\n")
        return "#Search results: " + "\n".join(extracts)    
    
def search_and_crawl(query: Annotated[str, 'Query to search for'], n=3):
    web_searcher = WebSearcher()
    return web_searcher.search_and_crawl(query, n)
