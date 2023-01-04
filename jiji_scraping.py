import sys
import logging
import time

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG)

BASE_URL = 'https://jiji.com.gh/cars'
page_num = 1

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}


def get_page(url):
    """
    Function for getting a page using a url.
    Sleep for 1 second before every request. Just to be good citizens of the internet.
    """
    time.sleep(1)
    page = requests.get(url, headers=HEADERS)
    page.encoding = 'utf-8'
    return page
    # return page.text

def collect_page_info(url):
    """
    This function collects the car items on every page, parses it and 
    calls the function collect_car_details_and_store_in_mongo to retrieve 
    the cars details and store in mongodb.
    """ 
    logging.info("getting page for url: {}".format(url))
    print(url)
    sys.exit(1)
    # page = get_page(url)
    # print(page)

    #Parsing with BeautifulSoup
    logging.info("Parsing page response with BeautifulSoup")
    page_content = BeautifulSoup(page.encode('utf-8','ignore'), 'html.parser')

    # print(page_content)

    #HTML tag that contains data I want to scrape
    all_cars = page_content.find_all('a')
    # attrs={"class":'b-list-advert-base qa-advert-list-item b-list-advert-base--vip b-list-advert-base--gallery'})

    print(all_cars)

    #calling the collect_car_details_and_store_in_mongo function and passing the all_cars variable to it
    collect_car_details_and_store_in_mongo(all_cars)

    #checking if there is more data
    # end = page_content.find("a", {"class": "product__item flex"})

    # if end is None:
    #     logging.info("No more data to scrape")
    # else:
    #     logging.info("On to the next page")
    #     #if end returns nothing, then there is more data
    # global page_num
    #     page_num += 1
    new_url = BASE_URL
    collect_page_info(new_url)
    sys.exit(1)

    # collect_page_info(BASE_URL)
    # sys.exit(1)

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

        new_link = 'https://jiji.com.gh/' + link
        req = get_page(new_link)
        r_content = BeautifulSoup(req, 'html.parser')

        extract = {}

        listing = r_content.find("h1", attrs={"class":"qa-advert-title b-advert-title-outer"}).text
        extract['Listing'] = listing

        price = r_content.find("span", attrs={"class":"qa-advert-price-view-title b-alt-advert-price__text"}).text
        extract['Price'] = price

        details = r_content.find("div", attrs={"class":"b-advert-icon-attributes-container"}).text
        extract['Details'] = details

        all_data = r_content.find('div', attrs={'class':'b-advert-attributes--tiles'})
        class_attribute = all_data.find_all("div", attrs={"class": 'b-advert-attribute'})
        for i in class_attribute:
            extract[i.find('div', attrs={'class':'b-advert-attribute__key'}).text] = i.find('div', attrs={'class':'b-advert-attribute__value'}).text

        
        extract['URL'] = new_link
        extract['Source'] = "Jiji"

        print(extract)
        
        logging.info("Saving to MongoDB")
        # client.all_cars.jiji.insert_one(extract)


if __name__ == "__main__":
    collect_page_info(BASE_URL)
