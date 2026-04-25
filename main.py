import requests
from concurrent.futures import ThreadPoolExecutor
import collections

def extract_website_date(response_text: str) -> tuple:
    # TODO: Implement scraping logic
    status = 200
    return (
        [], # phone numbers
        [], # social media links
        []  # address / location
    )

def process_website(website: str) -> tuple[str, int, list, list, list]:
    """Return: (website, status_code, phone_numbers, social_media_links, addresses)."""
    # TODO: Replace print with thread log
    print(f"Processing website: {website}")
    try:
        url = website if website.startswith("https") else f"https://{website}"
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response json: {response.json}")
            #print(f"Response text: {response.text}")

            # Save response to file for testing
            # TODO: Implement response caching to avoid fetching same website
            with open(f"responses/response_{website.replace('.', '_')}.txt", "w") as f:
                f.write(response.text)

            return (website, response.status_code, *extract_website_date(response.text))
        
        return (website, response.status_code, [], [], [])
    except Exception as e:
        print(f"Error: {e}")
    
    return (website, 0, [], [], [])

    
if __name__ == "__main__":
    SAMPLE_WEBSITES_PATH = r"docs/Task 1 Company Data API/sample-websites.csv"
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
    websites = set(websites)
    websites = list(websites)
    print(f"Unique websites: {len(websites)}")

    # Randomly sample 10 websites for testing
    # TODO: Remove in prod
    import random
    random.shuffle(websites)
    websites = websites[:10]
    print(f"Sampled websites: {websites}")

    # Needs parallel processing for speed
    # TODO: Use submit instead of map to handle exceptions better and log progress?
    with ThreadPoolExecutor(max_workers=THREAD_POOL_WORKERS) as executor:
        raw_websites_data = list(executor.map(process_website, websites))
    statuscode_counts = collections.Counter([data[1] for data in raw_websites_data])
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