Logging
============

### 目录结构
```
|—— content
|   |—— Tech # 偏技术类
|   |   |—— article1.md
|   |   |—— Python # 技术子类
|   |   |   |—— pelicanxxxx.md
|   |—— Note  # 笔记类
|   |   |—— Python.md
|   |   |—— Javascript.md
|   |—— Life # 生活类
|   |   |—— 小结.md
|   |—— pages # 自定义页
|   |—— tpages # 模板页
|   |—— images  # 静态文件：图片
|   |—— pdfs  # 静态文件：pdf
```

以下内容为给未来可能忘掉为什么这么设置的自己的解释。

原本在博客中只会放技术类文章，现在想想，博客里可以放生活中的任何东西，技术类文章供别人看，笔记供自己翻阅，生活及琐碎供未来的自己回忆，所以对目录结构进行了一系列的调整：

- Tech：这个目录下放技术类文章，也就是原先供读者看的内容，以Tech作为未分类文章的Category，内部可以自行细分子目录建立更细的Category，如Python；本页将会取代原先的Home；
- Note：这个目录下放各种笔记，一些小TIPS；
- Life：这个目录下放些生活相关的东西，比如年度小结、吃喝玩乐等，可以在这里面更新各种浪的内容23333；

这三个目录都需要像原先的`index.html`那样建立相关的`Template Page`，都放在`tpages`目录下，并在`pelicanconf.py`中设置`TEMPLATE_PAGES`的值，同时需要把`tpages`目录从文章中排出（即修改`ARTICLE_EXCLUDES`变量）。

显然，这四个页面所显示的文章需要通过`article.category`来区分，但是，一个大类下可能会有子类（如Tech下可能会有Python），为了方便修改，在`pelicanconf.py`中为四个类别分别增加了一个变量，命名为`XXX_CATEGORIES`，然后模板里通过这四个变量来区分文章。

- `pages`目录目前只放About页面；
- `images`和`pdfs`用于放静态文件，以供文章中使用。

目前每个页面都只会显示10篇最新的内容（Note是笔记，全部都显示），要查看所有的内容，需要到Archive里面查看，由于分了类，`archives.html`也要修改，分成各类来查看。

### 对源码的修改
Pelican版本：3.6.3

__（1）TemplatePageGenerator__

在目录结构的设计中提到了需要增加4个`Template Page`，同时需要将它们增加到导航栏里，但是如何区分这四个页面从而正确的设置对应的导航项的样式为`class="active"`成了一个问题。。

对于必备的那些`index`、`categories`等，pelican在生成的时候会向模板引擎的context中插入`page_name`等变量；而`page`、`article`这类也会有一个对应的`page`变量，从而可以获取到`slug`之类的信息。

但是，`Template Page`并没有。。为了区分，我手动修改了源码，主要目的就是增加一个`tp_slug`变量表示该页的`slug`，如下：

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

修改过后，就可以对`base.html`中的导航栏进行修改了，如下：

```
<li {% if tp_slug == 'tech.html' %} class="active"{% endif %}><a href="{{ SITEURL }}/tech.html">Tech</a></li>
<li {% if tp_slug == 'note.html' %} class="active"{% endif %}><a href="{{ SITEURL }}/note.html">Note</a></li>
```

### 文章规则
文件名、方法名、变量名、路径等使用``包裹，其他的英文均直接写且不加任何的空格。
