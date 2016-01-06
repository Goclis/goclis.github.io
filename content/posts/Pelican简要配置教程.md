Title: Pelican简要配置教程  
Date: 2014-5-25 20:30  
Tags: pelican, python  
Slug: pelican-blog  
Author: Goclis Yao  


最近看操作系统遇到不少问题，感觉记在书上有点不靠谱，所以一个一个的连带解答写在了trello里，但是总觉得写多了之后就好乱，于是又萌发了搭个blog的想法，想来想去还是用pelican吧，以后有空再买个域名挂上去。

### 博客初始化
总归先得把pelican搭好吧，好像还比较简单，接下来的一切操作都在Linux下。

__Install__

```
pip install pelican

pip install markdown
```

__Quick-Start__

自己新建一个文件夹，然后：

```
pelican-quickstart
```

按照向导建立好就行了，突然想起这货对中文不友好，语言那选en凑合吧。

__Usage__

在Quick-Start中如果是一路回车过来的话应该会有个Makefile，pelican的很多操作是基于这个文件的，对Linux有所了解的同学应该是知道make这个命令的，至于关系的绑定也就是写在Makefile里的，下面介绍一些常用的pelican操作：

```
make html # 将content中的markdown (or others) 生成为html

make regenerate

make serve

make devserver
```

make一般涉及到一些生成的操作，pelican自带了一个**develop_server.sh**以供开发的时候调试：

```
./develop_server.sh start  # http://localhost:8000

./develop_server.sh stop
```

### 博客配置
pelican支持了不少的特性，比如RSS之类的，但是其实我暂时都用不着，所以我得根据需求定制一些，接下来慢慢看文档慢慢折腾，先在开头记录我个人主要在意的几点东西，有个向导。

 - 主题，暂时喜欢bootstrap的风格
 - 静态文件的良好关联，如文章中使用到的图片之类的
 - content文件夹的层次结构，强迫症不喜欢文件夹太乱。。
 - 暂时注释掉一些不用的功能（RSS之类）

接下来一个个处理吧。

pelican的content目录结构：

```
|—— content
|   |—— articles  # blog或者其他按日期排序的文本
|   |   |—— article1.md
|   |   |—— article2.md
|   |—— pages  # 一些不经常变动的页面，比如about，contact
|   |   |—— about.md
|   |   |—— contact.md
|   |—— images  # 图片（静态文件）
|   |—— pdfs  # 文本（静态文件）
```
__articles and pages__

> Pelican considers “articles” to be chronological content, such as posts on a blog, and thus associated with a date.

> The idea behind “pages” is that they are usually not temporal in nature and are used for content that does not change very often (e.g., “About” or “Contact” pages).

总之，articles下放各种文章就对了。。

__file metadata__

pelican会从你的文件的开头获取一些关于这个文件的信息，比如标题、日期等，下面以markdown为例：

```
# your file xxx.md

Title: My first file        # 标题
Date: 2014-5-25 20:30       # 时间
Category: Python            # 类别
Tags: pelican, publishing   # 分类标志
Slug: my-super-post         # 
Author: Goclis Yao          # 作者
Summary: Somethings         # 概要

正文here...
```

注意，除了标题以外，其他的属性如果没有指定的话，pelican会自动指定，比如说Category会基于该文件的当前目录，Date会基于该文件的mtime等。

__static folders__

静态文件路径（典型的是突破）是静态博客必须要指定好的一个东西。

pelican默认会在生成文章时拷贝content目录中的images文件夹到output的文件夹中。

如果你想要自己手动添加一个新的文件夹（比如pdfs）让其在生成文章时被拷贝到output中，可以在pelicanconf.py中添加：

```
STATIC_PATHS = ['images', 'pdfs']  # 这意味着这两个文件夹都会被copy过去
```

__theme settings__

pelican的默认主题不是很好看。。所以得研究研究怎么换了。。

这有一些[主题][1]，所以打算基于这些修改了。。

更换主题很容易，直接在配置文件里修改主题路径即可：

```
THEME = "/home/user/pelican-themes/theme-folder"
```

__配置文件__

在移植的时候需要注意主题的路径需要修改pelicanconf.py：

```
# -*- coding: utf-8 -*-
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

THEME = "/home/goclis/SHARE/Blog/themes/pelican-bootstrap3"
# THEME = "/home/goclis/niu-x2-sidebar"
```

### 结合nginx
修改nginx.conf，添加server如下：

```
server {
        listen [::]:80;
        listen 80;

        server_name localhost;
        root C:/Users/Goclis/Desktop/VMSHARE/Blog/output;

        location = / {
            # Instead of handling the index, just
            # rewrite / to /index.html
            rewrite ^ /index.html;
        }

        location / {
            # Serve a .gz version if it exists
            gzip_static on;
            # Try to serve the clean url version first
            try_files $uri.htm $uri.html $uri =404;
        }

        location = /favicon.ico {
            # This never changes, so don't let it expire
            expires max;
        }

        location ^~ /theme {
            # This content should very rarely, if ever, change
            expires 1y;
        }
    }
```

不同情况适当更换root路径。

重启后访问localhost即可。

### Some bugs
基本都解决了，但是有一些中文的原因导致的不兼容，比如说代码高亮。

代码高亮中会认为中文是err所以给中文加上了.err这个class，使得整体很难看，可以查看base.html中具体的css文件，将该文件中的.err给注释掉即可，当然，这不是长久解决，我觉得应该存在一种方式可以关闭这种检查。

[1]:https://github.com/getpelican/pelican-themes