AUTHOR = 'Alexei'
SITENAME = 'Parallels'
SITEURL = ""
SITESUBTITLE = "Mostly maps."

# Theme
THEME = "custom-theme"
STYLESHEET_URL = "/theme/static/css/style.css"
THEME_STATIC_DIR = "custom-theme"

PATH = "content"
ARTICLE_PATHS = ['blog']
ARTICLE_SAVE_AS = '{date:%Y}/{slug}.html'
ARTICLE_URL = '{date:%Y}/{slug}.html'


TIMEZONE = 'Europe/London'
DEFAULT_DATE_FORMAT = '%d %B %Y'
DEFAULT_LANG = 'en'

# DEFAULT_METADATA = {
#     'status': 'skip',
# }

TYPOGRIFY = True
SUMMARY_MAX_LENGTH = 50
SUMMARY_MAX_PARAGRAPHS = 1
SUMMARY_END_SUFFIX = "..."
WITH_FUTURE_DATES = False

# Archive pages
YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'
YEAR_ARCHIVE_URL = 'posts/{date:%Y}/'
MONTH_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/index.html'
MONTH_ARCHIVE_URL = 'posts/{date:%Y}/{date:%b}/'

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# Plugins
PLUGINS = ["image_process", "sitemap"]

# Image processing plugin
IMAGE_PROCESS = {
    "article-image": ["scale_in 300 300 True"],
    "thumb": ["crop 0 0 50% 50%", "scale_out 150 150 True", "crop 0 0 150 150"],
}
