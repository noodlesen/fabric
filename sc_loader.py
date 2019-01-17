import requests
from bs4 import BeautifulSoup

url = "https://finviz.com/screener.ashx?v=111&f=cap_smallover,geo_usa,ipodate_more5&o=-high52w"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

soup = BeautifulSoup(requests.get(url.strip(), headers=headers).text, 'html.parser')

table = soup.find("div", id="screener-content")

rows = table.find_all("tr", {'class': ["table-dark-row-cp", "table-light-row-cp"]})

with open('scan.txt', 'w') as f:
    for r in rows:
        line = '\t'.join([t.text for t in r.find_all('td')])+'\n'
        f.write(line)
