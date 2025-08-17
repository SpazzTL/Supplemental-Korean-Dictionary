# Supplemental-Korean-Dictionary
A supplemental korean dictionary for Yomitan. Mainly for reading webnovels. Currently WIP with (``100 Main Terms``) as of (``8/16/2025``) | (``160~ total Terms Including Hanja``)
( Release is actively updated )


<img width="742" height="628" alt="image" src="https://github.com/user-attachments/assets/1d15178b-b9d2-4193-b051-fffd305aac1f" />



Made using custom .pyw program (Located in scripts/Yomitan Word Adder-BETA.py).

### Yomitan Dictionary Creation Guide
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/0cadd9e8-b01a-413e-b001-7c52dd4804ea" />
<img width="500" height="500" alt="image" src=Images/BetaIMG.png />


This guide will walk you through the process of creating a custom dictionary for Yomitan using the above script.

#### Step One: Create `index.json`

The `index.json` file is a required file that provides metadata about your dictionary. This file should be created manually in a text editor. The following is a template based on the provided schema, with required fields marked.

```json
{
    "title": "Your Dictionary Title",  // (Required)
    "revision": "1",                 // (Required)
    "format": 3,                     // (Required, use 3 for latest features)
    "sequenced": false,
    "author": "Your Name",
    "description": "A brief description of your dictionary.",
    "url": "https://example.com/your-dictionary-source",
    "attribution": "Source of your data, if any.",
    "sourceLanguage": "ja",
    "targetLanguage": "en"
}
```

  * **Required Fields**: `title`, `revision`, and either `format` or `version`. Using `format: 3` is recommended.
  * **Recommended Fields**: `author`, `description`, `sourceLanguage`, and `targetLanguage` are highly recommended for clarity.
  * **Note**: The `index.json` file needs to be in the same directory as your `term_bank_*.json` files.

#### Step Two: Use the Program to Add Words

Use the provided Python script to add and edit words. The script automatically saves your entries to a file named `term_bank_1.json`. You can rename this file to `term_bank_2.json`, `term_bank_3.json`, etc., to create multiple term banks. The script's "Add Word" button will either add a new term or update an existing one to prevent duplicates.

#### Step Three: Zip and Import

Once you have created your `index.json` and added your words using the script:

* 0. [OPTIONAL] Use generate_hanja_bank.py to generate new entries for each term containing a alternative_form field. Use clean_term_bank.py to remove blank example sentences and neaten formatting. (Both Create Backups in /backup folder) 
* 1.  Use the "Zip Dictionary" button in the program. This will create a `dictionary_archive.zip` file in the same directory.
* 2.  Alternatively, you can manually select the `index.json` and all `term_bank_*.json` files and create a zip archive.
* 3.  Open the Yomitan extension in your browser.
* 4.  Navigate to the settings page.
* 5.  Go to the "Dictionaries" tab.
* 6.  Click "Import" and select your new zip file.

Your custom dictionary is now ready to be used in Yomitan.
