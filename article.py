import logging
# from bs4 import BeautifulSoup
from process_url import get_response, clean_tags
from extractor import Node
import re


class Article:
    """docstring for Article"""

    def __init__(self, url):
        self.url = url
        self.html = None
        self.source_html = None
        self.published_time = ''
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

        html = clean_tags(html)
        self.html = html
        body = html.find('body')
        extractor = Node.create(body)

        authors, author_tags = self.get_authors(html)
        if not authors:
            logging.warning('Cannot get authors from article')
        self.authors = authors
        self.author_tags = author_tags

        published_time = self.get_published_time(html)
        if not published_time:
            logging.warning('Cannot get publised date from article')
        self.published_time = published_time

        content = extractor.extract_content()
        if not content:
            logging.warning('Cannot get content from article')
        self.content = content

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

        return unique_check(authors), author_tags

    def get_published_time(self, html):
        LIMIT_TAG_TO_FIND = 3
        DATE_REGEX = r'(((\w{3})|([0-3]?\d))(\.|\/|,|\s|\-|_){0,2}([0-3]?\d)(\.|\/|,|\s|\-|_){0,2}(19|20)\d{2}(\.|\/|,|\s|\-|_){0,3})'
        DATE_REGEX_BACKWARD = r'(19|20)\d{2}(\.|\/|,|\s|\-|_){0,3}(\.|\/|,|\s|\-|_){0,2}([0-3]?\d)(\.|\/|,|\s|\-|_){0,2}((\w{3})|([0-3]?\d))'
        TIME_REGEX = r'((\d{1,2})(:|\.)(\d{2})(\s)?(([aA]|[pP])([mM]))?((\s)?(\w{3})?))?'

        # Find time started with date or month: Ex: 24-12-2020
        DATE_AND_TIME = DATE_REGEX + TIME_REGEX

        # Find time started with year: Ex: 2020-12-24
        DATE_AND_TIME_BACKWARD = DATE_REGEX_BACKWARD + TIME_REGEX

        def extract_time(time_tag):
            date_time_match = re.search(DATE_AND_TIME, time_tag.decode())

            if date_time_match:
                return date_time_match.group(0).strip()

            # try to look backward
            else:
                date_time_match = re.search(DATE_AND_TIME_BACKWARD, time_tag.decode())
                if date_time_match:
                    return date_time_match.group(0).strip()
            return None

        # Get published time by searching in the tag name "time"
        time_tag = html.find_all('time')
        for tag in time_tag:
            published_time = extract_time(tag)
            if published_time:
                return published_time

        # Get published time by looking up in tags around author_tags
        author_tags = self.author_tags
        if not author_tags:
            return None

        for tag in set(author_tags):
            start_tag = tag.parent
            for i in range(LIMIT_TAG_TO_FIND):
                start_tag = start_tag.parent

            published_time = extract_time(start_tag)
            if published_time:
                return published_time

        return None

    def get_content(self, html):
        content = html.extract_content()
        if isinstance(content, str):
            logging.warning('The content extracted is not valid')
        return content
