
# 📸 Pinterest Webscraper

**Pinterest Webscraper** is a Python-based tool that automates the process of downloading images from Pinterest based on a user-defined search term. It uses **Selenium** for dynamic scrolling and **requests** for downloading, then packages all images into a `.zip` file.

---

## 🚀 Features

* 🔍 Search any keyword on Pinterest
* 🔄 Auto-scrolls the page to load more content
* 💾 Downloads all discovered images into a ZIP archive
* 🧼 Removes duplicate images based on URLs
* 👻 Runs in **headless** mode (no browser popup)

---

## 🧰 Requirements

Install dependencies:

```bash
pip install selenium requests urllib3
```

You also need:

* **Google Chrome** browser
* **ChromeDriver** matching your Chrome version
* Update the `chrome_driver_path` in the script:

  ```python
  chrome_driver_path = r'C:\Program Files\chromedriver\chromedriver.exe'
  ```

---

## 📁 Project Structure

```
.
├── pinterest_webscraper.py       # Main script
├── chromedriver/
│   └── chromedriver.exe          # ChromeDriver binary
└── README.md
```

---

## ⚙️ How It Works

1. Prompts user for a **search term** and number of scrolls
2. Navigates to Pinterest search results for that term
3. Scrolls down repeatedly to load more images
4. Extracts image URLs and downloads them
5. Saves all images into a **single .zip file**

---

## 🖥️ Usage

Run in terminal:

```bash
python pinterest_webscraper.py
```

Follow the prompts:

```text
Enter the search term: sushi
Enter the number of scroll attempts: 5
```

After scraping:

```text
Downloading x29ab3a.jpg
Downloading a7bc889.jpg
...
Zip file 'sushi_images.zip' created and saved locally.
```

---

## 🧠 Notes

* More scroll attempts = more images
* Duplicate images are automatically skipped
* Works best with stable internet
* `verify=False` is used to skip SSL warnings (can be removed if needed)

---

## 📌 Example

**Search:** `"waffles"`
**Scrolls:** `3`
**Output:** `waffles_images.zip` with \~50+ images


