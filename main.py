from app.webscrapers.autotrader_scraper import AutotraderWebscraper

if __name__ == "__main__":
    scraper = AutotraderWebscraper("autotrader_london_red_hatchbacks", headless=False, data_folder="raw_data/",image_folder="raw_data/images")
    scraper.run()