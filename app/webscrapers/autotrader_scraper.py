from .webscraper import WebScraperBase
from time import sleep
import re
import urllib.request
import json
import os

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
        if self.auto_trader_is_wide_button_active(sub_element) == False:
            raise Exception(f'A button "{test_id}" was disabled, indicating that your search is too narrow.')
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
                raise Exception("There are no cars to be found with current settings. Please make sure your search criteria is not too narrow.")
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

    def auto_trader_is_wide_button_active(self, element):
        sleep(1)
        hidden_element = element.find_element(self.GET_TYPE_XPATH, "../input")
        return hidden_element.get_attribute("disabled") == None

    def go_next_page(self):
        url = self.driver.current_url
        match = re.search('page=[0-9]*', url)
        page_number = int(match.group().replace("page=", ""))
        url = url.replace(match.group(), f"page={page_number + 1}")
        self.driver.get(url)
        sleep(2)

    def __generate_multichoice_argument(self, d: dict, argument_name: str) -> str or None:
        types = []
        for _type, include in d.items():
            if include == True:
                types.append(_type)

        if len(types) == 0:
            return None
        else:
            return f"{argument_name}={'%2C'.join(types)}"

    def __generate_body_type_multichoice_argument(self) -> str or None:
        return self.__generate_multichoice_argument(self.config['search']['Body type'], 'body-type')

    def __generate_fuel_type_multichoice_argument(self) -> str or None:
        return self.__generate_multichoice_argument(self.config['search']['Fuel type'], 'fuel-type')
    
    def __generate_colour_type_multichoice_argument(self) -> str or None:
        return self.__generate_multichoice_argument(self.config['search']['Specification']['Colour'], 'colour')

    def __append_optional_argument(self, argument: str, value, current_arguments: list, default_value = "Any"):
        if type(value) == dict:
            tmp_value = default_value
            for v, b in value.items():
                if b == True:
                    tmp_value = v
                    break

            value = tmp_value

        if value != default_value:
            current_arguments.append(f"{argument}={value}")
            return True
        else:
            return False

    def search(self):

        search_arguments = []
        config = self.config["search"]

        search_arguments.append(f"postcode={config['Postcode']}")
        if config['Distance'] != 'National':
            search_arguments.append(f"radius={config['Distance']}")

        if self.__append_optional_argument("make", config['Make'], search_arguments):
            if self.__append_optional_argument("model", config['Model'], search_arguments):
                self.__append_optional_argument("aggregatedTrim", config['Model variant'], search_arguments)


        if config['Buying with'] == "Finance":
            self.__append_optional_argument("min-monthly-price", config['Min price'], search_arguments)
            self.__append_optional_argument("max-monthly-price", config['Max price'], search_arguments)
            search_arguments.append(f"deposit={config['Finance']['Deposit']}")
            search_arguments.append(f"term={config['Finance']['Term']}")
            search_arguments.append(f"yearly-mileage={config['Finance']['Mileage']}")
        else:
            self.__append_optional_argument("price-from", config['Min price'], search_arguments)
            self.__append_optional_argument("price-to", config['Max price'], search_arguments)

        if config['Remote options']['Home delivery'] == True:
            search_arguments.append("only-delivery-option=on")
        else:
            search_arguments.append("include-delivery-option=on")

        if config['Remote options']['Click & collect'] == True:
            search_arguments.append("click-and-collect-available=on")

        keywords = config['Keywords']

        if not "wheelchair" in keywords and config['WAV'] == True:
                keywords.append("wheelchair")

        if len(keywords) > 0:
            search_arguments.append(f"keywords={'%2C'.join(keywords)}")

        body_types = self.__generate_body_type_multichoice_argument()

        if body_types:
            search_arguments.append(body_types)

        fuel_types = self.__generate_fuel_type_multichoice_argument()

        if fuel_types:
            search_arguments.append(fuel_types)

        self.__append_optional_argument("maximum-mileage", config['Mileage'], search_arguments)
        self.__append_optional_argument("transmission", config['Gearbox'], search_arguments)

        if config['Age']['Select year'] == False:
            search_arguments.append("year-from=new")
            if config['Age']['Only new'] == True:
                search_arguments.append("newCarHasDeal=on")
        else:
            self.__append_optional_argument("year-from", config['Age']['Min year'], search_arguments)
            self.__append_optional_argument("year-to", config['Age']['Max year'], search_arguments)
        
        colours = self.__generate_colour_type_multichoice_argument()

        if colours:
            search_arguments.append(colours)

        self.__append_optional_argument("quantity-of-doors", config['Specification']['Doors'], search_arguments)
        self.__append_optional_argument("minimum-seats", config['Specification']['Min seats'], search_arguments)
        self.__append_optional_argument("maximum-seats", config['Specification']['Max seats'], search_arguments)

        self.__append_optional_argument("minimum-badge-engine-size", config['Performance']['Min engine size'], search_arguments)
        self.__append_optional_argument("maximum-badge-engine-size", config['Performance']['Max engine size'], search_arguments)

        self.__append_optional_argument("min-engine-power", config['Performance']['Min engine power'], search_arguments)
        self.__append_optional_argument("max-engine-power", config['Performance']['Max engine power'], search_arguments)

        self.__append_optional_argument("zero-to-60", config['Performance']['Acceleration'], search_arguments)

        self.__append_optional_argument("drivetrain", config['Performance']['Drivetrain'], search_arguments)

        self.__append_optional_argument("annual-tax-cars", config['Running cost']['Annual tax'], search_arguments)
        self.__append_optional_argument("insuranceGroup", config['Running cost']['Insurance group'], search_arguments)
        self.__append_optional_argument("fuel-consumption", config['Running cost']['Fuel consumption'], search_arguments)
        self.__append_optional_argument("co2-emissions-cars", config['Running cost']['CO2 emissions'], search_arguments)
        if config["Running cost"]["Only ULEZ"] == True:
            search_arguments.append("ulez-compliant=on")

        self.__append_optional_argument("seller-type", config['Preferences']['Private & trade'], search_arguments)
        self.__append_optional_argument("seller-type", config['Preferences']['Private & trade'], search_arguments)

        include_write_off = config["Preferences"]["Cat S/C/D/N"]

        if include_write_off != "Any":
            if include_write_off == True:
                search_arguments.append("only-writeoff-categories=on")
            else:
                search_arguments.append("exclude-writeoff-categories=on")

        if config["Preferences"]["Nothern Ireland"] == True:
            search_arguments.append("ni-only=on")

        if config["Preferences"]["Manufacturer approved"] == True:
            search_arguments.append("ma=Y")

        if config["Preferences"]["Additional ads"] == True:
            search_arguments.append("include-non-classified=on")

        search_arguments.append("page=1")
        search_url = f"{self.target_website}car-search?{'&'.join(search_arguments)}"
        print(search_url)
        self.driver.get(search_url)

    def scrape_links(self):
        maxPage = self.config["maxPage"]
        # TODO: this is very prone to errors if changed and needs to be redone
        page = 1
        while page <= maxPage:
            listings = self.driver.find_elements_by_class_name("search-page__result")

            for listing in listings:
                if listing.get_attribute("data-is-promoted-listing") == None and listing.get_attribute("data-is-yaml-listing") == None:
                    listing_id = listing.get_attribute("data-advert-id")
                    if not os.path.exists(f"raw_data/{listing_id}.json"):
                        self.scraped_links.append(listing_id)
                        print("New listing:", listing_id)
                    else:
                        print("Ignored:", listing_id)

            self.go_next_page()
            page += 1

    def scrape_all_details(self):
        # f = open("raw_data/results.csv", "w")
        # f.write(self.__get_csv_header())
        # f.write("\n")
        # f.close()
        for listing_id in self.scraped_links:
            self.scrape_details(self.create_detail_page_address(listing_id), listing_id)

    def scrape_details(self, link: str, listing_id: str):
        self.driver.get(link)
        sleep(2)
        listing_image = self.driver.find_element(self.GET_TYPE_XPATH, "//img")
        image_url = listing_image.get_attribute("src")
        if image_url:
            urllib.request.urlretrieve(image_url, f"raw_data/images/{listing_id}.jpeg")

        data = {}

        title = self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="advert-title"]').text
        make, model = title.split(" ", 1)


        total_price = self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-testid="total-price-value"]').text
        mileage = self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-testid="mileage"]').text
        details_panel = self.driver.find_element(self.GET_TYPE_XPATH, '//*[@data-gui="key-specs-section"]')


        type = details_panel.find_element(self.GET_TYPE_XPATH, "li[1]").text
        engine_size = details_panel.find_element(self.GET_TYPE_XPATH, "li[2]").text
        gearbox = details_panel.find_element(self.GET_TYPE_XPATH, "li[3]").text
        fuel = details_panel.find_element(self.GET_TYPE_XPATH, "li[4]").text
        doors = details_panel.find_element(self.GET_TYPE_XPATH, "li[5]").text
        seats = details_panel.find_element(self.GET_TYPE_XPATH, "li[6]").text

        data["id"] = listing_id
        data["mileage"] = mileage.replace(",", "").replace(" miles", "").replace(" mile", "")
        data["price"] = total_price.replace("£", "", 1).replace(",", "")
        data["make"] = make
        data["model"] = model
        data["type"] = type
        data["engine"] = engine_size
        data["gearbox"] = gearbox
        data["fuel"] = fuel
        data["doors"] = doors
        data["seats"] = seats

        self.__save_data(data)

        # TODO: missing year, ULEZ, numbers of owners

        #f = open("raw_data/results.csv", "a")
        # f.write(
        #     self.__format_csv_line(
        #         listing_id=listing_id,
        #         type=type,
        #         engine_size=engine_size,
        #         gearbox=gearbox,
        #         fuel=fuel,
        #         doors=doors,
        #         seats=seats,
        #         make=make,
        #         model=model,
        #         total_price=total_price,
        #         mileage=mileage
        #     ))
        # f.write("\n")
        # f.close()


    def __save_data(self, data: dict):
        f = open(f"raw_data/{data['id']}.json", "w")
        json.dump(data, f, indent=4)
        f.close()

    def __get_csv_header(self):
        return ", ".join([
            "Listing ID",
            "Price",
            "Type",
            "Make", 
            "Model",
            "Year",
            "Doors",
            "Seats",
            "Engine",
            "Gearbox",
            "Fuel",
            "Mileage",
            "Previous owners",
            "ULEZ"
            ])

    def __format_csv_line(self,
        listing_id = None, 
        make = None, 
        model = None, 
        mileage = None, 
        gearbox = None, 
        fuel = None, 
        owners = None, 
        doors = None, 
        seats = None, 
        total_price = None, 
        year = None, 
        ulez = None, 
        type = None, 
        engine_size = None
        ):
        return ", ".join([
            listing_id if listing_id != None else "", 
            total_price if total_price != None else "",
            type if type != None else "",
            make if make != None else "", 
            model if model != None else "", 
            year if year != None else "", 
            doors if doors != None else "",
            engine_size if engine_size != None else "", 
            seats if seats != None else "", 
            gearbox if gearbox != None else "", 
            fuel if fuel != None else "", 
            mileage if mileage != None else "",
            owners if owners != None else "", 
            "true" if ulez != None else "false"
            ])