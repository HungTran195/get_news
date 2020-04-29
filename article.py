import logging
# from bs4 import BeautifulSoup
from process_url import get_response, clean_tags
from extractor import Node


class Article:
    """docstring for Article"""

    def __init__(self, url):
        self.url = url
        self.html = None
        self.source_html = None
        self.date_publish = ''
        self.authors = []
        self.content = ''

    def extract(self):
        if self.url is None:
            logging.warning('URL is not inputted!')
            return

        # Get response from url and clean irrelevant tags
        source_html, html = get_response(self.url)
        if not source_html:
            logging.warning('Cannot get response from %s' % self.url)
            return

        self.source_html = source_html

        authors = self.get_authors(source_html)
        if not authors:
            logging.warning('Cannot get authors from article')
        self.authors = authors

        date_publish = self.get_date_publish(source_html)
        if not date_publish:
            logging.warning('Cannot get publised date from article')
        self.date_publish = date_publish

        self.html = clean_tags(html)
        body = html.find('body')
        content = self.get_content(body)
        if not content:
            logging.warning('Cannot get content from article')
        self.content = content

    def get_authors(self, html):
        pass

    def get_date_publish(self, html):
        pass

    def get_content(self, html):
        extractor = Node.create(html)
        return extractor.extract_content()
