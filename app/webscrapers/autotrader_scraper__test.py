import unittest
import re
import os
from .autotrader_scraper import AutotraderWebscraper
class AutotraderTester(unittest.TestCase):
    
    def __create_tmp(self):
        os.makedirs("tmp/images", exist_ok=True)

    def __remove_tmp(self):
        if os.path.exists("tmp/images"):
            self.__clear_tmp()
            os.removedirs("tmp/images")
            if os.path.exists("tmp"):
                os.removedirs("tmp")

    def __clear_tmp(self):
        if os.path.exists("tmp/images"):
            images = os.listdir("tmp/images")
            for image in images:
                os.remove(f"tmp/images/{image}")

        if os.path.exists("tmp"):
            files = os.listdir("tmp")
            for file in files:
                if os.path.isfile(f"tmp/{file}"):
                    os.remove(f"tmp/{file}")
        

    def test_default_config(self):
        scraper = AutotraderWebscraper("autotrader_default", headless=True)
        scraper.go_to_home()
        scraper.close()

    def test_homepage(self):
        scraper = AutotraderWebscraper("",headless=True, config={})
        scraper.go_to_home()
        scraper.close()

    def test_cookie_accept(self):
        scraper = AutotraderWebscraper("",headless=True, config={})
        scraper.go_to_home()
        if scraper.check_for_cookie_prompt():
            scraper.accept_cookies()
        else:
            assert(True)

        assert(not scraper.check_for_cookie_prompt())
        scraper.close()

    def test_page_number(self):
        def get_page_number(driver):
            match = re.search("page=[0-9]*", driver.current_url)
            print(driver.current_url)
            if match != None:
                return int(match.group().replace("page=", ""))
            else:
                return -1

        scraper = AutotraderWebscraper("autotrader_default", headless=True)
        scraper.search()
        scraper.go_to_page(1)
        assert(get_page_number(scraper.driver) == 1)
        scraper.go_to_page(2)
        assert(get_page_number(scraper.driver) == 2)
        scraper.go_to_page(3)
        assert(get_page_number(scraper.driver) == 3)
        scraper.close()

    def test_details_scrape(self):
        try:
            self.__clear_tmp()
            self.__create_tmp()
            scraper = AutotraderWebscraper("autotrader_default", headless=True, data_folder="tmp/")
            scraper.search()
            scraper.scrape_links()
            assert(len(scraper.scraped_links) != 0)
            scraper.scrape_all_details()
            scraper.close()
        finally:
            files = os.listdir("tmp")
            self.__remove_tmp()
            assert(len(files) != 0)

    def test_link_scrape(self):
        try:
            self.__clear_tmp()
            self.__create_tmp()
            scraper = AutotraderWebscraper("autotrader_default", headless=True, data_folder="tmp/")
            scraper.search()
            scraper.scrape_links()
            scraper.scrape_all_details()
            assert(len(scraper.scraped_links) != 0)
        finally:
            scraper.close()
            self.__remove_tmp()
