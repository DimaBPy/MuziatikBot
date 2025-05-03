import requests

CATS = 'https://api.thecatapi.com/v1/images/search'
response = requests.get(CATS).json()