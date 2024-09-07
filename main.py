from flask import Flask, request, send_file, jsonify
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

app = Flask(__name__)

# In-memory storage for zip files
zip_files = {}

def download_images(name):
    # Setup ChromeDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode for background operation
    chrome_driver_path = '/usr/bin/chromedriver'  # Path to ChromeDriver
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

    # Pinterest URL
    url = f'https://www.pinterest.com/search/pins/?q={name}&rs=typed'
    driver.get(url)

    # Allow some time for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))

    def download_images_from_elements(images, zipf):
        for image in images:
            img_url = image.get_attribute('src')
            if img_url:
                img_name = img_url.split('/')[-1].split('?')[0]
                
                # Download the image
                try:
                    img_response = requests.get(img_url, verify=False)
                    img_response.raise_for_status()
                    if img_response.status_code == 200:
                        # Write image to zip file in memory
                        zipf.writestr(img_name, img_response.content)
                except requests.RequestException as e:
                    print(f"Error downloading image {img_url}: {e}")

    # Create an in-memory file object for the zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        # Scroll and download images incrementally
        scroll_attempts = 20
        for _ in range(scroll_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Allow time for new images to load

            # Find image elements after each scroll
            images = driver.find_elements(By.TAG_NAME, 'img')
            download_images_from_elements(images, zipf)

            time.sleep(2)  # Adjust this time if needed

    driver.quit()

    # Rewind the zip file to the beginning
    zip_buffer.seek(0)
    
    return zip_buffer

@app.route('/submit_name', methods=['POST'])
def submit_name():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    zip_filename = f'{name}_images.zip'
    zip_buffer = download_images(name)

    if zip_buffer:
        # Store the zip file in memory
        zip_files[zip_filename] = zip_buffer
        print(f"Zip file created and stored: {zip_filename}")
    else:
        print(f"Failed to create zip file for: {name}")

    # Log the current state of zip_files
    print(f"Current stored zip files: {list(zip_files.keys())}")

    return jsonify({'message': 'Processing started. Use the download endpoint to get the zip file.'}), 200

@app.route('/get_zip', methods=['GET'])
def get_zip():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    zip_filename = f'{name}_images.zip'
    if zip_filename in zip_files:
        print(f"Serving zip file: {zip_filename}")
        # Get the zip file from in-memory storage
        zip_buffer = zip_files.pop(zip_filename)  # Remove from storage to prevent memory leak

        # Send the zip file to the user
        response = send_file(
            zip_buffer,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )

        return response
    else:
        # Log the available files and the requested file
        print(f"Requested zip file: {zip_filename}")
        print(f"Available zip files: {list(zip_files.keys())}")
        return jsonify({'error': 'No zip file available for this name'}), 404

if __name__ == '__main__':
    app.run(debug=True)
