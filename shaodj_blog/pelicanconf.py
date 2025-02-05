AUTHOR = 'DJ.shao'
SITENAME = "ShaoDJ's World"
SITEURL = "https://shaodongjun.github.io"
TIMEZONE = 'Asia/Shanghai'
DEFAULT_LANG = 'zh-cn'

PATH = "content"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'
RSS_FEED_SUMMARY_ONLY = False
TYPOGRIFY = True
DISPLAY_PAGES_ON_MENU = True

THEME = "notmyidea"
STATIC_PATHS = ['images']
EXTRA_PATH_METADATA = {
    'images/extras/favicon.ico': {'path': 'favicon.ico'},
  }

ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'
YEAR_ARCHIVE_URL = 'posts/{date:%Y}/'
MONTH_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/index.html'
MONTH_ARCHIVE_URL = 'posts/{date:%Y}/{date:%m}/'

DATE_FORMATS = {
  'en':('usa','%a, %d %b %Y'),
  'zh':('chs','%Y/%m/%d (%a)'),
}

# Blogroll
LINKS = (
    ("UP#AI", "https://www.upyun.com"),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True