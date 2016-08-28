from lxml import html
import sqlite3
import requests
import time
import config

conn = sqlite3.connect('base.db')

c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS listings (link text)")

sendEmails = False

def scrape():
    print('Scraping')
    page = requests.get(config.search_url)
    tree = html.fromstring(page.content)

    objects = tree.xpath('//tr[@class="item imageitem"]');

    newListItems = []

    for obj in objects:
        link = obj.xpath("*/a/@href")
        c.execute('SELECT * FROM listings WHERE link=?', link)

        if (c.fetchone() == None):
            rent = obj.xpath('*/p[@class="rent"]')
            newListItems.append(link)
            c.execute('INSERT INTO listings VALUES (?)', link)
            conn.commit()

    if (len(newListItems) > 0):
        print('New links found. Sending email')
        if (sendEmails):
            OutputList(newListItems)
    else:
        print('No new links found')


def OutputList(list):
    SendEmail(list)

def SendEmail(text):
    return requests.post(
        "https://api.mailgun.net/v3/" + str(config.request_url) + "/messages",
        auth=("api", config.api_key),
        data={"from": "Boplats Scraper <postmaster@" + str(config.request_url) + ">",
              "to": "Patrik Olsson <patrik.m.olsson@gmail.com>",
              "subject": "Ny lägenhet!",
              "text": text})

while True:
    scrape()
    time.sleep(60 * 60 * 2) # Every two hours


