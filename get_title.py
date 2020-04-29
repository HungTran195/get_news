import requests
import bs4
import os
import logging
import json


class Get_Articles:
    """docstring for Get_Articles"""

    def __init__(self, url):
        self.url = url
        self.page_name = url.split('.')[1]
        # number of min characters
        self.THRESH_HOLD = 25
        self.news_tag = []
        self.news_title = []
        self.news_url = []

    def get_article(self):
        response = requests.get(self.url)
        if response:
            soup = bs4.BeautifulSoup(response.content, 'html5lib')
        else:
            print('Cannot get page response')

        tags = soup.find_all("a")
        for tree in tags:
            if 'href' in tree.attrs and tree.string:
                if len(tree.string) > self.THRESH_HOLD:
                    if 'article' in str(tree.attrs.values()) \
                            or 'https://www.' + self.page_name + '.com/' in str(tree.attrs.values()):
                        self.news_tag.append(tree)
        self.export()

    def export(self):
        self.total_articles = len(self.news_tag)
        if not self.total_articles:
            logging.warn('Cannot get any news from %s' % self.url)
            return

        for i in range(len(self.news_tag)):
            if 'www.' not in self.news_tag[i]['href']:
                self.news_url.append('https://www.' + self.page_name + '.com' + self.news_tag[i]['href'])
            else:
                self.news_url.append(self.news_tag[i]['href'])
            self.news_title.append(self.news_tag[i].text.strip())

    def save_to_file(self, file=None):
        if not self.news:
            logging.warn('There is nothing to save')
        if not file:
            file_path = os.getcwd() + '/output/articles/'
            if not os.path.isdir(file_path):
                try:
                    os.makedirs(file_path)
                except FileExistsError:
                    print('Cannot create output folder')
            file = file_path + self.page_name + '_articles.txt'
        with open(file, 'w+') as saved_file:
            json.dump(self.news, saved_file, indent=4, ensure_ascii=False)
