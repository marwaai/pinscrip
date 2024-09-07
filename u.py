from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import io
import zipfile
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

# In-memory storage for zip files
zip_files = {}

class NameRequest(BaseModel):
    name: str

def download_images(name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_driver_path = '/usr/bin/chromedriver'
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

    url = f'https://www.pinterest.com/search/pins/?q={name}&rs=typed'
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))

    def download_images_from_elements(images, zipf):
        for image in images:
            img_url = image.get_attribute('src')
            if img_url:
                img_name = img_url.split('/')[-1].split('?')[0]
                try:
                    img_response = requests.get(img_url, verify=False)
                    img_response.raise_for_status()
                    if img_response.status_code == 200:
                        zipf.writestr(img_name, img_response.content)
                except requests.RequestException as e:
                    print(f"Error downloading image {img_url}: {e}")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        scroll_attempts = 20
        for _ in range(scroll_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            images = driver.find_elements(By.TAG_NAME, 'img')
            download_images_from_elements(images, zipf)
            time.sleep(2)

    driver.quit()
    zip_buffer.seek(0)
    return zip_buffer

@app.post("/submit_name")
async def submit_name(request: NameRequest):
    name = request.name
    zip_filename = f'{name}_images.zip'
    zip_buffer = download_images(name)

    if zip_buffer:
        zip_files[zip_filename] = zip_buffer
        return {"message": "Processing started. Use the download endpoint to get the zip file."}
    else:
        raise HTTPException(status_code=500, detail="Failed to create zip file")

@app.get("/get_zip")
async def get_zip(name: str = Query(...)):
    zip_filename = f'{name}_images.zip'
    if zip_filename in zip_files:
        zip_buffer = zip_files.pop(zip_filename)
        return StreamingResponse(zip_buffer, media_type='application/zip', headers={"Content-Disposition":
