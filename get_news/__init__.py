from extractors import Extractor
import re
# from gtts import gTTS
import os
import json


class Data:
    """Update articles from sources and store to database"""

    def __init__(self):
        self.website_urls = self.get_website_urls()
        self.data = self.get_data()

    def get_website_urls(self):
        ''' Get website urls from datebase'''
        websites = ['https://www.theverge.com/',
                    'https://www.vox.com/',
                    'https://www.nola.com/',
                    'https://www.businessinsider.com/']
        return websites

    def add_website_url(self, url):
        ''' Add new website url to database'''
        pass

    def update_data(self):
        for url in self.get_website_urls():
            pass

    def get_data(self):
        data = {}
        for url in self.website_urls:
            website_name = self.get_website_name(url)
            extractor = Extractor(url)
            article = extractor.extract_article()
            data[website_name] = article

        return data

    def get_website_name(self, url):
        return url.split('.')[1].title()


if __name__ == "__main__":

    PATH = '/home/tony/Documents/Project/news_aggregator/get_news/tests/'
    file = PATH + 'article_url.json'

    # data = Data()
    # with open(file, 'w+') as saved_file:
    # json.dump(data.data, saved_file, indent=4, ensure_ascii=False)
    with open(file) as data:
        source = json.load(data)

    while True:
        text_news = "\nwhat news do you want to read, sir?\n"
        subject = input(text_news)
        subject = subject.strip()

        if subject == 'exit' or subject == "Exit":
            print("Exitting the program...")
            break

        matched_url = []
        matched_title = []
        count = 0
        for site, _ in source.items():
            if subject.lower() == site.lower():
                for url, title in source[site].items():
                    count += 1
                    print(str(count) + ' - ' + title + '\n')
                    matched_url.append(url)
                    matched_title.append(title)
                break
            for url, title in source[site].items():
                if subject in title:
                    count += 1
                    print(str(count) + ' - From ' + site + ': ')
                    print(title + '\n')
                    matched_url.append(url)
                    matched_title.append(title)
        if not matched_title:
            print('There is nothing about that subject on today\'s news')
        if matched_title:
            text_read = "\nWhich one do you want to read, sir?\n"
            index = int(input(text_read))

            if not index == 0:
                url = matched_url[index]
                extractor = Extractor(url)
                extractor.extract_content()
                content = extractor.content
                author = ''.join([a + ' ' for a in extractor.authors])
                time = extractor.published_time
                print(matched_title[index])
                print('\n Read more: ' + matched_url[index])
                print('\nFrom: ' + author)
                print('\nPublished from: ' + time)
                print('\n' + content)
