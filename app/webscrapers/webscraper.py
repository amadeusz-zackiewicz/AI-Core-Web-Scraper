from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

class WebScraperBase:
    def __init__(self, headless=False):

        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        #options.add_argument("--shm-size 2g")

        profile = FirefoxProfile()
        profile.set_preference("htpp.response.timeout", 5)
        profile.set_preference("dom.max_script_run_time", 5)

        self.driver = webdriver.Firefox(firefox_profile=profile, options=options, service_log_path="log.txt")

        print("driver set up")
        self.driver.get("https://www.autotrader.co.uk/")

    def scrape(self):
        pass

    def close(self):
        self.driver.close()
