from addressParser import AddressParser
from unidecode import unidecode
import pandas as pd
import requests
import spacy
import glob
import os

address_parser_path = r'C:\Workbench\libpostal\src\address_parser.exe'
libpostal_path = r'C:\Workbench\libpostal\src\libpostal.exe'
parser = AddressParser(address_parser_path, libpostal_path)

nlps = spacy.load('en_core_web_lg')

addresses = []
addressesDf = pd.DataFrame()

addressesDf.to_csv('addresses.csv', sep='\t', index=False)

def get_country_by_postcode(postcode):
    try:
        username = 'simeh86'  # Replace with your GeoNames username
        countryCodeUrl = f'http://api.geonames.org/searchJSON?name={postcode}&maxRows=1&username={username}'
        response = requests.get(countryCodeUrl)
        if response.status_code == 200:
            data = response.json() 
            return data['geonames'][0]['countryName']
    except Exception as e:
        print("Error occurred while fetching country name: ", e)
path = os.getcwd() + '\\CSVs\\'
csv_files = glob.glob(os.path.join(path, "*.csv")) 

for f in csv_files:
    df = pd.read_csv(f, sep='\t')

    df.drop_duplicates(subset=['text'], keep='first', inplace=True)

    pattern = r'[^\w\s]'

    df['text'] = df['text'].replace(r'\n', ' ', regex=True)
    df['text'] = df['text'].replace(pattern, '', regex=True)
    df['text'] = df['text'].apply(lambda x: unidecode(str(x)))

    df = df.drop(df.text[df.text.str.len() > 2000].index)

    for row in df['text']:
        processed_text = nlps(str(row))
        ok = [0, 0]
        ents = []
        for ent in processed_text.ents:
            # print(ent.text, ent.label_)
            ents.append(ent.text)
            if ent.label_ in 'GPE':
                ok[0] = 1
            if ent.label_ in 'CARDINAL':
                ok[1] = 1
        if ok != [1, 1]:
            df.drop(df[df['text'] == row].index, inplace=True)
        else:
            df['text'] = df['text'].replace(row, ' '.join(ents))
        # print('\n')
        # input()

    for addressLine in df['text']:
        address = addressLine
        try:
            parsed_address = parser.parse_address(address)
            if(parsed_address['city'] != None):
                country_name = get_country_by_postcode(parsed_address['postcode'])
                parsed_address['country'] = country_name
                addresses.append(parsed_address)
                addressesDf = pd.DataFrame(addresses)
                addressesDf = addressesDf.drop('house', axis=1)
                # print(addressesDf)
                addressesDf.to_csv('addresses.csv', sep='\t', index=False)

        except (FileNotFoundError, RuntimeError) as e:
            continue
        except Exception as e:
            # print("Failed to parse address: ", e)
            continue


