from app.webscrapers.autotrader_scraper import AutotraderWebscraper

if __name__ == "__main__":
    scraper = AutotraderWebscraper()
    scraper.go_to_home()
    if scraper.check_for_cookie_prompt():
        scraper.accept_cookies()

    print(scraper.check_for_cookie_prompt())