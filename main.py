from app.webscrapers.autotrader_scraper import AutotraderWebscraper

import getopt
import sys

if __name__ == "__main__":
    s3_bucket = None
    s3_region = "us-east-1"

    terminal_args, _ = getopt.gnu_getopt(sys.argv[1:], "", ["s3_bucket=", "s3_region="])

    for o, a in terminal_args:
        if o == "--s3_bucket":
            s3_bucket = a
        if o == "--s3_region":
            s3_region = a

    scraper = AutotraderWebscraper("autotrader_london_red_hatchbacks", headless=False, data_folder="raw_data/",image_folder="images/", s3_bucket=s3_bucket, s3_region=s3_region)
    scraper.run()