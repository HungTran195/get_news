# get_news

Reference:  [DOM Based Content Extraction via Text Density](http://ofey.me/papers/cetd-sigir11.pdf)

### How to use
- Extract content from an url:

```
from .extractors import Extractor
news = Extractor(url)
news.extract_content()
```
The extracted content is saved in: news.title, news.published_time, news.authors, news.img_of_content_url, news.content
