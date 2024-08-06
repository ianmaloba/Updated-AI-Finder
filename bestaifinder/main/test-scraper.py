# Run this file to test the scraper, this will print the data and write it into an excel file
import requests
from bs4 import BeautifulSoup
import pandas as pd


# Function to scrape data from a single page
def scrape_page(url):
    # Make a request to the website with headers
    # Note that I used headers here to surpass a security measure if any, this User-Agent header makes the the request appear as if its coming from a web browser.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # List to hold the extracted tool data
    tools = []

    # Find all tool items
    for item in soup.select('.aitools-item'):
        # Extract the AI name
        ai_name_element = item.select_one('.aitools-tool-title')
        ai_name = ai_name_element.text.strip() if ai_name_element else 'Name not found'
        
        # Extract the main image
        ai_image_element = item.select_one('.aitools-screenshot')
        ai_image = ai_image_element.get('src') if ai_image_element else 'Image not found'

        # Extract the tool logo
        ai_tool_logo_element = item.select_one('.aitools-logo')
        ai_tool_logo = ai_tool_logo_element.get('src') if ai_tool_logo_element else 'Logo not found'

        # Extract the short description
        ai_short_description_element = item.select_one('.aitools-tool-description')
        ai_short_description = ai_short_description_element.text.strip() if ai_short_description_element else 'Description not found'

        # Extract the pricing tag, handling cases where it might be missing
        ai_pricing_tag_element = item.select_one('.pricing-price')
        ai_pricing_tag = ai_pricing_tag_element.text.strip() if ai_pricing_tag_element else 'Pricing not specified'
        
        # Extract the tags
        ai_tags = [tag.text.strip() for tag in item.select('.aitools-category')]

        # Extract the tool link
        tool_link_element = item.select_one('.aitools-visit-link')
        tool_link = tool_link_element.get('href') if tool_link_element else 'Link not found'

        tools.append({
            'ai_name': ai_name,
            'ai_image': ai_image,
            'ai_tool_logo': ai_tool_logo,
            'ai_short_description': ai_short_description,
            'ai_pricing_tag': ai_pricing_tag,
            'ai_tags': ai_tags,
            'tool_link': tool_link
        })

    return tools

# List to hold all tools from all pages
all_tools = []


# Sample loop (I later on decided to use a while loop)
"""
# Example of a Loop through pages from 1 to 37

for page_number in range(1, 38):
    page_url = f"https://www.insidr.ai/ai-tools/page/{page_number}/"
    print(f"Scraping page {page_number}...")
    page_tools = scrape_page(page_url)
    all_tools.extend(page_tools)
"""

page_number = 1  # Start with the first page
while True:
    page_url = f"https://www.insidr.ai/ai-tools/page/{page_number}/"
    print(f"Scraping page {page_number}...")
    page_tools = scrape_page(page_url)
    if not page_tools:  # If the page doesn't contain any tools, break the loop
        print(f"No tools found on page {page_number}. Stopping.")
        break
    all_tools.extend(page_tools)
    page_number += 1  # Move to the next page

print("......................................................")

# Print the extracted data from all pages
for index, tool in enumerate(all_tools, start=1):
    print(f"Tool {index}:")
    print(f"AI Name: {tool['ai_name']}")
    print(f"AI Image: {tool['ai_image']}")
    print(f"AI Tool Logo: {tool['ai_tool_logo']}")
    print(f"AI Short Description: {tool['ai_short_description']}")
    print(f"AI Pricing Tag: {tool['ai_pricing_tag']}")
    print(f"AI Tags: {tool['ai_tags']}")
    print(f"AI Tool Link: {tool['tool_link']}")
    print()

print("......................................................")
print(f"Total number of tools found: {len(all_tools)}")



# Create a DataFrame from the list of tools
df = pd.DataFrame(all_tools)

# Write the DataFrame to an Excel file
df.to_excel('scraped_ai_tools.xlsx', index=False)
print("Data has been written to 'scraped_ai_tools.xlsx'")

