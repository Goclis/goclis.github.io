Title: 和Shadowsocks一起科学上网  
Tags: Shadowsocks, VPS, VPN, Ubuntu, DigitalOcean  
Slug: fuck-the-gfw-with-shadowsocks  
Date: 2016-05-27 9:50 
 
[TOC]

拖延症晚期，本来上上个月把新机器折腾好了之后就想写这个内容的，丢到Todo里后就没理它了，今天发现还有一个更早前想写的内容至今也没开始码。
这篇东西呢，没什么干货，只是一个整理，记下如何利用Shadowsocks来科学上网，包括VPS相关的内容。因此，对于不同的VPS提供商、不同的OS可能不适用，可以自行搜索。

### VPS搭建服务器
稍微讲讲VPS的选择吧，一句话，**你选的VPS所在的网络必须能够访问你的目标网站**，比如你想通过VPS上Google，那选阿里云你就只会一脸懵逼了。

穷人表示我用的是[DigitalOcean][1]，还是最便宜的$5一个月那种，不过也够用了，流量好像是不限制的，带宽貌似是百兆，以下简称DO。

额，毕竟不是软文也不是小白教程，就不截没必要的图了。Droplet选的Ubuntu 14.04，创建完毕后，DO会给你发邮件，里面有VPS的IP以及root用户的密码，用ssh工具（Windows下可以下载putty）连接上去进行如设置root密码等一系列基础的配置后即可：

- *unix: `ssh root@IP`
- Windows: 在putty里填写IP，然后点击连接

#### 开启IPv6
默认的情况下DO是关闭IPv6的，可以到Droplet的管理页面中开启，系统会为VPS分配相应的IPv6地址，如下图：

![](http://ww1.sinaimg.cn/large/006y8lVagw1f86x20lhcej30su0eg3zg.jpg)

接着需要到VPS上[配置IPv6][3]，使用ssh连接，编辑`/etc/network/interfaces`，在`auto eth0`后加上下面的内容：

```
iface eth0 inet6 static
        address primary_ipv6_address
        netmask 64
        gateway ipv6_gateway
        autoconf 0
        dns-nameservers 2001:4860:4860::8844 2001:4860:4860::8888 209.244.0.3
```

其中`primary_ipv6_address`和`ipv6_gateway`换成上面那张图里DO分配给你的内容，保存后`service networking restart`重启网络即可，实在不行重启VPS，可以使用`ifconfig`来查看是否配置成功。

### 在VPS上配置Shadowsocks服务
在VPS上配置Shadowsocks实质上就是搭建一个SOCKS5服务，在Ubuntu下安装很容易：

```
apt-get install python-pip
pip install shadowsocks
```

安装完后还需要对Shadowsocks进行配置，找个地方创建一个配置文件即可，比如：

```
mkdir /etc/shadowsocks
vim /etc/shadowsocks/config.json
```

配置文件的基本内容：

```json
{
	"server":"::",
	"server_port": 8382,
	"local_port": 1080,
	"password": "yourpassword",
	"timeout": 600,
	"method": "aes-256-cfb"
}
```

稍微解释下：

- server: 指定SOCKS5服务监听的IP，指定为`::`的话可以同时监听IPv4及IPv6。
- server_port: 指定监听的端口。
- password: 客户端连接SOCKS5服务时的密码。

更多的配置可以到[Shadowsocks官网][2]查看。

关于服务的启动，ssh连上服务器然后执行下面这个命令：

```
# 注意配置文件的路径
nohup ssserver -c /etc/shadowsocks/config.json >> /var/log/shadowsocks.log&
```

关闭服务的话。。不大优雅：

```
# 利用lsof通过端口号找到pid
lsof -i:port
kill xxx
```

### 使用Shadowsocks客户端
这里只讲Windows的，OSX上的也基本一样。

客户端的话到[Github][4]下载即可，Windows推荐使用[Release][5]里的2.5.6，亲测比较妥。

解压后直接启动，在服务器设定里添加服务器即可，填写你在VPS配置的那些内容：

- VPS IP (v4/v6均可)
- 端口、密码、加密方式均按配置文件填

#### 代理模式
Shadowsocks的客户端有两种代理模式：PAC及全局模式。PAC就是只代理部分网站，而全局模式是代理所有的网站。

Shadowsocks客户端实质是在本机运行了一个HTTP(s)代理服务，默认监听端口为1080（可以通过配置修改）。之后所有的80及443端口的出境流量，都会经过`localhost:1080`的过滤，Shadowsocks根据代理模式来判断如何处理流量，PAC模式的话则会查看PAC列表（只有在列表中的站点才会代理），而全局模式则全部代理。

在Windows上，Shadowsocks是通过修改`Internet选项->连接->局域网(LAN)设置`中的内容实现的代理，如下图：

![](http://ww3.sinaimg.cn/large/006y8lVagw1f86x0qp7gfj30cp0c5jst.jpg)

当那个checkbox被勾上的时候，Windows会将它判定的LAN流量都经过Shadowsocks的脚本的过滤，这也就导致，你开启全局模式的时候，一些客户端中的浏览器（如QQ）也会被代理，这一定程度上会影响到使用。建议是不勾上，然后在需要的软件中自行设置HTTP代理。

比如说，Chrome中可以安装SwitchSharp这样的插件，设置代理服务器地址为`127.0.0.1:1080`，就可以比较灵活地使用Rule来控制代理了。同理，网易云音乐也可以在工具中设置相关的代理服务器，如下图：

![](http://ww1.sinaimg.cn/large/006y8lVagw1f86x15ike6j30g308bwep.jpg)

自己可以查看一下使用的软件是否要被代理，比如IDM、迅雷之类的下载软件就可以考虑设置代理。

#### 利用IPv6
如果你的运营商支持IPv6的话，建议在客户端配置上增加一个服务器，IP设置为VPS的IPv6 IP。Shadowsocks的服务端程序非常机智，如果你访问的网站是v4站点的话，服务器会在它那边使用v4访问该站，但结果依旧通过v6返回给你。对于校园网用户来说，IPv6一般都是免费的，可以省一笔流量费，并且，v6由于使用人数较少，网络状况也比较好。

### PPTP VPN
这个是额外的，除了在VPS上搭建Shadowsocks服务以外，你还可以自己去做些别的，这里贴个PPTP VPN的[教程][6]。

### 参考资料
1. [Shadowsocks官网](https://shadowsocks.org)
2. [Shadowsocks on Github][4]
3. [PPTP VPN搭建][6]

[1]: https://www.digitalocean.com
[2]: https://shadowsocks.org/en/config/quick-guide.html
[3]: http://4b3r.com/digitalocean-enable-ipv6/
[4]: https://github.com/shadowsocks/
[5]: https://github.com/shadowsocks/shadowsocks-windows/releases
[6]: http://blog.kunyu.li/digitalocean-ubuntu-vps-vpn.html
