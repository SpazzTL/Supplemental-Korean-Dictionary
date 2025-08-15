import json

def is_example_sentence_with_content(item):
    """
    Checks if a 'details' tag has the 'Example Sentences' summary
    and contains a non-empty list of examples.
    """
    if item.get('tag') != 'details':
        return False
    
    # Check for the correct summary text
    if not item.get('content') or item['content'][0].get('content') != 'Example Sentences':
        return False
        
    # Check for the 'ul' tag
    if len(item.get('content', [])) < 2:
        return False
    
    ul_tag = item['content'][1]
    
    if ul_tag.get('tag') == 'ul':
        # Check if the 'ul' list contains any non-empty 'li' items
        for li_item in ul_tag.get('content', []):
            if li_item.get('content'):
                return True
                
    return False

def process_term_bank(file_path):
    """
    Processes a JSON file to format definitions and handle example sentences.
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        input("Press Enter to close...")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        input("Press Enter to close...")
        return

    for entry in data:
        # Navigate to the main content list for the entry
        structured_content = entry[5][0]['content']
        
        # This flag must be reset for each term/entry
        found_valid_example = False
        
        # Process all content blocks, including nested ones
        for top_level_item in structured_content:
            # The items we want to clean are in a nested list
            if isinstance(top_level_item.get('content'), list):
                
                processed_inner_content = []
                inner_content_list = top_level_item.get('content', [])
                
                for item in inner_content_list:
                    # 1. Find the definition and prepend "1. "
                    if (item.get('tag') == 'div' and 
                        item.get('style', {}).get('fontWeight') == 'bold' and 
                        isinstance(item.get('content'), str)):
                        
                        if not item['content'].startswith("1. "):
                            item['content'] = "1. " + item['content']
                        processed_inner_content.append(item)
                    
                    # 2. Find the first valid example sentence block and keep it
                    elif is_example_sentence_with_content(item):
                        if not found_valid_example:
                            processed_inner_content.append(item)
                            found_valid_example = True
                    
                    # 3. Discard any block that is an empty or duplicate "Example Sentences"
                    elif (item.get('tag') == 'details' and 
                          item.get('content') and 
                          item['content'][0].get('content') == 'Example Sentences'):
                        pass # Do not append, thereby removing it
                    
                    # 4. Keep all other items
                    else:
                        processed_inner_content.append(item)
                
                # Replace the old inner list with the newly cleaned one
                top_level_item['content'] = processed_inner_content

    # Write the cleaned data back to the same file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # --- MODIFIED SECTION ---
    print(f"\nSuccessfully processed and updated '{file_path}'.")
    print(f"Total terms: {len(data)}")
    input("\nPress Enter to close...")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_term_bank(sys.argv[1])
    else:
        print("Error: No file path provided. Usage: python clean_term_bank.py <filename>")
        input("\nPress Enter to close...")