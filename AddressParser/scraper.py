# Import necessary modules
import os.path
import pandas as pd
import multiprocessing 
from multiprocessing import Pool
from multiprocessing import Lock

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

# Create a lock object to prevent race conditions
lock = Lock()

# Function to scrape a single URL
def scrape(url):
    try:
        # Add 'https://' to the start of the URL if it's not already there
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        print("Scraping:", url)
        # Set up Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")

        # Start the Chrome driver
        driver = webdriver.Chrome()
        driver.get(url)

        # Get the text of the HTML body
        html_tag = driver.find_element(By.XPATH, '/html/body')
        text = html_tag.text
        text.replace('\n', ' ')

        # Remove 'https://' or 'http://' from the URL and replace '/' with ' '
        if url.find("https://") != -1:
            x = url.replace("https://", "")
        else:
            x = url.replace("http://", "")
        x = x.replace("/", " ")
        x = x[:x.find(" ") if x.find(" ") != -1 else len(x)]
        
        # Get the current directory and the path to the 'TXTs' directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        txt_dir = os.path.join(current_dir, 'TXTs')

        # Write the text to a file in the 'TXTs' directory
        with lock:
            if f'{x}.txt' not in os.listdir(txt_dir):
                if os.access(txt_dir, os.W_OK):
                    print(f"Writing to {txt_dir}/{x}.txt")
                    f = open(f'{txt_dir}/{x}.txt', 'w', encoding='utf-8')
                    f.write(text)
                else:
                    print(f"Do not have write permissions for '{txt_dir}' directory")

    # Handle exceptions
    except selenium.common.exceptions.StaleElementReferenceException:
        print("StaleElementReferenceException")
    except WebDriverException:
        print(f"Failed to scrape {url} due to connection timeout.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Quit the driver
        try:
            driver.quit()
        except UnboundLocalError:
            pass

# Function to scrape multiple URLs in parallel
def parallel_scrape(urls):
    with Pool(processes=10) as pool:
        all_embeded_urls = pool.map(scrape, urls)
    
    return all_embeded_urls

# Function to scrape all sites from a database of links
def scrapeAllSites(linksDatabase):
    # Load the links from the database
    links = pd.read_parquet(linksDatabase, engine='pyarrow')
    linkArray = links["domain"].to_list()

    # Scrape all the links
    emb = parallel_scrape(linkArray)
    parallel_scrape(emb)