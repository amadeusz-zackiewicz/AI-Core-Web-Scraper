# What is this project?
A simple web scraper that can is capable of obtaining information about car listings from autotrader.co.uk.
## Milestone 1
I have decided to scrape data about cars from autotrader.co.uk as I can see this data having an actual practical use.
## Milestone 2
I have managed to bypass the cookies prompt and navigate to the search page. The search page will then be filled in based on the created json config file that allows the user to search only for relevant data.

### Improvements to be made:
Instead of creating a whole algorithm for clicking and selecting options, I could've manually analysed how the search URL is created based on the options; while I have wasted some time doing this I have also learnt how to deal with buttons that are designed to block scraping, drop down menus and dynamically changing tick boxes. A better way of approaching this would've been to simply create a generator method that would generate a URL based on the config file, speeding up the process.

## Milestone 2.5
I have decided to refactor the search method to generate a URL instead of navigating to the advanced search page and simulating user input. This has reduced the amount of time the scraper spends getting the results significantly. 

## Milestone 3
I have created a folder where the data is going to be stored and prepared a function to save the data into a .json file. Then I started to scrape all the listing IDs from the search results, in this case all I had to to was to get a single attribute, and detecting if the listing was an advert, required me to check if it had a specific attribute attached. Every ID is being checked to prevent rescraping the same data by checking if a file for it already exists. Using urllib I'm also downloading the main image that is displayed for each listing and saving them in images folder.