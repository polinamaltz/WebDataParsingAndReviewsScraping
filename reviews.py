from selenium import webdriver
import asyncio
import aiohttp
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import csv
import pandas as pd
"""
The code provides a way to automate the extraction of feedbacks from the "Wildberries" website for multiple products using Selenium.

(*) Chrome Options and Service Configuration: Chrome options are set using `Options()` from `selenium.webdriver.chrome.options`. It includes configuring the remote debugging port (a workaround to overcome the limitation of not being able to view reviews). A `Service` object is created using the path to the Chrome driver executable ('chromedriver.exe').

(**) Scroll to Bottom Function: The `scroll_to_bottom` function is defined to scroll the page to the bottom. It takes the last element in the list and the browser driver as parameters. It uses JavaScript to scroll the page and checks if a new element has appeared. If a new element is found, the function calls itself recursively until the last element remains the same, indicating that the bottom of the page has been reached.

(***) Scraping Feedbacks for Each Product: For each product, a new Chrome browser instance is created using the Chrome driver service and options configured earlier. The browser navigates to the feedbacks page of the product. After a brief delay, it checks if there are any feedbacks available. If so, it proceeds to scroll down the page using the `scroll_to_bottom` function until the end of the feedbacks is reached.

(****) Extracting Feedback Information: The code finds all the feedback elements using the class name 'comments__item'. It then iterates over each feedback element and extracts information such as author, date, text, and vote. The extracted data is then written to a CSV file named '{product_id}.csv' in the 'new_data' folder. The CSV file includes columns like 'author', 'date_review', 'text_review', 'vote', 'general_rating', and 'rev_count'.
"""

products_csv = 'products.csv'
# Read the CSV file into a DataFrame
products_info = pd.read_csv(products_csv,sep=';')
# Remove leading and trailing spaces from column names
products_info.columns = products_info.columns.str.strip()
products_info.head(5)


chrome_options = Options()
# Create Chrome options and set the remote debugging port to 9222.
chrome_options.add_argument('--remote-debugging-port=9222')
service = Service(executable_path='chromedriver.exe')  # Set ChromeDriver executable path.

# Define a function named "scroll_to_bottom" that scrolls the list to the last review.
def scroll_to_bottom(elem, driver) -> False:
    """
    Scroll the list to the last review

    Parameters:
    elem: Last review in the list
    driver: chromedriver.exe
    :return: found (True or False)
    """
    driver.execute_script("arguments[0].scrollIntoView();",elem)
    time.sleep(1)
    new_elem = driver.find_elements(By.CLASS_NAME, "comments__item")[-1]
    found = (elem == new_elem)
    
    if found:
        return True
    scroll_to_bottom(new_elem, driver)
    
for index, row in products_info.iterrows():
    product_id = row['id']
    rev_num = row['feedbacks']
    general_rating = row['rating']
    url = f'https://www.wildberries.ru/catalog/{product_id}/feedbacks'
    browser = webdriver.Chrome(service=service, options=chrome_options)
    try:
        browser.get(url)
        time.sleep(3)
        length = 0
        if rev_num > 0:  # If there are reviews (more than 0), scroll the page to load more
            rec = False
            while rec is False and length < 300:
                elements = browser.find_elements(By.CLASS_NAME, "comments__item")
                length = len(elements)
                rec = scroll_to_bottom(elements[-1], browser)
        else:
            print('The product has no reviews.')
        time.sleep(3)

        feedbacks_list = browser.find_elements(By.CLASS_NAME, 'comments__item')
        with open(f'new_data/{product_id}.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, dialect='excel', delimiter=';')
            columns = ['author', 'date_review', 'text_review', 'vote', 'general_rating', 'rev_count']
            writer.writerow(columns)
            for feedback in feedbacks_list:
                author = feedback.find_element(By.CLASS_NAME, 'feedback__header').text.replace('\n', ' ')
                date_review = feedback.find_element(By.CLASS_NAME, 'feedback__date').get_attribute("content")
                text_review = feedback.find_element(By.CLASS_NAME, 'feedback__text').text.replace('\n', ' ')
                vote = feedback.find_element(By.CLASS_NAME, 'feedback__rating').get_attribute("class")[-1]
                writer.writerow([author, date_review, text_review, vote, general_rating, rev_num])
        time.sleep(15)
        browser.quit()

    except Exception as ex:
        # If any exception occurs, print the exception and close the browser
        print(ex)
        browser.quit()
# Close the browser
browser.quit()