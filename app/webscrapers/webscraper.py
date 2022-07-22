from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from app.aws.s3 import S3Client
import json
import os

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
    def __init__(self, config_file_name="", headless=False, driver=None, config=None, data_folder="raw_data/", image_folder="images/", s3_bucket=None, s3_region="us-east-1"):

        if driver == None:
            options = webdriver.FirefoxOptions()
            #options.add_argument("--shm-size 2g") # put this in again in case of docker problems
            if headless:
                options.add_argument("--headless")


            self.driver = webdriver.Firefox(options=options)
            self.driver.implicitly_wait(1)
            if not headless:
                self.driver.maximize_window()

        if config == None:
            config_file = open(f"app/config/{config_file_name}.json")
            self.config = json.load(config_file)
            config_file.close()
        else:
            self.config = config

        if self.config == None:
            raise FailedToLoadConfigFileException(config_file_name)

        self.target_website = ""
        self.scraped_links = []
        self.data_folder = data_folder
        self.image_folder = image_folder

        if s3_bucket == None or s3_bucket == "":
            self.s3_client = None
            os.makedirs(self.data_folder, exist_ok=True)
            os.makedirs(self.image_folder, exist_ok=True)
            print("No S3 bucket specified, using local storage")
        else:
            self.s3_client = S3Client(bucket_name=s3_bucket, region=s3_region)
            print(f"Using S3 bucket '{self.s3_client.bucket}' in region '{self.s3_client.bucket_region}'")

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
        """Navigates to the main page of the website"""
        self.driver.get(self.target_website)
        sleep(2)

    def run(self):
        raise NotImplementedException("run")

    def search(self):
        raise NotImplementedException("search")

    def scrape_details(self, link: str):
        raise NotImplementedException("scrape_link")

    def scrape_links(self):
        raise NotImplementedException("scrape_links")

    def go_to_page(self, page_number = 1):
        raise NotImplementedException("go_next")

    def create_detail_page_address(self, scraped_link: str):
        return f'{self.target_website}car-details/{scraped_link}'

    def input_text(self, element, text):
        """Simulates user input of specified keys on the element"""
        element.click()
        element.send_keys(text)

    def scrape_image(self, file_name: str, img_url: str):
        """Downloads image from the specified URL"""
        if self.s3_client == None:
            import urllib.request
            urllib.request.urlretrieve(img_url, f"{self.image_folder}{file_name}.jpeg")
        else:
            import requests
            data = requests.get(url=img_url, stream=True)
            self.s3_client.upload_image(f"{self.image_folder}{file_name}", data.raw)
            

    def get_text_by_xpath(self, xpath: str, parent_element = None):
        """Convienience function to get xpaths faster"""
        if parent_element == None:
            return self.driver.find_element(self.GET_TYPE_XPATH, xpath).text
        else:
            return parent_element.find_element(self.GET_TYPE_XPATH, xpath).text

    def format_currency_to_raw_number(self, currency: str, input: str):
        """Convienience function to remove currency symbols and commas from a number"""
        return input.replace(currency, "").replace(",", "")

    def check_for_cookie_prompt(self, return_element=False) -> bool:
        """Attempt to get element which hold the cookie prompt, it simply loops through all the self.cookie_promp_getters until it finds one or faills all of them"""
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
        """Accept cookies by clicking on the 'Accept All' button, the button path is configured by adding self.cookie_accept_button_getters"""
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
        """Simulates user clicking on the drop down menu and its element"""
        element.click()
        selection = Select(element)
        selection.select_by_value(target)
        sleep(0.5)
        selection.first_selected_option.click()

    def hover_and_click_element(self, element):
        """Simulates user moving the mouse over the element and clicking it"""
        action = ActionChains(self.driver)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        action.move_to_element_with_offset(element, 3, 3)
        action.click()
        action.perform()


    def close(self):
        """Closes the web driver and cleans up"""
        self.driver.close()
        if self.s3_client != None:
            self.s3_client.close()
