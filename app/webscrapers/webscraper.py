from email import header
from xml.dom.minidom import Element
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import json

class NotImplementedException(Exception):
    def __init__(self, funcName: str) -> None:
        super().__init__(funcName)
        self.funcName = funcName

    def __str__(self):
        return f"{self.funcName} function is not implemented"

class FailedToFindButtonToAcceptCookiesException(Exception):
    pass

class FailedToLoadConfigFileException(Exception):
    pass

class WebScraperBase:
    def __init__(self, config_file_name, headless=False):

        options = webdriver.FirefoxOptions()
        #options.add_argument("--shm-size 2g") # put this in again in case of docker problems

        if headless:
            options.add_argument("--headless")


        config_file = open(f"app/config/{config_file_name}.json")
        self.config = json.load(config_file)
        config_file.close()

        if self.config == None:
            raise FailedToLoadConfigFileException(config_file_name)

        profile = FirefoxProfile()
        profile.set_preference("htpp.response.timeout", 30)
        profile.set_preference("dom.max_script_run_time", 30)

        self.driver = webdriver.Firefox(firefox_profile=profile, options=options, service_log_path="log.txt")
        self.driver.implicitly_wait(1)
        if not headless:
            self.driver.maximize_window()

        self.config_path = ""
        self.target_website = ""
        self.scraped_links = []

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
        sleep(2)

    def search(self):
        raise NotImplementedException("search")

    def scrape_details(self, link: str):
        raise NotImplementedException("scrape_link")

    def scrape_links(self):
        raise NotImplementedException("scrape_links")

    def go_next_page(self):
        raise NotImplementedException("go_next")

    def create_detail_page_address(self, scraped_link: str):
        return f'{self.target_website}car-details/{scraped_link}'

    def input_text(self, element, text):
        element.click()
        element.send_keys(text)

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
                    sleep(2)
                    return
            except Exception as e:
                continue
            
        return FailedToFindButtonToAcceptCookiesException()

    def select_drop_down_by_value(self, element, target):
        element.click()
        selection = Select(element)
        selection.select_by_value(target)
        sleep(0.5)
        selection.first_selected_option.click()

    def hover_and_click_element(self, element):
        action = ActionChains(self.driver)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        action.move_to_element_with_offset(element, 3, 3)
        action.click()
        action.perform()


    def close(self):
        self.driver.close()
