import json
import pendulum
import requests
import numpy as np
from sklearn.externals import joblib
from bs4 import BeautifulSoup

class Gadalka:
    switch = "en"
    
    
    def __init__(self):
        self.tags_index_ru = json.load(open("tags_index_ru.json"))
        self.tags_index_en = json.load(open("tags_index_en.json"))
        
        self.lr_ru = joblib.load("educated/lr_ru.p")
        self.lr_en = joblib.load("educated/lr_en.p")
        
    def vectorize(self, tags, switch):
        if self.switch == "ru":
            l = 1774
        
            tags_vector = np.zeros(l)

            for tag in tags:
                if self.tags_index_ru.get(tag):
                    index, count = self.tags_index_ru[tag]
                    tags_vector[index] = count       
            return tags_vector
        elif self.switch == "en":
            l = 4049
        
            tags_vector = np.zeros(l)

            for tag in tags:
                if self.tags_index_en.get(tag):
                    index, count = self.tags_index_en[tag]
                    tags_vector[index] = count       
            return tags_vector

    def count_markdown_symbols_and_words(self, soup_obj):
        soup_text = soup_obj.text

        a = soup_text
        x = soup_text.split()
        for c in x:
            a = a.replace(c, "", 1)

        return len(a), len(x)
    
    def daytime(self, date_string):
        h = pendulum.parse(date_string).hour
        if 0 <= h <= 5:
            return 0
        elif 6 <= h <= 11:
            return 1
        elif 12 <= h <= 17:
            return 2
        elif 18 <= h <= 24:
            return 3
        else:
            return 4
    
    def predict(self, url):
        soup = BeautifulSoup(requests.get(url).content, "lxml")
        tags = [tag.string for tag in soup.find(class_="post-taglist")]
        
        tags_vector = self.vectorize(tags, self.switch)
        title_len = len(soup.title.string.split())
        body_len, markdown_len = self.count_markdown_symbols_and_words(soup.find(class_="post-text"))
        dtime = self.daytime(soup.find(class_="post-signature owner").find('span')["title"])
        
        x = np.append([title_len, body_len, markdown_len, dtime], tags_vector)
        
        if self.switch == "ru":
            return "Вам ответят через " + (pendulum.from_timestamp(self.lr_ru.predict(x)[0]) - pendulum.from_timestamp(0)).in_words(locale="ru")
        elif self.switch == "en":
            return "You will be answered in " + (pendulum.from_timestamp(abs(self.lr_en.predict(x)[0])) - pendulum.from_timestamp(0)).in_words(locale="en")
    