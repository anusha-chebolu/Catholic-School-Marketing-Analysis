## This script is used for scrapping websites of (Lumen Christi Catholic, Seton, Our Lady of Providence)
import concurrent.futures
import threading
import queue
import time
import logging
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup Selenium WebDriver options
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# Initialize WebDriver (each thread gets its own WebDriver)
def create_driver():
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Modify navigator.webdriver to avoid bot detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """
        })
        return driver
    except Exception as e:
        logger.error(f"Error creating WebDriver: {e}")
        return None

# Shared resources with threading protection
visited_urls = set()
unique_image_urls = set()  # Global set to store unique image URLs
image_data = queue.Queue()  # Thread-safe queue
lock = threading.Lock()

def parse_page(driver, url):
    """Fetches and parses a web page with explicit wait."""
    try:
        logger.info(f"Attempting to load {url}")
        driver.get(url)
        # Try waiting for images first, then fallback to body
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "img"))
            )
        except TimeoutException:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logger.warning(f"Timeout waiting for page to load: {url}")
        page_source = driver.page_source
        logger.info(f"Successfully retrieved page source for {url}")
        return BeautifulSoup(page_source, "html.parser")
    except WebDriverException as e:
        logger.error(f"WebDriver error loading {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading {url}: {e}")
        return None

def process_url(url, base_url):
    """Extracts image URLs and finds new links within the same domain."""
    driver = create_driver()  # Each thread gets its own WebDriver
    if not driver:
        logger.error("Failed to create WebDriver, skipping URL")
        return []
    
    with lock:
        if url in visited_urls:
            driver.quit()
            return []
        visited_urls.add(url)
        logger.info(f"Crawling: {url}")

    soup = parse_page(driver, url)
    if not soup:
        driver.quit()
        return []

    # Extract image URLs
    img_urls = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            try:
                full_url = urljoin(url, src)
                img_urls.append(full_url)
            except Exception as e:
                logger.warning(f"Error processing image URL {src}: {e}")

    # Extract links and join relative URLs to the base URL
    links = set()
    for a in soup.find_all("a", href=True):
        try:
            link = urljoin(base_url, a["href"])
            if base_url in link:  # Only include links within the same domain
                links.add(link)
        except Exception as e:
            logger.warning(f"Error processing link: {e}")

    # Safely store only unique image URLs
    with lock:
        for img_url in img_urls:
            if img_url not in unique_image_urls:
                unique_image_urls.add(img_url)
                image_data.put([url, img_url])

    driver.quit()  # Close the WebDriver instance for this thread

    # Return only new links within the same domain
    with lock:
        return [link for link in links if link not in visited_urls]

def crawl_site(base_url, max_pages=100):
    """Crawls the site using ThreadPoolExecutor with a page limit."""
    url_queue = [base_url]
    page_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_url, url, base_url): url for url in url_queue}
        while futures and page_count < max_pages:
            done, _ = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED, timeout=60
            )
            if not done:
                logger.warning("No tasks completed within timeout, checking for issues")
                continue
            for future in done:
                url = futures.pop(future)
                try:
                    new_links = future.result()
                    page_count += 1
                    logger.info(f"Processed page {page_count}/{max_pages}")
                    for link in new_links:
                        if link not in visited_urls and page_count < max_pages:
                            url_queue.append(link)
                            futures[executor.submit(process_url, link, base_url)] = link
                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")

def get_filename(url):
    """Extracts the main part of the domain from a URL and returns a filename."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    domain = domain.split('.')[0]
    filename = f"{domain}-school-image-urls.csv"
    return filename

def test_single_page(url):
    """Test function to check if a single page can be loaded."""
    logger.info("Running single page test")
    driver = create_driver()
    if not driver:
        logger.error("Failed to create WebDriver for test")
        return False
    try:
        logger.info(f"Attempting to load {url} for testing")
        driver.get(url)
        time.sleep(5)  # Wait a bit longer for test purposes
        logger.info(f"Page title: {driver.title}")
        logger.info(f"Page source length: {len(driver.page_source)}")
        driver.save_screenshot("test_screenshot.png")
        logger.info("Saved screenshot to test_screenshot.png")
        driver.quit()
        return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        if driver:
            driver.quit()
        return False

if __name__ == "__main__":
    base_url = input("Enter the base URL: ").strip()
    if not base_url.endswith("/"):
        base_url += "/"
    
    # Test single page load before starting crawler
    logger.info("Testing single page load before starting crawler")
    if test_single_page(base_url):
        logger.info("Single page test successful, starting crawler")
        max_pages = int(input("Enter maximum number of pages to crawl (default 100): ") or 100)
        crawl_site(base_url, max_pages)

        # Save data to CSV
        filename = get_filename(base_url)
        if not image_data.empty():
            df = pd.DataFrame(list(image_data.queue), columns=["Page URL", "Image URL"])
            df.to_csv(filename, index=False, encoding="utf-8")
            logger.info(f"Saved {len(df)} unique image URLs to {filename}")
        else:
            logger.warning("No image data collected!")
    else:
        logger.error("Single page test failed, please check your configuration")
