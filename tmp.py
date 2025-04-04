import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import urllib.request
import time
import os

# Read file
import json

# Đọc dữ liệu từ file input.json
with open('output.json', 'r', encoding='utf-8') as infile:
    data = json.load(infile)

folder_path = './down/'
os.makedirs(folder_path, exist_ok=True)

query = "trẻ em đang bò"

options = uc.ChromeOptions()
options.add_argument('--user-data-dir=/home/conanwinner/.config/google-chrome')
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options)

url = f"https://www.google.com/search?q={query}&hl=en&tbm=isch"
print("Accessing URL:", url)
driver.get(url)

img_results = driver.find_elements(By.XPATH, "//*[normalize-space(@class)='YQ4gaf']")

image_urls = [img.get_attribute('src') for img in img_results if img.get_attribute('src')]
print(f"Found {len(image_urls)} images.")

for i in range(min(5, len(image_urls))):
    try:
        urllib.request.urlretrieve(str(image_urls[i]),
                                   os.path.join(folder_path, f"{query.replace(' ', '_')}_{i + 1}.jpg"))
        print(f"Downloaded image {i + 1}")
    except Exception as e:
        print(f"Error downloading image {i + 1}: {e}")

driver.quit()
