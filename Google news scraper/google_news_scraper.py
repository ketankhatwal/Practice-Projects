# Import Libraries
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import nltk
import requests
import re
import time
import csv
import pandas as pd
from newspaper import Article
nltk.download('punkt')

pd.set_option('display.max_columns', None)

# Function for finding a word
def find_word(word, data):
    flag = False
    for i, news in enumerate(data):
        indexes = [(m.start(0), m.end(0)) for m in re.finditer(r'\b{}\b'.format(word), news)]
        for item in indexes:
            flag = True
            print(f"Found \'{word}\' in article {i+1} in starting from index {item[0]} to {item[1]}")
            print()
    if not flag:
        print("Sorry no element found. Try again!")
        print()

print("\nIt may take upto 10-15 minutes to get all the data.\n")
print("Note :- For searching for a word, you have to wait until whole page is scraped, then a prompt will appear.")
print("\nLog will be printed on the screen in case if any of the news link does not work, it will not affect the execution. Please wait while the program runs")

time.sleep(5)

# Creating a csv file for main news
main_file=open("Main news.csv",'w', encoding='utf-8')
main_writer=csv.writer(main_file)
main_writer.writerow(['Date','Title','Summary','Link'])

# Creating a csv file for sub news
sub_file=open("Sub news.csv",'w', encoding='utf-8')
sub_writer=csv.writer(sub_file)
sub_writer.writerow(['Date','Title','Summary','Link'])

# Get Info from URL
r = requests.get("https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN%3Aen")
soup = BeautifulSoup(r.text, "lxml")
all_news = soup.find_all("div", class_ = "xrnccd")

main_data = []
sub_data = []
for item in all_news:
    data = []
    title = item.find("h3", class_ = "ipQwMb ekueJc gEATFF RD0gLb")
    time = item.time['datetime']
    date, time = time.split('T')
    time = time[:-1]
    time = f"{date} {time} +0000"
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S %z')
    time = time.astimezone(pytz.timezone('Asia/Kolkata'))

    # Create link
    link = item.a['href']
    link = ''.join(["https://news.google.com",link[1:]])

    # Use Article from newspaper
    try:
        art = Article(link, language = "en")
        art.download()
        art.parse()
        art.nlp()

        # Create main data
        data.append(f"Article's Date :- {time.date()} {time.time()}")
        data.append(f"Article's Title :- {title.text}")
        data.append(f"Link for article :- {link}")
        data.append(f"Summary :- \n{art.summary}")
        
        # Write to main news csv 
        main_writer.writerow([f"{time.date()} {time.time()}", title.text, art.summary, link])
        main_data.append('\n\n'.join(data))

    except:
        print(f"\nLink to \"{title.text}\" does not work or there is a connection error")

    # Find Subnews
    sub_news = item.find("div", class_ = "SbNwzf")
    if sub_news:

        # Find Subnews if exists
        for i, news in enumerate(sub_news.find_all("article")):
            data = []
            try:
                time = news.time['datetime']
                date, time = time.split('T')
                time = time[:-1]
                time = f"{date} {time} +0000"
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S %z')
                time = time.astimezone(pytz.timezone('Asia/Kolkata'))
                sub_title = news.h4.text
                sub_link = news.a['href']
                sub_link = ''.join(["https://news.google.com",sub_link[1:]])
                art = Article(sub_link, language = "en")
                art.download()
                art.parse()
                art.nlp()
                summary = art.summary
                
                # Write to sub news csv
                sub_writer.writerow([f"{time.date()} {time.time()}", sub_title, summary, sub_link])
                
                # Create sub data
                data.append(f"Article's Date :- {time.date()} {time.time()}")
                data.append(f"\t{i+1}. {sub_title}")
                data.append(f"\t   Link :- {sub_link}")
                data.append(f"Summary :- \n{art.summary}")
                sub_data.append('\n\n'.join(data))
            except:
                print(f"\nLink to \"{sub_title}\" does not work or there is a connection error")
    

main_file.close()
sub_file.close()

# Printing the dataframe
try:
    main_df = pd.read_csv("Main news.csv")
    sub_df = pd.read_csv("Sub news.csv")
    print("Main news are :-")
    print(main_df.head())
    print("\n\n Sub News are :- ")
    print(sub_df.head())
except:
    print("Error while scraping the page")

# For searching a word
while True:
    choice = input("\nEnter y for searching for a word else any other key :- ").lower()
    if choice != 'y':
        break
    data = int(input("Enter 1 for searching in main news \nEnter 2 for searching in sub news\nEnter 0 for exitting\n"))
    if data == 1:        
        word = input("Enter the word you want to search for :- ")
        find_word(word, main_data)
    elif data == 2:
        word = input("Enter the word you want to search for :- ")
        find_word(word, sub_data)
    elif not data:
        break
    else:
        print("Wrong Input")

