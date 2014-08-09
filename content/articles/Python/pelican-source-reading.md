Title: Pelican源码解读  
Slug: pelican-source-reading  
Date: 2013-11-15  
Tags: pelican, python    

今天想要用peclian自己搭一个博客，装完之后发现是定制好的，虽然有主题可以更换，但是还是想自己定制一番，于是想改它的template，但模板中有着一系列的变量不知道具体是如何定义的，就想着回头往上层看看，结果发现没那么容易。。。最后。。因为自己最近也想找一份Python的源码来看看别人是如何写的，就决定把Pelican的源码自己看看吧，能看多少算多少，在这里做个记录。

###1. make html
看了看文档知道 [Pelican](http://docs.getpelican.com/en/3.3.0/) 是通过这个命令来将content目录下的.md之类的文件转换成了相应的html的，所以便打算从此入手。   
make是一个linux系统自带的命令（也有可能不是。。个人没深入理解），自己上网找了一些资料发现，当调用make xxx时会从当前目录中查找Makefile文件，并从中找其感兴趣的东西。   
使用Pelican的pelican-quickstart生成的工程中是有一个MakeFile文件的，部分如下：   

```makefile
PY=python
PELICAN=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

FTP_HOST=localhost
FTP_USER=anonymous
FTP_TARGET_DIR=/

SSH_HOST=localhost
SSH_PORT=22
SSH_USER=root
SSH_TARGET_DIR=/var/www

S3_BUCKET=my_s3_bucket

CLOUDFILES_USERNAME=my_rackspace_username
CLOUDFILES_API_KEY=my_rackspace_api_key
CLOUDFILES_CONTAINER=my_cloudfiles_container

DROPBOX_DIR=~/Dropbox/Public/

DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

help:
	@echo 'Makefile for a pelican Web site                                        '
	@echo '                                                                       '
	@echo 'Usage:                                                                 '
	@echo '   make html                        (re)generate the web site          '
	@echo '   make clean                       remove the generated files         '
	@echo '   make regenerate                  regenerate files upon modification '
	@echo '   make publish                     generate using production settings '
	@echo '   make serve [PORT=8000]           serve site at http://localhost:8000'
	@echo '   make devserver [PORT=8000]       start/restart develop_server.sh    '
	@echo '   make stopserver                  stop local server                  '
	@echo '   make ssh_upload                  upload the web site via SSH        '
	@echo '   make rsync_upload                upload the web site via rsync+ssh  '
	@echo '   make dropbox_upload              upload the web site via Dropbox    '
	@echo '   make ftp_upload                  upload the web site via FTP        '
	@echo '   make s3_upload                   upload the web site via S3         '
	@echo '   make cf_upload                   upload the web site via Cloud Files'
	@echo '   make github                      upload the web site via gh-pages   '
	@echo '                                                                       '
	@echo 'Set the DEBUG variable to 1 to enable debugging, e.g. make DEBUG=1 html'
	@echo '                                                                       '

html:
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)
```

其中有一个html: ...，那个便是使用**make html**时make这个命令会从这个Makefile文件中执行的命令，$(xxx)是一系列的变量，在文件的开头有定义，在这里其对应的命令就是：  
```bash
pelican ./content -o ./output -s ./pelicanconf.py # 最后一个参数为空
```
所以，归根结底还是调用了pelican这个命令，那么我们接下来就要找这个命令到底是做啥的了  

###2. pelican ....
很明显，pelican既然作为一个命令，说明其已经被加入到了**$PATH**中，一般就是在bin目录下了，找一找，发现了它，打开来看看：  
```python
#!/home/goclis/Program/Python/pelican/pelican/bin/python
# EASY-INSTALL-ENTRY-SCRIPT: 'pelican==3.3','console_scripts','pelican'
__requires__ = 'pelican==3.3'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('pelican==3.3', 'console_scripts', 'pelican')()
    )

```
噗。。还是不知道调用了哪个.py文件，上网查了查，这是python程序的一种入口方式，具体的调用了哪个文件是在python的site-packages中有文件定义的，找了找site-packages中pelican-3.3-py2.7egg-info这个文件夹（名字不一定是这个，但是认准那个**egg**）的**entry_points.txt**，打开来看看。
```txt
[console_scripts]
pelican = pelican:main
pelican-import = pelican.tools.pelican_import:main
pelican-quickstart = pelican.tools.pelican_quickstart:main
pelican-themes = pelican.tools.pelican_themes:main
```
这下可以看到了，pelican=pelican:main，所以可以知道pelican这个命令实际是调用了pelican文件夹中main.py，pelican文件夹在哪呢？同样地，它也在site-packages文件夹中，很容易找到，但是找不到main.py？！但是看到一个__init__.py这个文件，里面有个main函数，没错。。就是它。。  

好了，这下总算找到了入口。。继续读源码吧。。。  

###3. args...
= =# 第一行就读不懂了。。。贴下代码。。**顺序不是这样，只是为了方便讲解**
```python
def main():
    args = parse_arguments()
def parse_arguments():
    parser = argparse.ArgumentParser(description="""A tool to generate a
    static blog, with restructured text input files.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(dest='path', nargs='?',
        help='Path where to find the content files.',
        default=None)

    parser.add_argument('-t', '--theme-path', dest='theme',
        help='Path where to find the theme templates. If not specified, it '
             'will use the default one included with pelican.')
    
    ...
    
    return parser.parse_args()
```
这里涉及到了argparse这个python库，做啥用的？查。。[python文档](http://docs.python.org/2/library/argparse.html)
查询后可以发现是对sys.args进行处理的一个库，简单来说就是用来对命令带的参数进行处理的。回忆之前 **make html** 那句命令：  
```bash
pelican ./content -o ./output -s ./pelicanconf.py # 最后一个参数为空
```
这里调用的那个parse_arguments函数就是定义相应的命令并返回一个处理这些的Object，也就是返回的那个parser.parse_args()，具体的还是参考标准库吧。。

###4. Continue...
```python
def main():
    ...
    init(args.verbosity) # 初始化版本
    # 创建Pelican对象以及读取配置
    #（默认从pelicanconf.py中读取配置，不指定则从settings中的DEBUG_CONF获得）
    pelican, settings = get_instance(args) 
```

###5. TJ...
不怎么看的下去了。。因为pelican中加了一些我暂时不需要的功能，比如github upload, feed, rss之类的，使得看起来特别的累。   
不过自己还是将整体的架构给看了个大概，感觉还是得先提升自己的水平再考虑去找份好点的源码来继续进阶，否则只是一系列的无用功。  
现在只能先凑合改改theme（使用的是**simple-bootstrap**）的template来定义一下页面了，要添加功能时再具体去研究研究吧，比如评论添加的功能，这个往后加吧。  
最近实在是太忙太烦，自己的身体状况也很糟糕，只能如此了。  
虽然不是很完美的收场，但总归有点收获～