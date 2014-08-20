Title: PPTP VPN Process  
Slug: pptp-vpn-process    
Date: 2014-08-19 14:41  
Tags: vpn  
Author: Goclis Yao  

不久前因为StackOverflow上不去的缘故，找人借了下云梯VPN来用了一下，感觉很爽！但是自己脑抽，随之而来的伴随了一个问题，云梯VPN的限制设备数量能否区分同一个私有网络下的不同设备，是如何区分的？于是乎，就开始去各种找PPTP VPN的资料了，终于有点搞懂了，就通过这篇博文记下来吧。

以下文章中VPN如不特指皆为PPTP VPN。

首先找了个免费的VPN试了下，确认了在同一私有网络下不同设备用同一账号是可以连接上同一台VPN Server的，如果不能的话，我的问题也就没啥意义了。虽然这问题确实没啥意义，私有网络要实现共享VPN可以在出口的机器或者路由上建立Site to Site VPN就可以了，但是纯粹好奇，勿喷。。。

以前只是大概了解了一下VPN的原理，也没有去细究到协议的层次，这次就借着这个机会去好好了解了一下。

### VPN的两种架构
 - Remote access VPN
 - Site-to-site VPN

Remote access VPN是我们平时个人用的比较多的那种，也就是你在网上买了个VPN，然后拿着账号密码和服务器名连接上了的种，这种就只能保证你自己的那台设备是连上VPN的，而Site-to-site VPN则更像是，如果你用了路由这样的设备，在该设备上拨了VPN，这样路由的私有网络就是一个Site，而路由连上的VPN服务器又构成了另外一个Site，所以是Site-to-site，这种方式就能保证你私有网络中的所有设备都连上了VPN。

个人感觉，这两种其实差不多算是一种情况吧，只是因为现在的交换设备越来越牛逼了，Site to Site VPN站在路由的角度来看其实就是Remote access VPN了。

### 两种使用VPN的情境
 - Internet
 - Intranet

本来VPN不是个科学上网的工具的，纯粹就是为了满足在划分了私有网络后又能保证某些有特权的人能访问私有网络的资源，但是，总归是被发掘成了科学上网的工具了。纯吐槽，下面将正事。

这两种情境的区别就在于一个是在公开的互联网（Internet），而另一个则是在一个机构比如公司的大网络环境中（Intranet），接下来分别说说。

#### Internet-Based VPN
这一般是一种公司有个内部网络，而你现在的设备不在公司的网络里，比如说在家或者说外地出差，但是这时候你又想要使用公司内网的一些资源，那就得在Internet上使用Remote access VPN或者Site-to-site VPN来保证你能访问公司内网的资源了，所以这种方式是Internet-Based的了，当然，你得连上Internet，并且可以连接上那台公司内网对外的 VPN 服务器。

#### Intranet-Based VPN
这种情况一般用在一个大的私有网络之中，比如你的公司非常大，各个部门在同属于这一个大私有网络的前提下，又各自有着自己的内部私有网络，并且它们为了保证资源的保密性，将这一个个小的私有网络都在物理上隔离了，也就是一个人在没有权限的时候是无法访问另外一个部门的内部资源的。但是，老板所在的那个私有网络可能需要查看各个部门的情况，也就需要访问它们的内部资源，这种时候，类似于Internet-Based那样使用VPN进行即可。

### VPN Tunneling（隧道）
隧道是一种常用的网络技巧，目的在于在一个协议的数据报部分封装另一个协议的数据包，即datagram is a packet of anther type of protocol，数据报数据包傻傻分不清囧。

而VPN也就是使用了这样的技巧，把VPN协议的数据包当做数据报放到了IP包中，这样IP包像正常的数据包一样路由到对端就好了，然后对端通过IP包的IP Header中的协议是能够判断出包含的数据报是使用了某种VPN协议的，于是，对端就按那个协议处理，获取到了真正的数据报。

这里只是模糊的讲一下大概的过程，这也是我先前对VPN的理解程度，下面从数据包的程度来理解一下，以最简单的PPTP VPN为例了。


隧道的两端在连接建立的时候需要协商一系列配置变量：

1. 地址分配（address assignment）
2. 加密（encryption）
3. 压缩参数（compression parameters）
4. 更多

### Point-to-Point Tunneling Protocol (PPTP)
看英文全称就可以看出来，PPTP VPN本质上就是基于PPP的Tunneling，所以我们按照之前对隧道的描述，并结合这个协议是个二层协议可以大致猜想下它做的工作了：

1. 一个来自用户的TCP/IP包，下送到PPTP所在的第二层，交由PPTP协议进行处理。
2. PPTP协议对这个数据包做了点处理，即加上PPP Header和GRE Header，这个待会再说，然后转交给TCP/IP 层，准确来说是IP层。
3. IP层把来自PPTP处理后的这个东西当做数据报，再次加上IPHeader，这个IP Header的参数很重要，下面说，然后该把这个IP包发出去了，所以转交给二层。
4. 链路层会把这个IP包当做正常的数据包，加上头尾封成帧，丢给物理层发出去了，到此Over。

上面的这个工作过程讲得很粗糙，但大概就是这么个过程，下面讲的细致一些。

#### PPTP inherit PPP
> Authentication that occurs during the creation of a PPTP-based VPN connection uses the same authentication mechanisms as PPP connections, such as Extensible Authentication Protocol (EAP), Microsoft Challenge-Handshake Authentication Protocol (MS-CHAP), Microsoft Challenge-Handshake Authentication Protocol version 2 (MS-CHAP v2), CHAP, Shiva Password Authentication Protocol (SPAP), and Password Authentication Protocol (PAP). PPTP inherits encryption, compression, or both of PPP payloads from PPP. For PPTP connections, EAP-Transport Layer Security (EAP-TLS), MS-CHAP, or MS-CHAP v2 must be used for the PPP payloads to be encrypted using Microsoft Point-to-Point Encryption (MPPE).

