import requests
from bs4 import BeautifulSoup

url = "https://finviz.com/screener.ashx?v=111&f=fa_fpe_o20,fa_pe_u20&ft=2&o=-high52w&r=21"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

soup = BeautifulSoup(requests.get(url.strip(), headers=headers).text, 'html.parser')

table = soup.find("div", id="screener-content")

print(table.text)