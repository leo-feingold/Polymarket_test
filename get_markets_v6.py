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
                "yes_clob_id": yes_clob_id,
                "no_clob_id": no_clob_id
                })

    return markets



def main():
    data = fetch_polymarket_markets()
    markets = sort_data(data)

    df = pd.DataFrame(markets)
    print(df.head())
    df.to_csv("polymarket_markets4.csv", index=False)
    

if __name__ == "__main__":
    main()