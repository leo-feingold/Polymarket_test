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
    

def sort_data(data, client):
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
                clob_ids = market.get("clobTokenIds", [])
                yes_clob_id, no_clob_id = clob_ids[0], clob_ids[1]
            except:
                yes_clob_id = ""
                no_clob_id = ""


            '''
            if outcomes != ["Yes", "No"]:
                print("Non-binary market:", title, "| outcomes:", outcomes)
            '''

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


def create_client():
    client = ClobClient("https://clob.polymarket.com")
    return client


def getClobPrices(token_id_yes, token_id_no, client):

    if token_id_yes and token_id_no:

        yes_book = client.get_order_book(token_id_yes)
        no_book  = client.get_order_book(token_id_no)

        min_yes_ask = yes_book.asks[-1].price
        min_yes_ask_size = yes_book.asks[-1].size


        min_no_ask = no_book.asks[-1].price
        min_no_ask_size = no_book.asks[-1].size


        return [(min_yes_ask, min_yes_ask_size), (min_no_ask, min_no_ask_size)]

    else:
        return []



def main():
    data = fetch_polymarket_markets()
    client = create_client()
    markets = sort_data(data, client)

    df = pd.DataFrame(markets)
    print(df.head())
    df.to_csv("polymarket_markets4.csv", index=False)
    

if __name__ == "__main__":
    main()