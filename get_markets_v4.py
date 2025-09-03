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

def data_experiment(data):
    #print(type(data))
    #print(len(data))
    #print(data[0]["markets"])
    #print(data["pagination"].keys())
    #print(data["pagination"]["hasMore"])
    #print(data["pagination"]["totalResults"])
    #print(data[0]["markets"][0].keys())
    print(f"Orderbook Ids: {data[0]['markets'][0]['clobTokenIds']}")
    print(f"Market Name: {data[0]['markets'][0]['question']}")
    print(f"Last Trade Price: {data[0]['markets'][0]['lastTradePrice']}")

    '''
    print(len(data[0]["markets"]))
    print(data[0]["markets"])
    print(data[0]["markets"][0]["question"])
    print(data[0]["markets"][0]["outcomes"])
    print(data[0]["markets"][0]["outcomePrices"])
    
    print(data[0]["markets"][0]["lastTradePrice"])
    print(data[0]["markets"][0]["outcomePrices"])
    print(data[0]["markets"][0]["question"])
    '''
    

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
                yes_clob_id, no_clob_id = market["clobTokenIds"][0], market["clobTokenIds"][1]
                prices = getClobPrices(yes_clob_id, no_clob_id, client)
            except Exception as e:
                print("getClobPrices failed for market", market.get("id"), "-", repr(e))
                prices = []


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
                "prices": prices,
                })

    return markets


def create_client():
    client = ClobClient("https://clob.polymarket.com")
    return client


def getClobPrices(token_id_yes, token_id_no, client):

    #["60487116984468020978247225474488676749601001829886755968952521846780452448915", "81104637750588840860328515305303028259865221573278091453716127842023614249200"]

    yes_book = client.get_order_book(token_id_yes)
    no_book  = client.get_order_book(token_id_no)


    min_yes_ask = 1
    min_yes_ask_size = 0 
    min_no_ask = 1
    min_no_ask_size = 0

    
    print("Yes:")
    print(yes_book.asks)

    min_yes_ask1 = yes_book.asks[-1].price
    min_yes_ask_size1 = yes_book.asks[-1].size

    for ask in yes_book.asks:
        print(f"Ask Price: {ask.price}, Liquidity: {ask.size} Tokens")
        ask_price = float(ask.price)
        ask_size = float(ask.size)
        if ask_price < min_yes_ask:
            min_yes_ask = ask_price
            min_yes_ask_size = ask_size

    print("\nNo:")
    print(no_book.asks)

    min_no_ask1 = no_book.asks[-1].price
    min_no_ask_size1 = no_book.asks[-1].size

    
    for ask in no_book.asks:
        print(f"Ask Price: {ask.price}, Liquidity: {ask.size} Tokens")
        ask_price = float(ask.price)
        ask_size = float(ask.size)
        if ask_price < min_no_ask:
            min_no_ask = ask_price
            min_no_ask_size = ask_size

    print([(min_yes_ask, min_yes_ask_size), (min_no_ask, min_no_ask_size)])
    print([(float(min_yes_ask1), float(min_yes_ask_size1)), (float(min_no_ask1), float(min_no_ask_size1))])

    #return [(min_yes_ask, min_yes_ask_size), (min_no_ask, min_no_ask_size)]



def main():
    #data = fetch_polymarket_markets()
    client = create_client()
    #markets = sort_data(data, client)

    getClobPrices("60487116984468020978247225474488676749601001829886755968952521846780452448915", "81104637750588840860328515305303028259865221573278091453716127842023614249200", client)

    #df = pd.DataFrame(markets)
    #print(df.head())

    #df.to_csv("polymarket_markets3.csv", index=False)
    

if __name__ == "__main__":
    main()