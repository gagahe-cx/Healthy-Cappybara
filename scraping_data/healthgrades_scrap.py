import time
import requests
from urllib.parse import urlparse
import sys
import json
import lxml.html
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

ALLOWED_DOMAINS = ("https://www.healthgrades.com",)
REQUEST_DELAY = 1


def make_request(url):
    """
    Make a request to `url` and return the raw response.

    This function ensure that the domain matches what is expected and that the rate limit
    is obeyed.
    """
    # check if URL starts with an allowed domain name
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    for domain in ALLOWED_DOMAINS:
        if url.startswith(domain):
            break
    else:
        raise ValueError(f"can not fetch {url}, must be in {ALLOWED_DOMAINS}")
    time.sleep(REQUEST_DELAY)
    print(f"Fetching {url}")
    resp = requests.get(url, headers = headers)
    return resp


def make_link_absolute(rel_url, current_url):
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


def get_directory(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(10)    
    html_content = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        if link.get('href') and "directory" in link.get('href') and "https:" not in link.get('href') and 'specialty' not in link.get('href') and '/urgent-care-directory' not in link.get('href'):
            links.append(link.get('href'))
    return links
    

def get_illinois(url, state):
    '''
    Generalization of get state url, this could be replaced by url += state
    '''
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://www.healthgrades.com" + url)
    driver.implicitly_wait(10)  
    html_content = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        if link.get('href') and state in link.get('href'):
            links.append(link.get('href'))
    return links[0]


def get_city(url):
    url += '/il-illinois'
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://www.healthgrades.com" + url)
    driver.implicitly_wait(10)  
    html_content = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        if link.get('href') and "illinois/" in link.get('href'):
            links.append(link.get('href'))
    return links


def get_doctor_url(url):
    response = make_request(url)
    root = lxml.html.fromstring(response.text)
    links = root.xpath('//h3[@class="card-name card-name--link"]//a[@href]')
    return links


def get_next_page_url(url):
    response = make_request(url)
    root = lxml.html.fromstring(response.text)
    next_page_link = root.xpath('//a[@aria-label="Next Page"]/@href')
    if next_page_link:
        next_page_url = make_link_absolute(next_page_link[0], url)
        return next_page_url
    else:
        return None


def crawl_each_doctor(url):
    results = {}
    response = requests.get(url)
    root = lxml.html.fromstring(response.text)
    address = " ".join(root.xpath("//address[@class='location-row-address']/text()"))

    if not address:
        add_1 = root.xpath("//span[@data-qa-target='practice-address-street']/text()")
        add_2 = root.xpath("//span[@data-qa-target='practice-address-city']/text()")
        add_3 = root.xpath("//span[@data-qa-target='practice-address-state']/text()")
        add_4 = root.xpath("//span[@data-qa-target='practice-address-postalCode']/text()")
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
        "ratings": '//button[@class="star-reviews-count star-reviews-count-sm star-reviews-standard-redesign"]/text()'
    }

    for key, xpath in queries.items():
        query_result = root.xpath(xpath)
        results[key] = query_result[0] if query_result else 'Null'

    return results


def crawl(max_direc_to_crawl, max_city_to_crawl, max_pages_to_crawl, url):
    """
    This function starts at the base URL for the parks site and
    crawls through each page of parks, scraping each park page
    and saving output to a file named "parks.json".

    Parameters:
        * max_parks_to_crawl:  the maximum number of pages to crawl
    """
    doctors = []
    urls_visited = 0

    if not url:
        return
    
    directory_urls = get_directory(url)[:max_direc_to_crawl]
    base_city_url = "https://www.healthgrades.com"
    cities = [
        f"{base_city_url}{city}_1" 
        for url in directory_urls
        for city in get_city(url)[:max_city_to_crawl]
    ]
    print(cities)

    for city_url in cities:
        urls_visited = 0
        while city_url and urls_visited < max_pages_to_crawl:
            doctor_urls = get_doctor_url(city_url)

            for url in doctor_urls:
                url = url.get('href')
                doctor_info = crawl_each_doctor("https://www.healthgrades.com" + url)
                doctors.append(doctor_info)
            
            city_url = get_next_page_url(city_url)
            urls_visited += 1

    with open("doctors.json", "w") as f:
        json.dump(doctors, f, indent=1)
