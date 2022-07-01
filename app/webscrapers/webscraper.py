from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from time import sleep

class NotImplementedException(Exception):
    def __init__(self, funcName: str) -> None:
        super().__init__(funcName)
        self.funcName = funcName

    def __str__(self):
        return f"{self.funcName} function is not implemented"

class FailedToFindButtonToAcceptCookiesException(Exception):
    pass

class WebScraperBase:
    def __init__(self, headless=False):

        options = webdriver.FirefoxOptions()
        #options.add_argument("--shm-size 2g") # put this in again in case of docker problems

        if headless:
            options.add_argument("--headless")

        profile = FirefoxProfile()
        profile.set_preference("htpp.response.timeout", 30)
        profile.set_preference("dom.max_script_run_time", 30)

        self.driver = webdriver.Firefox(firefox_profile=profile, options=options, service_log_path="log.txt")
        self.driver.implicitly_wait(1)

        self.config_path = ""
        self.target_website = ""

        self.GET_TYPE_CSS = By.CSS_SELECTOR
        self.GET_TYPE_CLASS = By.CLASS_NAME
        self.GET_TYPE_ID = By.ID
        self.GET_TYPE_LINK = By.LINK_TEXT
        self.GET_TYPE_NAME = By.NAME
        self.GET_TYPE_PARTIAL_LINK = By.PARTIAL_LINK_TEXT
        self.GET_TYPE_TAG = By.TAG_NAME
        self.GET_TYPE_XPATH = By.XPATH

        self.cookie_accept_button_getters = []
        self.cookie_prompt_getters = []


        

    def go_to_home(self):
        self.driver.get(self.target_website)
        sleep(5)

    def search(self):
        raise NotImplementedException("search")

    def scrape_details(self, link: str):
        raise NotImplementedException("scrape_link")

    def scrape_links(self):
        raise NotImplementedException("scrape_links")

    def go_next_page(self):
        raise NotImplementedException("go_next")

    def check_for_cookie_prompt(self, return_element=False) -> bool:
        for getter in self.cookie_prompt_getters:
            try:
                element = self.driver.find_element(*getter)
                if element != None:
                    if return_element:
                        return element
                    else:
                        return True
            except Exception as e:
                continue
        
        if return_element:
            return None
        else:
            return False

    def accept_cookies(self):
        for getter in self.cookie_accept_button_getters:
            try:
                element = self.driver.find_element(*getter)
                if element != None:
                    element.click()
                    self.driver.switch_to.parent_frame()
                    sleep(5)
                    return
            except Exception as e:
                print(e)
                continue
            
        return FailedToFindButtonToAcceptCookiesException()

        

    def close(self):
        self.driver.close()
