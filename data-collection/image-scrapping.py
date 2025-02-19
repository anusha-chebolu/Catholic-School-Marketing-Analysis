import concurrent.futures
import threading
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# Setup Selenium WebDriver
options = Options()
options.add_argument("--headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Shared resources
visited_urls = set()
image_data = []
lock = threading.Lock()

def parse_page(url):
    try:
        driver.get(url)
        time.sleep(2)  # Allow content to load
        return BeautifulSoup(driver.page_source, "html.parser")
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None

def process_url(url, base_url):
    global visited_urls, image_data
    with lock:
        if url in visited_urls:
            return []
        visited_urls.add(url)
        print(f"Crawling: {url}")

    soup = parse_page(url)
    if not soup:
        return []

    # Get image URLs
    img_urls = [urljoin(url, img.get("src")) for img in soup.find_all("img") if img.get("src")]
    
    # Get links (join relative URLs to the base URL)
    links = {urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True)}

    with lock:
        for img_url in img_urls:
            image_data.append([url, img_url])

    # Return only links within the same domain that haven't been visited
    return [link for link in links if base_url in link and link not in visited_urls]

def crawl_site(base_url):
    url_queue = [base_url]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_url, url, base_url): url for url in url_queue}
        while futures:
            done, _ = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            for future in done:
                url = futures.pop(future)
                try:
                    new_links = future.result()
                    for link in new_links:
                        if link not in visited_urls:
                            url_queue.append(link)
                            futures[executor.submit(process_url, link, base_url)] = link
                except Exception as e:
                    print(f"Error processing {url}: {e}")

def get_filename(url):
    """
    Extracts the main part of the domain from a URL and returns a filename.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    domain = domain.split('.')[0]
    filename = f"{domain}-school-image-urls.csv"
    return filename

if __name__ == "__main__":
    base_url = input("Enter the base URL: ").strip()
    if not base_url.endswith("/"):
        base_url += "/"
    
    crawl_site(base_url)
    filename = get_filename(base_url)
    df = pd.DataFrame(image_data, columns=["Page URL", "Image URL"])
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Saved image URLs to {filename}")
    driver.quit()


# import concurrent.futures
# import threading
# import queue
# import time
# from urllib.parse import urljoin, urlparse
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# import pandas as pd

# # Setup Selenium WebDriver
# options = Options()
# options.add_argument("--headless")  # Run in headless mode
# options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option("useAutomationExtension", False)

# # Initialize WebDriver (each thread gets its own WebDriver)
# def create_driver():
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)

#     # Modify navigator.webdriver to avoid bot detection
#     driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#         "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
#     })
    
#     return driver

# # Shared resources with threading protection
# visited_urls = set()
# image_data = queue.Queue()  # Thread-safe queue
# lock = threading.Lock()

# def parse_page(driver, url):
#     """Fetches and parses a web page with explicit wait."""
#     try:
#         driver.get(url)
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))  # Wait for images to load
#         return BeautifulSoup(driver.page_source, "html.parser")
#     except Exception as e:
#         print(f"Error loading {url}: {e}")
#         return None

# def process_url(url, base_url):
#     """Extracts image URLs and finds new links within the same domain."""
#     driver = create_driver()  # Each thread gets its own WebDriver
    
#     with lock:
#         if url in visited_urls:
#             driver.quit()
#             return []
#         visited_urls.add(url)
#         print(f"Crawling: {url}")

#     soup = parse_page(driver, url)
#     if not soup:
#         driver.quit()
#         return []

#     # Extract image URLs
#     img_urls = [urljoin(url, img.get("src")) for img in soup.find_all("img") if img.get("src")]

#     # Extract links and join relative URLs to the base URL
#     links = {urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True)}

#     # Store image data safely
#     for img_url in img_urls:
#         image_data.put([url, img_url])

#     driver.quit()  # Close the WebDriver instance for this thread

#     # Return only new links within the same domain
#     return [link for link in links if base_url in link and link not in visited_urls]

# def crawl_site(base_url):
#     """Crawls the site using ThreadPoolExecutor."""
#     url_queue = [base_url]

#     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#         futures = {executor.submit(process_url, url, base_url): url for url in url_queue}

#         while futures:
#             done, _ = concurrent.futures.wait(
#                 futures, return_when=concurrent.futures.FIRST_COMPLETED
#             )
#             for future in done:
#                 url = futures.pop(future)
#                 try:
#                     new_links = future.result()
#                     for link in new_links:
#                         if link not in visited_urls:
#                             url_queue.append(link)
#                             futures[executor.submit(process_url, link, base_url)] = link
#                 except Exception as e:
#                     print(f"Error processing {url}: {e}")

# def get_filename(url):
#     """Extracts the main part of the domain from a URL and returns a filename."""
#     parsed_url = urlparse(url)
#     domain = parsed_url.netloc
#     if domain.startswith("www."):
#         domain = domain[4:]
#     domain = domain.split('.')[0]
#     filename = f"{domain}-school-image-urls.csv"
#     return filename

# if __name__ == "__main__":
#     base_url = input("Enter the base URL: ").strip()
#     if not base_url.endswith("/"):
#         base_url += "/"

#     crawl_site(base_url)

#     # Save data to CSV
#     filename = get_filename(base_url)
#     df = pd.DataFrame(list(image_data.queue), columns=["Page URL", "Image URL"])
#     df.to_csv(filename, index=False, encoding="utf-8")

#     print(f"Saved image URLs to {filename}")
