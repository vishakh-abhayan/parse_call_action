import os
import re
import requests
import markdown
from markdown.extensions.tables import TableExtension

# Configuration
LIST_MD_PATH = 'list.md'  # Path to your list.md file
API_BASE_URL = 'https://app.youlocate.me/api/v1/address/'  # Base API URL
OUTPUT_DIR = 'api_responses'  # Directory to store generated Markdown files

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Optional: Get API key from environment variables if required
API_KEY = os.getenv('API_KEY')  # Set this if your API requires authentication

def extract_locate_ids(markdown_file):
    """
    Extract LocateIds from the given Markdown table.
    """
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Use regex to find the LocateId column
    # Assumes LocateId is in the second column
    pattern = r'\|\s*\d+\s*\|\s*([^|\s]+)\s*\|'
    locate_ids = re.findall(pattern, content)
    return locate_ids

def call_api(locate_id):
    """
    Call the API for the given LocateId and return the JSON response.
    """
    url = f"{API_BASE_URL}{locate_id}"
    headers = {}
    if API_KEY:
        headers['Authorization'] = f"Bearer {API_KEY}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API for {locate_id}: {e}")
        return None

def generate_markdown(locate_id, data):
    """
    Generate a Markdown file with the API response data in table format.
    """
    md_filename = os.path.join(OUTPUT_DIR, f"{locate_id}.md")
    
    # Define table headers
    headers = ["Field", "Value"]
    # Prepare table rows
    rows = [[key.capitalize(), value] for key, value in data.items()]
    
    # Generate Markdown table
    table_md = "| " + " | ".join(headers) + " |\n"
    table_md += "| " + " | ".join(['---'] * len(headers)) + " |\n"
    for row in rows:
        table_md += "| " + " | ".join(map(str, row)) + " |\n"

    # Write to the Markdown file
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(f"# Address Details for {locate_id}\n\n")
        f.write(table_md)

    print(f"Generated {md_filename}")

def main():
    locate_ids = extract_locate_ids(LIST_MD_PATH)
    if not locate_ids:
        print("No LocateIds found in the Markdown file.")
        return

    print(f"Found LocateIds: {locate_ids}")

    for locate_id in locate_ids:
        print(f"Processing {locate_id}...")
        data = call_api(locate_id)
        if data:
            generate_markdown(locate_id, data)
        else:
            print(f"Skipping {locate_id} due to API error.")

if __name__ == "__main__":
    main()
