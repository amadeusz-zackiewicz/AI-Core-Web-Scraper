from app.webscrapers.autotrader_scraper import AutotraderWebscraper

if __name__ == "__main__":
    scraper = AutotraderWebscraper("autotrader_london_red_hatchbacks", headless=False)
    scraper.go_to_home()
    if scraper.check_for_cookie_prompt():
        scraper.accept_cookies()
    scraper.search()
    scraper.scrape_links()
    #scraper.scrape_all_details()
    #scraper.close()
    