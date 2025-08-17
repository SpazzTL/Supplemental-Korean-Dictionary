import json
import csv

# Define a recursive function to extract definitions from the nested structure
def extract_definitions(data):
    if isinstance(data, dict):
        if 'content' in data and isinstance(data['content'], str):
            return data['content'].strip()
        elif 'content' in data and isinstance(data['content'], list):
            extracted_texts = []
            for item in data['content']:
                text = extract_definitions(item)
                if text:
                    extracted_texts.append(text)
            return ' '.join(extracted_texts)
        else:
            return ' '.join(extract_definitions(v) for v in data.values() if extract_definitions(v))
    elif isinstance(data, list):
        extracted_texts = []
        for item in data:
            text = extract_definitions(item)
            if text:
                extracted_texts.append(text)
        return ' '.join(extracted_texts)
    return ''

# Read the JSON file
with open('term_bank_1.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# Initialize a list to store the extracted data
data_to_write = []

# Process the data
for item in json_data:
    word = item[0]
    hanja = item[-1]
    definition_data = item[5]
    definition = extract_definitions(definition_data)
    data_to_write.append([word, hanja, definition])

# Write the data to a CSV file
output_file = 'term_bank.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Word', 'Hanja', 'Definition'])
    csv_writer.writerows(data_to_write)

print(f"Successfully created '{output_file}' with the extracted data.")