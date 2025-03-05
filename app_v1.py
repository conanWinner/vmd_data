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
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options)

# Duyệt qua từng mục trong data
for item in data:
    for key, value in item.items():
        if key not in ['word', 'voice', 'status'] and isinstance(value, dict):
            query = value['example']
            filename = value['img']
            url = f"https://www.google.com/search?q={query}&hl=en&tbm=isch"
            print("Accessing URL:", url)
            driver.get(url)
            
            time.sleep(2)
            
            img_results = driver.find_elements(By.XPATH, "//*[normalize-space(@class)='YQ4gaf']")
            image_urls = [img.get_attribute('src') for img in img_results if img.get_attribute('src')]
            print(f"Found {len(image_urls)} images for query: {query}")
            
            for i in range(min(5, len(image_urls))):
                try:
                    img_url = image_urls[i]
                    # Kiểm tra URL hợp lệ
                    if not img_url.startswith("http"):
                        continue
                    save_path = os.path.join(folder_path, f"{filename}_{i+1}.jpg")
                    urllib.request.urlretrieve(img_url, save_path)
                    print(f"Downloaded image {i+1} for {filename}")
                    # Thêm delay nhỏ giữa các lần tải ảnh
                    time.sleep(1)
                except Exception as e:
                    print(f"Error downloading image {i+1} for {filename}: {e}")
            
            time.sleep(3)

driver.quit()
