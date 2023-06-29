# Web Data Parsing and Reviews Scraping

This repository contains a collection of Python scripts for web data parsing and reviews scraping. These scripts offer efficient and flexible solutions for extracting data from websites, enabling users to gather and analyze valuable information.

## Scripts

### 1. Website Data Parser

The Website Data Parser script utilizes asynchronous programming techniques with the `aiohttp` and `asyncio` libraries to parse data from a specified website. It supports pagination for retrieving data in batches and saves the extracted information into CSV files. The script showcases the ability to handle HTTP requests, process JSON data, and perform asynchronous web scraping, providing a scalable approach for data extraction from websites.

### 2. Web Reviews Scraper

The Web Reviews Scraper script focuses on extracting reviews from a specific website, using Wildberries (WB) as an example. It leverages the `selenium` library and Chrome WebDriver for web automation and dynamic content scraping. This project utilizes the --remote-debugging-port flag in Chrome Options and navigates to review pages for each product, extracting review details and storing them in separate CSV files. This script demonstrates techniques for handling authentication, interacting with dynamic elements, and extracting valuable insights from websites with user-generated content.

## Usage

The scripts might be useful for web scraping enthusiasts.