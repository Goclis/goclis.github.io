Title: Pelican进阶配置  
Date: 2016-01-16 13:58  
Tags: Pelican, Markdown  
Slug: advanced-pelican-configuration  
Authors: Goclis Yao  

[TOC]

上周在重新配置博客的时候涉及到了一些以前没接触过的Pelican的配置，现在考完试有空了来把它们理一理，算是个进阶的配置吧。

### Markdown扩展
我的内容的编写使用的是Markdown，所以在配置的时候需要适当的设置一下所使用的Markdown扩展，通过在`pelicanconf.py`中对`MD_EXTENSIONS`进行适当的赋值即可，我的配置如下：

```python
MD_EXTENSIONS = ['codehilite(css_class=highlight)', 'extra', 'toc(permalink=true)']
```

总共三项：

- 第一个是参考我所引用主题的作者的配置，应该是代码高亮的配置。
- 第二个包含了一系列的小扩展，我主要是为了获得表格及代码块的支持。
- 第三个是为了生成目录，我的主题会提取文章的目录。

Pelican的Markdown支持是直接使用的其他人的模块，因此更多的扩展以及详细内容可以参见[Markdown模块官方文档][1]。

### Pelican page
配置的时候涉及到page是因为我希望增加一个独立的about页面，但我的主题原先没有提供，所以得绕一点了（可能有不用绕的方法，但没搜到）。这部分只介绍一下page的概念以及相关的配置，如何绕的放在下一部分。

page按照直面的翻译也就是**页面**的意思，往后都用这个词来表示。它与你的文章拥有同级的地位，这一点可以从主题的`templates`中拥有`article.html`和`page.html`，只是文章更倾向于内容，而页面可以很随意，所以一般可以拿来构造导航栏（比如about页面）。

页面和文章一样，都是Pelican根据你所编写的内容生成的，内容的格式同样可以是Markdown（或是支持的其他格式），并且也必须放到`content`目录下，为了更好分辨，还可以在`pelicanconf.py`中指定页面所在的文件夹以及页面生成相关的内容，我的配置如下：

```python
PAGE_PATHS = ['pages']
PAGE_URL = '{slug}.html'
PAGE_SAVE_AS = '{slug}.html'
DISPLAY_PAGES_ON_MENU = True # 主题的模板可能会使用的值，一般用于导航栏
```

`content`的目录结构如下：

```
|—— content
|   |—— posts # 文章的目录
|   |   |—— article1.md
|   |   |—— article2.md
|   |—— pages # 一些不经常变动的页面，比如about
|   |   |—— about.md
|   |—— images  # 图片（静态文件）
|   |—— ...
```

我的`pages`目录下只有一个`about.md`，按照配置，Pelican会为我生成一个`about.html`的页面。

### 按需自定义
为了满足自己的需求，你可以任意的修改主题的内容（协议允许的话）或者Pelican的源码，以下为一些我的自己的修改。

#### 设置生成的表格为Bootstrap风格
默认情况下，Pelican为我生成的HTML中的表格使用的是`<table></table>`这样的标签，没有增加任何的样式，很难看。

在主题是基于Bootstrap的前提下，把表格改为Bootstrap风格就非常容易，只要改为`<table class="table">`即可，两个方法。

__(1) 修改生成的内容__

前面提到过，Pelican的Markdown支持是依赖于Markdown模块的，因而本质上，它是利用了Markdown模块对输入进行了解析，然后对解析得到的结果进行生成。所以，一个简单的办法就是直接把生成的内容当成字符串进行搜索替换，把`<table>`替换为`<table class="table">`，这需要修改Pelican的源码，修改`reader.py`中的`MarkdownReader`的`read`方法：

```python
self._source_path = source_path
self._md = Markdown(extensions=self.extensions)
with pelican_open(source_path) as text:
	content = self._md.convert(text)
metadata = self._parse_metadata(self._md.Meta)
# 增加下面这一行
content = content.replace('<table>', '<table class="table">')
```

这种方法要改源码，迁移的时候有点麻烦。

__(2) 改主题__

目的都是给table标签加上class，可以直接修改主题，插入相应的JS代码即可，未考虑兼容性的问题，我直接在主题的`base.html`的末尾增加了如下代码：

```javascript
<script>
	// Added by Goclis for rerendering table to bootstrap style
	$("table").addClass("table");
</script>
```

#### 增加about页面
在`pages`文件夹里增加了一个`about.md`，但希望在导航栏上增加一个About比较麻烦，对主题的`base.html`进行了小小的修改：

```html
<div class="nav-collapse collapse">
    <ul class="nav pull-right top-menu">
        <li {% if page_name == 'index' %} class="active"{% endif %}><a href="/">Home</a></li>
        <li {% if page_name == 'categories' %} class="active"{% endif %}><a href="{{ SITEURL }}/categories.html">Categories</a></li>
        <li {% if page_name == 'tags' %} class="active"{% endif %}><a href="{{ SITEURL }}/tags.html">Tags</a></li>
        <li {% if page_name == 'archives' %} class="active"{% endif %}><a href="{{ SITEURL }}/archives.html">Archives</a></li>

        {% if DISPLAY_PAGES_ON_MENU %}
        {% for p in pages %}
        {% if p.slug == 'about' %}
        <li {% if p == page %} class="active"{% endif %}><a href="{{ SITEURL }}/{{ p.url }}">About</a></li>
        {% endif %}
        {% endfor %}
        {% endif %}
    </ul>
</div>
```

逻辑主要是下面这部分，通过判断slug，只为`about.md`增加导航，其他页面忽略，这需要在`about.md`的开头设置`Slug: about`。

### 小结
总的来说，尽管Pelican是个静态博客，但能够玩出花样的地方还是很多的，[Pelican FAQ][2]里有不少可以参考的问题。

[1]: http://pythonhosted.org/Markdown/extensions/
[2]: http://docs.getpelican.com/en/latest/faq.html#how-do-i-assign-custom-templates-on-a-per-page-basis
