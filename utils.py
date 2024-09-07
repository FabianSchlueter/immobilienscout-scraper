"""
This module contains utility functions that are used throughout the project.
These functions are general-purpose and can be applied in various contexts
to support the main functionality of the application.
"""
import yaml
import shutil
import os
import re
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def load_yaml_config(file_path: str):
    """Load configuration from yaml file.

    Args:
        file_path (str): Path of the yaml file

    Returns:
        config
    """

    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)

    return config


def apply_formulas(df: pd.DataFrame, config: dict):
    """ Apply formulas to calculate new columns. The formulas are stored in a dictionary.

    Args:
        df (pd.DataFrame): Dataframe to apply the formulas to.
        config (dict): Dictionary containing the formulas written as pandas operations.

    Returns:
        df (pd.DataFrame)
    """

    print('\nCalculate new columns.')

    for col, formula in config['calculated_columns'].items():
        try:
            df[col] = eval(formula)
            print(f'Calculate {col} as {formula}.')
        except KeyError as e:
            print(
                f"KeyError: The column '{e.args[0]}' is not available in the data. Cannot calculate {col}")

    return df


def captcha_check(html: str):
    """ Check the html for a captcha.
    If so, pause the execution and ask the user to solve it.

    Args:
        html (string): html to be checked.
    """

    chaptcha_part = html.split(r'</title>')[0].split(r'<title>')[1]
    if 'Ich bin kein Roboter - ImmobilienScout24' in chaptcha_part:
        input('\nPlease solve the captcha and choose cookies settings. Then press any key to continue.')
        print('Continuing search.')


def get_previously_scraped_data_from_storage(storage_directory: str, storage_file: str):
    """
    Create necessary directories if needed.
    Make a copy of the previously scraped data file if it exists and attach a timestamp suffix to the copy.
    Read the file.
    If no previous data exists return an empty dataframe.

    Args:
        storage_directory(str): Directory for storing the data.
        storage_file(str): Path of the Excel file that contains the previously scraped data.

    Returns:
        df(pandas.DataFrame)
    """

    # Create directory and Archive directory if it not already exists
    os.makedirs(storage_directory, exist_ok=True)
    os.makedirs(f'{storage_directory}\\Archive', exist_ok=True)

    # Check if data of a previous search of the same city exists
    if os.path.exists(storage_file):
        # Create Copy
        copy_of_storage_file = storage_file.replace(storage_directory, f'{storage_directory}\\Archive\\').split(
            '.')[0] + '_snapshot_' + str(datetime.now().strftime('%Y-%m-%dT%H-%M-%S')) + '.xlsx'
        shutil.copy(storage_file, copy_of_storage_file)
        print(
            f'Created copy of {storage_file}. Name of copy is {copy_of_storage_file}.')
        df = pd.read_excel(storage_file)

    # Else return empty dataframe
    else:
        print('No previous data found. Creating new storage file.')
        df = pd.DataFrame()

    return df


def format_data(df: pd.DataFrame, format_config: dict):
    """Execute formatting on the scraped data to make it useable.
    This includes casting columns to certain types.

    Args:
        df (pd.DataFrame): Dataframe containing data
        format_config (dict): Information how to cast columns

    Returns:
        df (pd.DataFrame)
    """

    if 'cast_to_numeric' in format_config:
        # Nested dict containing the cast to numeric config for each downcast type (float, integer, etc.)
        cast_config = format_config['cast_to_numeric']
        for key, value in cast_config.items():
            print(f'\nCast the following columns to numeric type {key}:')
            print(value)
            for column in value:
                try:
                    df[column] = df[column].apply(
                        pd.to_numeric, downcast=key, errors='coerce')
                except KeyError as e:
                    print(
                        f"KeyError: The column'{e.args[0]}' is not available in the data.")

    if 'cast_to_string' in format_config:
        print('\nCast the following columns to string:')
        print(format_config['cast_to_string'])
        # The columns for string casting are stored as a list
        for column in format_config['cast_to_string']:
            try:
                df[column] = df[column].astype(str)
            except KeyError as e:
                print(
                    f"KeyError: The column'{e.args[0]}' is not available in the data.")

    return df


def get_number_of_result_pages(driver: webdriver.Chrome, search_url: str):
    """ Open the first result page for a given search URL and extract the total number of result pages.

    Args:
        driver (webdriver.Chrome): Instance of WebDriver(ChromiumDriver)
        search_url (str): The url of a search on the website

    Returns:
        num_pag (int): Number of result pages
    """

    print('Get number of result pages.')

    # Open first result page to get the number of result pages
    url = f'{search_url}1'
    driver.get(url)
    WebDriverWait(driver, 5)
    html = driver.page_source

    # Check for captcha.
    captcha_check(html)

    # If the number cannot be found then it is always 1
    try:
        html = driver.page_source
        html_reduced = html.split(
            '</a></li><li class="p-items p-next vertical-center-container">')[0]
        html_reduced = html_reduced[-3:]
        html_reduced = html_reduced.split('>')[1]
        num_pag = int(html_reduced)
    except:
        num_pag = 1

    print(f'Number of result pages: {num_pag}.\n')

    return num_pag


def get_unique_offers_from_result_page_source(html: str):
    """Extract all urls of real estate offers from a result page.

    Args:
        html (str): source of a result page.

    Returns:
        offers (list)
    """

    print('\nFind the links of the single offers.')

    # Define the pattern to match 'a' tags with href starting with '/expose/'.
    pattern = re.compile(
        r'<a\s+[^>]*href="(/expose/\d+[^"]*)"[^>]*>', re.IGNORECASE)
    # Find all matches
    matches = re.findall(pattern, html)
    # Use a set to remove duplicates
    unique_matches = set(matches)
    # Convert the set back to a list if you need an ordered list
    offers = list(unique_matches)

    return offers
