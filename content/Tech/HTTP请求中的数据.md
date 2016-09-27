Title: HTTP请求中的数据  
Date: 2016-04-16 22:47:20  
Slug: data-in-http-request  
Tags: HTTP请求  


[TOC]

那天在帮同学调代码的时候发现自己对于HTTP Request的细节很模糊，对于各种形式的数据是如何被处理封装成HTTP报文的、在报文中的哪个位置，并不是非常的清楚，因此，查了查资料后写了这篇东西。

### HTTP请求格式
先看看HTTP请求消息的格式 [1]：

- A Request Line
- Zero or more header (General|Request|Entity) fields followed by CRLF
- An empty line (i.e., a line with nothing preceding the CRLF) indicating the end of the header fields
- Optionally a message-body

从格式上来看，除了第三部分，都能够附带用户数据，但一般来说，不会在HTTP头里放数据，而且在第一部分的URL以及第四部分中放数据，下面分别讲一下，主要区分下：

- Query String
- Form Data
- JSON/File Data

### Query String
这个实际上就是HTTP请求消息的第一部分URL中?后面的那部分信息，因此，它与请求的类型无关，只和URL相关，下面是个例子：

```other
# 附带数据为name: xxx, age: 18
GET example.com?name=xxx&age=18
POST example.com?name=xxx&age=18
```

用python的requests库来实现这个请求的话就是下面这样：

```python
requests.get('example.com', params={name: 'xxx', age: 18})
requests.post('example.com', params={name: 'xxx', age: 18})
```

即这些数据会当做参数被编码到请求的URL中，而服务器端会解析这些参数。

### Form Data
一般来说，form data是指html中form标签提交的数据：

```html
<form action="xxx" method="GET">
    <input type="text" name="first" />
    <input type="text" name="second" />
    <input type="submit />
</form>
```

但是，form data是放在HTTP请求报文中的哪呢？？这个得看提交的方法：

- GET：会被当做Query String一样处理；
- POST：会放到请求消息的第四部分中，编码方式同Query String。

### JSON Data
其实这里所描述的情况不仅仅适用于JSON数据，而适用于使用其他类型的数据。对于一开始的Web，Query String和Form Data就基本够用了，但后来Web应用的数据的格式越来越复杂，就需要有一定的扩展。

扩展很简单，使用HTTP头中的Content-Type来表示附带的数据的类型，并按照类型编码数据，然后放到请求消息的第四部分中。服务端可以根据Content-Type来判断如何数据进行解码，常见的数据类型（实际上就是[Media Type][3]）有：

- text/html
- text/xml
- application/json
- ...

关于JSON的示例，可以查看[2]。

### 参考资料
1. [HTTP Requests][1]
2. [x-www-form-urlencoded vs json][2]
3. [IANA Media Types][3]

[1]:  http://www.tutorialspoint.com/http/http_requests.htm
[2]:  http://homakov.blogspot.com/2012/06/x-www-form-urlencoded-vs-json-pros-and.html
[3]: http://www.iana.org/assignments/media-types/media-types.xhtml


