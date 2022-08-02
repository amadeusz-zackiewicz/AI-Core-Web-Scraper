from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from app.aws.s3 import S3Client
from app.data.data_cleaner import DataCleaner
from app.postsgresql.db_client import DBClient
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
    def __init__(self, config_file_name="", headless=False, driver=None, config=None, data_folder="raw_data/", image_folder="images/", s3_bucket=None, s3_region="us-east-1", db_args=None):

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
        self.ids_to_scrape = []
        self.data_folder = data_folder
        self.image_folder = image_folder
        self.data_cleaner = DataCleaner()

        if db_args == None:
            self.db_client = None
            os.makedirs(self.data_folder, exist_ok=True)
            print("Tabular Data: No postgresql database specified, using local storage")
        else:
            self.db_client = DBClient(db_args)
            print("Tabular Data: Using postgresql database")


        if s3_bucket == None or s3_bucket == "":
            self.s3_client = None
            os.makedirs(self.image_folder, exist_ok=True)
            print("Images: No S3 bucket specified, using local storage")
        else:
            self.s3_client = S3Client(bucket_name=s3_bucket, region=s3_region)
            print(f"Images: Using S3 bucket '{self.s3_client.bucket}' in region '{self.s3_client.bucket_region}'")

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
        """
        Runs the scraper based on the information provided during initialisation.

        Raises:
            NotImplementedException: If this method is not overriden by the child class
        """
        raise NotImplementedException("run")

    def search(self):
        """
        Generates the search URL and navigates to the first page

        Args:
            config: A dictionary containing information required to create a search URL.
        
        Raises:
            NotImplementedException: If this method is not overriden by the child class
        """
        raise NotImplementedException("search")

    def scrape_details(self, link: str):
        raise NotImplementedException("scrape_link")

    def scrape_links(self):
        """
        Gets all the listing IDs from the current page and navigates to the next one, page amount can be specified in the config file.
        Any duplicate IDs will be ignored

        Raises:
            NotImplementedException: If this method is not overriden by the child class
        """
        raise NotImplementedException("scrape_links")

    def go_to_page(self, page_number = 1):
        """
        Replaces the current page number in the URL and navigates to it
        
        Args:
            page_number: the page number that will be navigated to

        Raises:
            NotImplementedException: If this method is not overriden by the child class
        """
        raise NotImplementedException("go_next")

    def create_detail_page_address(self, scraped_link: str):
        return f'{self.target_website}car-details/{scraped_link}'

    def input_text(self, element, text):
        """
        Input text into specified element.

        Args:
            element: web elements to input text into
            text: the text that will be entered
        """
        element.click()
        element.send_keys(text)

    def scrape_image(self, file_name: str, img_url: str):
        """
        Downloads image from the specified URL and either saves it into local storage or uploads it to the S3
        
        Args:
            file_name: name of the file or key for S3 bucket
            img_url: the URL from which the image will be taken from
        """
        if self.s3_client == None:
            import urllib.request
            urllib.request.urlretrieve(img_url, f"{self.image_folder}{file_name}.jpeg")
        else:
            import requests
            data = requests.get(url=img_url, stream=True)
            self.s3_client.upload_image(f"{self.image_folder}{file_name}", data.raw)
            

    def get_text_by_xpath(self, xpath: str, parent_element = None):
        """
        Convienience function to get xpaths faster
        
        Args:
            xpath: the xpath that will be used to get the element containing text
            parent_element: if provided, the xpath will be used relative from the element

        Returns:
            String or None
        """
        if parent_element == None:
            return self.driver.find_element(self.GET_TYPE_XPATH, xpath).text
        else:
            return parent_element.find_element(self.GET_TYPE_XPATH, xpath).text

    def format_currency_to_raw_number(self, currency: str, input: str) -> str:
        """
        Convienience function to remove currency symbols and commas from a number
        
        Args:
            currency: the currency symbol
            input: the raw text

        Returns:
            A string stripped from commas and currency symbol
        
        """
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
        """
        Open a drop down menu and select a value.

        Args:
            element: web element that contains the drop down menu
            target: the value that will be clicked on
        
        """
        element.click()
        selection = Select(element)
        selection.select_by_value(target)
        sleep(0.5)
        selection.first_selected_option.click()

    def hover_and_click_element(self, element):
        """
        Hover over the element and simulate a click.

        Args:
            element: web element that will be clicked on.
        """
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
        if self.db_client != None:
            self.db_client.close()
