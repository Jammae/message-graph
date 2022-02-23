import time
import requests
import http.cookiejar

import pandas as pd
import matplotlib.pyplot as plt

from datetime import date
from bs4 import BeautifulSoup
from collections import Counter


class Grapher:
    def __init__(self, url, cookies, outfile=None):
        self.outfile = outfile
        self.posters = []
        self.likes = Counter()
        self.page_count = 1
        self.message_count = 0
        self.top_posters = 10
        self.top_liked = 3
        self.wait = 3 #odotusaika sivulatausten välillä :joy:
        self.starturl = url

        self.cj = http.cookiejar.MozillaCookieJar(cookies)
        self.cj.load()

    def read_page(self):
        if self.page_count == 1:
            url = self.starturl
        else:
            url = self.starturl+'page-'+str(self.page_count)
        
        html = requests.get(url, cookies=self.cj).text
        soup = BeautifulSoup(html, 'lxml')
        time.sleep(self.wait)

        if soup.find('a', class_='pageNavSimple-el pageNavSimple-el--next'):
            self.count_messages(soup, last_page=False)
        else:
            self.count_messages(soup, last_page=True)
        

    def count_messages(self, soup, last_page):
        print(f'Page {self.page_count}')

        messages = soup.find_all('article', class_ = 'message')
        for message in messages:
            self.message_count += 1
            poster_name = message.find('a', class_ ='username').text
            self.posters.append(poster_name)

            reactions = message.find('a', class_ = "reactionsBar-link")
            if reactions:
                reactions = reactions.text
                if ',' in reactions:
                    spl = reactions.split(' ja ')
                    if '1 muu henkilö' in spl[-1]:
                        self.likes[poster_name] += len(spl[0].split(',')) + 1 
                    elif spl[-1].endswith('muuta'):
                        self.likes[poster_name] += len(spl[0].split(',')) + int(spl[1].split(' ')[0])
                    else:
                        self.likes[poster_name] += len(spl[0].split(',')) + 1
                elif ' ja ' in reactions:
                    self.likes[poster_name] += 2
                else:
                    self.likes[poster_name] += 1

        if last_page:
            print(f"Pages counted: {self.page_count}, messages counted: {self.message_count}, likes counted: {len(self.likes)}")

            title = soup.find('h1', class_='p-title-value').text
            self.create_graph(title)
        else:
            self.page_count += 1
            self.read_page()

    def create_graph(self, title):
        d1 = dict(Counter(self.posters).most_common(self.top_posters))

        plt.style.use('dark_background')

        df = pd.DataFrame.from_dict(d1, orient='index')
        ax = df.plot.bar()
        ax.set_title(title +' | '+str(self.message_count) + ' viestiä | ' + str(self.page_count) + f' sivua ' +'\n' + date.today().strftime("%d.%m.%y"), fontsize=10)
        ax.bar_label(ax.containers[0])
        ax.get_legend().remove()

        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.tick_params(axis='both', which='minor', labelsize=8)

        for tick in ax.get_xticklabels():
            tick.set_rotation(45)

        if self.likes:
            likestext = '\n'.join([x[0] + ' ' + str(x[1]) + ' tykkäystä' for x in self.likes.most_common(self.top_liked)])
            ax.annotate(f'Tykätyimmät postaajat:\n\n{likestext}', xy=(300, 350), xycoords='figure pixels')

        if self.outfile:
            ax.figure.savefig(self.outfile, dpi=100, bbox_inches='tight')
            print(f'Saved output to {outfile}')
        else:
            plt.show()


if __name__ == '__main__':
    url = 'https://bbs.io-tech.fi/threads/linuxin-vuosi-1994.377127/'
    cookies = 'io-tech.fi_cookies.txt'
    outfile = 'graph.png'
    grapher = Grapher(url, cookies, outfile)
    
    grapher.read_page()
