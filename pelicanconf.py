#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Goclis Yao'
SITENAME = u'Logging'
SITEURL = ''

TIMEZONE = 'Asia/Shanghai'
DATE_FORMATS = {
       'zh_CN': '%Y-%m-%d',
}
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATE = 'fs'  # use filesystem's mtime
DEFAULT_LANG = u'zh_CN'
FILENAME_METADATA = '(?P<slug>.*)'
DEFAULT_PAGINATION = False
THEME = "./themes/pelican-elegant" # 主题

# 相关链接及社交信息
LINKS =  (('Pelican', 'http://getpelican.com/'),
          ('Python.org', 'http://python.org/'),
          ('Jinja2', 'http://jinja.pocoo.org/'),)
SOCIAL_PROFILE_LABEL = u'Contact me'
SOCIAL = (('Github', 'https://github.com/Goclis/'),
          ('Twitter', 'https://twitter.com/Goclis'),
          ('Email', 'mailto:goclisyyh@gmail.com'))

# Page相关设置，主要是为了About页面
PAGE_PATHS = ['pages']
PAGE_URL = '{slug}.html'
PAGE_SAVE_AS = '{slug}.html'
DISPLAY_PAGES_ON_MENU = True

# Category相关
USE_FOLDER_AS_CATEGORY = True

# 使用Tempalte Page来把文章分类
TEMPLATE_PAGES = {
    # 'tpages/tech.html': 'tech.html', 使用index.html替代
    'tpages/life.html': 'life.html',
    'tpages/tweet.html': 'tweet.html',
    'tpages/note.html': 'note.html'
}
TECH_CATEGORIES = ['Tech', 'Python']
NOTE_CATEGORIES = ['Note']
LIFE_CATEGORIES = ['Life']
TWEET_CATEGORIES = ['Tweet']

# Markdown扩展：高亮、表格及代码等、目录
MD_EXTENSIONS = ['codehilite(css_class=highlight)', 'extra', 'toc(permalink=true)']

# 插件：提取目录
PLUGIN_PATHS = ['plugins']
PLUGINS = ['extract_toc']

# 文章生成
STATIC_PATHS = ['images', 'pdfs']  # 静态文件目录
ARTICLE_EXCLUDES = ['unposts', 'tpages'] # 生成忽略的目录
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}.html'
ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}.html'
ARTICLE_LANG_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}.html'
ARTICLE_LANG_URL = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}.html'
