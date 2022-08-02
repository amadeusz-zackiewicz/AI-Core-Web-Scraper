# What is this project?
A data collection pipeline that scrapes the web and uploads that data into specified cloud storage or local machine.

### How to run this:
1. In the terminal navigate to the root folder of the project.
2. Now run the main.py file with python.

The following arguments are available:

- `-h` or `--headless` to run this program without GUI.

- `--local_data` to specify where data should be saved on the local machine. 

Example:
- `--local_data=data/raw/`

- `--local_images` to specify where images should be sabed on the local machine. 

Example: `--local_images=data/images/`

- `--s3_bucket` to specify the name of the AWS S3 bucket that will receive image data.

- `--s3_region` to specify which region the bucket is located in. (defaults to us-east-1)

Example: `--s3_region=eu-west-2 --s3_bucket=my-bucket-name`

- `db_args` to specify connection information for the database.

Example: `--db_args="host=localhost dbname=postgres user=postgres password=postgres"`

---

## Milestone 1
I have decided to scrape data about cars from autotrader.co.uk as I can see this data having an actual practical use.

---

## Milestone 2
I have managed to bypass the cookies prompt and navigate to the search page. The search page will then be filled in based on the created json config file that allows the user to search only for relevant data.

### Improvements to be made:
Instead of creating a whole algorithm for clicking and selecting options, I could've manually analysed how the search URL is created based on the options; while I have wasted some time doing this I have also learnt how to deal with buttons that are designed to block scraping, drop down menus and dynamically changing tick boxes. A better way of approaching this would've been to simply create a generator method that would generate a URL based on the config file, speeding up the process.

## Milestone 2.5
I have decided to refactor the search method to generate a URL instead of navigating to the advanced search page and simulating user input. This has reduced the amount of time the scraper spends getting the results significantly. 

---

## Milestone 3
I have created a folder where the data is going to be stored and prepared a function to save the data into a .json file. Then I started to scrape all the listing IDs from the search results, in this case all I had to to was to get a single attribute, and detecting if the listing was an advert, required me to check if it had a specific attribute attached. 

Every ID is being checked to prevent rescraping the same data by checking if a file for it already exists. Using urllib I'm also downloading the main image that is displayed for each listing and saving them in images folder.

---

## Milestone 4
I have made the scrapers more test friendly by making it possible to provide custom config file and change the directory where the data is scraped. 

I have also added unit tests for the Autotrader scraper, to run the tests you can run the 'test_all.sh' file from the terminal.

---

## Milestone 5
I have installed and set up a local postgresql database and AWS CLI on my machine for testing then I created an AWS account to set up S3 storage instance, RDS instance and an EC2 instance. I will be using the S3 to store images, RDS to store the data and the EC2 to run my data collection. The option to save files on the local machine is still available. 

---