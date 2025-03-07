import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import urllib.request
import time
import os
import json

# Load dữ liệu từ file
with open('output.json', 'r', encoding='utf-8') as infile:
    data = json.load(infile)

folder_path = './down/'
os.makedirs(folder_path, exist_ok=True)

# Biến để theo dõi tiến độ tải (nếu restart thì sẽ tiếp tục chứ không lặp lại)
progress_file = 'download_progress.json'
if os.path.exists(progress_file):
    with open(progress_file, 'r', encoding='utf-8') as f:
        downloaded = json.load(f)
else:
    downloaded = {}

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)
    return driver

def safe_get_url(driver, url, retries=3, wait_time=300):
    for attempt in range(retries):
        try:
            driver.get(url)
            time.sleep(5)  # Đợi thêm chút sau khi load để tránh bị chặn
            return True
        except Exception as e:
            print(f"Error accessing URL (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
    print("Failed to access URL after retries, skipping...")
    return False

def save_progress():
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(downloaded, f, ensure_ascii=False, indent=4)

for item in data:
    word = item.get('word', '')
    if word in downloaded and downloaded[word]:
        print(f"Skipping {word}, already downloaded.")
        continue

    for key, value in item.items():
        if key not in ['word', 'voice', 'status'] and isinstance(value, dict):
            query = value['example']
            filename = value['img']

            url = f"https://www.google.com/search?q={query}&hl=en&tbm=isch"
            print("Accessing URL:", url)

            # Mở trình duyệt mới sau mỗi từ khóa
            driver = init_driver()

            if not safe_get_url(driver, url):
                driver.quit()
                continue

            img_results = driver.find_elements(By.XPATH, "//*[normalize-space(@class)='YQ4gaf']")
            image_urls = [img.get_attribute('src') for img in img_results if img.get_attribute('src')]
            print(f"Found {len(image_urls)} images for '{word}'.")

            for i in range(min(3, len(image_urls))):
                try:
                    urllib.request.urlretrieve(str(image_urls[i]),
                                               os.path.join(folder_path, f"{filename}_{i + 1}.jpg"))
                    print(f"Downloaded image {i + 1} for '{word}'")
                    time.sleep(10)  # Nghỉ giữa mỗi lần tải để giảm rủi ro bị chặn
                except Exception as e:
                    print(f"Error downloading image {i + 1}: {e}")

            # Đánh dấu là đã tải xong
            downloaded[word] = True
            save_progress()

            # Đóng trình duyệt sau khi xử lý xong 1 từ khóa để reset session
            driver.quit()

            # Nghỉ lâu giữa mỗi từ để tránh bị phát hiện là bot
            print(f"Finished '{word}', waiting 30s before next word...")
            time.sleep(30)

print("All done!")
