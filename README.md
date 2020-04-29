# get_news

Reference:  [DOM Based Content Extraction via Text Density](http://ofey.me/papers/cetd-sigir11.pdf)

### How to use
- Extract content from an url:

```
from article import Article
news = Article(url)
news.extract()
```

The content extracted in save within `news.content`

- Get titles and urls of news from a website:
```
from get_title import Get_Articles
news = Get_Articles(url)
news.get_article()
```
The title of each news if saved in: `news.news_title` and its url is in `news.news_url`
