import requests
import bs4
import re
import logging
from content_extractor import Content_Extractor


class Extractor:
    """docstring for Extractor"""

    def __init__(self, url, parser=None):
        self.MIN_TITLE_LENGTH = 26
        self.LIMIT_TIME_TAG_TO_FIND = 3
        self.DATE_REGEX = r'(((\w{3})|([0-3]?\d))(\.|\/|,|\s|\-|_){0,2}([0-3]?\d)(\.|\/|,|\s|\-|_){0,2}(19|20)\d{2}(\.|\/|,|\s|\-|_){0,3})'
        self.DATE_REGEX_BACKWARD = r'(19|20)\d{2}(\.|\/|,|\s|\-|_){0,3}(\.|\/|,|\s|\-|_){0,2}([0-3]?\d)(\.|\/|,|\s|\-|_){0,2}((\w{3})|([0-3]?\d))'
        self.TIME_REGEX = r'((\d{1,2})(:|\.)(\d{2})(\s)?(([aA]|[pP])([mM]))?((\s)?(\w{3})?))?'

        self.url = url
        self.html = None
        if not parser:
            self.parser = 'lxml'
        self.content = ''
        self.published_time = ''
        self.authors = []
        self.articles = {}

    def extract_content(self):
        url = self.url
        html = self.download_page(url)
        if not html:
            return
        self.html = html

        authors = self.get_authors(html)
        if not authors:
            logging.warning('Cannot get authors from article')
        self.authors = authors

        published_time = self.get_published_time(html)
        if not published_time:
            logging.warning('Cannot get publised date from article')
        self.published_time = published_time

        content = self.get_content(html)
        if not content:
            logging.warning('Cannot get content from article')
        self.content = content

    def download_page(self, url):
        response = self.get_response(url)
        if not response:
            logging.warning('Cannot get response from %s' % url)
            return ''

        html = bs4.BeautifulSoup(response.content, self.parser)
        return html

    def get_response(self, url):
        """HTTP response code"""
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as err:
            logging.exception(err)
            return ''
        return response

    def get_authors(self, html):
        attrs = ['rel', 'class', 'href', 'name', 'id', 'itemprop']
        value = re.compile('[\w|\-|\/|\.]?(author)|(editor)[\w|\-|\/|\.]?')
        authors = []
        author_tags = []
        matched_tag = []

        for attr in attrs:
            scanned_tag = html.find_all('a', attrs={attr: value})
            matched_tag.extend(scanned_tag)

        if matched_tag:
            for tag in matched_tag:
                text_inside = tag.text.strip()
                text_inside = re.sub(' [ \t]+', ' ', text_inside)

                # Remove words like "By", "From" and delimiters: "-","," from author names
                if 0 < len(text_inside) < 100:
                    names = re.sub('([bB][yY])|([fF][rR][oO][mM])[\s\:]', '', text_inside)
                    names = re.split('[\-\,]', names)
                    authors.extend(names)
                    author_tags.append(tag)

        else:
            authors = ''

        # fatest way to remove duplicate element from list
        # solution from: https://stackoverflow.com/a/480227
        def unique_check(author_list):
            seen = set()
            seen_add = seen.add
            return [x.title() for x in author_list if not (x in seen or seen_add(x))]

        self.author_tags = author_tags

        return unique_check(authors)

    def get_published_time(self, html):
        # Find time started with date or month: Ex: 24-12-2020
        DATE_AND_TIME = self.DATE_REGEX + self.TIME_REGEX
        # Find time started with year: Ex: 2020-12-24
        DATE_AND_TIME_BACKWARD = self.DATE_REGEX_BACKWARD + self.TIME_REGEX

        def extract_time(time_tag):
            date_time_match = re.search(DATE_AND_TIME, time_tag.decode())

            if date_time_match:
                return date_time_match.group(0).strip()

            # try to look backward
            else:
                date_time_match = re.search(DATE_AND_TIME_BACKWARD, time_tag.decode())
                if date_time_match:
                    return date_time_match.group(0).strip()
            return ''

        # Get published time by searching in the tag name "time"
        time_tag = html.find_all('time')
        for tag in time_tag:
            published_time = extract_time(tag)
            if published_time:
                return published_time

        # Get published time by looking up in tags around author_tags
        author_tags = self.author_tags
        if not author_tags:
            return ''

        for tag in set(author_tags):
            start_tag = tag.parent
            for _ in range(self.LIMIT_TIME_TAG_TO_FIND):
                start_tag = start_tag.parent

            published_time = extract_time(start_tag)
            if published_time:
                return published_time

        return ''

    def get_content(self, html):
        cleaned_html = self.clean_tags(html)

        body = cleaned_html.find('body')
        extractor = Content_Extractor.create(body)
        content = extractor.extract()
        return content

    def clean_tags(self, html):
        # Unwarp tags
        merging_tags = ['p', 'br', 'li', 'table', 'tbody', 'tr', 'td', 'theader', 'tfoot']
        tags = html.find_all(merging_tags)
        for tag in tags:
            tag.unwrap()

        # Remove tags:
        remove_tag = ['head', 'script', 'link', 'style', 'form', 'option', 'header', 'footer', 'nav', 'noscript', 'aside']
        tags = html.find_all(remove_tag)
        for tag in tags:
            tag.decompose()

        # Remove hidden tags:
        for hidden in html.find_all(style=re.compile(r'display:\s*none')):
            hidden.decompose()

        return html

    def extract_article(self):
        url = self.url
        html = self.download_page(url)
        if not html:
            return
        self.html = html

        if url[-1] == '/':
            url = url[:-1]

        article_tags = self.get_article_tags(html, url)

        if not article_tags:
            logging.warning('Cannot get any news from %s' % url)
            return ''

        articles = {}
        article_url = []
        article_title = []

        for i in range(len(article_tags)):
            if 'https://www.' not in article_tags[i]['href']:
                article_url = url + article_tags[i]['href']
            else:
                article_url = article_tags[i]['href']

            article_title = article_tags[i].text.strip()
            articles[article_url] = article_title

        return articles

    def get_article_tags(self, html, url):
        article_tags = []
        tags = html.find_all("a")
        for tree in tags:
            if 'href' in tree.attrs and tree.string:
                if len(tree.string.strip()) > self.MIN_TITLE_LENGTH:
                    article_tags.append(tree)

        return article_tags
