import asyncio
import aiohttp
import csv
import json
from datetime import date
"""
This Python script is designed for parsing data from a website. It uses the `asyncio` and `aiohttp` libraries to efficiently retrieve and process data. The script is primarily focused on extracting information from the "Wildberries" website, but it can be adapted for other websites with appropriate modifications.

The `ParserWB` class serves as the main component of the script. It contains several methods responsible for different tasks.

1. Initialization: The class constructor initializes various attributes including headers, URL, query, counts of sessions, and a product list.

2. Analysis of the Number of Goods: The `analysis_of_the_number_of_goods` method determines the number of sessions required to retrieve all the product data. It sends a request to the website's API to fetch the total count of products matching the query. If the count is less than 6000, it calculates the number of sessions required to retrieve all the data. Otherwise, it sets the counts of sessions to 60, indicating that only the data for the 6000 most popular products will be gathered.

3. Data Extraction: The `data_extraction` method extracts relevant information from the received JSON data. It iterates over the products in the JSON and appends the desired attributes, such as product name, ID, brand ID, supplier ID, feedbacks, and rating, to the product list.

4. Get Product Data from JSON: The `get_product_data_from_json` method retrieves the JSON data for each page of products. It sends a request to the website's API with the appropriate parameters, including the query, page number, and regions. It then calls the `data_extraction` method to extract the required data from the JSON response.

5. Save Excel: The `save_excel` method saves the collected data to a CSV file. It creates the file with the naming convention of "query date.csv" and writes the column names as headers. It then iterates over the product list and writes each product's values as a new row in the CSV file.

6. Session Creation: The `session_creation` method manages the creation of an asynchronous session using `aiohttp`. It first creates a session and then calls the `analysis_of_the_number_of_goods` method to determine the number of sessions needed. After a brief sleep, it creates a list of tasks for fetching data from each page using the `get_product_data_from_json` method. The tasks are executed concurrently using `asyncio.gather`. Finally, it calls the `save_excel` method to save the collected data.

7. Start Asynchronous Parsing: The `start_asynchronous_parsing` method serves as the entry point for running the parser. It prompts the user to enter a search query, initiates the parsing process by creating an instance of `ParserWB`, and calls the `session_creation` method.

Overall, this script provides a flexible and efficient approach to extract data from the "Wildberries" website based on user input. The extracted data is saved in a CSV file for further analysis or processing.
"""

class ParserWB:
    def __init__(self, query):
        self.headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        self.url = 'https://search.wb.ru/exactmatch/ru/common/v4/'
        self.query = query
        self.counts_of_sessions = 0
        self.product_list = []

    async def analysis_of_the_number_of_goods(self, session):
        """Determines the number of sessions."""
        url_count = f'{self.url}search?appType=1&curr=rub&dest=-1257786&query={self.query}' \
                    f'&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,71,114' \
                    f'&resultset=filters&spp=0&suppressSpellcheck=false'
        async with session.get(url=url_count, headers=self.headers) as response:
            response_json = await response.json(content_type=None)
        count_goods: int
        count_goods = response_json['data']['total']

        if count_goods < 6000:
            print(f"Total found {count_goods} products. Gathering data for all products.")
            self.counts_of_sessions = count_goods // 100 + (0 if count_goods % 100 == 0 else 1)
        else:
            print(f"Total found {count_goods} products. Gathering data for the 6000 most popular products.")
            self.counts_of_sessions = 60

    async def data_extraction(self, response_json):
        """Extracts data from the JSON."""
        print(response_json)
        if response_json is None or response_json.get('data') is None or response_json.get('data').get('products') is None:
            return
        for product in response_json['data']['products']:
            self.product_list.append({
                'name': product['name'],
                'id': product['id'],
                #'price': int(product['salePriceU']) / 100,
                #'starting price': int(product['priceU']) / 100,
                #'sale': product['sale'],
                #'brand': product['brand'],
                'brand id': product['brandId'],
                'supplier id': product['supplierId'],
                'feedbacks': product['feedbacks'],
                'rating': product['rating'],
                #'product url': f'https://www.wildberries.ru/catalog/{product["id"]}/detail.aspx',
                #'supplier url': f'https://www.wildberries.ru/seller/{product["supplierId"]}'
            })

    async def get_product_data_from_json(self, session, page):
        """Retrieves JSON data for products and extracts data from the JSON data, page by page."""
        url_page = f'{self.url}search?appType=1&curr=rub&dest=-1075831,-77677,-398551,12358499&page={page}' \
                   f'&query={self.query}&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,71,114' \
                   f'&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false'

        async with session.get(url=url_page, headers=self.headers) as response:
            response_json = await response.json(content_type=None)
            await self.data_extraction(response_json)

    def save_excel(self):
        """Saves the result to a CSV file."""
        columns = self.product_list[0].keys()
        with open(f'{self.query} {date.today()}.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, dialect='excel', delimiter=';')
            writer.writerow(columns)
            for product in self.product_list:
                writer.writerow(product.values())

    async def session_creation(self):
        """Creates a session for asynchronous parsing."""
        async with aiohttp.ClientSession() as session:
            await self.analysis_of_the_number_of_goods(session)
            await asyncio.sleep(1)
            tasks = []
            for page in range(1, self.counts_of_sessions + 1):
                task = asyncio.create_task(self.get_product_data_from_json(session, page))
                tasks.append(task)
            await asyncio.gather(*tasks)
            self.save_excel()

    def start_asynchronous_parsing(self):
        """This function starts the parser."""
        asyncio.run(self.session_creation())


if __name__ == '__main__':
    query = input('Enter your search query: ')
    print("Processing...")
    ParserWB(query).start_asynchronous_parsing()
    print("Processing completed.")