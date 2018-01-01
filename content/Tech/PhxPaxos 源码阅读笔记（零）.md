Title: PhxPaxos 源码阅读笔记（零）  
Tags: PhxPaxos, 分布式, 一致性算法  
Date: 2017-07-28 20:20:00  


## 前言
其实之前就很想阅读 PhxPaxos 的源码来加深一下自己对 Paxos 的理解，但因为中途出差一个月加上前前后后的相关准备就搁置了，对于 Paxos 的理解一直停留在纸面上。最近阿里的 X-Paxos 宣传的很火，而自己也稍微闲了一些，就准备把阅读源码这个坑给填了。

PhxPaxos 的整体代码量不是很大，注释虽然不多，但是可读性还是非常高的，配合着那些日志代码以及官方博客中的模型介绍，基本上可以很容易地理解它的大部分内容。

利用零零碎碎的晚上休息时间，大概用了快一周把代码读完了，就想着反正自己从中也学到了不少内容，干脆写一个系列的阅读笔记吧。这是我第一次尝试写一个系列，希望能够写的稍微有点条理吧，这篇博客算是挖坑了。不过最近依旧比较忙，尽可能保持比较快的速度更新吧。

## 前置内容
我自己并不是一上来就试图通过阅读 PhxPaxos 来理解 Paxos 的，所以肯定是必须有前置内容的，希望对本系列感兴趣的读者能够先看完下面这些相关的内容（如果后续某篇文章与前置内容无关的话，我会在文章开头标注）。

PhxPaxos 作者之一对于 Paxos 的介绍，至少读完前两篇：

1. [Paxos理论介绍(1): 朴素Paxos算法理论推导与证明][1]
2. [Paxos理论介绍(2): Multi-Paxos与Leader][2]
3. [Paxos理论介绍(3): Master选举][3]
4. [Paxos理论介绍(4): 动态成员变更][4]

PhxPaxos 架构相关，必读：

1. [微信团队对 PhxPaxos 的介绍][5]

PhxPaxos 源码阅读系列（@chenneal），建议配合源码食用：

1. [一：走马观花][6]
2. [二：粮草先行][7]
3. [三：粉墨登场][8]
4. [四：各个击破][9]
5. [五：暗度陈仓][10]
6. [六：完结篇][11]

## 本系列主要内容
前置内容里也提到了 chenneal 写的源码阅读系列，我个人觉得他的系列对 PhxPaxos 的核心算法部分有了很好的解读了，如果读者是对这部分感兴趣的话，建议直接去阅读。

这个系列，我将尽量把整个PhxPaxos 中的各部分都写写，包括：

- 网络 I/O 模型
- 状态机
- 存储层
- 核心算法
- Checkpoint
- Maybe more...

后面如果有空的话可能会自己基于 PhxPaxos 实现一些示例，也会贴上来。因为目前 PhxPaxos 给出的三个示例中都没有实现 Checkpoint 相关的东西（也可能是我看漏了），只能够自己实现下加深理解。

坑大概就挖到这里，慢慢填了。

[1]: https://zhuanlan.zhihu.com/p/21438357
[2]: https://zhuanlan.zhihu.com/p/21466932
[3]: https://zhuanlan.zhihu.com/p/21540239
[4]: https://zhuanlan.zhihu.com/p/22148265
[5]: https://mp.weixin.qq.com/s?__biz=MzI4NDMyNTU2Mw==&mid=2247483695&idx=1&sn=91ea422913fc62579e020e941d1d059e#rd
[6]: http://chenneal.github.io/2017/03/16/phxpaxos%E6%BA%90%E7%A0%81%E9%98%85%E8%AF%BB%E4%B9%8B%E4%B8%80%EF%BC%9A%E8%B5%B0%E9%A9%AC%E8%A7%82%E8%8A%B1/
[7]: http://chenneal.github.io/2017/03/18/phxpaxos%E6%BA%90%E7%A0%81%E9%98%85%E8%AF%BB%E4%B9%8B%E4%BA%8C%EF%BC%9A%E7%B2%AE%E8%8D%89%E5%85%88%E8%A1%8C/
[8]: http://chenneal.github.io/2017/03/26/phxpaxos%E6%BA%90%E7%A0%81%E9%98%85%E8%AF%BB%E4%B9%8B%E4%B8%89%EF%BC%9A%E7%B2%89%E5%A2%A8%E7%99%BB%E5%9C%BA/
[9]: http://chenneal.github.io/2017/03/30/phxpaxos%E6%BA%90%E7%A0%81%E9%98%85%E8%AF%BB%E4%B9%8B%E5%9B%9B%EF%BC%9A%E5%90%84%E4%B8%AA%E5%87%BB%E7%A0%B4/
[10]: http://chenneal.github.io/2017/04/04/phxpaxos%E6%BA%90%E7%A0%81%E9%98%85%E8%AF%BB%E4%B9%8B%E4%BA%94%EF%BC%9A%E6%9A%97%E5%BA%A6%E9%99%88%E4%BB%93/
[11]: http://chenneal.github.io/2017/04/05/phxpaxos%E6%BA%90%E7%A0%81%E9%98%85%E8%AF%BB%E4%B9%8B%E5%85%AD%EF%BC%9A%E5%AE%8C%E7%BB%93%E7%AF%87/
