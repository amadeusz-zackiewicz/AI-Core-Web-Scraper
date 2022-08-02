from app.webscrapers.autotrader_scraper import AutotraderWebscraper

import getopt
import sys

if __name__ == "__main__":
    s3_bucket = None
    s3_region = "us-east-1"
    local_data = "raw_data/"
    local_images = "images/"
    db_args = None
    headless = False

    terminal_args, _ = getopt.gnu_getopt(sys.argv[1:], "-h", [
        "headless",
        "local_data=",
        "local_images=",
        "s3_bucket=", 
        "s3_region=", 
        "db_args="
        ])

    for o, a in terminal_args:
        if o == "--local_data":
            local_data = a
        if o == "--local_images":
            local_images = a
        if o == "--s3_bucket":
            s3_bucket = a
        if o == "--s3_region":
            s3_region = a
        if o == "--db_args":
            db_args = a
        if o == "-h" or o == "--headless":
            headless = True

    scraper = AutotraderWebscraper("autotrader_default", headless=headless, data_folder=local_data,image_folder=local_images, s3_bucket=s3_bucket, s3_region=s3_region, db_args=db_args)
    try:
        scraper.run()
    except:
        scraper.close()