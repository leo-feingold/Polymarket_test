import requests, json
import pandas as pd

def fetch_polymarket_markets(limit=200, active=True, closed=False):
    url = "https://gamma-api.polymarket.com/events"
    params = {"limit": limit, "active": active, "closed": closed}
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    return data[:10]

def data_experiment(data):
    #print(len(data))
    #print(type(data))
    #print(data[0])

    '''
    print(len(data[0]["markets"]))
    print(data[0]["markets"])
    print(data[0]["markets"][0]["question"])
    print(data[0]["markets"][0]["outcomes"])
    print(data[0]["markets"][0]["outcomePrices"])
    '''
    print(data[0]["markets"][0]["lastTradePrice"])
    print(data[0]["markets"][0]["outcomePrices"])
    print(data[0]["markets"][0]["question"])

    

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
                outcome_prices = json.loads(market["outcomePrices"])
            except:
                outcome_prices = []

            
            if len(outcomes) == len(outcome_prices):
                outcome_to_price = dict(zip(outcomes, outcome_prices))
                yes_price = outcome_to_price.get("Yes")
                no_price  = outcome_to_price.get("No")

            else:
                yes_price = None
                no_price = None

            if outcomes != ["Yes", "No"]:
                print("Non-binary market:", title, "| outcomes:", outcomes)

            markets.append(
                {"event_title": event_name, 
                "event_id": event_id, 
                "id": id, 
                "title": title, 
                "outcomes": outcomes, 
                "outcome_prices": outcome_prices,
                "yes": yes_price,
                "no": no_price
                })

    return markets

def main():
    data = fetch_polymarket_markets()
    data_experiment(data)

    '''
    markets = sort_data(data)
    print(markets)

    df = pd.DataFrame(markets)
    print(df.head())

    df.to_csv("polymarket_markets.csv", index=False)

    '''

if __name__ == "__main__":
    main()