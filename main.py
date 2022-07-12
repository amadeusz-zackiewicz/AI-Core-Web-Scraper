from app.webscrapers.autotrader_scraper import AutotraderWebscraper
import os
import platform

if __name__ == "__main__":
    scraper = AutotraderWebscraper("autotrader_london_red_hatchbacks", headless=False)
    scraper.go_to_home()
    if scraper.check_for_cookie_prompt():
        scraper.accept_cookies()
    scraper.search()
    scraper.scrape_links()
    scraper.scrape_all_details()
    scraper.close()


    project_root_path = os.path.dirname(os.path.abspath(__file__))
    if platform.system == "Linux":
        os.popen(f"xdg-open {project_root_path}/data/results.csv")
    elif platform.system == "Windows":
        os.popen(f"{project_root_path}/data/results.csv")