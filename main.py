import os
import json

import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import numpy as np
import math


# Load API Key
load_dotenv(find_dotenv())
API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    raise Exception("API_KEY is not set")


def calculate_cci30(data):
    # Pars json to Data Frame
    df = pd.json_normalize(data)
    # Drop Unnecessary data
    df = df.loc[:, ["symbol", "quote.USD.market_cap"]]
    df["adjusted_market_cap"] =   df.apply(adjusted_market_cap_prep,axis=1) 
    # Calculate SQRT Market Cap
    df["SQRT_market_cap"] = np.sqrt(df["adjusted_market_cap"])
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
        'limit': '30',
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



def adjusted_market_cap_prep(row):
    global symbols
    return adjusted_market_cap(symbols[row[0]])

def adjusted_market_cap(market_caps, alpha=2500):    
    adjusted_cap = 0
    normalizer = 0
    
    for i, market_cap in enumerate(market_caps):
        weight = math.exp(-alpha*i)
        adjusted_cap += weight * market_cap
        normalizer += weight
        
    return adjusted_cap / normalizer



if __name__ == "__main__":
    f = open("data.json","r").read()
    symbols = {}
    data = json.loads(f)
    for i in data:
        if i["coin"]["symbol"] in symbols.keys():
            symbols[i["coin"]["symbol"]].append(i["market_cap"])
        else:
            symbols.update({i["coin"]["symbol"]:[]})
    main()