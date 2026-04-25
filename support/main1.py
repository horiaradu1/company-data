import re
import os
import requests
from bs4 import BeautifulSoup, Comment
from concurrent.futures import ThreadPoolExecutor
from collections import Counter

def clean_domain(url: str) -> str:
    url = re.sub(r'^https?://', '', url.strip())
    url = re.sub(r'^www\.', '', url)
    return url.split('/')[0].split('?')[0]

def clean_soup(soup: BeautifulSoup) -> BeautifulSoup:
    # TODO: Test on all data with different attributes to see perf impact and if we actually needed some of those attributes
    for tag in soup(["style", "script"]): # TODO: Are those all the tags?
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr.startswith(("data-", "aria-", "on")):
                del tag[attr]
        del tag["style"]

    return soup

def extract_website_data(response_soup: BeautifulSoup) -> tuple:
    """Return: (phone_numbers, social_media_links, addresses)."""
    # TODO: Implement scraping logic

    

    return (
        [], # phone numbers
        [], # social media links
        []  # address / location
    )

def process_website(website: str) -> tuple[str, int, list, list, list]:
    """Return: (website, status_code, phone_numbers, social_media_links, addresses)."""
    # TODO: Replace print with thread log
    website = clean_domain(website)
    print(f"Processing website: {website}")
    try:
        url = website if website.startswith("https") else f"https://{website}"
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            # print(f"Response json: {response.json}")
            # print(f"Response text: {response.text}")
            soup = BeautifulSoup(response.text, "html.parser")
            soup = clean_soup(soup)

            # Save response to file for testing
            # TODO: Implement response caching to avoid fetching same website
            with open(f"responses/response_{website.replace('.', '_')}.html", "w") as f:
                f.write(str(soup.prettify()))
                # f.write(str(soup))

            return (website, response.status_code, *extract_website_data(soup))
        
        return (website, response.status_code, [], [], [])
    except Exception as e:
        print(f"Error: {e}")
    
    return (website, 0, [], [], [])

    
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # SAMPLE_WEBSITES_PATH = r"../docs/Task 1 Company Data API/sample-websites.csv"
    SAMPLE_WEBSITES_PATH = os.path.join(BASE_DIR, "../docs/Task 1 Company Data API/sample-websites.csv")
    TIMEOUT_SECONDS = 5
    THREAD_POOL_WORKERS = 5

    # mkdir responses if not exists
    import os
    if not os.path.exists("responses"):
        os.makedirs("responses")
    
    websites = []
    websites_data = dict()
    raw_websites_data = []

    # Read websites from file
    with open(SAMPLE_WEBSITES_PATH, "r") as f:
        next(f)
        for line in f:
            websites.append(line.strip())
    
    print(f"Total websites: {len(websites)}")
    print(f"First 3 websites: {websites[:3]}")
    print(f"Last 3 websites: {websites[-3:]}")

    # Check unique websites
    # websites = set(websites)
    websites = sorted(set(websites))
    websites = list(websites)
    print(f"Unique websites: {len(websites)}")

    # Randomly sample 10 websites for testing
    # TODO: Remove in prod
    import random
    random.seed(1234)
    random.shuffle(websites)
    websites = websites[:10]
    print(f"Sampled websites: {websites}")

    # Needs parallel processing for speed
    # TODO: Use submit instead of map to handle exceptions better and log progress?
    with ThreadPoolExecutor(max_workers=THREAD_POOL_WORKERS) as executor:
        raw_websites_data = list(executor.map(process_website, websites))
    statuscode_counts = Counter([data[1] for data in raw_websites_data])
    print(f"Status code counts: {statuscode_counts}")

    # Merge raw into structured
    for i in range(len(websites)):
        websites_data[raw_websites_data[i][0]] = {
            "status_code": raw_websites_data[i][1],
            "phone_numbers": raw_websites_data[i][2],
            "social_media_links": raw_websites_data[i][3],
            "address": raw_websites_data[i][4]
        }

    print(f"Websites data count: {len(websites_data)}")
    print(f"Websites data: {websites_data}")