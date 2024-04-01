# Import necessary modules from the AddressParser package
from AddressParser import scraper
from AddressParser import editingData
from AddressParser import addressDetectionGliner

# This script is used to scrape all sites, parse addresses, and edit addresses.

if __name__ == '__main__':
    # Scrape all sites from the provided parquet file.
    # The file should contain a list of company websites.
    scraper.scrapeAllSites('list of company websites.snappy.parquet')
    
    # Parse addresses with a threshold of 0.4.
    # The threshold is used to determine the confidence level for address detection.
    addressDetectionGliner.parseAddresses(0.4)
    
    # Edit the addresses obtained from the previous steps.
    # This function will perform cleaning on the addresses. (Experimental feature)
    editingData.editAddresses()