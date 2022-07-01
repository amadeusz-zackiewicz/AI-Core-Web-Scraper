import imp
from xml.dom.minidom import Element
from .webscraper import WebScraperBase
from time import sleep


class AutotraderWebscraper(WebScraperBase):
    def __init__(self, config_file_name, headless=False):
        super().__init__(config_file_name, headless)
        
        self.target_website = "https://www.autotrader.co.uk/"

        self.cookie_accept_button_getters.extend(
            [
                (self.GET_TYPE_XPATH, '/html/body/div/div[2]/div[3]/div[2]/button[2]')
            ])
        self.cookie_prompt_getters.extend(
            [
                (self.GET_TYPE_XPATH, '/html/body/div[3]/iframe')
            ])
        

    # def accept_cookies(self):
    #     ac = ActionChains(self.driver)
    #     ac.move_to_element_with_offset(self.check_for_cookie_prompt(True), 560, 500).click()

    def accept_cookies(self):
        cookie_holder = self.check_for_cookie_prompt(True)
        self.driver.switch_to.frame(cookie_holder)
        super().accept_cookies()
    
    def go_to_advanced_search(self):
        element = self.driver.find_element(self.GET_TYPE_CLASS, "atds-hero__more-options")
        element.click()
        sleep(5)

    def auto_trader_click_wide_toggle(self, parent_element, test_id: str):
        sub_element = parent_element.find_element(self.GET_TYPE_XPATH, f'//*[@data-testid="{test_id}-toggle"]')
        self.hover_and_click_element(sub_element)

    def select_drop_down_by_value(self, element, target):
        if target == "Any":
            return
        
        super().select_drop_down_by_value(element, target)

    def search(self):
        ### Post code
        element = self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="postcode"]')
        element.click()
        element.send_keys(self.config["search"]["Postcode"])
        ### Distance
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="distance"]'), self.config["search"]["Distance"])

        make = self.config["search"]["Make"]
        
        ### Make
        if make != "Any":
            model = self.config["search"]["Model"]
            self.select_drop_down_by_value(self.GET_TYPE_XPATH, '//*[@id="make"]', make)
            self.select_drop_down_by_value(self.GET_TYPE_XPATH, '//*[@id="model"]', model)
            ### Model
            if model != "Any":
                ### Model variant
                self.select_drop_down_by_value(self.GET_TYPE_XPATH, '//*[@id="aggregatedTrim"]', self.config["search"]["Model variant"])

        ### Buying with
        element = self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="search-price-panel"]')
        buying_with = self.config["search"]["Buying with"]
        self.auto_trader_click_wide_toggle(element, buying_with.lower())
        
        if buying_with == "Finance":
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="minMonthlyPrice"]'), self.config["search"]["Min price"])
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="maxMonthlyPrice"]'), self.config["search"]["Max price"])
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="finance-deposit"]'), self.config["search"]["Finance"]["Deposit"])
            self.auto_trader_click_wide_toggle(element, self.config["search"]["Finance"]["Term"])
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="finance-mileage"]'), self.config["search"]["Finance"]["Mileage"])
        else:
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="minPrice"]'), self.config["search"]["Min price"])
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="maxPrice"]'), self.config["search"]["Max price"])

        element = self.hover_and_click_element(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="search-cars-button"]'))