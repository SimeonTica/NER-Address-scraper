# Import necessary modules
from gliner import GLiNER
from unidecode import unidecode
import pandas as pd
import glob
import os

# Function to parse addresses from text files
def parseAddresses(threshold=0.4):
    # Load the GLiNER model
    model = GLiNER.from_pretrained("urchade/gliner_base")
    # Define the labels for the entities to be extracted
    labels = ['region', 'city', 'postcode', 'road with number', 'country', 'state']

    # Initialize a dictionary to store the extracted addresses
    addresses = {'site': [], 'region': [], 'city': [], 'postcode': [], 'road with number': [], 'country': [], 'state': []}
    # Initialize a DataFrame to store the addresses
    addressesDf = pd.DataFrame()

    # Save the empty DataFrame to a CSV file
    addressesDf.to_csv('addresses.csv', sep='\t', index=False)

    # Get the current directory and the path to the 'TXTs' directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, 'TXTs')
    # Get a list of all text files in the 'TXTs' directory
    txt_files = glob.glob(os.path.join(path, "*.txt")) 

    # Loop through all text files in the directory
    for f in txt_files:
        # Open the current file in read mode with utf-8 encoding
        file = open(f, 'r', encoding='utf-8')
        print(f"Processing file: {f}\n")
        # Read the entire content of the file into a string
        text = file.read()

        # Replace newline characters with spaces and decode the text
        text = text.replace('\n', ' ')
        text = unidecode(text)
        try:
            # If the text is not empty, predict entities in the text
            if text != "":
                entities = model.predict_entities(text, labels, threshold=threshold)
                # For each entity, append the entity text to the corresponding label in the addresses dictionary
                for ent in entities:
                    addresses[ent['label']].append(ent['text'])
                # Find the maximum length of the lists in the addresses dictionary
                max_len = max([len(addresses[key]) for key in addresses.keys()])
                # For each key in the addresses dictionary, if the list is shorter than max_len, append the filename (for 'site') or 'None' (for other keys)
                for key in addresses.keys():
                    while len(addresses[key]) < max_len:
                        if key == 'site':
                            filename = os.path.basename(f)
                            addresses[key].append(filename[:filename.find('.txt')])
                        else:
                            addresses[key].append('None')
                # Convert the addresses dictionary to a pandas DataFrame
                addressesDf = pd.DataFrame(addresses)

                # Save the DataFrame to a CSV file
                addressesDf.to_csv('addresses.csv', sep='\t', index=False)
        except Exception as e:
            # Print any exceptions that occur during the parsing process
            print("Failed to parse text: ", e)
            continue