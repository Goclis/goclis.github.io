Title: Python with Xpath获取全校考试安排  
Date: 2013-01-03  
Category: Python  
Tags: python, spider, xpath  
Author: Goclis Yao  

= =#又到考试周。。去年就想写个爬全校考试安排的。。可是当年还不会。。现在知道了东西就写一个来用吧。。不长不短。。记下来当**笔记**。。。  

虽然现在对整个流程有了点了解。。但写起来还是比较蛋疼。。因为既然是学习，就得不断尝试点新的。。这次就体验了一把[xpath][1]的方便，确实很赞！  

不过过程还是有点苦逼。。虽然xpath之前看过。。但是没用基本就忘完了。。现在即使写了出来还是不怎么理解其中的一些具体细节。。有空再补了。。  

好，开始正文。。  

## Python中的lxml
首先要用xpath就得装上Python相应的模块吧，也就是[lxml][2]
```
sudo apt-get install libxml2-dev libxlst1-dev
sudo apt-get install python-lxml
```
STO上找到的。。能用，OK～

## 请看代码。。。。
接下来就不好分了。。直接上代码。。看注释吧。。
```python
#encoding: UTF-8 

import urllib, urllib2, re, sys, MySQLdb
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf-8')

# 从网站上拿到包含各个院系考试安排链接的那个页面，把这些链接解析出来，直接用正则了。。
url1 = "http://xk.urp.seu.edu.cn/jw_service/service/runAcademyClassDepartmentQueryAction.action"
source = urllib2.urlopen(url1).read()
ptrn = r'runDetailClassDepartmentQueryAction.action.*?"'
urls = ['http://xk.urp.seu.edu.cn/jw_service/service/' + u[0 : -len('"')] \
		for u in re.findall(ptrn, source)]

# 连接数据库，对应表是goclis.exams，表的结构就保留了考试安排页的那个表头（除了序号改成ID以外）
conn = MySQLdb.connect(host="localhost",user="goclis",passwd="qqqqqq",db="goclis",charset="utf8")  
cursor = conn.cursor() 

# 针对各个链接开始获取，这个pattern是为了获取考试安排页中每一门科目。。看看源码就很容易发现。。
ptrn = r"""<tr height="30" onMouseOver=this.style.backgroundColor='#bbbbbb' 
		onMouseOut=this.style.backgroundColor=''>.*?</tr>"""
for url in urls:
	exam_source = urllib2.urlopen(url).read().decode("utf-8") \
					.replace('\n','').replace('\t', '') \
					.replace('\r', '').replace('&nbsp;', '') # 获取源文件并处理格式
	exams = re.findall(ptrn, exam_source) # 通过正则拿到所有的<tr>...</tr>，也就是一门门的考试

	for e in exams:
		html = etree.HTML(e) # 使用lxml.html.etree.HTML将拿到的字符串解析成XML树
		tds = html.xpath('//td') # 获取其中所有的td项，为了下一步拿值
		values = [] # 暂存各个td的值。。
		for td in tds:
			vl = td.xpath('./text()') # 拿td的值
			if len(vl):
				values.append(vl[0].replace('&nbsp;', '').strip())
			else:
				values.append('')

		# 插入数据库
		sql = "INSERT INTO exams (term, campus, exam_name, teacher, time, location, duration, note) \
				VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
				(values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8])

		n = cursor.execute(sql)
		conn.commit() # 0.0 以防插入不回去。。


```

OK~搞定了。。数据怎么用就自己看着办吧。。  

这种简单的爬虫真的不难～尤其是在这些牛掰的脚本语言以及一系列的类库的辅助下～博客里现在也没有关于爬虫的文章。。这篇就当抛砖引玉吧～


###在结尾附上一些xpath的使用

随便给个html。。xml也可以的
```html
<html>
<body>
	<tr onmouseover="xxx">
    	<td>A</td>
        <td>B</td>
	</tr>
    <tr>
    	<td>A</td>
    </tr>
    <tr onmouseover="xxx">
    </tr>
</body>
</html>
```
下面是几种情况及代码  

__通过lxml的etree把html变成Tree__  
```python
from lxml import etree
source = requests.get('xxx').text # 获取到的html网页的源码

tree = etree.HTML(source) # 即可
```

__根据属性获取节点__
```python
tree.xpath('//tr[@*]') # 获取所有带属性(任意)的tr节点

tree.xpath('/tr[@*]') # 获取所有带属性(任意)的子tr节点

tree.xpath('//tr[@onmouseover]') # 获取所有带onmouseover属性的tr节点

tree.xpath("//tr[@onmouseover='xxx']") # 获取所有onmouseover属性值为xxx的tr节点
```

__获取第一个td文本为A的tr节点__
```python
tree.xpath("//tr/td[1][contains(text(), 'A']/parent::*")
这里用了contains来实现

tree.xpath("//td[text()='A']")
```

__注意区分//和/的不同__


[1]:http://www.w3schools.com/xpath/
[2]:http://lxml.de/parsing.html