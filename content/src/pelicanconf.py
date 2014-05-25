#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Goclis Yao'
SITENAME = u'Logging'
SITEURL = ''

TIMEZONE = 'Asia/Shanghai'
DATE_FORMATS = {
        'zh_CN': '%Y-%m-%d %H:%M:%S',
}
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATE = 'fs'  # use filesystem's mtime
# LOCALE = ('zh_CN.utf8',)
DEFAULT_LANG = u'zh_CN'
FILENAME_METADATA = '(?P<slug>.*)'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (('Pelican', 'http://getpelican.com/'),
          ('Python.org', 'http://python.org/'),
          ('Jinja2', 'http://jinja.pocoo.org/'),)

# Social widget
SOCIAL = (('Github', 'https://github.com/Goclis/'),)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

STATIC_PATHS = ['images', 'pdfs', 'src']  # images and pdf files

THEME = "/home/goclis/SHARE/pelican-bootstrap3"
# THEME = "/home/goclis/niu-x2-sidebar"
