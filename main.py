"""
This script is the main entry point for the immobilienscout24 scraper project.

Usage:
    python main.py

Ensure that the necessary dependencies are installed and the configuration file is correctly set up before running the script.

For details see README.md

Author: Fabian Schlueter
Date: 2024-09-07
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import json
from datetime import datetime
import time
import pandas as pd
import utils


def main():

    # Load configs
    search_parameters = utils.load_yaml_config(
        file_path=r'config\search_config.yml')['Cities']
    storage_directory = utils.load_yaml_config(
        file_path=r'config\search_config.yml')['Storage_Directory'][0]
    output_format_config = utils.load_yaml_config(
        file_path=r'config\format_config.yml')
    calculation_config = utils.load_yaml_config(
        file_path=r'config\calculations_config.yml')

    # Open webbrowser
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options=options)

    # Loop through list of search parameters for each city
    for search_city in search_parameters:

        # Open output from previous searches for this city if existing. New results will be appended at the end of scraping process.
        main_data_storage_file = f'{storage_directory}{search_city}.xlsx'
        df_previous_data = utils.get_previously_scraped_data_from_storage(storage_directory=storage_directory,
                                                                          storage_file=main_data_storage_file)

        # Dataframe for collecting all data of the current search_city
        df_search_city = pd.DataFrame()

        # Loop through all search urls
        for search_url in search_parameters[search_city]:
            print(f'\nSearch in {search_city} with url {search_url}.')

            number_of_result_pages = utils.get_number_of_result_pages(
                driver=driver, search_url=search_url)

            # Loop through all result pages
            for i in range(1, number_of_result_pages+1):
                print(f'\nReading result page number {i} at')
                print(datetime.now().strftime('%H:%M:%S'))

                # Open result page
                driver.get(f'{search_url}{i}')
                WebDriverWait(driver, 3)
                html_result_page = driver.page_source
                # Check for captcha. If captcha then solve it manually
                utils.captcha_check(html_result_page)

                # Get list of unique offers on the result page
                offers = utils.get_unique_offers_from_result_page_source(
                    html=html_result_page)

                # Loop through all offers
                for o in offers:
                    offer_url = f'https://www.immobilienscout24.de{o}'
                    try:

                        # Get offer page source
                        driver.get(offer_url)
                        WebDriverWait(driver, 2)
                        html_offer = driver.page_source

                        # Check for captcha. If captcha then solve it manually
                        utils.captcha_check(html_offer)
                        time.sleep(1)

                        # Read html source again in case there was a captcha
                        html_offer = driver.page_source

                        # Most features are written in one json formatted block within html source code
                        html_offer_json = html_offer.split('keyValues = ')[1]
                        html_offer_json = html_offer_json.split(r'};')[
                            0] + r'}'

                        # Feature "Online since" is outside of json part
                        html_offer_online_since = html_offer.split(
                            'exposeOnlineSince: "')[1]
                        html_offer_online_since = html_offer_online_since.split(r'",')[
                            0]

                        # Title is outside of json part
                        html_title = html_offer.split(
                            r'</title>')[0].split(r'<title>')[1]

                        # Dictionary for storing the extracted offer data
                        offer_dict = {}

                        offer_dict = json.loads(html_offer_json)

                        offer_dict['url'] = offer_url
                        offer_dict['ExtractDate'] = datetime.now().strftime(
                            '%Y-%m-%d')
                        offer_dict['ExtractTime'] = datetime.now().strftime(
                            '%H:%M:%S')
                        offer_dict['OnlineSince'] = html_offer_online_since
                        offer_dict['ExposeTitle'] = html_title

                        offer_dict_master = {}
                        offer_dict_master['URL'] = offer_dict
                        # Transpose dict and store in dataframe
                        df_offer = pd.DataFrame(offer_dict_master).T
                        # Append to main dataframe of current loop
                        df_search_city = pd.concat([df_search_city, df_offer])

                    except Exception as e:
                        print(f'{e} for offer {o}.')

                print(f'\nAppended offers data from result page number {i} at')
                print(datetime.now().strftime('%H:%M:%S'))
                print('Number of appended offers: ' + str(len(offers)))

        # Store dataframe of current search_city as temporary excel
        df_search_city.to_excel(f'{storage_directory}{search_city}_temp.xlsx')

        # Concat dataframe of current search_city and previous data of same search_city
        df_previous_and_new_data = pd.concat(
            [df_previous_data, df_search_city])

        # Keep only latest extract of each offer
        df_previous_and_new_data.drop_duplicates(
            subset='url', inplace=True, keep='last')

        # Format the data and calculate columns
        df_previous_and_new_data = utils.format_data(
            df=df_previous_and_new_data, format_config=output_format_config)
        df_previous_and_new_data = utils.apply_formulas(
            df=df_previous_and_new_data, config=calculation_config)

        # Store output in file for the city
        df_previous_and_new_data.to_excel(main_data_storage_file, index=False)


if __name__ == '__main__':
    main()
