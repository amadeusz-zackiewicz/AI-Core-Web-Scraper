from lib2to3.pgen2 import driver
from selenium import webdriver
from time import sleep

class WebScraperBase:
    def __init__(self):
        self.driver = webdriver.Firefox()
        print(self.driver.get("https://coinmarketcap.com/"))