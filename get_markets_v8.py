import requests, json
import pandas as pd
from py_clob_client.client import ClobClient

def fetch_polymarket_markets(limit=200, active=True, closed=False, max_pages = 2):
    print("Starting!")
    url = "https://gamma-api.polymarket.com/events/pagination"
    
    offset = 0
    params = {"limit": limit, "active": active, "closed": closed, "offset": offset}

    all_markets = []
    page = 0 

    while True:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data["data"]:
            all_markets.extend(data["data"])
            print(f"Parsed Page {page}")
            page += 1
            offset += len(data["data"])
            params["offset"] = offset

        if not data["pagination"]["hasMore"] or page > max_pages:
            break


    return all_markets
    

def sort_data(data):
    markets = []

    for event in data:
        try:
            event_name = event["title"]
        except:
            event_name = "Unkown Event Title"

        try:
            event_id = event["id"]
        except:
            event_id = ""

        for market in event["markets"]:
            try:
                id = market["id"]
            except:
                id = ""

            try:
                title = market["question"]
            except:
                title = "Unknown Title"

            try:
                outcomes = json.loads(market["outcomes"])
            except:
                outcomes = []

            try:
                clob_ids = json.loads(market.get("clobTokenIds", []))
                yes_clob_id, no_clob_id = clob_ids[0], clob_ids[1]
            except:
                yes_clob_id = ""
                no_clob_id = ""

            markets.append(
                {"event_title": event_name, 
                "event_id": event_id, 
                "id": id, 
                "title": title, 
                "outcomes": outcomes, 
                "clob_ids": (yes_clob_id, no_clob_id)
                })

    df = pd.DataFrame(markets)
    print(df.head())

    return df

def get_payload(df):
    payload = []
    for index, row in df.head(30).iterrows():
        payload.append({"token_id": str(row["yes_clob_id"])})
        payload.append({"token_id": str(row["no_clob_id"])})

    return payload


def calc_prices_batch(payload):

    id_to_price_and_size_map = {}

    url = "https://clob.polymarket.com/books"

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    for asset in data:
        asset_id = asset["asset_id"]
        ask_price = float(asset["asks"][-1]["price"]) if asset["asks"] else None
        asset_size = float(asset["asks"][-1]["size"]) if asset["asks"] else None

        id_to_price_and_size_map[asset_id] = (ask_price, asset_size)

    return id_to_price_and_size_map


def main():
    #data = fetch_polymarket_markets()
    #markets = sort_data(data)

    df = pd.read_csv("/Users/leofeingold/Desktop/Polymarket_test/polymarket_markets4.csv")
    payload = get_payload(df)
    data_map = calc_prices_batch(payload)

    print(data_map)
    

if __name__ == "__main__":
    main()