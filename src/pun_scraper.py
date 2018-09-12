import requests
from bs4 import BeautifulSoup
import json


def pun_scrape():
    for page_number, category in zip([4, 12, 9, 6, 8, 5, 10, 7, 11, 3, 13, 1, 2],
                                     ["body", "crime", "entertainment", "health", "people",
                                      "technology", "work", "business", "education",
                                      "food", "nature", "places", "transport"]):

        print "Scraping", category, "puns"
        puns = []
        for i in range(1, 6):
            url = "http://www.punoftheday.com/cgi-bin/disppuns.pl?ord=S&cat=" + str(page_number) + "&sub=" + \
                  str(page_number).zfill(2) + "01&page=" + str(i)
            response = requests.get(url)
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table", "pundisplay")
            for tr in table.find_all('tr'):
                for td, count in zip(tr, xrange(10)):
                    if count == 2:
                        if td.div:
                            puns.append(td.text[:-len(td.div.text)])
                        else:
                            puns.append(td.text)

        puns = list(set(puns))
        with open("../data/puns/" + category + "_puns.json", 'w') as f:
            json.dump(puns, f, indent=4)


def idiom_scrape():

    with open("../data/idioms.json") as f:
        idioms = json.load(f)

    # for character in "ABCDEFGHIJKLMNOPQRSTUVW":
    #     url = "https://www.englishclub.com/ref/Idioms/" + character
    #     response = requests.get(url)
    #     html = response.text
    #     soup = BeautifulSoup(html, "html.parser")
    #     main = soup.find("main")
    #     links = main.find_all("div", "linklisting")
    #
    #     for link in links:
    #         idioms.append((link.a.text.strip(), link.div.text.strip()))

    url = "https://www.englishclub.com/ref/Idioms/" + "XYZ"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    links = main.find_all("div", "linklisting")

    for link in links:
        idioms.append((link.a.text.strip(), link.div.text.strip()))

    # print idioms

    print len(idioms)
    with open("../data/idioms.json", 'w') as f:
        json.dump(idioms, f, indent=4)


def dump_puns():
    heterographic_puns = json.load(open("../data/puns/heterographic_puns.json"))
    homographic_puns = json.load(open("../data/puns/homographic_puns.json"))
    puns = json.load(open("../data/puns/puns.json"))

    for pun in puns:
        if pun not in heterographic_puns and pun not in homographic_puns:
            print pun
            answer = str(raw_input("Heterographic? "))
            if answer == 'y':
                heterographic_puns.append(pun)
            else:
                homographic_puns.append(pun)

    with open("../data/puns/heterographic_puns.json", 'w') as f:
        json.dump(heterographic_puns, f, indent=4)
    with open("../data/puns/homographic_puns.json") as f:
        json.dump(homographic_puns, f, indent=4)


def random_english_sentence_scrape():
    sentences = set()
    url = "http://www.englishinuse.net/"

    while True:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        tds = soup.find_all("tr")
        for td in tds:
            sent = td.text.split(".")[1]
            if sent[-1] != '?':
                sent += '.'
            sentences.add(sent.encode('ascii'))
            if len(sentences) == 1000:
                return list(sentences)


if __name__ == "__main__":
    sents = random_english_sentence_scrape()
    with open("../data/english_sentences.json", 'w') as f:
        json.dump(sents, f, indent=4)


















