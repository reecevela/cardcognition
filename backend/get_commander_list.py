import requests
import re

# Make a request to the Scryfall API to get a list of all Commander cards
response = requests.get('https://api.scryfall.com/cards/search?q=is%3Acommander')

full_query = response.json()

if response.json()['has_more']:
    while response.json()['has_more']:
        response = requests.get(response.json()['next_page'])
        full_query['data'].extend(response.json()['data'])

print(len(full_query['data']))

# Parse the response JSON to get the name of each Commander card
commanders = [card['name'] for card in full_query['data']]

# Convert each Commander name to the correct format
formatted_commanders = []
for commander in commanders:
    first_name = commander.split(' // ')[0]  # Keep only the first part when there are two names separated by ' // '
    formatted_name = first_name.lower().replace(' ', '-').replace("\"", "").replace("'", "").replace(",", "").replace(".", "")
    formatted_commanders.append(formatted_name)
    
# Write the formatted Commander names to a text file
with open('commanders.txt', 'w') as f:
    f.write('\n'.join(formatted_commanders))
