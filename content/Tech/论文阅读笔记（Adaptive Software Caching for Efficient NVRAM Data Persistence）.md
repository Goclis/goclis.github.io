Title: 论文阅读笔记（Adaptive Software Caching for Efficient NVRAM Data Persistence）  
Date: 2018-05-02  
Tags: NVRAM


[TOC]

原文：Pengcheng Li et al. Adaptive Software Caching for Efficient NVRAM Data Persistence. IPDPS, 2017.

## 背景
### NVRAM（Non-volatile Random Access Memory）
顾名思义，NVRAM 和 SDD/HDD 等存储一样，都拥有断电后保留数据的能力，同时和目前普遍使用的 DRAM 一样，采用 [DIMM][1] 接入计算机中，且按照字节寻址（byte-addressing）。

![Intel memory to storage](https://ws3.sinaimg.cn/large/006tKfTcgy1fqwslj3kvlj30kz0bpjtc.jpg)

上图来自 Intel，其中的 3D XPoint 就是 Intel 的 NVRAM 实现。相较于 DRAM，NVRAM 拥有更高的密度（10x DRAM），从而可以更便宜且拥有更大的空间，但是速度更慢，具体有多慢是取决于实现的，从 Intel 的宣传来看，至少带来 10 倍于 DRAM 的时延。

尽管 NVRAM 可能要到今年下半年才会有可用的硬件出现，但如何去应用 NVRAM 的相关研究已经开展。

### 持久化语义（Durability Semantics）
对于此处的持久化语义，我理解的是对程序状态的持久化，即程序可以在重启后恢复上一次的运行状态并继续运行。

![Durability semantic](https://ws4.sinaimg.cn/large/006tKfTcgy1fqwtl3nvwvj30z90lxdme.jpg)

这里借助一张其他文章的 [PPT][3] 来简化理解。实际上，在 NVRAM 出现之前，持久化语义就可以通过磁盘等存储介质实现，只是内存和磁盘之间的数据访问方式的不同导致我们需要分别维护两种格式，从而程序需要增加序列化和反序列化代码，这带来了一些性能问题。从理论上来看， NVRAM 作为内存的一种，使得我们不再需要维护两种格式，直接将需要持久化的数据放到 NVRAM 即可，但实际上仍存在问题。

影响 NVRAM 为程序提供持久化语义的原因之一是当前计算机体系结构中的临时存储（transient memories），比如 CPU 缓存。我们都知道，在程序执行的任何时候都有可能存在这样一种情况：数据已经在 CPU 缓存中更新，但是尚未写回（flush, write-back）内存中。如果程序在这种情况下发生故障，NVRAM 中的状态将变得与实际情况不一致，从而影响了程序重启时的恢复。

因此，想要利用 NVRAM 来实现持久化语义，还需要一些额外的工作，解决的思路是在合适的时机，通过 CPU 提供的指令（比如 x86 的 clflush），主动地将缓存中的内容写回 NVRAM。以下是两个最基本的写回策略：

- eager: 在每次进行写内存操作后都执行写回，相当于同步方式。
- lazy: 记录下被修改数据的地址，然后集中写回，相当于异步方式。

同步方式会导致大量的写回指令需要执行，这会严重影响性能。异步方式需要在某个时机集中写回，如果写回的数据量过大，则可能造成过长的 CPU 停滞时间（CPU stall time），可能会延长程序的执行时间。下图是对 SPLASH2 测试集中的程序进行同步方式改进后的性能对比，从中可以明显看到，同步方式严重地降低了程序的性能。

![SPLASH2 benchmark](https://ws2.sinaimg.cn/large/006tKfTcgy1fqwxk3f81sj30e004xt9z.jpg)

由于同步方式的糟糕性能，目前的方案大多会采用异步方式，不同的是写回时机的控制。

### Atlas
本文的所有工作是基于已有的 [Atlas 系统][2]实现的，所以这里需要简要介绍一下。

#### 编程模型及 FASE
Atlas 通过扩展编程模型，为基于锁的多线程程序（Lock-based Multithreaded Programs）提供持久化语义（Durability Semantics），从而实现在发生故障导致程序崩溃时，程序可以在重启过程中自动地恢复状态。

显然，Atlas 对编程模型的扩展对程序代码提出了一些要求。在 Atlas 的编程模型中，程序的数据结构由一组不变量组成，它们需要处于一致状态，个人感觉这里的一致状态指的就是 CPU 缓存和 NVRAM 之间的一致。程序可以对数据结构进行修改，但是修改可能会违反不变量，因此，Atlas 要求程序将违反不变量的代码都需要被组织起来，以 FASE（failure-atomic section）进行表示，一个程序可以拥有多个 FASE。

Atlas 对 FASE 以外的代码的限制使得当程序崩溃发生在 FASE 之外时，程序重启后 NVRAM 中的状态即上一次的运行状态，可以继续运行。而当崩溃发生在 FASE 中时，Atlas 保证**在 FASE 中所有更新，要么全部应用，要么全部不应用**，这里有点类似于事务，但不同的是，Atlas 对此事务的 commit/abort 的确认发生在程序重启时，Atlas 会在重启的最开始检查 NVRAM 中数据的状态并进行恢复。

再来说说 FASE。之前说过，Atlas 是针对于基于锁的多线程程序的，作者认为，在这类程序中，违反数据结构的一致状态（我觉得可能就是对数据结构的修改，读大部分不会违反）的代码一般都发生在 lock/unlock 之间的临界区，因此，Atlas 在实现中通过 lock/unlock 操作来标识 FASE。以下是 FASE 的形式化定义。

给定一个单线程的动态执行的指令序列 $A_1A_2...A_n$，如果 $A_i...A_j$ 这样一个执行范围满足以下要求，则被称为 FASE：

- $A_i$ 之前的所有指令都是线程一致的，此处即之前的执行过程中，线程没有获取任何锁。
- $A_j$ 之后的所有指令也是线程一致的。
- $A_i$ 和 $A_j$ 之间的所有指令执行过程中，均不是线程一致的，即整个执行过程中都持有锁。

需要注意的是，对于嵌套临界区的情况，Atlas 忽略了内部的临界区，将 FASE 的区域扩展为最外层的临界区。下图虽然描述的是 Outermost Critical Section，但实质是和 Atlas 的 FASE 一样的，可以辅助一下理解。

![OCS](https://ws2.sinaimg.cn/large/006tKfTcgy1fqy5xo7mtrj30s40gqabi.jpg)

个人感觉，Atlas 对于程序的限制还是比较严格的，但是它利用锁来构建 FASE 一定程度上还是有道理的。这里简单地提一下 Atlas 的实现，对于这类提供恢复能力的设计，往往是基于日志的，Atlas 也不例外，它通过在 FASE 中插入一些额外代码来记录日志，重启的过程中依赖于日志。关于日志本身的持久化问题，Atlas 中日志是存储于 NVRAM 的，并采用了同步方式来保证它在发生崩溃时的一致性。

#### 软缓存（Software Cache）
这里的软缓存区别于 CPU 缓存，是 Atlas 在运行时构建的，具体实现时是构建于 DRAM 之中的，它的存在是为了实现异步方式的写回，从而减少执行写回指令的数量。根据 Atlas 编程模型的要求，异步写回这种会导致不一致的操作只会发生在 FASE 区中，所以软缓存的实际跟踪就是在进入 FASE 时开始的，它在代码执行进入 FASE 时初始化，以表的形式记录每一个写入操作。在两种情况下会发生软缓存的写回，一种情况是表满了，它将选择（实现貌似是随机选择）一个记录，将记录写回，然后插入新的记录；另一种情况是在 FASE 的最后，它在此处将表中的所有记录写回 NVRAM。

![software cache](https://ws2.sinaimg.cn/large/006tKfTcgy1fqy83l073dj30po09wjw4.jpg)

上图是一张软缓存的示意图，每个线程有独立的软缓存，图中展示了很常见的一个缓存置换过程。图中的缓存大小为 2，当新的 0x600 被写入时，需要向软缓存中插入，但由于大小已满，缓存中的 0x400 被弹出并要求 CPU 缓存执行了写回操作。

按照我的理解，软缓存的写回一定配合了一些日志记录的过程，从而在故障发生于 FASE 内时，Atlas 能够重启并根据日志进行恢复。

### 缓存大小和缓存命中率
显然，随着缓存大小的增加，缓存的命中率（Hit Ratio，HR）会有所提高，同时未命中率（Miss Ratio, MR）也会下降。但是，更大的缓存大小意味着在 FASE 的结束阶段需要写回的数据量越大，这会导致更长的 CPU 停滞时间。因此，针对每个程序选择各自合理的缓存大小是有意义的。

![cache size and miss ratio](https://ws3.sinaimg.cn/large/006tKfTcgy1fqwzl7qaelj30dz0a1jtf.jpg)

上图是针对 SPLASH2 测试集中的 water-spatial 的测试，随着缓存大小的增加，MR 在不断地下降，但是从图中可以看到，当缓存大小为 23 时，能够带来更好的一个收益。

图中的曲线被称为 miss ratio curve（MRC）。显然，不同的程序拥有不同的 MRC，从而它们最佳的缓存大小也会有所差异。本文将描述一个新的理论来构建 MRC，从而帮助基于 Atlas 的程序选择最佳的缓存大小。

## 本文工作（Optimized Adaptive Write Caching）
本文的主要工作是对 Atlas 的软缓存进行改进。从先前的介绍中可以看到，Atlas 的软缓存采用的是全映射随机置换和固定大小的方式实现的，这样的一种情况难以适应不同程序的实际情况。因此，本文提出了基于 LRU 的可变大小的软缓存实现。

### 写缓存（Write Caching）
一般来说，缓存是为了快速读而构建的，但是在本文的环境下，缓存的构建是为了记录程序的写回操作，以减少程序整体执行的写回指令数量为目标的，因此也被称为**写缓存**。

在写缓存中，当一个写入操作发生时，如果它的目标地址已经在缓存中时，被称之为**复用（reuse）**，显然，在我们执行集中写回前，每一次复用都意味着相比同步方式少执行了一次写回指令。因此，**最大化写缓存的性能等价于最大化写缓存中复用的数量**。

对复用的优化可以使用**访问局部性（access locality）**和**时间段局部性（timescale locality）**两类局部性理论进行分析。但是由于前者开销过大（尤其针对在线的 CPU 缓存计算），现在的研究普遍采用后者进行，本文同样基于后者构建模型，从而达到和它相同的效率。

### 基于复用的时间段局部性：复用局部性
本文将引入复用对时间段局部性进行扩展，并通过理论推导得出复用与缓存命中率之间的关系，依此作为构建 MRC 的基础，帮助程序选择最佳的缓存大小。

我们以一个数据访问（写入）的序列来表示一个执行过程，每个数据访问都有对应的逻辑时间来决定先后顺序。**时间窗口**被定义了两个数据访问和它们之间的数据访问构成的序列，其中数据访问的数量即为时间窗口的长度。时间窗口的**复用局部性（Reuse locality）**通过它包含的复用个数来衡量。

为进一步分析，定义两个概念：

- 复用间隔（Reuse interval）：针对一个相同的数据，本次访问和下次访问之间的数据访问记录数量。
- 窗口内复用数（Intra-window reuse）：给定时间窗口内的复用数量。

显然，不同的窗口有不同的复用数量，定义 $reuse(k)$ 为所有长度为 k 的窗口的窗口内复用数的平均值，长度 k 被称为时间段参数。在给定一个序列的情况下，$reuse(k)$ 的值的唯一确定的，以访问序列「abb」为例，长度为 2 的时间窗口有两个，窗口内复用数分别为 0 和 1，所有 $reuse(2)=1/2$。

![Eq 1](https://ws3.sinaimg.cn/large/006tKfTcgy1fqx164m8kqj30ro064wg2.jpg)

公式 1 表达的是 $reuse(k)$ 的计算可以由统计所有长度为 k 的窗口的窗口内复用数的平均值转换为针对每个长度小于 k 的复用，统计包含它们的窗口数量的平均值（这个很好理解，一个窗口包含两个复用，那这两个复用都分别被至少一个窗口包含）。为此，我们可以根据复用的起始，将情况分为四类，它们各自的计算方法如下图所示。

![Figure 3](https://ws1.sinaimg.cn/large/006tKfTcgy1fqx1ajnafkj30sy0fmwi9.jpg)

> Q: 前三个都比较容易得到，第四个感觉有点怪，为什么会和 s、e 完全不关呢？

通过汇总四种情况，得到计算 $reuse(k)$ 的公式 2（其中，$I$ 是一个条件判别函数，如果满足条件则值为 1，否则值为 0）：

![Eq 2](https://ws1.sinaimg.cn/large/006tKfTcgy1fqx1byi703j30rm052t9p.jpg)

关于公式 2 的计算，作者基于自己先前的 all-window liveliness 的[工作][4]，能够在线性时间 O(r) 内求解所有时间段 k 的 $reuse(k)$。这里我没有去细看这篇参考文献，就不多描述了。

现在我们把时间窗口和缓存关联一下。假设有一个 LRU 缓存，在任意一个时刻，它包含了最近的 k 个访问关联的数据，而 $reuse(k)$ 正好表示了这 k 个数据访问中复用的个数，因此，从平均意义上来说，缓存中包含了 $k-reuse(k)$ 个不同的数据。**考虑下一个访问，如果它是一个复用，也就意味着缓存命中，否则就是个 miss**。而下一个访问是一个复用的概率：$reuse'(k)=reuse(k+1)-reuse(k)$。因此，缓存大小为 $k-reuse(k)$ 时，下一个数据的缓存命中率即为：

![Eq 3](https://ws1.sinaimg.cn/large/006tKfTcgy1fqx1wxyit5j30p402qmxp.jpg)

其中 $c=k-reuse(k)$，即缓存的大小。

> Q: 虽然能够理解 reuse'(k) 和 hr(c) 的关联。但是 reuse'(k) 表示的是 reuse(k) 对 k 的导数，而 reuse(k) 应该是个关于 k 的离散函数，按道理应该无法求导吧。即使按照差分法计算，貌似也没法如此直接的得出此结果。
> 但 reuse(k) 和 hr(c) 之间的关联从直觉上还是比较容易理解的。

在原文中还有一部分内容说明了本文此处的推导和现有理论的关联，通过该理论可以转换成本文推导得出的结果，并且该理论的正确性也证明了本文推导的正确性，这里不再赘述。

至此，我们得到了此模型下缓存命中率的计算方法，随后便可利用此方法，根据程序中的数据访问的情况，计算得到它们各自的最佳缓存大小。

### Adaptive Caching 实现
- The Cache: 每个线程一个 LRU 软缓存，软缓存通过 hashmap 和双链表构建，所有操作均为 O(1) 时间复杂度。
- MRC 分析：在线方法通过采样来得到计算 MRC 的数据，采集程序最开始的 64M 的写入操作（作者发现这样的一次采样已经足够），然后计算 MRC 进行调整。离线方法则通过采集整个程序执行过程中的所有写入操作，选出针对此程序的最佳缓存大小。在本文实现中，针对每个线程都进行了独立额的 MRC 计算，未来工作考虑通过分组来降低多线程情况下的开销，即按照相似程度对线程分组，一个组内的线程只计算一个 MRC。
- 缓存大小优化：对于在线方法，将缓存大小的初始值设为 8，为了避免缓存过大导致的 FASE 结束阶段的长时间 CPU 停滞，实现将最大缓存大小限制为 50。在程序初始阶段，使用默认大小，在采样结束得到 MRC 后，实现会计算 MRC 曲线中的斜率变化点，取发生斜率变化的缓存大小中的最大值作为最佳缓存大小。
- 编译器支持：显然，本文对于 FASE 以及软缓存的修改都需要嵌入到目标程序代码中，所以基于 LLVM 实现了相应编译器。

## 实验评估
### 实验方法
NVRAM 预计 2018 年下半年才会有真正的硬件出现，所以本文的实验使用的是仿真系统。为了比较效果，本文划分了以下 6 组比较：

- SC: 本文工作的在线版本，即先采样、计算 MRC 后再调整缓存大小。
- SC-offline: 本文工作的离线版本。
- AT (Atlas approach): Atlas 的原始实现。
- ER (eager approach): 同步方式。
- LA (lazy approach): 异步方式，相较于 AT，它的软缓存没有大小限制，在 FASE 的最后集中写回。
- BEST: 程序原始状态，没有提供缓存和插入主动的写回指令，作为最佳对照组。

### Case study: MDB
Memory-mapped database (MDB) 是一个针对读优化、基于 B+ 树的键值数据存储，它采用 MVCC 实现事务，从而读操作可以独立于写操作（因为它们读快照），而写仍旧需要独占锁来更新旧版本的数据。针对 MDB 的测试使用了它自己提供的 Mtest 工作负载，该工作负载中总共包含 65558123 次持久化内存存储（persistent memory stores）、FASE 的数量为 100516 个，每个平均有 652 次持久化内存存储。

![Table 2](https://ws1.sinaimg.cn/large/006tKfTcgy1fqx2vnygbfj30ry07076z.jpg)

上图为测试结果，其中没有 LA 的数据（因为实在太慢）。从速度上来看，BEST > SC-o > SC > AT > ER，而主要的性能提升在于写回指令的减少。原始的 MDB 中拥有 66 millions 次写入，Atlas 减少至 20 millions 次，SC 进一步减少至 7.4 millions，这也导致了它们之间的性能差异。

由于写回数量的减少，SC 降低了 CPU 缓存的 miss ratio，从 Atlas 的 83.21% 降低到 68.50%。SC 和 SC-o 之间的比较结果说明了运行期的 MRC 计算的代价还可以接受，只占了 10% 的运行时间（0.45s），相比于整体对 Atlas 的提升（4s），cost-effective。

### The Write-Back Reduction
测试包含两组程序：

- SPLASH2: 测试集中的程序的规模各异，非常适合用于实验，测试中将所有程序的堆分配程度都修改为使用 NVRAM 的栈分配。
- Micro benchmarks: 自行编写的测试程序，代表一些常见的数据结构。
    - persistent-array: 简单的单 FASE 程序，两层循环，内层 400 外层 2500，每次内层循环都将内层下标作为值写入对应下标的数组。此程序用于测试缓存写回的代价和缓存大小的效果，测试机的缓存块大小为 64 字节（16 个 int），所以内层循环会访问 25 到 26 个块（取决于是否对齐）。Atlas 的缓存大小为 8，减少了 15/16 的写回，所以写回率为 0.0625。但是本文的 SC 可以获取到最佳的缓存大小（26），从而可以将写回率降低至 0.00003。
    - queue: 多线程队列，非常常见的并发数据结构。
    - hash: 单线程哈希表。
    - singly linked-list: 多线程单链表。

各个测试程序的规模和结果如下表所示，表中的 ER 到 SC 列表示四个情况的写回率，其中 ER 因为是每次都写回，所以作为基准 1。另外，AT/SC 和 SC/LA 用于直观的比较本文和原始 Atlas 的效果以及本文和最少写回情况（LA）相比的效果。

![Table 3](https://ws1.sinaimg.cn/large/006tKfTcgy1fqx347obiuj30sp0aajyl.jpg)

从结果中可见，尽管程序规模各不相同，但本文的 SC 总能够取得比原始 Atlas（AT）更好的效果（相同的情况可能是因为 Atlas 默认的缓存大小即可满足要求）。

### The Running Time
进一步地，实验选择了测试集中的一些应用对执行时间进行了比较，结果见下图，以 ER 的执行时间作为基准。

![Figure 4](https://ws1.sinaimg.cn/large/006tKfTcgy1fqx49rcholj30ei0bmtcu.jpg)

从结果中可以发现：

- SC 的结果都优于 AT，这主要得益于动态确定的缓存大小带来的写回数量的减少。对于 persistent-array 这类提升不明显的程序，这是因为大部分的写回操作和计算发生了重叠，所以 SC 能够带来的提升不明显。
- SC-offline 比 SC 更快，有两方面的原因。一方面是 MRC 的计算代价，另一方面是在采样 MRC 的期间，在线版本的 SC 的缓存大小为 8，这期间相比 SC-offline 产生了更多的写回。

> Q: 这里的写回操作和计算重叠是指的什么？写回指令应该会占据其他指令的执行时间吧？

### Parallel Performance
进一步地，实验给测试程序增加了不同的线程数，对并行性能进行了评估，实验结果如下图所示。

![Figure 5](https://ws4.sinaimg.cn/large/006tKfTcgy1fqx4ltvsdgj30sq09vth7.jpg)

从结果来看：

- 85%（36/42）的情况下，SC 优于 AT。
- 当线程数在 1 到 8 时，SC 均优于 AT。

我们将本文的 adaptive caching 的额外代价分为两部分进行分析：指令的额外代价和缓存冲突。

![Figure 6](https://ws2.sinaimg.cn/large/006tKfTcgy1fqx4rleojxj30dx08odhd.jpg)

上图是 7 个程序随着线程数增加时的执行效率下降情况，纵轴是 SC 相对于 BEST 的下降情况。从图中可以看到，当线程数增加时，下降情况基本上都是在缓解或维持稳定（除了 barnes 在最后的时候增长了），并没有随之带来更多的额外代价。

指令的额外代价部分来源于 MRC 的分析，但是从本节最开始的图中可知，SC-offline 比 AT 好的情况为 90%（40/42），相较于 SC 并没有很大的优势，可以推断 MRC 的分析不会带来过多的额外代价。

缓存冲突的代价指的是 CPU 缓存（此处指 L1 缓存）中的冲突，当线程增多时，单个核心上的线程数可能会增多，从而 L1 缓存发生冲突的概率也随之增大，这个也是 SC 在 fmm 和 water-spatial 这两个用例的多线程情况下不如 AT 的原因。为此，我们进一步分析 water-spatial 在各种线程数情况下的缓存情况，如下图所示。

![Table IV](https://ws1.sinaimg.cn/large/006tKfTcgy1fqx53elqscj30dx07ytba.jpg)

从表中可以看到，当线程增多时，即使在 BEST 情况下，L1 缓存的 miss ratio 也非常的高，即使此情况下 SC 相对于 AT 带来了更低的 flush ratio 和 miss ratio，但它增多了约 0.3 billions 的指令，这加剧了缓存的冲突情况，最终**导致 flush ratio 和 miss ratio 带来的好处无法抵消此时的缓存冲突的代价**。其他的一些随着线程增加而变慢的程序也都是出于相似的原因。

### MRC Analysis Precision and Overhead
![Figure 7](https://ws1.sinaimg.cn/large/006tKfTcgy1fqx58ycdfoj30s60qcgts.jpg)

上图是在线和离线得到的 MRC 的对比，从图中可以看到，虽然在线情况下采样得到的 MRC 无法完好拟合真实的 MRC，但它能够很好地表达出真实 MRC 的趋势，从而得到正确的最佳缓存大小。

> Note: 图中的 liveliness 应该就是作者先前的工作，本文也是利用此工作来计算 reuse(k) 从而得到 MRC 的。

![Figure 8](https://ws3.sinaimg.cn/large/006tKfTcgy1fqx59cvohqj30rq0hetl1.jpg)

上图是线程是为 1 和 8 时的 MRC 的计算分析时间占整体执行时间的比例，可以看到，额外代价能够控制在 10% 以内，相较于 SC 能够提供的效果，还是非常值得的。

## 总结
> We have developed a software cache solution minimizing the cache flush overhead of NVRAM data persistence, using a reuse-based locality theory and a linear time algorithm for efficient online analysis to select the best cache size. We extensively evaluated the effect of write caching and found it efficient and effective, reducing the number of cache line flushes by 12× and improves the running time by 2.1× for both sequential and parallel applications.


[1]: https://www.wikiwand.com/en/DIMM
[2]: http://www.hpl.hp.com/techreports/2013/HPL-2013-78.pdf
[3]: https://www.usenix.org/sites/default/files/conference/protected-files/chakrabarti_hotpar13_slides.pdf
[4]: http://dl.acm.org/citation.cfm?id=2602988.2602997
