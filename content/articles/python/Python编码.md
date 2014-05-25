Title: Python编码。。。。  
Category: Python  
Date: 2014-02-06  
Tags: python, unicode  
Author: Goclis Yao    

= = 记下来提醒自己写爬虫的时候注意。。。。

直接举遇到的坑吧。。爬教务处的时候这样一个字段。。。
```
[1-16周] 周二(1-2)教二-403,周四(双3-4)教二-403
```
要把它切成。。
```
1，16，2，1，2，教二-403
1，16，4，3，4，教二-403
```
额。。内容是什么意思就不说了。。大概就是需要使用python的slice来获取，如下
```python
s = "周四(双3-4)教二-403"
# 获取3
l = s[s.find('双')+len('双'): s.find('-')]
```
看起来是行得通的。。但是并不一定。。  
问题就在于字符串s和slice中使用的'双'的编码不同时就会出错。。  

因为使用requests.get获取到的response的text是Unicode编码的（不是很确定），而我们的硬编码中的字符串是utf-8编码的，这就导致slice的并非我们所要的  
额。。可以先看看这有什么区别
```
s = "周四(双3-4)教二-403" 
print '%r' % s 
# '\xe5\x91\xa8\xe5\x9b\x9b(\xe5\x8f\x8c3-4)\xe6\x95\x99\xe4\xba\x8c-403' utf-8编码

us = s.decode('utf-8') # 将字符串s按utf-8解码成ASCII，python中会变成unicode
print '%r' % us 
# u'\u5468\u56db(\u53cc3-4)\u6559\u4e8c-403' unicode编码

# 比较下不同
print "utf8:", len(s), "unicode:", len(us)
# utf8: 24 unicode: 14

print "utf8:", s[s.find('双')+len('双'): s.find('-')]
# utf8: 3

print "unicode", us[us.find('双')+len('双'): us.find('-')]
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xe5 in position 0: ordinal not in range(128)
```

额。。看上面的代码已经能感受到不同了吧。。如果两种编码混合的话就可能会导致结果不是想要的  
先来解决一下UnicodeDecodeError这个问题，添加如下代码
```
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
```
然后再运行
```
print "unicode:", us[us.find('双')+len('双'): us.find('-')]
# unicode: 
```
后面那个slice的结果是""

原因呢，就是之前讲的'双'的编码和us字符串的编码不同了，所以将其decode成unicode就可以得到想要的结果了
```
print "unicode:", us[us.find('双'.decode('utf-8'))+len('双'.decode('utf-8')): us.find('-')]
# unicode: 3

# 简单点的。。。
print "unicode:", us[us.find(u'双')+len(u'双'): us.find('-')]
```
好了。。得到想要的结果了。。

建议：  
1. 自己硬编码的字符串最好前面都加上u以确保其是unicode编码
2. 确定一下自己使用的库(urllib2，requests)获取到的页面的文本是什么编码的。。最好都转成unicode来处理。
