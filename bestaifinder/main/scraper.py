import os
import re
import requests
from bs4 import BeautifulSoup
import sqlite3

# Directory paths
base_dir = '/bestaifinder/media/images'
screenshot_dir = os.path.join(base_dir, 'ai-screenshot')
logo_dir = os.path.join(base_dir, 'logos')

# Create directories if they don't exist
os.makedirs(screenshot_dir, exist_ok=True)
os.makedirs(logo_dir, exist_ok=True)

# Function to sanitize the filename
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename.split("?")[0])

# Function to download images
def download_image(url, save_dir):
    if not url or url == 'Image not found' or url == 'Logo not found':
        return url
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        image_name = sanitize_filename(url.split('/')[-1])
        save_path = os.path.join(save_dir, image_name)
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return save_path
    return url

# Function to scrape data from a single page
def scrape_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    tools = []

    for item in soup.select('.aitools-item'):
        ai_image_element = item.select_one('.aitools-screenshot')
        ai_image_url = ai_image_element.get('src') if ai_image_element else 'Image not found'
        ai_image = download_image(ai_image_url, screenshot_dir)

        ai_tool_logo_element = item.select_one('.aitools-logo')
        ai_tool_logo_url = ai_tool_logo_element.get('src') if ai_tool_logo_element else 'Logo not found'
        ai_tool_logo = download_image(ai_tool_logo_url, logo_dir)

        ai_name_element = item.select_one('.aitools-tool-title')
        ai_name = ai_name_element.text.strip() if ai_name_element else 'Name not found'

        ai_short_description_element = item.select_one('.aitools-tool-description')
        ai_short_description = ai_short_description_element.text.strip() if ai_short_description_element else 'Description not found'

        ai_pricing_tag_element = item.select_one('.pricing-price')
        ai_pricing_tag = ai_pricing_tag_element.text.strip() if ai_pricing_tag_element else 'Pricing not specified'

        ai_tags = [tag.text.strip() for tag in item.select('.aitools-category')]

        tool_link_element = item.select_one('.aitools-visit-link')
        tool_link = tool_link_element.get('href') if tool_link_element else 'Link not found'

        tools.append({
            'ai_image': ai_image,
            'ai_name': ai_name,
            'ai_tool_logo': ai_tool_logo,
            'ai_short_description': ai_short_description,
            'ai_pricing_tag': ai_pricing_tag,
            'ai_tags': ", ".join(ai_tags),
            'ai_tool_link': tool_link
        })

    return tools

# Insert data into the database
def insert_into_db(tools, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for tool in tools:
        cursor.execute('''
        INSERT INTO ai_tools (ai_image, ai_name, ai_tool_logo, ai_short_description, ai_pricing_tag, ai_tags, ai_tool_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tool['ai_image'], tool['ai_name'], tool['ai_tool_logo'], tool['ai_short_description'], tool['ai_pricing_tag'], tool['ai_tags'], tool['ai_tool_link']))
    
    conn.commit()
    conn.close()

# List to hold all tools from all pages
all_tools = []

page_number = 1
while True:
    page_url = f"https://www.insidr.ai/ai-tools/page/{page_number}/"
    print(f"Scraping page {page_number}...")
    page_tools = scrape_page(page_url)
    if not page_tools:
        print(f"No tools found on page {page_number}. Stopping.")
        break
    all_tools.extend(page_tools)
    page_number += 1

# Insert all tools into the database
db_path = 'D:/OneDrive - University of the People/Desktop/GITHUB CLONED/Best-AI-Finder/bestaifinder/db.sqlite3'
insert_into_db(all_tools, db_path)

print("......................................................")
print(f"Total number of tools found: {len(all_tools)}")
print("Data has been written to the database.")
