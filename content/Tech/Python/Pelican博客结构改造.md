Title: Pelican博客结构改造  
Date: 2016-04-02 23:43:50  
Tags: Pelican, Jinja2  
Slug: reconstruction-of-pelican-blog  
Author: Goclis Yao  

[TOC]

最近想要在博客里写一些生活相关的东西（也就是吃喝玩乐啦），同时还希望能够比较清晰地区分开技术文章和生活文章，所以这两天就在折腾着博客内容的改造，不得不提一下，这个折腾过程中看代码的感觉真的是让我找回了一丝大二时的感觉，很爽！

这篇文章把一些我在改造过程中遇到的问题以及解决思路记录下来。

### 使用Template Page划分内容
博客的改造是希望把内容分成四块：技术、生活、笔记、琐碎。技术就是先前写的这些博文；生活记录一些小结或是感想的东西；笔记实质上是我平时针对一些具体技术记录的一些Tip，打算一并放上来；琐碎实际上就类似于微博，一些短的想法之类的。

按照上面的想法，在内容呈现上也就自然而然地希望每类对应一个单独的页面了，先前用过Pelican中的Page的功能来做过“关于我”的页面，但是这个功能并不能满足我的需求。因为Page对应的模板`page.html`决定了所有的页面必须得遵循一样的格式，然而，这四块内容对应的页面的格式是不同的，比如说，技术和生活的页面就只显示最近的数篇文章，而笔记页面会显示所有的，更不一样的是，琐碎页面可能会显示文章的内容而非标题。

因此，需要使用到Template Page的功能。这个功能用起来其实挺简单的，只需要在`pelicanconf.py`中对`TEMPLATE_PAGES`进行相关的设置即可，如下：

```python
TEMPLATE_PAGES = {
    'tpages/life.html': 'life.html',
    'tpages/tweet.html': 'tweet.html',
    'tpages/note.html': 'note.html'
}
```

字典的键是页面的模板的路径，相对于content目录，这个模板的语法遵从是Pelican使用的Jinja2的模板引擎的规定。字典的值是生成的页面的输出路径，相对于output目录。这里只有三个页面，因为我直接修改了`index.html`这个模板，把它作为了技术文章的页面。

在实现这块的时候，遇到了导航栏的激活的问题。我希望把这四个页面都加入到导航栏，关于导航栏的内容，一般都在`base.html`这个模板里，对于每个页面哪个导航项该被激活，实现一般如下：

```html
# 1
<li {% if page_name == 'categories' %} class="active"{% endif %}><a href="{{ SITEURL }}/categories.html">Categories</a></li>

# 2
{% if page %}
<li {% if page.slug == 'about' %} class="active"{% endif %}><a href="{{ SITEURL }}/about.html">About</a></li>
{% else %}
<li><a href="{{ SITEURL }}/about.html">About</a></li>
{% endif %}
```

实现的不同是因为Pelican生成时的处理不同。我们知道，对于Jinja2这样的模板引擎来说，你除了需要给定它模板文件，还需要指定一个context，也就是你这个模板文件中使用到的变量对应的具体的值，Pelican针对不同类型的输入给定了不同的context

实现1用于几个特殊的模板，如`index.html`、`categories.html`、`tags.html`等，Pelican规定了每一个主题都需要提供这些模板，在调用Jinja2生成它们时，Pelican会把如`page_name`等变量传到对应的context里，所以我们可以通过判断当前页面的`page_name`来确定激活对应导航项。

实现2用于Page，是先前在实现“关于我”页面的时候，为该页面增加导航项的做法，之所以这样做在于我上面提到的context的问题，Pelican在Page页面的context中提供了一个`page`变量，其中包含了一系列的信息，但由于`base.html`不仅仅供Page使用，需要加个判断。类似的，Pelican在Article页面的context中提供了一个`article`变量。

但是，并没有办法区分两个Template Page，因为Pelican没有为它的context提供额外的信息，这点我是通过查看源代码确认的，关于它的代码在`generators.py`中，下面给出一部分，其中包含了我的修改：

```python
# generators.py
class TemplatePagesGenerator(Generator):

     def generate_output(self, writer):
         for source, dest in self.settings['TEMPLATE_PAGES'].items():
             self.env.loader.loaders.insert(0, _FileLoader(source, self.path))
             try:
                 template = self.env.get_template(source)
                 rurls = self.settings['RELATIVE_URLS']
                 self.context['tp_slug'] = dest # 为TemplatePage增加slug供模板使用
                 writer.write_file(dest, template, self.context, rurls,
                                   override_output=True)
             finally:
                 del self.env.loader.loaders[0]
             # 删除掉以避免影响其他的模板context
             if self.context.get('tp_slug', None):
                 del self.context['tp_slug']
```

