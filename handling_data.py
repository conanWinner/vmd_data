import time
import json
from google import genai
from pymongo import MongoClient
from google.genai import types

# Khởi tạo client cho Gemini với API key của bạn
genai_client = genai.Client(api_key="...") 

def gemini_process(doc):
    # Chuyển đổi ObjectId sang chuỗi nếu có
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    
    # Chuyển document thành chuỗi JSON
    text_input = json.dumps(doc, ensure_ascii=False)
    contents = [{"parts": [{"text": text_input}]}]
    
    retries = 3  # Số lần retry tối đa
    for attempt in range(retries):
        try:
            response = genai_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        'chèn thêm 2 cột là "desc_en" và "example_en" được dịch từ cột tương ứng, '
                        'nếu bạn thấy nội dung chưa hay, có thể chỉnh sửa để phù hợp với người học tiếng việt, '
                        'bạn không cần giải thích gì thêm, trả về đúng dạng json.'
                    )
                ),
            )
            print("Response:", response)
            
            # Lấy chuỗi JSON từ response.text bằng cách loại bỏ các dấu code block nếu có
            json_str = response.text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[len("```json"):].strip()
            if json_str.endswith("```"):
                json_str = json_str[:-len("```")].strip()
            
            formatted_doc = json.loads(json_str)
            return formatted_doc
        
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                delay = 2 ** attempt  # exponential backoff: 1, 2, 4, ... giây
                print(f"Lỗi 429: Đang chờ {delay} giây, thử lại lần {attempt+1}/{retries}")
                time.sleep(delay)
            else:
                print("Lỗi khác:", e)
                raise e
    
    raise Exception("Không thể xử lý document sau khi retry do lỗi rate limit.")

# Kết nối tới MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["data"]

source_collection = db["output"]
target_collection = db["vmd_1"]


# skip(57).limit(100):
for doc in source_collection.find().skip(1433).limit(2000):
    while True:
        try:
            formatted_doc = gemini_process(doc)
            target_collection.insert_one(formatted_doc)
            print("Đã xử lý và chèn document có _id:", doc.get("_id"))
            # Sleep 1 giây giữa các request để giảm tải
            time.sleep(1)
            break  # Nếu thành công, thoát vòng lặp while
        except Exception as e:
            print("Lỗi khi xử lý document _id:", doc.get("_id"), ":", e, ". Đang thử lại sau 1 giây.")
            time.sleep(1)
