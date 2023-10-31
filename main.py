import os

import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import numpy as np


# Load API Key
load_dotenv(find_dotenv())
API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    raise Exception("API_KEY is not set")


def calculate_cci30(data):
    # Pars json to Data Frame
    df = pd.json_normalize(data)
    # Drop Unnecessary data
    df = df.loc[:, ["name", "quote.USD.market_cap"]]
    # Calculate SQRT Market Cap
    df["SQRT_market_cap"] = np.sqrt(df["quote.USD.market_cap"])
    # Calculate Total Market Cap
    total_sqrt_market_cap = df["SQRT_market_cap"].sum()
    # Calculate Weights
    df["Weight"] = df["SQRT_market_cap"] / total_sqrt_market_cap * 100
    return df


def get_market_cap():
    # https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=500&convert=USD
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '500',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }

    try:
        response = requests.get(url, params=parameters, headers=headers)
        return response.json()
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def main():
    json_data = get_market_cap()
    result = calculate_cci30(json_data["data"])
    print(result)


if __name__ == "__main__":
    main()
