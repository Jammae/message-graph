import http.cookiejar
import requests
from bs4 import BeautifulSoup
import time
from collections import Counter
import matplotlib.pyplot as plt
from datetime import date
import pandas as pd
posters = []
p = 1
v = 0
top = 10
wait = 3 #odotusaika sivulatausten välillä :joy:
starturl = 'https://bbs.io-tech.fi/threads/bejing.372965/'

cj = http.cookiejar.MozillaCookieJar('io-tech.fi_cookies.txt')
cj.load()

def ReadPage():
    if p == 1:
        url = starturl
    else:
        url = starturl+'page-'+str(p)
    soup = BeautifulSoup(requests.get(url, cookies=cj).text, 'lxml')
    time.sleep(wait)
    if soup.find('a', class_='pageNavSimple-el pageNavSimple-el--next'):
        print("sending to count")
        CountMsgs(soup,s=True)
    else:
        print("sending last page to count")
        CountMsgs(soup,s=False)
    

def CountMsgs(soup,s):
    print('arrived at countmsg')
    global p
    messages = soup.find_all('article', class_ = 'message')
    for message in messages:
        global v
        v += 1
        poster_name = message.find('a', class_ ='username').text
        posters.append(poster_name)
    print(f"Pages counted: {p}, messages counted: {v}")
    if s:
        p += 1
        
        ReadPage()
    else:
        title = soup.find('h1', class_='p-title-value').text
        FinishUp(title)

def FinishUp(title):
    d1 = dict(Counter(posters).most_common(top))
    plt.style.use('dark_background')
    df = pd.DataFrame.from_dict(d1, orient='index')
    ax = df.plot.bar()
    ax.set_title(title +' | '+str(v) + ' viestiä | ' + str(p) + f' sivua ' +'\n' + date.today().strftime("%d.%m.%y"), fontsize=25)
    ax.bar_label(ax.containers[0])
    ax.get_legend().remove()
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    plt.show()
ReadPage()