从源码中可以看到，`writer.write_file`的参数中并没有传入额外的参数，仅仅是`self.context`，我修改了代码把该变量打印了一下，发现并没有可以区分`Template Page`的信息，所以，改动也很简单，我自己加了一个表示`slug`的`tp_slug`变量到`context`中，这样就可以简单区分了，模板中的导航项实现如下：

```html
<li {% if tp_slug == 'note.html' %} class="active"{% endif %}><a href="{{ SITEURL }}/note.html">Note</a></li>
```

搞定了这个问题后，我就只需要好好的设计`index.html`、`life.html`、`note.html`以及`tweet.html`这四个分别对应四块内容的模板就行了。

### Jinja2模板使用
在设计模板的过程中遇到了一些问题，并查到了一些解决方案，这里记录一下。

#### Jinja2变量作用域
Jinja2的变量的作用域比较奇怪，不是全局的那种，如下例子：

```
% set last_year = 0 %}
{% for article in dates %}
{% if article.category in TECH_CATEGORIES %}
{% set year = article.date.strftime('%Y') %}
{%if last_year != year %}
<h2 id="{{year }}"><a href="#{{year}}">{{ year }}</a></h2>
{% set last_year = year %}
{% endif %}
	{% set next_year = 0 %}/{% set g_next_year = [0] %}
{% if not loop.last %}
{% set base = loop.index0 + 1 %}
{% set found = 0 %}
{% for na in dates[base:] %}
{% if found == 0 and na.category in TECH_CATEGORIES %}
{% set next = base + loop.index0 %}
{% set next_article = dates[next] %}
	{% set next_year = next_article.date.strftime('%Y') %}
{% set found = 1 %}
	{% set _ = g_next_year.pop() %}
	{% set _ = g_next_year.append(next_year) %}
{% endif %}
{% endfor %}
{% endif %}
	{%if next_year != year %}/{% if g_next_year[0] != year %}
<article class="last-entry-of-year">
{% else %}
<article>
{% endif %}
<a href="{{ SITEURL }}/{{ article.url }}">{{ article.title }} {%if article.subtitle %} <small> {{ article.subtitle }} </small> {% endif %} </a>
<time pubdate="pubdate" datetime="{{ article.date.isoformat() }}">{{ article.locale_date }}</time>
</article>
{% endif %}
{% endfor %}
```

注意我特别缩进的几行，希望达到的目的是：外部设置初值，内部改变值，再出来后检查值是否有改变。从执行过程来说，内部是会对值进行改变的，但是由于Jinja2的作用域问题，它改变的并不是外部那个变量，从而导致出来后的检查永远是未改变。

解决办法是[使用列表][1]，貌似列表变量的作用域是全局的，所以可行，逻辑也很简单，初始化为只包含初值的列表，修改值即为弹出再插入值，然后读取值即为访问第一个元素。

#### Jinja2把文章分类
这个其实不是很通用，但还是说一下，发生在我改造`archives.html`模板的时候，希望能够把所有的文章给分一下类，然后再挨个处理。从编程的角度来看，实际上就是把一个列表拆分成四个列表嘛，在Jinja2里也是能做的，如下：

```jinja2
{# -- 把所有文章按大类分到不同的list中 -- #}
{% set tech_articles = [] %}
{% set life_articles = [] %}
{% set tweet_articles = [] %}
{% for article in dates %}
    {% if article.category in TECH_CATEGORIES %}
        {% set _ = tech_articles.append(article) %}
    {% endif %}
    {% if article.category in LIFE_CATEGORIES %}
        {% set _ = life_articles.append(article) %}
        {{ article.title }}
    {% endif %}
    {% if article.category in TWEET_CATEGORIES %}
        {% set _ = tweet_articles.append(article) %}
    {% endif %}
{% endfor %}
```

这里只有三个，是因为笔记类的不归档。代码里涉及到了`XXX_CATEGORIES`这样的变量，它们是我自己添加，用于对文章进行类型划分的，主要是针对一个大类下可能有不同小类的情况（比如技术类下有Python子类），在`pelicanconf.py`中添加：

```python
TECH_CATEGORIES = ['Tech', 'Python']
NOTE_CATEGORIES = ['Note']
LIFE_CATEGORIES = ['Life']
TWEET_CATEGORIES = ['Tweet']
```

### 参考资料
- http://stackoverflow.com/questions/4870346/can-a-jinja-variables-scope-extend-beyond-in-an-inner-block

[1]: http://stackoverflow.com/questions/4870346/can-a-jinja-variables-scope-extend-beyond-in-an-inner-block
