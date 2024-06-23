

# Install Selenium package
!pip install selenium

# Update package lists on the system
!apt-get update

# Install Chromium browser
!apt-get install -y chromium-browser

# Install Chromium WebDriver
!apt-get install -y chromium-chromedriver

import time,sys,os
import random
import requests
import logging
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Set environment variables for ChromeDriver
os.environ['PATH'] += ':/usr/lib/chromium-browser/:/usr/lib/chromium-browser/chromedriver'

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the WebScraper class
class WebScraper:
    def __init__(self, retries=5, delay=5, timeout=30):
        # Initialize the scraper with retries, delay, and timeout settings
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.retries = retries
        self.delay = delay
        self.timeout = timeout
        self.driver = self.init_webdriver()  # Added WebDriver initialization

    def init_webdriver(self):  # New method to initialize WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=options)

    # Fetch URL content with retry mechanism
    def fetch_url(self, url):
        for attempt in range(self.retries):
            try:
                logging.info(f"Fetching URL: {url}, Attempt: {attempt + 1}")
                self.driver.get(url)  # Use Selenium WebDriver to fetch the URL
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
                return self.driver.page_source.lower()  # Return the page source
            except Exception as e:
                logging.error(f"Error fetching {url} on attempt {attempt + 1}: {e}")
                time.sleep(self.delay)
        return None

    # Search for alternative sources if the original link fails
    def search_alternative_sources(self, manufacturer, product_name):
        search_query = f"{manufacturer} {product_name}"
        search_url = f"https://www.google.com/search?q={search_query}"
        try:
            self.driver.get(search_url)
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            results = soup.select('a[href]')
            for link in results:
                href = link.get('href')
                if 'url?q=' in href and 'webcache.googleusercontent' not in href:
                    new_url = href.split('url?q=')[1].split('&')[0]
                    return new_url
        except Exception as e:
            logging.error(f"Error searching alternative sources: {e}")
        return None

    # Check if any of the keywords are present in the text
    def check_feature_support(self, text, keywords):
        if text is None:
            return 'F'
        return 'T' if any(keyword in text for keyword in keywords) else 'F'

    # Extract price information from the text
    def extract_price(self, text):
        price_patterns = [
            r'\$\s?\d+(\.\d{2})?', r'\d+(\.\d{2})?\s?usd', r'\d+(\.\d{2})?\s?dollars', r'\d+\s?bucks',
            r'\$\s?\d+(,\d{3})*(\.\d{2})?',  # Matches prices like $1,234.56 or $1234.56
            r'\d+(,\d{3})*(\.\d{2})?\s?usd',  # Matches prices like 1,234.56 USD or 1234.56 USD
            r'\d+(,\d{3})*(\.\d{2})?\s?dollars',  # Matches prices like 1,234.56 dollars or 1234.56 dollars
            r'\d+(,\d{3})*(\.\d{2})?\s?bucks'  # Matches prices like 1,234.56 bucks or 1234.56 bucks
        ]
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    # Extract relevant text based on keywords
    def extract_relevant_text(self, full_text, keywords):
        if full_text is None:
            return ''
        lines = full_text.split('
')
        relevant_text = []
        for line in lines:
            if any(keyword in line for keyword in keywords):
                relevant_text.append(line)
        return ' '.join(relevant_text)

    # Find AI algorithm mentions in the text
    def find_ai_algorithm(self, text):
        if text is None:
            return 'Not specified'
        algorithms = [
            'machine learning', 'deep learning', 'neural network', 'support vector machine', 'random forest',
            'gradient boosting', 'k-nearest neighbors', 'logistic regression', 'naive bayes', 'decision tree',
            'artificial intelligence', 'AI algorithm', 'supervised learning', 'unsupervised learning',
            'reinforcement learning', 'genetic algorithm', 'fuzzy logic', 'bayesian network', 'markov model',
            'ensemble learning', 'transfer learning', 'representation learning', 'natural language processing',
            'computer vision', 'speech recognition', 'recommender system', 'anomaly detection'
        ]

        ai_phrases = [
            'ai','artificial intelligence','powered by ai', 'ai-driven', 'ai-enabled', 'intelligent system', 'smart technology',
            'predictive model', 'automated learning', 'adaptive system', 'smart assistant'
        ]

        for algo in algorithms:
            if algo in text:
                return algo.capitalize()

        for phrase in ai_phrases:
            if phrase in text:
                return 'AI-based technology'

        return 'Not specified'

    # Find release date and context in the text
    def find_release_date_and_context(self, text):
        if text is None:
            return 'Not found', 'No context found'
        patterns = [
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},\s+\d{4}',
            r'\d{1,2}[\/\-\s]\d{1,2}[\/\-\s]\d{2,4}',
            r'\d{4}[\/\-\s]\d{1,2}[\/\-\s]\d{1,2}',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                context_phrases = [
                    'release date', 'launched on', 'introduced on', 'available from', 'available starting',
                    'release on', 'release schedule', 'launch date', 'first released', 'release', 'launch',
                    'available', 'introduced', 'starting'
                ]
                context = 'No context found'
                for phrase in context_phrases:
                    phrase_start = text.find(phrase)
                    if phrase_start != -1 and phrase_start < match.start():
                        context = phrase
                        break
                return match.group(0), context

        return 'Not found', 'No context found'

    def extract_price_details(self, text):
        if text is None:
            return {}
        prices = {}
        price_patterns = [
            r'\$\s?\d+(,\d{3})*(\.\d{2})?', r'\d+(,\d{3})*(\.\d{2})?\s?usd', r'\d+(,\d{3})*(\.\d{2})?\s?dollars', r'\d+(,\d{3})*(\.\d{2})?\s?bucks'
        ]
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                prices['Retail Price($)'] = match.group(0)
                break

        # Extracting monthly fees
        service_fee_keywords = ['monthly fee', 'subscription fee', 'service fee', 'membership fee', 'monthly subscription', 'service charge', 'subscription charge', 'monthly cost']
        service_fee_text = self.extract_relevant_text(text, service_fee_keywords)
        service_fee_price = self.extract_price(service_fee_text)
        prices['Service Monthly Fee($/month)'] = service_fee_price if service_fee_price else 'N/A'
        return prices

    # Extract relevant text from HTML content
    def extract_relevant_text_from_html(self, html_content):
        if html_content is None:
            return ''
        soup = BeautifulSoup(html_content, 'html.parser')
        relevant_text = ''
        product_description = soup.find('div', {'id': 'productDescription'})
        feature_bullets = soup.find('div', {'id': 'feature-bullets'})
        price_block = soup.find('div', {'id': 'priceblock_ourprice'})  # Added price block

        if product_description:
            relevant_text += product_description.get_text(separator=' ').lower()

        if feature_bullets:
            relevant_text += ' ' + feature_bullets.get_text(separator=' ').lower()

        if price_block:
            relevant_text += ' ' + price_block.get_text(separator=' ').lower()  # Added price block text

        return relevant_text


    # Check for gas usage in the text
    def check_gas_usage(self, text):
        if text is None:
            return ''
        pattern = re.compile(r'(\d+\.?\d*)\s*(btu|british thermal unit|therms?|cf|cubic feet|ft³|m³|cubic meters|megajoules|mj|gas|gas usage)', re.IGNORECASE)
        matches = pattern.findall(text)
        if matches:
            return '; '.join([f"{match[0]} {match[1]}" for match in matches])
        return ''

# Load CSV file into a DataFrame
def load_csv(file_path):
    return pd.read_csv(file_path)

# Identify rows with missing information in a specific column
def identify_missing_info(data, column_name):
    missing_info = data[data[column_name].isnull()]
    return missing_info.dropna(subset=['Source(Link)'])

# Process URLs and update the DataFrame
def process_urls(data, column_name, keywords, error_urls, scraper):
    missing_info = identify_missing_info(data, column_name)
    urls = missing_info['Source(Link)'].tolist()
    total_urls = len(urls)

    for i, url in enumerate(urls):
        if pd.isna(url):
            continue

        try:
            start_time = time.time()
            html_content = scraper.fetch_url(url)
            if html_content is None:
                # Search for alternative sources if the original link fails
                manufacturer = missing_info.iloc[i]['Manufacturer']
                product_name = missing_info.iloc[i]['Product Name']
                new_url = scraper.search_alternative_sources(manufacturer, product_name)
                if new_url:
                    html_content = scraper.fetch_url(new_url)
                    data.loc[data['Source(Link)'] == url, 'New_Source(Link)'] = new_url
                    if html_content is None:
                        error_urls.append(url)
                        continue
                else:
                    error_urls.append(url)
                    continue

            supports = scraper.check_feature_support(html_content, keywords)
            data.loc[data['Source(Link)'] == url, column_name] = 'T' if supports else 'F'
            time.sleep(random.uniform(1, 3))
            elapsed_time = time.time() - start_time
            logging.info(f"Processed {i + 1}/{total_urls} URLs - Elapsed time: {elapsed_time:.2f} seconds")
            print(f"Processed {i + 1}/{total_urls} URLs - Elapsed time: {elapsed_time:.2f} seconds")
        except Exception as e:
            logging.error(f"Unexpected error processing {url}: {e}")
            error_urls.append(url)

    return error_urls

# Process voice command support information
def process_voice_commands(data, scraper):
    data['Voice Commands(T/F)'] = ''
    error_urls = []
    total_rows = len(data)
    keywords = ['personal assistant', 'smart speaker', 'hands-free control', 'ivr', 'voice', 'speech']

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            # Search for alternative sources if the original link fails
            manufacturer = row['Manufacturer']
            product_name = row['Product Name']
            new_url = scraper.search_alternative_sources(manufacturer, product_name)
            if new_url:
                html_content = scraper.fetch_url(new_url)
                data.at[i, 'New_Source(Link)'] = new_url
                if html_content is None:
                    error_urls.append(url)
                    continue
            else:
                error_urls.append(url)
                continue

        support = scraper.check_feature_support(html_content, keywords)
        data.at[i, 'Voice Commands(T/F)'] = support
        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls


# Process geofencing support information
def process_geofencing(data, scraper):
    data['Geofencing(T/F)'] = ''
    error_urls = []
    total_rows = len(data)
    keywords = [
        'geofencing', 'geolocation features', 'location-based automation', 'GPS smart home', 'location-triggered',
        'proximity sensors', 'GPS gadgets', 'location tracking', 'geolocation products', 'proximity automation',
        'GPS integration', 'GPS-triggered automation', 'location services', 'geolocation tech', 'location-aware devices',
        'proximity-based devices', 'geolocation', 'GPS home', 'location-based'    ]

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue
        support = scraper.check_feature_support(html_content, keywords)
        data.at[i, 'Geofencing(T/F)'] = support
        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls

# Process health and wellness monitoring support information
def process_health_wellness_monitoring(data, scraper):
    data['Health and Wellness Monitoring(T/F)'] = ''
    error_urls = []
    total_rows = len(data)
    keywords = [
        'health', 'healthy', 'air quality monitors', 'sleep trackers', 'fitness equipment', 'air purifiers',
        'wellness technology', 'fall detection', 'medication reminders', 'activity trackers', 'monitoring systems',
        'medical alert systems', 'diagnostic devices', 'fitness tracker features', 'wearable health tech',
        'fitness wearables', 'activity tracking', 'tracking devices', 'medical devices', 'air monitors', 'fitness devices',
        'remote monitoring', 'pressure monitors', 'glucose monitors', 'wellness tech', 'fitness tracker', 'wearable tech',
        'wellness tracking', 'activity tracking', 'temperature monitors', 'humidity monitors', 'air purifiers', 'stress monitors',
        'monitoring systems', 'alert systems', 'impact sensors'
    ]

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue
        support = scraper.check_feature_support(html_content, keywords)
        data.at[i, 'Health and Wellness Monitoring(T/F)'] = support
        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls

# Process routine automation and schedule setup support information
def process_routine_automation_schedule_setup(data, scraper):
    data['Routine Automation and Schedule Setup(T/F)'] = ''
    error_urls = []
    total_rows = len(data)
    keywords = [
        'routine', 'schedule', 'schedules', 'scheduling', 'personalized home automation', 'personalized smart home features',
        'smart home task automation', 'smart home event automation', 'smart home lifestyle automation', 'smart home habit automation',
        'smart home personalized automation', 'smart home task integration', 'smart home automation planner', 'personalized automation',
        'task automation', 'event automation', 'automated setup', 'automation management', 'calendar integration', 'event setup',
        'task manager', 'lifestyle automation', 'habit automation', 'task integration', 'automation planner'
    ]

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue
        support = scraper.check_feature_support(html_content, keywords)
        data.at[i, 'Routine Automation and Schedule Setup(T/F)'] = support
        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls

# Process energy monitoring support information
def process_energy_monitoring(data, scraper):
    data['ENERGY Monitoring(T/F)'] = ''
    error_urls = []
    total_rows = len(data)
    keywords = [
        'energy monitoring devices', 'smart home energy monitoring', 'energy usage tracking', 'home energy management',
        'smart energy meters', 'energy consumption monitoring', 'smart home power monitoring', 'real-time energy monitoring',
        'energy efficiency devices', 'smart home energy tracking', 'energy-saving devices', 'energy usage monitoring',
        'smart energy systems', 'home energy analytics', 'energy management systems', 'power consumption monitoring',
        'energy usage sensors', 'smart home energy analytics', 'home power tracking', 'energy monitoring solutions',
        'smart home energy meters', 'smart power meters', 'energy data monitoring', 'energy usage analytics', 'home energy tracking',
        'smart home power tracking', 'energy consumption tracking', 'energy monitoring tech', 'smart home energy management',
        'energy-saving technology', 'home energy sensors', 'energy management tech', 'smart energy monitoring', 'power usage monitoring',
        'energy tracking devices', 'energy usage devices', 'smart home power management', 'energy monitoring systems', 'smart home energy solutions',
        'home energy efficiency', 'energy usage solutions', 'energy management devices', 'smart home energy tech', 'energy tracking systems',
        'power monitoring devices', 'energy consumption sensors', 'smart energy tech', 'home energy solutions', 'energy management systems',
        'energy-saving solutions', 'energy efficiency monitoring', 'smart home power meters', 'energy consumption analytics',
        'energy efficiency tracking', 'energy monitoring', 'energy tracking', 'power monitoring', 'energy management', 'energy sensors',
        'energy analytics', 'smart energy', 'home energy', 'energy efficiency', 'energy solutions', 'power tracking', 'smart meters'
    ]

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue
        support = scraper.check_feature_support(html_content, keywords)
        data.at[i, 'ENERGY Monitoring(T/F)'] = support
        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls

# Process rebate program support information
def process_rebate_program(data, scraper):
    data['Rebate program(T/F)'] = ''
    error_urls = []
    total_rows = len(data)
    keywords = [
        'smart home discount program', 'eligible for smart device discounts', 'smart home incentives', 'energy savings programs',
        'discount smart home devices', 'offers on smart devices', 'programs for smart home discounts', 'energy efficient discounts',
        'smart home offers', 'smart device eligibility for discounts', 'programs for energy device discounts', 'incentives for smart home',
        'programs for smart home device discounts', 'eligible energy devices for discounts', 'opportunities for smart home discounts',
        'smart home technology discounts', 'qualified smart devices for discounts', 'smart home savings programs', 'energy device discounts',
        'offers for smart home devices', 'smart home discounts', 'smart home energy incentives', 'eligible home automation discounts',
        'smart home incentive offers', 'smart energy device discounts', 'home energy savings programs', 'programs for smart technology discounts',
        'smart home solutions discounts', 'qualified energy devices for discounts', 'offers for smart technology', 'opportunities for smart home savings',
        'smart home gadgets discounts', 'energy management system discounts', 'smart home tech savings', 'energy monitoring device discounts',
        'offers on smart gadgets', 'smart home systems discounts', 'energy efficient device discounts', 'home automation system discounts',
        'offers for home technology', 'programs for smart meters', 'smart meters discounts', 'offers on energy devices', 'eligible home devices for discounts',
        'smart home appliance discounts', 'smart home tech offers', 'programs for home tech discounts', 'qualified home devices for discounts',
        'energy solutions discounts', 'opportunities for energy device savings', 'incentives for smart home', 'programs for energy management discounts',
        'offers on smart appliances', 'home energy device savings', 'home device discounts', 'device offers', 'savings programs',
        'discount devices', 'smart home incentives', 'eligible for discounts', 'incentives programs', 'energy savings', 'tech discounts',
        'energy offers', 'home tech savings', 'smart device discounts', 'energy management savings', 'rebate', 'rebates'
    ]

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue
        support = scraper.check_feature_support(html_content, keywords)
        data.at[i, 'Rebate program(T/F)'] = support
        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls

# Process AI support information
def process_ai(data, scraper):
    data['AI(T/F)'] = ''
    error_urls = []
    total_rows = len(data)
    keywords = [
        'AI', 'ML', 'DL', 'artificial intelligence', 'deep learning', 'intelligent home systems', 'smart home predictive technology',
        'intelligent automation devices', 'intelligent home assistants', 'intelligent home devices', 'intelligent home tech', 'smart home intelligence'
    ]

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue

        support = scraper.check_feature_support(html_content, keywords)
        data.at[i, 'AI(T/F)'] = support
        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls

# Process AI algorithm information
def process_ai_algorithm(data, scraper):
    data['AI algorithm'] = ''
    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        if row['AI(T/F)'] == 'T':
            url = row['Source(Link)']
            if pd.isna(url):
                continue
            html_content = scraper.fetch_url(url)
            if html_content is None:
                error_urls.append(url)
                continue
            ai_algorithm = scraper.find_ai_algorithm(html_content)
            data.at[i, 'AI algorithm'] = ai_algorithm
            time.sleep(random.uniform(1, 3))
            logging.info(f"Processed {i + 1}/{total_rows} rows")
            print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls

# Process release date information
def process_release_dates(data, scraper):
    data['Release Date'] = ''
    data['Release Date Context'] = ''
    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue
        release_date, context = scraper.find_release_date_and_context(html_content)
        data.at[i, 'Release Date'] = release_date
        data.at[i, 'Release Date Context'] = context
        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls

# Process ENERGY STAR certification information
def process_energy_star(data, scraper):
    data['ENERGY STAR (T/F)'] = ''
    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue
        energy_star = scraper.check_feature_support(html_content, ['energy star', 'energy-star'])
        data.at[i, 'ENERGY STAR (T/F)'] = 'T' if energy_star else 'F'
        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls

# Process smart home platform support information
def process_smart_home_platforms(data, scraper):
    columns_to_add = ['Amazon Alexa(T/F)', 'Apple HomeKit(T/F)', 'Google Assistant(T/F)', 'Samsung SmartThings(T/F)', 'IFTTT(T/F)']
    for column in columns_to_add:
        if column not in data.columns:
            data[column] = 'F'

    features_keywords = {
        'Amazon Alexa(T/F)': ['amazon alexa', 'alexa compatible', 'works with alexa'],
        'Apple HomeKit(T/F)': ['apple homekit', 'works with apple homekit', 'homekit compatible', 'works with homekit', 'siri',
                          'apple smart home', 'apple home', 'apple home app', 'works with siri', 'compatible with siri',
                          'apple', 'homekit', 'siri shortcuts', 'apple homekit enabled', 'apple homekit certified'],
        'Google Assistant(T/F)': ['google assistant', 'works with google assistant', 'google home', 'google nest', 'works with nest',
                             'compatible with google', 'google smart home', 'google assistant enabled', 'google assistant certified'],
        'Samsung SmartThings(T/F)': ['samsung smartthings', 'samsung', 'samsung home', 'smartthings', 'works with smartthings',
                                'compatible with samsung smart home', 'compatible with samsung smartthings', 'compatible with smartthings',
                                'samsung smart home', 'samsung smartthings certified'],
        'IFTTT(T/F)': ['ifttt', 'works with ifttt', 'compatible with ifttt', 'ifttt support']
    }

    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        text = scraper.fetch_url(url)
        if text is None or text in ['Error', 'Too many redirects']:
            error_urls.append(url)
            continue

        for column, keywords in features_keywords.items():
            data.at[i, column] = scraper.check_feature_support(text, keywords)

        time.sleep(random.uniform(1, 3))
        logging.info(f'Processed {i + 1}/{total_rows} rows')
        print(f'Processed {i + 1}/{total_rows} rows')

    return error_urls

# Process power and energy data
def process_power_energy_data(data, scraper):
    features_keywords = {
        'Power (Watts)': ['power', 'maximum output power', 'max output power', 'idle power', 'standby power', 'active use power', 'max power', 'charging power', 'watts'],
        'Annual Energy Consumption (kWh/year)': ['annual energy consumption', 'energy consumption', 'kwh/year'],
        'Voltage (V)': ['voltage', 'v /', 'volts'],
        'Frequency (Hz)': ['frequency', 'hz'],
        'Amperage (A)': ['ampere', 'amps', 'amperage']
    }

    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        text = scraper.fetch_url(url)
        if text is None or text in ['Error', 'Too many redirects']:
            error_urls.append(url)
            continue

        for feature, keywords in features_keywords.items():
            relevant_text = scraper.extract_relevant_text(text, keywords)
            pattern = re.compile(r'(\d+\.?\d*)\s*(watts|watt|w|kwh/year|v|volts|hz|amperes|amps|a|hours|h|years|min|°c|% rh|ft|in|lb/kwh|w/hr|kwh|kwh/year)', re.IGNORECASE)

            matches = pattern.findall(relevant_text)
            if matches:
                extracted_values = [f"{match[0]} {match[1]}" for match in matches if any(kw in match[1].lower() for kw in keywords)]
                data.at[i, feature] = '; '.join(extracted_values) if extracted_values else 'No'

        time.sleep(random.uniform(1, 3))
        logging.info(f'Processed {i + 1}/{total_rows} rows')
        print(f'Processed {i + 1}/{total_rows} rows')

    return error_urls

# Process battery data
def process_battery_data(data, scraper):
    data['Battery (T/F)'] = ''
    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue
        energy_star = scraper.check_feature_support(html_content, ['battery', 'batteries'])
        data.at[i, 'Battery (T/F)'] = 'T' if energy_star else 'F'
        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls

# Process gas usage information
def process_gas_usage(data, scraper):
    data['Gas(T/F)'] = 'F'
    data['Gas Usage (BTU)'] = ''
    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue
        relevant_text = scraper.extract_relevant_text_from_html(html_content)
        gas_result = scraper.check_gas_usage(relevant_text)
        data.at[i, 'Gas(T/F)'] = 'T' if gas_result else 'F'
        data.at[i, 'Gas Usage (BTU)'] = gas_result
        time.sleep(random.uniform(1, 3))
        logging.info(f"{url}: Gas - {gas_result}")
        print(f"{url}: Gas - {gas_result}")

    return error_urls

# Process connectivity features
def process_connectivity_features(data, scraper):
    columns_to_add = ['WiFi(T/F)', 'Bluetooth(T/F)', 'Zigbee(T/F)', 'Z-Wave(T/F)', 'Thread(T/F)', 'Matter(T/F)', 'AirPlay(T/F)']
    for column in columns_to_add:
        if column not in data.columns:
            data[column] = 'F'

    features_keywords = {
        'WiFi(T/F)': ['wifi', 'wi-fi'],
        'Bluetooth(T/F)': ['bluetooth'],
        'Zigbee(T/F)': ['zigbee'],
        'Z-Wave(T/F)': ['z-wave', 'zwave'],
        'Thread(T/F)': ['thread'],
        'Matter(T/F)': ['matter'],
        'AirPlay(T/F)': ['airplay']
    }

    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        text = scraper.fetch_url(url)
        if text is None or text in ['Error', 'Too many redirects']:
            error_urls.append(url)
            continue

        for column, keywords in features_keywords.items():
            data.at[i, column] = scraper.check_feature_support(text, keywords)

        time.sleep(random.uniform(1, 3))
        logging.info(f'Processed {i + 1}/{total_rows} rows')
        print(f'Processed {i + 1}/{total_rows} rows')

    return error_urls

# Process prices information
def process_prices(data, scraper):
    data['Retail Price($)'] = ''
    data['Price per Unit($)'] = ''
    data['Service Monthly Fee($/month)'] = ''
    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        html_content = scraper.fetch_url(url)
        if html_content is None:
            error_urls.append(url)
            continue

        # Extract retail price
        price_details = scraper.extract_price_details(html_content)
        data.at[i, 'Retail Price($)'] = price_details.get('Retail Price($)', 'N/A')
        data.at[i, 'Service Monthly Fee($/month)'] = price_details.get('Service Monthly Fee($/month)', 'N/A')

        # Extract price per unit if applicable
        product_name = row['Product Name']
        if product_name and 'pack' in product_name.lower():
            try:
                units = int(re.search(r'\d+', product_name).group())
                if units and price_details.get('Retail Price($)'):
                    price_per_unit = float(re.sub(r'[^\d.]', '', price_details.get('Retail Price($)'))) / units
                    data.at[i, 'Price per Unit($)'] = f"{price_per_unit:.2f}"
            except (AttributeError, ValueError):
                pass

        time.sleep(random.uniform(1, 3))
        logging.info(f"Processed {i + 1}/{total_rows} rows")
        print(f"Processed {i + 1}/{total_rows} rows")

    return error_urls if error_urls else []

# Create an HTTP session with retry logic
def create_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    })
    print("HTTP session created with retry and custom user-agent.")
    return session

