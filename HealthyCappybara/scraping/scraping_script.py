'''
Written by: Yijia (Gaga) He
'''
import time
import requests
import os
import json
import sys
import pathlib
import lxml.html
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

ALLOWED_DOMAINS = ("https://www.healthgrades.com",)
REQUEST_DELAY = 1

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
})


def make_request(url):
    # This function follows CAPP122 PA2 taught by James Turk
    """
    Make a request to `url` and return the raw response.
    """
    if not any(url.startswith(domain) for domain in ALLOWED_DOMAINS):
        raise ValueError(f"cannot fetch {url}, must be in {ALLOWED_DOMAINS}")
    
    sleep(REQUEST_DELAY)
    print(f"Fetching {url}")
    response = session.get(url)
    response.raise_for_status()  
    return response

def make_link_absolute(rel_url, current_url):
    # This function is taken from CAPP122 PA2 taught by James Turk
    """
    Given a relative URL like "/abc/def" or "?page=2"
    and a complete URL like "https://example.com/1/2/3" this function will
    combine the two yielding a URL like "https://example.com/abc/def"

    Parameters:
        * rel_url:      a URL or fragment
        * current_url:  a complete URL used to make the request that contained a link to rel_url

    Returns:
        A full URL with protocol & domain that refers to rel_url.
    """
    url = urlparse(current_url)
    if rel_url.startswith("/"):
        return f"{url.scheme}://{url.netloc}{rel_url}"
    elif rel_url.startswith("?"):
        return f"{url.scheme}://{url.netloc}{url.path}{rel_url}"
    else:
        return rel_url


def get_doctor_url(url):
    """
    Extracts and returns a list of doctor profile URLs from a given webpage URL.
    
    Args:
        url (str): The URL of the webpage to scrape doctor profile links from.
        
    Returns:
        list: A list of absolute URLs to individual doctor profiles found on the 
            page.
    """
    response = make_request(url)
    root = lxml.html.fromstring(response.text)
    links = root.xpath('//h3[@class="card-name card-name--link"]//a[@href]')
    return [make_link_absolute(link, url) for link in links]


def get_next_page_url(url):
    """
    Determines and returns the URL of the next page of listings from the current 
        webpage.
    
    Args:
        url (str): The URL of the current webpage from which the next page URL 
        is to be found.
    
    Returns:
        str or None: The absolute URL of the next page if found, otherwise None.
    """
    response = make_request(url)
    root = lxml.html.fromstring(response.text)
    next_page_link = root.xpath('//a[@aria-label="Next Page"]/@href')
    
    if next_page_link:
        next_page_url = make_link_absolute(next_page_link[0], url)
        return next_page_url
    else:
        return None


def crawl_each_doctor(url):
    """
    Scrapes detailed information from a single doctor's profile page and returns 
        it as a dictionary.
    
    Args:
        url (str): The URL of the doctor's profile page to scrape.
    
    Returns:
        dict: A dictionary containing various pieces of information scraped from 
            the doctor's profile.
    """
    results = {}
    response = requests.get(url)
    root = lxml.html.fromstring(response.text)
    address = " ".join(root.xpath("//address[@class='location-row- \
        address']/text()"))

    # Deal with situation when address might be stored in other forms sometimes
    if not address:
        add_1 = root.xpath("//span[@data-qa-target='practice-address- \
            street']/text()")
        add_2 = root.xpath("//span[@data-qa-target='practice-address- \
            city']/text()")
        add_3 = root.xpath("//span[@data-qa-target='practice-address- \
            state']/text()")
        add_4 = root.xpath("//span[@data-qa-target='practice-address- \
            postalCode']/text()")
        address = ' '.join(add_1 + add_2 + add_3 + add_4) 
        
    title = " ".join(root.xpath("//title/text()"))
    results['address'] = address if address else 'Null'
    results['title'] = title if title else 'Null'
    queries = {
        "description": '//meta[@name="description"]/@content',
        "primarySpecialty": '//meta[@name="primarySpecialty"]/@content',
        "specialties": '//meta[@name="specialties"]/@content',
        "providerId": '//meta[@name="providerId"]/@content',
        "conditions": '//meta[@name="conditions"]/@content',
        "procedures": '//meta[@name="procedures"]/@content',
        "ratings": '//button[@class="star-reviews-count star-reviews-count-sm \
            star-reviews-standard-redesign"]/text()'
    }

    # Add doctors' each piece of information
    for key, xpath in queries.items():
        query_result = root.xpath(xpath)
        results[key] = query_result[0] if query_result else 'Null'

    return results


