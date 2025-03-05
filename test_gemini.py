from google import genai
from pymongo import MongoClient
from google.genai import types
import json

genai_client = genai.Client(api_key="AIzaSyDset7NPxC61oXVoTmBwX9Ye463iqLfEb8") 

def gemini_process(doc):
    # Chuyển đổi ObjectId sang chuỗi nếu có
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    
    text_input = json.dumps(doc, ensure_ascii=False)
    contents = [{"parts": [{"text": text_input}]}]
    
    response = genai_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=(
                'chèn thêm 2 cột là "desc_en" và "example_en" được dịch từ cột tương ứng, nếu bạn thấy nội dung chưa hay, có thể chỉnh sửa để phù hợp với người học tiếng việt, bạn không cần giải thích gì thêm, trả về đúng dạng json.'
            )
        ),
    )
    print("Response:", response)
    
    new_doc = doc.copy()
    new_doc["processed_text"] = response.text
    return new_doc


# Kết nối tới MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["data"]

source_collection = db["output"]
target_collection = db["vmd_1"]

# Duyệt qua từng document trong collection gốc, xử lý và chèn vào collection mới
for doc in source_collection.find().limit(1):
    processed_doc = gemini_process(doc)
    target_collection.insert_one(processed_doc)
    print("Đã xử lý và chèn document có _id:", doc.get("_id"))