# Check if a device is portable
def is_portable(url, session):
    try:
        # print(f"Processing URL: {url}")
        # response = session.get(url, timeout=10)
        # soup = BeautifulSoup(response.text, 'html.parser')
        # description = soup.find('body').get_text().lower()

        print(f"Processing URL: {url}")
        response = session.get(url, timeout=10)
        html_content = scraper.fetch_url(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        description = soup.get_text().lower()

        keywords = ['portable', 'battery', 'handheld', 'easy to carry', "mobile", 'wearable']
        for keyword in keywords:
            if keyword in description:
                print(f"Device at {url} is portable.")
                return 'T'

        print(f"Device at {url} is not portable.")
        return 'F'
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return 'F'

# Scrape additional data from a URL using Selenium
def scrape_additional_data(url, driver):
    try:
        driver.get(url)
        time.sleep(2)

        def get_element_text(selectors, keywords=None, retries=3):
            for selector in selectors:
                for attempt in range(retries):
                    try:
                        elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                        for element in elements:
                            text = element.text.strip()
                            if keywords:
                                for keyword in keywords:
                                    if keyword.lower() in text.lower():
                                        return keyword
                            else:
                                if text:
                                    return text
                    except:
                        time.sleep(1)
                        continue
            return 'N/A'

        user_ratings_selectors = [
            'span#acrCustomerReviewText',
            'div#averageCustomerReviews',
            'div.a-row.a-spacing-medium.averageStarRatingNumerical'
        ]

        security_features_selectors = [
            'div#feature-bullets ul li',
            'div#productDescription',
            'div.a-section.a-spacing-medium.a-spacing-top-small'
        ]

        security_keywords = [
            'security', 'privacy', 'encryption', 'secure', 'data protection', 'password', 'authentication', 'voice control', 'mic off'
        ]

        user_ratings = get_element_text(user_ratings_selectors)
        security_features = get_element_text(security_features_selectors, security_keywords)

        if "ratings" in user_ratings.lower():
            user_ratings = user_ratings.split()[0] + " ratings"

        return user_ratings, security_features
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return 'N/A', 'N/A'

# Process user ratings using Selenium
def process_user_ratings(data, driver):
    data['User Ratings'] = ''
    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        print(f"Scraping URL {i + 1}/{total_rows}: {url}")
        user_ratings, _ = scrape_additional_data(url, driver)
        data.at[i, 'User Ratings'] = user_ratings
        print(f"User Ratings for {row['Product Name']}: {user_ratings}")
        time.sleep(random.uniform(1, 3))

    return error_urls

def process_security_features(data, driver):
    data['Security Features'] = ''
    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        print(f"Scraping URL {i + 1}/{total_rows}: {url}")
        _, security_features = scrape_additional_data(url, driver)
        data.at[i, 'Security Features'] = security_features
        print(f"Security Features for {row['Product Name']}: {security_features}")
        time.sleep(random.uniform(1, 3))

    return error_urls

# Process portability information
def process_portable(data, scraper):
    data['Portable(T/F)'] = ''
    error_urls = []
    total_rows = len(data)

    for i, row in data.iterrows():
        url = row['Source(Link)']
        if pd.isna(url):
            continue
        print(f"Checking portability for URL {i + 1}/{total_rows}: {url}")
        html_content = scraper.fetch_url(url)  # Corrected method call
        if html_content is None:
            error_urls.append(url)
            continue
        soup = BeautifulSoup(html_content, 'html.parser')
        description = soup.get_text().lower()

        keywords = ['portable', 'battery', 'handheld', 'easy to carry', "mobile", 'wearable']
        is_portable = 'F'
        for keyword in keywords:
            if keyword in description:
                is_portable = 'T'
                break

        data.at[i, 'Portable(T/F)'] = is_portable
        time.sleep(random.uniform(1, 3))

    return error_urls


# Main function to execute the script
def main():
    start_time = time.time()
    scraper = WebScraper()
    file_path = 'Smart_Home_Platform_Database.csv'
    final_data = load_csv(file_path)
    final_data['New_Source(Link)'] = 
    error_urls = []

    try:
        logging.info("Starting to process smart home platforms")
        print("Starting to process smart home platforms")
        error_urls.extend(process_smart_home_platforms(final_data, scraper))
        logging.info("Finished processing smart home platforms")
        print("Finished processing smart home platforms")

        logging.info("Starting to process release dates")
        print("Starting to process release dates")
        error_urls.extend(process_release_dates(final_data, scraper))
        logging.info("Finished processing release dates")
        print("Finished processing release dates")

        logging.info("Starting to process prices")
        print("Starting to process prices")
        error_urls.extend(process_prices(final_data, scraper))
        logging.info("Finished processing prices")
        print("Finished processing prices")

        logging.info("Starting to process connectivity protocols")
        print("Starting to process connectivity protocols")
        error_urls.extend(process_connectivity_features(final_data, scraper))
        logging.info("Finished processing connectivity protocols")
        print("Finished processing connectivity protocols")

        logging.info("Starting to process ENERGY STAR certification")
        print("Starting to process ENERGY STAR certification")
        error_urls.extend(process_energy_star(final_data, scraper))
        logging.info("Finished processing ENERGY STAR certification")
        print("Finished processing ENERGY STAR certification")

        logging.info("Starting to process energy monitoring")
        print("Starting to process energy monitoring")
        error_urls.extend(process_energy_monitoring(final_data, scraper))
        logging.info("Finished processing energy monitoring")
        print("Finished processing energy monitoring")

        logging.info("Starting to process power and energy data")
        print("Starting to process power and energy data")
        error_urls.extend(process_power_energy_data(final_data, scraper))
        logging.info("Finished processing power and energy data")
        print("Finished processing power and energy data")

        logging.info("Starting to process battery data")
        print("Starting to process battery data")
        error_urls.extend(process_battery_data(final_data, scraper))
        logging.info("Finished processing battery data")
        print("Finished processing battery data")

        logging.info("Starting to process gas usage data")
        print("Starting to process gas usage data")
        error_urls.extend(process_gas_usage(final_data, scraper))
        logging.info("Finished processing gas usage data")
        print("Finished processing gas usage data")

        logging.info("Starting to process AI(T/F)")
        print("Starting to process AI(T/F)")
        error_urls.extend(process_ai(final_data, scraper))
        logging.info("Finished processing AI(T/F)")
        print("Finished processing AI(T/F)")

        logging.info("Starting to process AI algorithms")
        print("Starting to process AI algorithms")
        error_urls.extend(process_ai_algorithm(final_data, scraper))
        logging.info("Finished processing AI algorithms")
        print("Finished processing AI algorithms")

        logging.info("Starting to process rebate program")
        print("Starting to process rebate program")
        error_urls.extend(process_rebate_program(final_data, scraper))
        logging.info("Finished processing rebate program")
        print("Finished processing rebate program")

        logging.info("Starting to process portable")
        print("Starting to process portable")
        error_urls.extend(process_portable(final_data, scraper))
        logging.info("Finished processing portable")
        print("Finished processing portable")

        logging.info("Starting to process voice_commands")
        print("Starting to process voice_commands")
        error_urls.extend(process_voice_commands(final_data, scraper))
        logging.info("Finished processing voice_commands")
        print("Finished processing voice_commands")

        logging.info("Starting to process routine_automation_schedule_setup")
        print("Starting to process routine_automation_schedule_setup")
        error_urls.extend(process_routine_automation_schedule_setup(final_data, scraper))
        logging.info("Finished processing routine_automation_schedule_setup")
        print("Finished processing routine_automation_schedule_setup")

        logging.info("Starting to process process_health_wellness_monitoring")
        print("Starting to process process_health_wellness_monitoring")
        error_urls.extend(process_health_wellness_monitoring(final_data, scraper))
        logging.info("Finished processing process_health_wellness_monitoring")
        print("Finished processing process_health_wellness_monitoring")

        logging.info("Starting to process user ratings")
        print("Starting to process user ratings")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        error_urls.extend(process_user_ratings(final_data, driver))
        driver.quit()
        logging.info("Finished processing user ratings")
        print("Finished processing user ratings")

        logging.info("Starting to process security features")
        print("Starting to process security features")
        driver = webdriver.Chrome(options=options)
        error_urls.extend(process_security_features(final_data, driver))
        driver.quit()
        logging.info("Finished processing security features")
        print("Finished processing security features")

        updated_file_path = 'Smart_Home_Platform_Database_Updated.csv'
        final_data.to_csv(updated_file_path, index=False)
        print("The database has been updated and saved to", updated_file_path)

        logging.info('Final results saved')
        print('Final results saved')

        if error_urls:
            logging.info("Logging error URLs")
            print("Logging error URLs")
            with open('error_urls.log', 'w') as f:
                for url in error_urls:
                    f.write(f"{url}
")
            logging.info(f'Logged error URLs: {len(error_urls)} URLs')
            print(f'Logged error URLs: {len(error_urls)} URLs')

    except KeyboardInterrupt:
        logging.warning("Script interrupted by user. Saving progress...")
        print("Script interrupted by user. Saving progress...")
        partial_file_path = 'Smart_Home_Platform_Database_Partial.csv'
        final_data.to_csv(partial_file_path, index=False)
        print(f"Partial results saved to {partial_file_path}")

    total_time = time.time() - start_time
    logging.info(f"Total execution time: {total_time:.2f} seconds")
    print(f"Total execution time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()


