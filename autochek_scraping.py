import sys
import logging
import time

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

page_num = 1

logging.basicConfig(level=logging.DEBUG)

BASE_URL = 'https://autochek.africa/gh/cars-for-sale'
page_num = 1

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}


def get_page(url):
    """
    Function for getting a page using a url.
    Sleep for 1 second before every request. Just to be good citizens of the internet.
    """
    time.sleep(2)
    page = requests.get(url, headers=HEADERS)
    page.encoding = 'utf-8'
    return page.text

def collect_page_info(url):
    """
    This function collects the car items on every page, parses it and 
    calls the function collect_car_details_and_store_in_mongo to retrieve 
    the cars details and store in mongodb.
    """
    logging.info("getting page for url: {}".format(url))
    page = get_page(url)

    #Parsing with BeautifulSoup
    logging.info("Parsing page response with BeautifulSoup")
    page_content = BeautifulSoup(page.encode('utf-8','ignore'), 'html.parser')

    #HTML tag that contains data I want to scrape
    all_cars = page_content.find_all('div', attrs={'class':'car-item'})

    print(all_cars)

    #calling the collect_car_details_and_store_in_mongo function and passing the all_cars variable to it
    collect_car_details_and_store_in_mongo(all_cars)

    #checking if there is more data
    end = page_content.find("a", {"class": "js-handle-click-ctr", "text":"500"})

    if end is None:
        logging.info("On to the next page")
        #if end returns nothing, then there is more data
        global page_num
        # page_num += 1
        new_url = BASE_URL + "?country=gh&page_number={}".format(page_num)
        collect_page_info(new_url)

    else:
        logging.info("No more data to scrape")
        sys.exit(1)

def collect_car_details_and_store_in_mongo(content):
    """
    This function extracts car details from a page, and saves it in mongodb
    """
    logging.info("Connecting to MongoDB")
    client = MongoClient('mongodb+srv://adubea_baidoo:nIOayw2UM4THZ8RL@all-cars.6hhg73m.mongodb.net/?retryWrites=true&w=majority')

    logging.info("Scraping data")
    
    #looping through tag we will be scraping 
    for each in content:
        link = each.get('href')

        new_link = 'https://autochek.africa/en/gh/car/' + link
        req = get_page(new_link)
        r_content = BeautifulSoup(req, 'html.parser')

        extract = {}

        listing = r_content.find("h1", attrs={"itemprop":"name"}).text
        extract['Listing'] = listing

        price = r_content.find("h1", attrs={"itemprop":"name"}).find_next('h5').text
        # price = r_content.find("span", attrs={"itemprop":"price"}).text
        extract['Price'] = price

        details = r_content.find("div", attrs={"class":"main-details__tags flex wrap"}).text
        extract['Details'] = details

        overview = r_content.find("div", attrs={"class":"svg flex"}).text
        extract['Overview'] = overview

        all_data = r_content.find('div', attrs={'class':'general-info grid'})
        no_class_attribute = all_data.find_all("div", attrs={"class": None})
        for i in no_class_attribute:
            extract[i.find('span', attrs={'class':None}).text] = i.find('p', attrs={'class': None}).text

        
        extract['URL'] = new_link
        extract['Source'] = "Autochek"

        print(extract)
        
        logging.info("Saving to MongoDB")
        # client.all_cars.autochek.insert_one(extract)
 

if __name__ == "__main__":
    collect_page_info(BASE_URL)