from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# URL of the website
url = "https://aitoolguru.com/"

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # You might need to specify the path to your chromedriver
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

# Close the WebDriver
driver.quit()
