import io
import zipfile
import os
import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_images(name, scroll_attempts):
    # Setup ChromeDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode for background operation

    # Path to the ChromeDriver executable
    chrome_driver_path = r'C:\Program Files\chromedriver\chromedriver.exe'
    print(chrome_driver_path)

    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

    # Pinterest URL
    url = f'https://www.pinterest.com/search/pins/?q={name}&rs=typed'
    driver.get(url)

    # Allow some time for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))

    def download_images_from_elements(images, zipf, seen_urls):
        for image in images:
            img_url = image.get_attribute('src')
            if img_url and img_url not in seen_urls:
                seen_urls.add(img_url)  # Track the URL to avoid duplicates
                img_name = img_url.split('/')[-1].split('?')[0]
                
                # Download the image
                try:
                    img_response = requests.get(img_url, verify=False)  # Verify False if using HTTP instead of HTTPS
                    img_response.raise_for_status()
                    if img_response.status_code == 200:
                        # Write image to zip file in memory
                        print(f"Downloading {img_name}")
                        zipf.writestr(img_name, img_response.content)
                except requests.RequestException as e:
                    print(f"Error downloading image {img_url}: {e}")

    # Create an in-memory file object for the zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        seen_urls = set()  # Initialize a set to keep track of seen URLs
        # Scroll and download images incrementally
        for _ in range(scroll_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Allow time for new images to load

            # Find image elements after each scroll
            images = driver.find_elements(By.TAG_NAME, 'img')
            download_images_from_elements(images, zipf, seen_urls)

            time.sleep(2)  # Adjust this time if needed

    driver.quit()

    # Rewind the zip file to the beginning
    zip_buffer.seek(0)
    
    return zip_buffer

def main():
    # Get user input
    name = input("Enter the search term: ")
    scroll_attempts = int(input("Enter the number of scroll attempts: "))

    # Download images and create zip file
    zip_buffer = download_images(name, scroll_attempts)

    # Save the zip file to disk
    zip_filename = f'{name}_images.zip'
    with open(zip_filename, 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    print(f"Zip file '{zip_filename}' created and saved locally.")

if __name__ == '__main__':
    main()
