from py_clob_client.client import ClobClient

# Initialize client in read-only mode
client = ClobClient("https://clob.polymarket.com")

# Fetch the first page of simplified market data
resp = client.get_markets(next_cursor="")

print(resp["data"][0])