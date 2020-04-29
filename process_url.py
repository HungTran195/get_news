import bs4
import requests
import re


def get_response(url):
    response = requests.get(url)
    if response:
        source_html = bs4.BeautifulSoup(response.content, 'html5lib')
    return response.content, source_html


def clean_tags(html):
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
