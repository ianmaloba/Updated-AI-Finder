import os
import re
import requests
from bs4 import BeautifulSoup
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import django

# Manually configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bestaifinder.settings')
django.setup()

from main.models import AITool

# Directory paths
base_dir = 'D:/OneDrive - University of the People/Desktop/GITHUB CLONED/Best-AI-Finder/bestaifinder/media/images'
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
    if not url or url in ['Image not found', 'Logo not found']:
        return 'images/default.jpg'  # Return default image path

    # If URL is relative, prepend base URL
    if url.startswith('/'):
        url = 'https://aitoolguru.com' + url

    # Check if the url is a valid URL or a local path
    if not re.match(r'http(s?):', url):
        return url

    # Extract filename from URL
    image_name = sanitize_filename(url.split('/')[-1])
    save_path = os.path.join(save_dir, image_name)

    # Check if image already exists
    if os.path.exists(save_path):
        return save_path

    # Download the image
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return save_path
        else:
            return 'images/default.jpg'  # Return default image path if download fails
    except Exception as e:
        print(f"Failed to download image from {url}: {str(e)}")
        return 'images/default.jpg'  # Return default image path on exception

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # You might need to specify the path to your chromedriver
url = "https://aitoolguru.com/"
driver.get(url)

# Initialize WebDriverWait
wait = WebDriverWait(driver, 10)

# Scroll down to load all tools
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_pause_time = 3  # Increase the scroll pause time to ensure all tools load
total_tools_loaded = 0  # Initialize the total tools counter

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)  # Wait for new tools to load
    new_height = driver.execute_script("return document.body.scrollHeight")

    # If no more content is loaded, break the loop
    if new_height == last_height:
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tool-box')))
        except:
            break
        break
    last_height = new_height

    # Count the tools on the page
    tools = driver.find_elements(By.CLASS_NAME, 'tool-box')
    total_tools_loaded = len(tools)
    print(f"Total tools loaded so far: {total_tools_loaded}")

# Final count of the tools on the page
print(f"Total number of tools found: {total_tools_loaded}")

# Parse the page content with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# Function to scrape detailed information from a tool's page
def scrape_detailed_page(tool_link):
    try:
        response = requests.get(tool_link, timeout=10)
        detailed_soup = BeautifulSoup(response.text, 'html.parser')

        # Extract detailed short description
        detailed_description_element = detailed_soup.select_one('p[itemprop="description"]')
        detailed_description = detailed_description_element.text.strip() if detailed_description_element else 'Description not found'

        # Extract additional tags
        additional_tags_elements = detailed_soup.select('.tags .btn-secondary, .tags .text-gradient')
        additional_tags = ["#" + tag.text.strip().replace("#", "") for tag in additional_tags_elements]

        # Extract external tool link from "Visit" button
        external_link_element = detailed_soup.select_one('a[itemprop="url"]')
        external_tool_link = external_link_element.get('href') if external_link_element else '#'

        return detailed_description, additional_tags, external_tool_link

    except Exception as e:
        print(f"Error scraping tool details for {tool_link}: {str(e)}")
        return 'Description not found', [], '#'

# Collect data from the main page and scrape detailed information
tools_data = []

start_index = 1  # Start index to collect tools

for index, item in enumerate(soup.select('.tool-box'), start=1):
    if index < start_index:
        continue

    ai_image_element = item.select_one('img')
    ai_image_url = 'https://aitoolguru.com' + ai_image_element.get('src') if ai_image_element else 'Image not found'
    ai_image = download_image(ai_image_url, screenshot_dir)
    print(f"Downloaded image for tool {index}")

    ai_name_element = item.select_one('h4')
    ai_name = ai_name_element.text.strip() if ai_name_element else 'Name not found'
    print(f"Tool name: {ai_name}")

    ai_pricing_tag_element = item.select_one('.t-price')
    ai_pricing_tag = ai_pricing_tag_element.text.strip() if ai_pricing_tag_element else 'Pricing not specified'
    print(f"Pricing tag: {ai_pricing_tag}")

    ai_tags_elements = item.select('.tag')
    ai_tags = ["#" + tag.text.strip().replace("#", "") for tag in ai_tags_elements]
    print(f"Tags: {ai_tags}")

    tool_link_element = item.select_one('a.btn-primary')
    tool_link = 'https://aitoolguru.com' + tool_link_element.get('href') if tool_link_element else '#'
    print(f"Tool link: {tool_link}")

    # Visit the tool's detailed page to get additional information
    try:
        ai_short_description, additional_tags, external_tool_link = scrape_detailed_page(tool_link)
    except Exception as e:
        print(f"Error scraping tool details for {ai_name}: {str(e)}")
        continue

    # Combine tags from main page and detailed page
    all_tags = ai_tags + additional_tags
    all_tags = list(set([tag.replace("#", "") for tag in all_tags]))  # Remove duplicates and extra # signs
    all_tags = ["#" + tag for tag in all_tags]  # Ensure each tag has one #

    print(f"Combined tags: {all_tags}")

    # Add the tool link from the detailed page, if available
    tools_data.append({
        'ai_image': ai_image,
        'ai_name': ai_name,
        'ai_tool_logo': 'Logo not found',  # No logo available
        'ai_short_description': ai_short_description,
        'ai_pricing_tag': ai_pricing_tag,
        'ai_tags': ", ".join(all_tags),
        'ai_tool_link': external_tool_link
    })

    print(f"Tool {index} info done")

# Insert data into the Django database
for tool_data in tools_data:
    ai_image_path = download_image(tool_data['ai_image'], screenshot_dir) if tool_data['ai_image'].startswith('http') else tool_data['ai_image']
    AITool.objects.create(
        ai_image=ai_image_path,
        ai_name=tool_data['ai_name'],
        ai_tool_logo='images/default_logo.jpg',  # Use default logo path
        ai_short_description=tool_data['ai_short_description'],
        ai_pricing_tag=tool_data['ai_pricing_tag'],
        ai_tags=tool_data['ai_tags'],
        ai_tool_link=tool_data['ai_tool_link']
    )

print("......................................................")
print(f"Total number of tools found: {len(tools_data)}")
print("Data has been written to the database.")
