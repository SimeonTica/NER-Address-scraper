import pandas as pd
import requests

def get_country(postcode):
    try:
        username = 'simeh86'
        countryCodeUrl = f'http://api.geonames.org/searchJSON?name={postcode}&maxRows=1&username={username}'
        response = requests.get(countryCodeUrl)
        if response.status_code == 200:
            data = response.json() 
            return data['geonames'][0]['countryName']
        else:
            return 'None' 
    except Exception as e:
        print("Error occurred while fetching country name: ", e)
        return 'None'


def editAddresses():
    addressesDf = pd.read_csv('addresses.csv', sep='\t')
    addressesDf.dropna(subset=['road with number'], inplace=True)

    for state in addressesDf['state']:
        if state != 'None':
            country = get_country(state)
            addressesDf.loc[addressesDf['state'] == state, 'country'] = country

    addressesDf.to_csv('addresses_edited.csv', sep='\t', index=False)