上面这段引用很好的诠释了标题，即PPTP直接使用了很大一部分属于PPP的东西，比如加密、压缩等等。

#### PPTP Control Connection
PPTP毕竟不是PPP那般简单，它最基础的工作就在于它得维护一个隧道，这就是PPTP Control Connection去协商的了，具体的过程参考 [RFC 2637][1]（我怎么没找到要协商的参数囧）。

![PPTP Control Connection Packet](http://i.technet.microsoft.com/dynimg/IC196814.gif)

#### PPTP Data Tunneling
这是在使用PPTP Control Connection建立起连接后用来传送数据的，数据包格式如下：

![Tunneled PPTP Data](http://i.technet.microsoft.com/dynimg/IC196815.gif)

#### PPTP VPN 连接过程
我打算以Windows的PPTP VPN连接的建立过程作为参照，也就是网络连接那，点击一个PPTP VPN，然后输入用户名密码，连接的那个过程，通过wireshark辅助抓包来分析分析。我尽量讲的细致，因为我自己在去分析的时候遇到了好多自己以前都没有考虑过的问题，比如PPP Authentication，PPP Configuration之类很多的地方，这些都很重要，因为PPTP VPN直接就是继承自PPP，不理解那些根本没法继续较细地分析。

这个问题是链路层的协议问题，与这儿关系不大，先抛开，下面开始描述整个连接过程：

 - Pharse 1. 确定VPN Server可达，且支持PPTP
创建一个TCP连接，请求连接VPN Server的1723端口（PPTP的端口），三次握手，失败就Over，成功进入下一步。
 - Pharse 2. PPTP Control Connection
PPTP Control有着一系列的Message，需要依次确认，其中很关键的步骤为Set-Link-Info，这个步骤需要协商一系列的参数，如身份验证协议等等。但正如之前提及的，PPTP使用的这些实际上是PPP的，所以这个过程和PPP的连接过程类似，单处放于Pharse 3。
 - Pharse 3. PPP Configuration
这个其实是属于Set-Link-Info中的一步，本质上就是PPP Link Negotiation with LCP，这个过程大致就是设置一系列PPP的参数，比如说用什么协议来进行身份验证，乃至加密协议等等。参考文章中有较为详细的过程。

整个连接过程执行完后，一系列的参数也就大概协商完毕了，接下来讲讲传输数据的过程。

#### PPTP VPN Data Transfer Process
数据包的格式在PPTP Data Tunneling那给出过，现在按照那个格式，走一遍封装过程，以下建立在PPTP VPN连接已建立的基础上：

发送方：

1. PPTP在第二层收到一个IP数据包，它使用建立过程时协商的参数对IP包进行加密等处理，得到Encrypted PPP Payload，然后加上PPP Header，构成PPP packet。
2. 添加上GRE Header，GRE Header中的协议类型为PPP (0x880b)，构成GRE packet，然后转交给TCP/IP栈。
3. TCP/IP栈根据机器的IP地址，VPN Server的IP地址，把GRE packet当成payload后，新增一个IP Header，IP Header的协议类型为GRE (47)。至此，新的IP packet生成完毕，交由链路层往外发。
4. 链路层加上头和尾构成帧，外发。

接收方：

1. 拿到一个在发送方第三步结束后生成的IP packet，发现IP Header中协议为GRE，所以内部是个GRE packet。
2. 处理GRE Packet，发现GRE Header的协议是PPP，所以内部是个PPP packet。
3. PPP反操作，拿到内部的IP包，重新分发出去，往后该包和正常路由没啥区别。

### 云梯VPN区分设备
回归到一开始的问题，可以发现，整个过程中有着不少的地方能用来让VPN Server限制一个账号密码的同时使用设备数，下面是我的一些猜想，可能实际中并不会用到。

1. 在PPTP VPN登录的时候是需要验证用户名和密码的，或许这个时候Server就可以认为有一台设备登录了。
2. 非NAT网络下，IP进行区分。
3. NAT网络下，GRE Header中有一个字段将会替换成Port，这个可以区分。

2和3我并不是很确定，因为有些问题我还没搞清楚，有空的话研究一下，下一篇讲吧。

### Problems
上面描述的过程中，有很多细节都没有具体的讲，尤其是关于PPP的加密之类的，原因是个人也没了解过链路层的协议，对这方面也很晕，打算接下来要补补，下面有一些遗留的问题，可能很蠢但是还是得解决呀，先把工作搞定囧。

1. 我们平常在连接Internet的时候，总会有输入账号密码进行身份验证的环节，验证的环节究竟做了些什么？验证过后，协议又是如何保证往后的数据包（或许该是帧）是经过验证的呢？？
2. 一台PPTP VPN Server是可以服务于多台机器的，那么，在接收的第三个步骤拿到的PPP包，服务器是如何知道该用哪个密钥或什么参数去反操作这个包（每个用户怎么可能都协商出相同的参数呢！）？


### 总结
微软TechNet的科普文业界良心，Reference值得一看！

###References
1. [RFC 2637][1]
2. [PPP Connection Process][2]
3. [How VPN Works: Virtual Private Network (VPN)][3]
4. [PPP Link Negotiation with LCP][4]


[1]:  http://tools.ietf.org/html/rfc2637
[2]:  http://technet.microsoft.com/en-us/library/cc958006.aspx
[3]:  http://technet.microsoft.com/zh-cn/library/cc779919(v=ws.10).aspx
[4]:  http://technet.microsoft.com/en-us/library/cc957992.aspx
