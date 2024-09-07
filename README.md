# Real Estate Data Scraper

This repository contains a Python-based web scraper designed to gather real estate data from the German website <https://www.immobilienscout24.de/>. The primary goal of this project is to collect and store historical real estate offer data over an extended period, allowing for deeper analysis and better-informed decisions when actively searching for properties in the future.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Remarks](#remarks)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Finding the right real estate offer can be challenging, especially in smaller cities where only a few properties are listed at any given time. This project aims to address this by collecting real estate offers over a longer period of time, providing a rich dataset that can be used to compare current offers against historical data.

## Features

- **Web Scraping**: Automatically scrapes specified real estate websites for buying and renting offers.
- **Data Storage**: Saves collected data to a structured format for easy access and analysis.
- **Flexible Configuration**: Easily configurable to target different cities, property types, and other criteria.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/FabianSchlueter/immobilienscout-scraper.git
   cd immobilienscout-scraper

2. **Install Dependencies**

   ```bash
    pip install -r requirements.txt

3. **Set Up Pre-commit Hooks (optional but recommended):**

   ```bash
    pre-commit install

## Usage

1. **Configure the Scraper:** Edit the configuration files to specify search criteria and storage location - see [Configuration](#configuration).

2. **Run the Scraper:** The scraper will start fetching real estate offers based on the configuration provided.

   ```bash
    python main.py

3. **View Collected Data:** The collected data will be stored in an Excel file in the configured location. You can analyze this data using Excel or other tools.

## Configuration

The scraper's behavior is controlled via a configuration file [search_config.yml](config/search_config.yml). This file allows you to specify:

- **Search Criteria:** Filters for location, property type, price range, etc. You can go to https://www.immobilienscout24.de/ and filter for your criteria manually. Then, copy the URL of the first search result page and add it to the list of URLs of a city. Make sure that the URLs end with "&pagenumber=". Each city can have multiple URLs to scrape. The data is aggregated in one file per city.
- **Data Storage:** Specify the directory where the data should be stored.

Also, if you want to cast columns of the output data to numeric or string, you can set those in [format_config.yml](config/format_config.yml). For calculating columns like rent per squaremeter you can set those in [calculations.yml](config/calculations_config.yml)

## Remarks

After a successful scraping run the newly gathered data is added to previously scraped data in the storage file if existing. If so, the data is de-duplicated, so that only the newest entry per offer will remain in the data. If you want to analyze offers that were published during a specified time, use the column 'OnlineSince', which is the first publish date of each offer.

## Contributing

Contributions are welcome! If you have suggestions, bug reports, or new features to add, feel free to open an issue or submit a pull request. Please follow the existing code style and ensure that your code passes all pre-commit checks.

### How to Contribute

1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Make your changes.
4. Commit your changes (git commit -m 'Add some feature').
5. Push to the branch (git push origin feature-branch).
6. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency.

To set up pre-commit hooks locally, run the following command after having [installed dependencies](#installation):

```bash
pre-commit install
