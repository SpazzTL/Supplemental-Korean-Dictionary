import json
import copy
import os
import shutil
from datetime import datetime

def find_hanja(structured_content):
    """
    Recursively searches for a span tag with a specific style that contains Hanja.
    """
    if isinstance(structured_content, list):
        for item in structured_content:
            hanja = find_hanja(item)
            if hanja:
                return hanja
    elif isinstance(structured_content, dict):
        if structured_content.get('tag') == 'span' and structured_content.get('style', {}).get('color') == '#555':
            return structured_content.get('content')
        if 'content' in structured_content:
            hanja = find_hanja(structured_content['content'])
            if hanja:
                return hanja
    return None

def clean_hanja_string(hanja_str):
    """
    Removes surrounding symbols from a Hanja string.
    """
    if not isinstance(hanja_str, str):
        return ""
    
    # Remove any leading/trailing whitespace and symbols
    clean_str = hanja_str.strip()
    clean_str = clean_str.replace('〔', '').replace('〕', '')
    clean_str = clean_str.replace('[', '').replace(']', '')
    clean_str = clean_str.replace('{', '').replace('}', '')
    clean_str = clean_str.replace('(', '').replace(')', '')
    
    return clean_str.strip()

def generate_hanja_term_bank(file_path):
    """
    Processes a JSON file to create a new term bank with Hanja as the main term.
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        return

    new_data = []
    for entry in data:
        if len(entry) > 5 and 'content' in entry[5][0]:
            hanja_raw = find_hanja(entry[5][0]['content'])
            if hanja_raw and hanja_raw.strip():
                hanja_clean = clean_hanja_string(hanja_raw)
                
                # Check if the cleaned string is not empty before proceeding
                if not hanja_clean:
                    continue
                
                new_entry = copy.deepcopy(entry)
                new_entry[0] = hanja_clean

                structured_content = new_entry[5][0]['content']
                if isinstance(structured_content, list):
                    for item in structured_content:
                        if item.get('tag') == 'div' and isinstance(item.get('content'), list):
                            for span_item in item['content']:
                                if span_item.get('tag') == 'span' and span_item.get('style', {}).get('fontWeight') == 'bold':
                                    span_item['content'] = hanja_clean
                                if span_item.get('tag') == 'span' and span_item.get('style', {}).get('color') == '#555':
                                    span_item['content'] = hanja_clean

                new_data.append(new_entry)

    output_file = "term_bank_2.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSuccessfully generated '{output_file}' with {len(new_data)} terms.")

if __name__ == "__main__":
    INPUT_FILE = "term_bank_1.json"
    BACKUP_DIR = "backups"

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Created directory: {BACKUP_DIR}")

    if os.path.exists(INPUT_FILE):
        timestamp = datetime.now().strftime("%m_%d_%y")
        backup_path = os.path.join(BACKUP_DIR, f"term_bank_1_BACKUP_{timestamp}.json")
        shutil.copyfile(INPUT_FILE, backup_path)
        print(f"Created backup at: {backup_path}")
        generate_hanja_term_bank(INPUT_FILE)
    else:
        print(f"Error: '{INPUT_FILE}' not found.")
    
    input("\nPress Enter to close...")