import requests
import time
from bs4 import BeautifulSoup

flag = False
def alert(comp_name, previous, diff):
    if diff < 0:
        print(f"\nPrice decreased for {comp_name} by {abs(diff)} % from {previous} to {round(previous + diff,2)}")
    else:
        print(f"\nPrice increased for {comp_name} by {abs(diff)} % from {previous} to {round(previous + diff,2)}")

start_time = time.time()
stock = {}

print("Getting Information From MoneyControl.com.\nPlease wait while we fetch data.\nWe'll let you know if %chg changes by 2%")

while int(time.time()-start_time) < 1200:
    try:
        r = requests.get("https://www.moneycontrol.com/stocks/marketstats/indexcomp.php?optex=NSE&opttopic=indexcomp&index=9")
        soup = BeautifulSoup(r.text, "lxml")
        all_data = soup.find_all("tr")
        for data in all_data:
            item = data.find_all("td", class_ = "brdrgtgry")
            if item:
                comp_name = item[0].b.text
                perc_ch = float(item[4].text)
                if comp_name in stock:
                    diff = round(float(item[4].text) - stock[comp_name],2)
                    if abs(diff) >= 2:
                        flag = True
                        alert(comp_name, stock[comp_name], diff)
                    stock[comp_name] = float(item[4].text)

                else:
                    stock[comp_name] = perc_ch

        time.sleep(120)
    except:
        pass
if not flag:
    print("\nStock Prices didn't change by 2%")
print("\nProgram Executed Successfully")
