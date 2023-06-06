import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re


def parse_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        xml_content = response.content
        root = ET.fromstring(xml_content)

        urls = []
        last_mod_dates = []

        for child in root:
            loc_element = child.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            lastmod_element = child.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')

            if loc_element is not None and lastmod_element is not None:
                loc = loc_element.text
                lastmod = lastmod_element.text

                urls.append(loc)
                last_mod_dates.append(lastmod)

        return urls, last_mod_dates

    except ET.ParseError as e:
        print(f"An error occurred while parsing sitemap.xml for {sitemap_url}: {e}")
        return [], []
    except Exception as e:
        print(f"An error occurred for {sitemap_url}: {e}")
        return [], []


with open(r'domainspostcheck.txt', 'r') as file:
    websites = file.read().splitlines()

for site in websites:
    sitemap_url = site + '/sitemap.xml'

    try:
        urls, last_mod_dates = parse_sitemap(sitemap_url)
        if urls:
            latest_date = None
            latest_url = None

            for i in range(len(urls)):
                date_string = re.sub(r'[+-]\d{2}:?\d{2}$', '', last_mod_dates[i])
                current_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=None)

                if latest_date is None or current_date > latest_date:
                    latest_date = current_date
                    latest_url = urls[i]

            if latest_date:
                latest_date = latest_date.strftime("%B %d, %Y")

                print("Domain: ", site)
                print("Last Post URL: ", latest_url)
                print("Last Post Date: ", latest_date)
                print("------------------------")
            else:
                print("No sitemap.xml found for ", site)

        else:
            print("No sitemap.xml found for ", site)

    except Exception as e:
        print(f"An error occurred for {site}: {e}")
        print("Skipping to the next website...")
        print("------------------------")
        continue
