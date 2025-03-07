import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import urllib.request
import time
import os
import json

with open('output.json', 'r', encoding='utf-8') as infile:
    data = json.load(infile)

folder_path = './down/'
os.makedirs(folder_path, exist_ok=True)

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options)


def safe_get_url(url, retries=3, wait_time=300):
    for attempt in range(retries):
        try:
            driver.get(url)
            return True
        except Exception as e:
            print(f"Error accessing URL (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
    print("Failed to access URL after retries, skipping...")
    return False


for item in data[...]:
    for key, value in item.items():
        if key not in ['word', 'voice', 'status'] and isinstance(value, dict):
            query = value['example']
            filename = value['img']
            url = f"https://www.google.com/search?q={query}&hl=en&tbm=isch"
            print("Accessing URL:", url)

            if not safe_get_url(url):
                continue

            img_results = driver.find_elements(By.XPATH, "//*[normalize-space(@class)='YQ4gaf']")
            image_urls = [img.get_attribute('src') for img in img_results if img.get_attribute('src')]
            print(f"Found {len(image_urls)} images.")

            for i in range(min(3, len(image_urls))):
                try:
                    urllib.request.urlretrieve(str(image_urls[i]),
                                               os.path.join(folder_path, f"{filename}_{i + 1}.jpg"))
                    print(f"Downloaded image {i + 1}")
                except Exception as e:
                    print(f"Error downloading image {i + 1}: {e}")


driver.quit()
