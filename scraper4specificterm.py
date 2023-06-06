import requests
from bs4 import BeautifulSoup

def search_in_source(file_path, search_terms):
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file]

    for url in urls:
        try:
            response = requests.get('http://' + url)  
            response.raise_for_status() 
        except requests.HTTPError as http_err:
            print(f'HTTP error occurred for {url}: {http_err}')
            continue
        except Exception as err:
            print(f'Error occurred for {url}: {err}')
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        for search_term in search_terms:
            if search_term in soup.prettify():
                print(f'The term "{search_term}" was found in the source code of {url}')
            else:
                print(f'The term "{search_term}" was not found in the source code of {url}')


search_terms = ['wordofchoise', 'wordofchoise2,3,4,5']
search_in_source('domains1.txt', search_terms)