def fetch_html_content(url):
    """
    Fetches and returns the HTML content of a webpage. This is useful when the
        html file cannot parsed by urlparse
    
    Args:
        url (str): The URL of the webpage to fetch.
    
    Returns:
        str: The HTML content of the webpage.
    """
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = Chrome(service=Service(ChromeDriverManager().install()), \
        options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(10)
    html_content = driver.page_source
    driver.quit()
    return html_content


def get_directory(url):  
    """
    Scrapes and returns a list of directories(doctor categories) found on the 
        listed all directory page.
    
    Args:
        url (str): The URL of the webpage to scrape directory links from.
    
    Returns:
        list: A list of relative URLs to directory pages found on the webpage.
    """
    html_content = fetch_html_content(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []

    # Filter all directory base urls
    for link in soup.find_all('a'):
        if link.get('href') and "directory" in link.get('href') and "https:" \
            not in link.get('href') and 'specialty' not in link.get('href') \
            and '/urgent-care-directory' not in link.get('href'):
            links.append(link.get('href'))

    return links


def get_city(url):
    """
    Scrapes each city link from each directory (doctor category) link.
    
    Args:
        url (str): The base URL to append the path segment to before scraping.
    
    Returns:
        list: A list of relative URLs to city-specific pages found on the webpage.
    """
    url += '/il-illinois' 
    html_content = fetch_html_content(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []

    # Filter all city base urls
    for link in soup.find_all('a'):
        if link.get('href') and "illinois/" in link.get('href'):
            links.append(link.get('href'))

    return links


def crawl(max_direc_to_crawl, max_city_to_crawl, max_pages_to_crawl, url):
    """
    Crawls through directories, cities, and pages to scrape doctor information 
    and saves it to a JSON file.
    
    Args:
        max_direc_to_crawl (int): The maximum number of directories to crawl.
        max_city_to_crawl (int): The maximum number of cities to crawl within 
                            each directory.
        max_pages_to_crawl (int): The maximum number of pages to crawl within 
                            each city.
        url (str): The base URL to start crawling from.
    """
    doctors = []
    urls_visited = 0

    # Check whether the city has data on that directory (category)
    if not url:
        return
    
    # Find all links satisfying the input requiremnts
    directory_urls = get_directory(url)[:max_direc_to_crawl]
    cities = [
        f"{ALLOWED_DOMAINS[0]}{city}_1" 
        for url in directory_urls
        for city in get_city(url)[:max_city_to_crawl]
    ]

    # Fetch all the doctor data from links obtained above
    for city_url in cities:
        urls_visited = 0
        while city_url and urls_visited < max_pages_to_crawl:
            doctor_urls = get_doctor_url(city_url)

            for url in doctor_urls:
                url = url.get('href')
                doctor_info = crawl_each_doctor(ALLOWED_DOMAINS[0] + url)
                doctors.append(doctor_info)

            city_url = get_next_page_url(city_url)
            urls_visited += 1

    with open(f"{file_name}.json", "w") as f:
        json.dump(doctors, f, indent=1)


def merge_json_files(directory_path):
    """
    Merges data from multiple JSON files in current directory into a single JSON 
        file. This is helpful when the scrapper breaks at some times and leave 
        different json file for each scrape.
    
    Args:
        directory_path (str or Path): The path to the directory containing JSON 
                            files to be merged.
    """
    directory_path = os.path.expanduser(directory_path)
    merged_data = []  
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]  
    file_count = len(json_files)
    output_filename = f"doctors_data_{file_count}.json"

    # Merge all files end with json
    for filename in json_files:
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r') as f:
            data = json.load(f)
            merged_data.append(data) 

    with open(output_filename, 'w') as f:
        json.dump(merged_data, f, indent=4)

directory_path = pathlib.Path(__file__).parent / "../"
merge_json_files(directory_path)