#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Goclis Yao'
SITENAME = u'Logging'
FAVICON_URL = '/images/favicon.ico'
PORTRAIT_URL = '/images/panda.jpg'
BACKGROUND_URL = '/images/background.png'
SITEURL = 'http://goclis.github.io'

TIMEZONE = 'Asia/Shanghai'
DATE_FORMATS = {
       'zh_CN': '%Y-%m-%d',
}
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATE = 'fs'  # use filesystem's mtime
DEFAULT_LANG = u'zh_CN'
FILENAME_METADATA = '(?P<slug>.*)'
THEME = "./themes/goclis"

# Jinja2模板引擎的扩展
JINJA_EXTENSIONS = ['jinja2.ext.do']

# 相关链接及社交信息
LINKS =  (('Pelican', 'http://getpelican.com/'),
          ('Python.org', 'http://python.org/'),
          ('Jinja2', 'http://jinja.pocoo.org/'),)
SOCIAL_PROFILE_LABEL = u'联系我'
SOCIAL = (('Github', 'https://github.com/Goclis/'),
          ('Twitter', 'https://twitter.com/Goclis'),
          ('Email', 'mailto:goclisyyh@gmail.com'),
          ('Weibo', 'http://weibo.com/u/3312761102'))

# Page
PAGE_PATHS = ['pages']
PAGE_URL = '{slug}.html'
PAGE_SAVE_AS = '{slug}.html'
DISPLAY_PAGES_ON_MENU = False

# Category
USE_FOLDER_AS_CATEGORY = True

# Markdown扩展：高亮、表格及代码等、目录
MD_EXTENSIONS = ['codehilite(css_class=highlight)', 'extra', 'toc(permalink=true)']

# 插件：提取目录
PLUGIN_PATHS = ['plugins']
PLUGINS = ['extract_toc', 'sitemap', 'tipue_search']

# 文章生成
STATIC_PATHS = ['images', 'pdfs']  # 静态文件目录
ARTICLE_EXCLUDES = ['unposts'] # 生成忽略的目录
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}.html'
ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}.html'
ARTICLE_LANG_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}.html'
ARTICLE_LANG_URL = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}.html'

# Disqus
DISQUS_SITENAME = "goclis"
COMMENTS_INTRO = u"有啥想说的就留个言呗~"

# 分页，下面的URL设置是为了避免分页生成错误
DEFAULT_PAGINATION = 3
PAGINATION_PATTERNS = (
	(1, '{base_name}/', '{base_name}/index.html'),
	(2, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html')
)
TAG_URL = 'tag/{slug}/index.html'
TAG_SAVE_AS = 'tag/{slug}/index.html'
CATEGORY_URL = 'category/{slug}/index.html'
CATEGORY_SAVE_AS = 'category/{slug}/index.html'
AUTHOR_URL = 'author/{slug}/index.html'
AUTHOR_SAVE_AS = 'author/{slug}/index.html'
