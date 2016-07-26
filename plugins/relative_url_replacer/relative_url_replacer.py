# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from pelican import signals, contents


def replace_relative_url(content):
    """检查<img>的src，将相对路径替换成绝对路径
    """

    if isinstance(content, contents.Static):
        return

    ABSOLUTE_BASE = '/images'
    soup = BeautifulSoup(content._content, 'html.parser')
    imgs = soup.find_all('img')
    for img in imgs:
        src = img['src']
        if src.startswith('.'):
            img['src'] = ABSOLUTE_BASE + '/' + src[src.rfind('/') + 1:]
    content._content = soup.decode()

def register():
    signals.content_object_init.connect(replace_relative_url)

