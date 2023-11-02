import json
import pandas as pd

f = open("data.json","r").read()


symbols = {}

# # print(f)
data = json.loads(f)

for i in data:
    if i["coin"]["symbol"] in symbols.keys():
        symbols[i["coin"]["symbol"]].append(i["market_cap"])
    else:
        symbols.update({i["coin"]["symbol"]:[]})

# # print(symbols.keys())



import math

def adjusted_market_cap_prep(row):
    return adjusted_market_cap(symbols[row[0]])

def adjusted_market_cap(market_caps, alpha=2500):    
    adjusted_cap = 0
    normalizer = 0
    
    for i, market_cap in enumerate(market_caps):
        weight = math.exp(-alpha*i)
        adjusted_cap += weight * market_cap
        normalizer += weight
        
    return adjusted_cap / normalizer




df = pd.read_csv("r.csv")
df["adjusted"] =   df.apply(adjusted_market_cap_prep,axis=1) 
print(df)

# for i in symbols:
#     print(i,adjusted_market_cap(symbols[i]),symbols[i])
#     input()


