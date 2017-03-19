import os
import re
import datetime
import pytz
from bs4 import BeautifulSoup, element
import urllib2
import csv
import pandas as pd
#key = '24e4b45e64854a6d99c23dd4f14baf10'

news_sources = ["https://bitcoinmagazine.com", "http://www.coindesk.com"]

def get_bitcoinmagazine_content(page):
    soup = BeautifulSoup(page)
    div = soup.find_all("div", class_="row article-side-pad m-t-sm-all")
    content = soup.find_all("div", class_="row m-t-all")[0].getText()
    date_text = div[0].getText().replace('\n','')

    article_content = soup.find_all("section", class_="article--content")[0].getText()
    article_content = article_content.encode('ascii','ignore')

    headline = soup.find_all("h1", class_="article--headline js-headline-text")[0].getText()
    headline = headline.encode('ascii','ignore')

    eastern=pytz.timezone('US/Eastern')
    utc=pytz.utc
    
    p = re.compile(r'by\s+')
    p = re.compile("(by.*)($)")
    date_str = p.subn('', date_text)[0]     
    date = datetime.datetime.strptime(date_str[:-4], '%b %d, %Y%I:%M %p')
    if date_str[-3:] == 'EST':
        date_eastern = eastern.localize(date)
    date_utc=date_eastern.astimezone(utc)
    return headline, article_content, date_utc

def get_coindesk_content(page):
    # shit this doesnt work
    soup = BeautifulSoup(page)  
    content = soup.find_all("div", class_="single-content")[0].getText().split('Shutterstock')[0]
    article_content = content.encode('ascii','ignore')
    headline = soup.find('title').getText().encode('ascii','ignore')

    date_str = soup.find_all('span', class_="single-date")[0].getText()
    date = datetime.datetime.strptime(date_str[:-4], 'Published on %B %d, %Y at %H:%M')
    eastern = pytz.timezone('US/Eastern')
    gmt = pytz.timezone('GMT')
    utc = pytz.utc

    if date_str[-3:] == 'EST':
        date_local = eastern.localize(date)
    elif date_str[-3:] == 'GMT':
        date_local = gmt.localize(date)
    date_utc=date_local.astimezone(utc)
    return headline, article_content, date_utc


def get_articels_from_page(page, url, hdr):
    soup = BeautifulSoup(page)

    article_links = []
    if 'bitcoinmagazine' in url:
        article_divs = soup.find_all("div", class_="fixed-bottom")
        for div in article_divs:
            suffix = div.a["href"]
            if isinstance(suffix, element.Tag):
                l = source_url + suffix.a['href']
            else:
                l = source_url + suffix     
            article_links.append(l)
    elif 'coindesk' in url:
        posts = soup.find_all("div", class_="post-info")
        for post in posts:
            article_links.append(post.find_all('h3')[0].a['href'])

    headlines = []
    contents = []   
    dates = []
    for link in article_links:
        req = urllib2.Request(link, headers=hdr)
        page = urllib2.urlopen(req).read()
        if 'bitcoinmagazine' in url:
            headline, article_content, date_utc = get_bitcoinmagazine_content(page)
        elif 'coindesk' in url:
            headline, article_content, date_utc = get_coindesk_content(page)
        dates.append(date_utc)
        contents.append(article_content)
        headlines.append(headline)

    return pd.DataFrame({'Headline': headlines, 'Date': dates, 'Content': contents})


if __name__ == "__main__":  
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}    
    #for source_url in news_sources:
    #source_url = "https://bitcoinmagazine.com"
    source_url = "http://www.coindesk.com/page/"
    for p in range(1,700):
        if p%10==0:
            print "{}/700 pages done".format(p)
        req = urllib2.Request(source_url+str(p), headers=hdr)
        page = urllib2.urlopen(req).read()
        articles = get_articels_from_page(page, source_url, hdr)
        filename = 'news_'+source_url.split('.')[1]+'.csv'      
        with open(os.path.join('backtester/data/news', filename), 'a') as f:
            articles.to_csv(f, index=False)

    # access pages on coindesk as http://www.coindesk.com/page/3/
