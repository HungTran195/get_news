import requests
import bs4
import os
# import json


class Get_Articles:
    """docstring for Get_Articles"""

    def __init__(self):
        # number of min characters
        self.THRESH_HOLD = 25
        self.news_tag = []

    def get_article(self, html):
        self.page_name = html.split('.')[1]
        response = requests.get(html)
        if response:
            soup = bs4.BeautifulSoup(response.content, 'html5lib')
        else:
            print('Cannot get page source')

        tags = soup.find_all("a")
        for tree in tags:
            if 'href' in tree.attrs and tree.string:
                if len(tree.string) > self.THRESH_HOLD:
                    if 'article' in str(tree.attrs.values()) \
                            or 'https://www.' + self.page_name + '.com/' in str(tree.attrs.values()):
                        self.news_tag.append(tree)
        self.export_to_json()

    def export_to_json(self):
        news = {}
        file_path = os.getcwd() + '/output/articles/'
        if not os.path.isdir(file_path):
            try:
                os.makedirs(file_path)
            except FileExistsError:
                print('Cannot create output folder')

        with open(file_path + self.page_name + '_articles.txt', 'w+') as file:
            news['Total articles: '] = str(len(self.news_tag))
            for i in range(len(self.news_tag)):
                news['Headline ' + str(i)] = self.news_tag[i].text.strip()
                if 'www.' not in self.news_tag[i]['href']:
                    news['URL ' + str(i)] = 'https://www.' + self.page_name + '.com' + self.news_tag[i]['href']
                else:
                    news['URL ' + str(i)] = self.news_tag[i]['href']
            # json.dump(news, file, indent=4, ensure_ascii=False)
            return news
