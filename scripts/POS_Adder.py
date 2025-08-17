import json

# Define a mapping for the full and short forms
part_of_speech_map = {
    "n": {"full": "Noun", "short": "n"},
    "v": {"full": "Verb", "short": "v"},
    "a": {"full": "Adjective", "short": "adj"}
}

def find_definition(content_list):
    """
    Finds the definition by looking for a 'div' with bolded content.
    """
    for item in content_list:
        if isinstance(item, dict) and item.get('tag') == 'div':
            # Check for the style that indicates a definition line
            style = item.get('style', {})
            if style.get('fontWeight') == 'bold' and isinstance(item.get('content'), str):
                return item['content']
            
            # Recurse into nested content if it's a list
            nested_content = item.get('content', [])
            if isinstance(nested_content, list):
                result = find_definition(nested_content)
                if result and result != "No definition found.":
                    return result
    return "No definition found."

try:
    # Open and load the term_bank_1.json file
    with open('term_bank_1.json', 'r', encoding='utf-8') as file:
        term_bank = json.load(file)

    # Iterate through each term entry with an index
    for i, entry in enumerate(term_bank):
        # Check if the part of speech and its short form are already filled
        if entry[2] and entry[3]:
            print(f"\n--- Entry {i+1} of {len(term_bank)} ---")
            print(f"Skipping term '{entry[0]}' as both fields are already filled.")
            continue

        # Extract the TERM, ALTERNATIVE FIELD, and structured content
        term = entry[0]
        alternative_field = entry[1]
        
        # Access the structured content array, and get the content from the first object
        structured_content = entry[5][0].get('content', [])

        # Find and display the definition
        definition = find_definition(structured_content)

        # Display the term, alternative field, and definition to the user
        print(f"\n--- Entry {i+1} of {len(term_bank)} ---")
        print(f"Term: {term}")
        print(f"Alternative Field: {alternative_field}")
        print(f"Definition: {definition}")

        # Prompt the user to enter the Part of Speech
        while True:
            pos_input = input("Enter Part of Speech (n, v, or a) or 'q' to quit: ").lower()
            if pos_input == 'q':
                print("Quitting script. The file has been saved up to this point.")
                exit()
            if pos_input in part_of_speech_map:
                # Update the full Part of Speech field (index 2)
                entry[2] = part_of_speech_map[pos_input]["full"]
                # Update the abbreviation field (index 3)
                entry[3] = part_of_speech_map[pos_input]["short"]
                break
            else:
                print("Invalid input. Please enter 'n', 'v', or 'a'.")

        # Save the updated data back to the original file after each entry
        with open('term_bank_1.json', 'w', encoding='utf-8') as file:
            json.dump(term_bank, file, indent=2, ensure_ascii=False)

    print("\nProcessing complete. All entries in 'term_bank_1.json' have been updated.")

except FileNotFoundError:
    print("Error: The file 'term_bank_1.json' was not found in the current directory.")
except Exception as e:
    print(f"An error occurred: {e}")