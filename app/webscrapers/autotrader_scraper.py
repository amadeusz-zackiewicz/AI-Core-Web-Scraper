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
        self.auto_trader_confirm_search_viable()

    def auto_trader_add_keywords(self, keywords):
        keywords_input = self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="keywords"]')
        keywords_panel = self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="field-panel"]')

        for keyword in keywords:
            self.input_text(keywords_input, keyword)
            keywords_panel.find_element(self.GET_TYPE_XPATH, '//*[text()="Add"]').click()
            self.auto_trader_confirm_search_viable()

    def auto_trader_confirm_search_viable(self):
        if self.config["earlyAbortSearch"] == True:
            sleep(1)
            element = self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="search-cars-button"]')
            if element.text == "No cars found":
                self.driver.close()
                raise Exception("There are no cars to be found with current settings.")
            else:
                print("Current results:", element.text.replace("searchSearch ", ""))
            
    def hover_and_click_element(self, element):
        super().hover_and_click_element(element)
        self.auto_trader_confirm_search_viable()

    def select_drop_down_by_value(self, element, target):
        if target == "Any":
            return
        
        super().select_drop_down_by_value(element, target)

        self.auto_trader_confirm_search_viable()

    def input_text(self, element, text):
        super().input_text(element, text)

        self.auto_trader_confirm_search_viable()

    def search(self):

        config = self.config["search"]

        ### Post code
        self.input_text(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="postcode"]'), config["Postcode"])
        ### Distance
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="distance"]'), config["Distance"])

        make = config["Make"]
        
        ### Make
        if make != "Any":
            model = config["Model"]
            self.select_drop_down_by_value(self.GET_TYPE_XPATH, '//*[@id="make"]', make)
            self.select_drop_down_by_value(self.GET_TYPE_XPATH, '//*[@id="model"]', model)
            ### Model
            if model != "Any":
                ### Model variant
                self.select_drop_down_by_value(self.GET_TYPE_XPATH, '//*[@id="aggregatedTrim"]', config["Model variant"])

        ### Buying with
        element = self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="search-price-panel"]')
        buying_with = config["Buying with"]
        self.auto_trader_click_wide_toggle(element, buying_with.lower())
        
        if buying_with == "Finance": ## Finance
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="minMonthlyPrice"]'), config["Min price"])
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="maxMonthlyPrice"]'), config["Max price"])
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="finance-deposit"]'), config["Finance"]["Deposit"])
            self.auto_trader_click_wide_toggle(element, config["Finance"]["Term"])
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="finance-mileage"]'), config["Finance"]["Mileage"])
        else: ## Cash
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="minPrice"]'), config["Min price"])
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="maxPrice"]'), config["Max price"])

        ### Remote options
        if config["Remote options"]["Home delivery"] == True:
            self.hover_and_click_element(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="homeDeliveryAdverts"]'))
        if config["Remote options"]["Click & collect"] == True:
            self.hover_and_click_element(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="clickAndCollectAvailable"]'))
        
        ### Keywords
        self.auto_trader_add_keywords(config["Keywords"])

        ### Mileage
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="maxMileage"]'), config["Mileage"])
        ### Gearbox
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="transmission"]'), config["Gearbox"])

        ### Age
        if config["Age"]["Select year"] == True:
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="minYear"]'), config["Age"]["Min year"])
            self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="maxYear"]'), config["Age"]["Max year"])
        else:
            self.auto_trader_click_wide_toggle(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="search-year-panel"]'), "brand-new")

        ## this just switches the toggle above to "Brand new", as far as I can tell it's pointless
        # if config["Age"]["Only new"] == True:
        #     self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="deals"]/../span').click()

        ### Wheelchair accessible
        if config["WAV"] == True:
            self.hover_and_click_element(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@for="wheelchair-accessible"]'))

        ### Performance
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="minEngineSizeLitres"]'), config["Performance"]["Min engine size"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="maxEngineSizeLitres"]'), config["Performance"]["Max engine size"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="minEnginePower"]'), config["Performance"]["Min engine power"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="maxEnginePower"]'), config["Performance"]["Max engine power"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="accelerationValue"]'), config["Performance"]["Acceleration"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="drivetrain"]'), config["Performance"]["Drivetrain"])

        ### Specification, without color
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="doorsValue"]'), config["Performance"]["Doors"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="minSeats"]'), config["Performance"]["Min seats"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="maxSeats"]'), config["Performance"]["Max seats"])

        ### Running cost
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="annualTaxValue"]'), config["Running cost"]["Annual tax"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="maxInsuranceGroup"]'), config["Running cost"]["Insurance group"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="fuelConsumptionValue"]'), config["Running cost"]["Fuel consumption"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="co2EmissionValue"]'), config["Running cost"]["CO2 emissions"])
        if config["Running cost"]["Only ULEZ"] == True:
            self.hover_and_click_element(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="emissionScheme"]'))

        ### Preferences
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="sellerType"]'), config["Preferences"]["Private & trade"])
        self.select_drop_down_by_value(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="showWriteOff"]'), config["Preferences"]["Cat S/C/D/N"])
        if config["Preferences"]["Nothern Ireland"] == True:
            self.hover_and_click_element(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="postalRegion"]'))
        if config["Preferences"]["Manufacturer approved"] == True:
            self.hover_and_click_element(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="isManufacturerApproved"]'))
        if config["Preferences"]["Additional ads"] == True:
            self.hover_and_click_element(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@id="advertClassification"]'))
        
        #self.auto_trader_confirm_search_viable()
        #self.hover_and_click_element(self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="search-cars-button"]')) # Press search button