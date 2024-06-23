# SmartHomeDataExtractor

## Overview

SmartHomeDataExtractor is a comprehensive web scraping tool designed to collect detailed information about smart home devices from various online sources. This script is capable of extracting data such as platform support (e.g., Amazon Alexa, Google Assistant), power and energy specifications, release dates, AI features, pricing, and more. It leverages Selenium for web scraping and uses Pandas for data handling and manipulation.

## Features

- **Smart Home Platform Support:** Checks if devices support platforms like Amazon Alexa, Apple HomeKit, Google Assistant, Samsung SmartThings, and IFTTT.
- **AI Features:** Identifies AI algorithms and mentions in the text.
- **Release Dates:** Extracts release dates and related context.
- **Pricing Information:** Extracts retail prices and subscription fees.
- **Energy and Power Data:** Extracts information about power consumption, annual energy consumption, voltage, frequency, and amperage.
- **Connectivity Features:** Identifies support for connectivity features like WiFi, Bluetooth, Zigbee, Z-Wave, Thread, Matter, and AirPlay.
- **Voice Commands:** Checks for voice command support.
- **Health and Wellness Monitoring:** Extracts information related to health and wellness monitoring features.
- **Routine Automation:** Identifies support for routine automation and schedule setup.
- **Energy Monitoring:** Checks for energy monitoring capabilities.
- **Rebate Programs:** Identifies devices eligible for rebate programs.
- **Portability:** Checks if the device is portable.
- **User Ratings:** Scrapes user ratings for the devices.
- **Security Features:** Extracts security features information.
- **Gas Usage:** Extracts gas usage information.

## Installation

To use this script, you need to have the following packages installed:

- `selenium`
- `beautifulsoup4`
- `pandas`
- `requests`
- `logging`

You can install these packages using pip:

\`\`\`bash
pip install selenium beautifulsoup4 pandas requests logging
\`\`\`

Additionally, you need to install Chromium browser and Chromium WebDriver:

\`\`\`bash
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
\`\`\`

## Usage

1. **Prepare Your CSV File:**

   Ensure your CSV file is formatted with the following columns:
   - No.
   - Manufacturer
   - Product Name
   - Source(Link)
   - Category
   - Type

2. **Run the Script:**

   Execute the script using Python:

   \`\`\`bash
   python SmartHomeDataExtractor.py
   \`\`\`

   The script will process the data, fetch additional details from the web, and update the CSV file.

3. **Output:**

   The updated CSV file will be saved as `Smart_Home_Platform_Database_Updated.csv`. If the script encounters any errors while fetching URLs, those URLs will be logged in `error_urls.log`.

## Contribution

Feel free to fork this repository, submit issues, and make pull requests. Your contributions are welcome!

## License

This project is licensed under the MIT License.
