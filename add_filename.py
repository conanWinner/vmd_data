import json
import unidecode

# Đọc dữ liệu từ file input.json
with open('output_8k.json', 'r', encoding='utf-8') as infile:
    data = json.load(infile)

for item in data:
    for key, value in item.items():
        if key not in ['word', 'voice', 'status'] and isinstance(value, dict):
            value['img'] = f"{unidecode.unidecode(item['word']).replace(" ", "_")}_{key}"


# Lưu dữ liệu đã định dạng sang file output.json
with open('output.json', 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=4)
