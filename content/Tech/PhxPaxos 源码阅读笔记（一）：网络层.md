Title: PhxPaxos 源码阅读笔记（一）：网络层  
Tags: PhxPaxos  
Date: 2017-08-30 21:59:30  
Modified: 2017-08-31 16:19:20  


[TOC]

**本篇不需要前置内容。**

我在看源码的时候，如果对整体架构上有一些了解的话，会尽可能地以自底向上的顺序去看。PhxPaxos 因为之前阅读过相关的文章，所以对于架构也比较清楚，于是也优先去阅读和消息交换相关的代码。毕竟是一个分布式算法的实现，起码现阶段是逃不开网络的，所以先把它看完也有利于后续忘掉消息交换细节专心理解算法。

## 接口
对于网络层，PhxPaxos 为使用者留了扩展的余地，在 include/phxpaxos/network.h 中定义了网络层所需要提供的一些接口，这里简单的贴一下：

```cpp
class NetWork
{
public:
    NetWork();
    virtual ~NetWork() {}

    //Network must not send/recieve any message before paxoslib called this funtion.
    virtual void RunNetWork() = 0;

    //If paxoslib call this function, network need to stop receive any message.
    virtual void StopNetWork() = 0;

    virtual int SendMessageTCP(const std::string & sIp, const int iPort, const std::string & sMessage) = 0;

    virtual int SendMessageUDP(const std::string & sIp, const int iPort, const std::string & sMessage) = 0;

    //When receive a message, call this funtion.
    //This funtion is async, just enqueue an return.
    int OnReceiveMessage(const char * pcMessage, const int iMessageLen);

private:
    friend class Node;
    Node * m_poNode;
};
```

除了启动和停止的接口，另外三个接口你就当做：

- SendMessageTCP：保证可靠的消息发送接口。
- SendMessageUDP：不保证可靠的消息发送接口。
- OnReceiveMessage：收到了消息的回调接口。

对于 OnReceiveMessage 接口，默认实现是调用 Node 成员的 OnReceiveMessage 接口进行消息传递。如果用户自行实现了网络层的话，利用 Options::poNetwork 去传递自定义的网络层对象即可。

为了简化用户使用，PhxPaxos 提供了默认的网络层实现，和这部分相关的代码基本都在 src/communicate 下，下图为相关的类图，下面将依次展开来讲。

![](https://ws2.sinaimg.cn/large/006tKfTcly1fj249s86zsj317c0igjvj.jpg)

## 默认实现：DFNetwork
该类定义在 dfnetwork.h 和 dfnetwork.cpp 中，是一个默认的网络层实现，不知道这个 DF 是不是 default 的意思。。

整个类中比较关键的是它的三个成员变量，所有消息的发送和接收都是交由它们处理：

```cpp
class DFNetwork : public Network
{
public:
    ...
private:
    UDPRecv m_oUDPRecv;
    UDPSend m_oUDPSend;
    TcpIOThread m_oTcpIOThread;
};
```

通过名字就可以很直观地理解，前两个负责 UDP 的接收和发送，第三个负责 TCP 相关的操作。

### UDP
实现很简单，主要就是对 Socket 的操作进行了封装，设置一些相关的 Socket 选项，比如 UDPRecv 的 SO\_REUSEADDR。

UDPRecv 和 UDPSend 都是独立的线程：

- 接收线程利用 poll 进行阻塞，调用 recvfrom 接收数据，然后利用保存在成员变量下的 DFNetwork 指针将收到的消息向上回调。
- 发送线程利用队列同步队列实现消息的异步发送，DFNetwork 利用 UDPSend::AddMessage 将消息拷贝到队列中，随后由发送线程取出消息进行发送。

实现过程中涉及的线程、锁、同步队列等系统相关的内容，大多基于 C++11 STL 封装或直接使用。如果个人有需要的话，完全可以拿出去单独使用。（哎，不能用 C++11 的项目实在有点惨。

### Event & EventLoop
在介绍 TCP 部分前，先讲一下 PhxPaxos 内部基于 epoll 封装的一些与事件循环相关的类。它们的用途之一就是为 DFNetwork 中的 TCP 部分服务。

如果用过 epoll 或者 libevent 的读者可能可以比较容易地理解 PhxPaxos 这块的设计。大致的流程就是把数据、通知这样的行为封装成 Event，然后交由 EventLoop 去执行。

在实现上，PhxPaxos 为 Event 基类定义了两个具体的子类：MessageEvent 和 Notify。其中前者对应于数据的读写任务，内部逻辑较复杂。后者的用途是提供一个唤醒调用事件循环线程的接口，基于管道和 EPOLLIN 事件实现，通过源码很容易理解。

关于 Event 的添加、移除和修改，因为基本上是封装 epoll 并记录一些上下文信息，出于篇幅，此处就忽略了。除了 Event 以外，EventLoop 还提供了设置定时器的接口，但这部分我们留到后头再去讲，此处暂时忽略。

EventLoop 类本身不提供任何的执行线程，需要由外部线程去调用 EventLoop::StartLoop 开始进行事件循环处理。这里结合代码稍微讲一下事件循环相关的逻辑：

```cpp
void EventLoop :: StartLoop()
{
    // 实际上和我们平时写 Thread::Run 的结构差不多，只是交由外部线程去调用而已。
    m_bIsEnd = false;
    while(true)
    {
        // BP 实际上是一个 PhxPaxos 提供的监控功能，为一些关键操作都提供了接口，
        // 出于简洁，往后的代码中将不再贴出这些内容。
        BP->GetNetworkBP()->TcpEpollLoop();

        // 处理定时器的超时。
        int iNextTimeout = 1000;
        DealwithTimeout(iNextTimeout);

        // 事件循环主逻辑。
        OneLoop(iNextTimeout);

        //deal with accept fds
        // 与 TCP 接受连接和数据相关的逻辑。
        if (m_poTcpAcceptor != nullptr)
        {
            m_poTcpAcceptor->CreateEvent();
        }
        // 与 TCP 数据发送相关的逻辑。
        if (m_poTcpClient != nullptr)
        {
            m_poTcpClient->DealWithWrite();
        }

        if (m_bIsEnd)
        {
            PLHead("TCP.EventLoop [END]");
            break;
        }
    }
}

void EventLoop :: OneLoop(const int iTimeoutMs)
{
    // 利用 epoll_wait 去等待时间响应，最后一个参数指定了超时（1 ms）。
    int n = epoll_wait(m_iEpollFd, m_EpollEvents, MAX_EVENTS, 1);
    if (n == -1)
    {
        if (errno != EINTR)
        {
            PLErr("epoll_wait fail, errno %d", errno);
            return;
        }
    }

    // 存在可处理的 epoll 事件，进行处理。
    for (int i = 0; i < n; i++)
    {
        int iFd = m_EpollEvents[i].data.fd;
        auto it = m_mapEvent.find(iFd);
        if (it == end(m_mapEvent))
        {
            continue;
        }

        // poEvent 是添加事件时加入的上下文对象。
        int iEvents = m_EpollEvents[i].events;
        Event * poEvent = it->second.m_poEvent;

        int ret = 0;
        if (iEvents & EPOLLERR)
        {
            OnError(iEvents, poEvent);
            continue;
        }
        
        try
        {
            // 缓冲区有数据，调用 OnRead，由事件对象处理。
            // 这里可能是数据到来，也可能是一个新的连接到来。
            if (iEvents & EPOLLIN)
            {
                ret = poEvent->OnRead();
            }

            // 缓冲区可写，调用 OnWrite，由事件对象处理。
            if (iEvents & EPOLLOUT)
            {
                ret = poEvent->OnWrite();
            }
        }
        catch (...)
        {
            ret = -1;
        }

        if (ret != 0)
        {
            OnError(iEvents, poEvent);
        }
    }
}
```

其中 EventLoop::StartLoop 中和 TCP 的发送和接收相关的逻辑，我们放到下一节。

### TCP
TCP 稍微比较复杂，因为 Network 对于 TCP 接口的要求也是以消息为单位的，所以在实现的时候需要对 TCP 的流模式进行一些相应的封装。

在类 TcpIOThread 中有 TcpRead 和 TcpWrite 两个成员变量，和 UDP 中提到的 UDPRecv 和 UDPSend 有些类似，它们也有着各自独立的线程，分别处理接收和发送的任务。

TcpWrite 和 TcpRead 的成员变量中都包含了一个 EventLoop 对象，为了使用 EventLoop 进行事件循环，它们都继承了共同的 Thread 父类，重写了 run 函数来调用 EventLoop::StartLoop，进入事件循环状态。

#### TcpWrite

可能是为了简化 TcpWrite 中的逻辑，TcpWrite 的成员变量中包括了一个额外的 TcpClient 对象，将所有的操作（其实也就一个 AddMessage）都委托给该类负责，TcpClient 使用 TcpWrite 内部的 EventLoop 对象来进行初始化，同时 TcpWrite 对象在构造时将 TcpClient 对象利用 EventLoop::SetTcpClient 这个接口注册到 EventLoop 中。

下面结合代码简述下 TcpClient 利用事件循环来发送数据的过程：

```cpp
int TcpClient :: AddMessage(const std::string & sIP, const int iPort, const std::string & sMessage)
{
    // 将发送消息的任务转换为一个 MessageEvent，GetEvent 是内部函数。
    MessageEvent * poEvent = GetEvent(sIP, iPort);
    if (poEvent == nullptr)
    {
        PLErr("no event created for this ip %s port %d", sIP.c_str(), iPort);
        return -1;
    }

    // 真正开始进行的发送任务入列。
    return poEvent->AddMessage(sMessage);
}

MessageEvent * TcpClient :: GetEvent(const std::string & sIP, const int iPort)
{
    // 根据消息的目标 IP 和端口号构建出一个 64 位的唯一事件 ID，从而保证每个目标（连接）
    // 拥有唯一一个与之对应的 MessageEvent 对象。
    uint32_t iIP = (uint32_t)inet_addr(sIP.c_str());
    uint64_t llNodeID = (((uint64_t)iIP) << 32) | iPort;

    std::lock_guard<std::mutex> oLockGuard(m_oMutex);

    auto it = m_mapEvent.find(llNodeID);
    if (it != end(m_mapEvent))
    {
        return it->second;
    }

    return CreateEvent(llNodeID, sIP, iPort);
}

MessageEvent * TcpClient :: CreateEvent(const uint64_t llNodeID, const std::string & sIP, const int iPort)
{
    // 创建 Socket 并连接目标，随后创建发送类型（MessageEventType_SEND）的 MessageEvent 对象。
    Socket oSocket;
    ...
    oSocket.connect(oAddr);
    
    MessageEvent * poEvent = new MessageEvent(MessageEventType_SEND, oSocket.detachSocketHandle(), 
            oAddr, m_poEventLoop, m_poNetWork);
    assert(poEvent != nullptr);

    m_mapEvent[llNodeID] = poEvent;
    m_vecEvent.push_back(poEvent);
    return poEvent;
}

int MessageEvent :: AddMessage(const std::string & sMessage)
{
    // 逻辑非常清楚：更新活动时间、检查队列状态、插入队列、尝试唤醒事件循环线程。
    m_llLastActiveTime = Time::GetSteadyClockMS();
    std::unique_lock<std::mutex> oLock(m_oMutex);

    if ((int)m_oInQueue.size() > TCP_QUEUE_MAXLEN)
    {
        return -2;
    }

    if (m_iQueueMemSize > MAX_QUEUE_MEM_SIZE)
    {
        return -2;
    }

    QueueData tData;
    tData.llEnqueueAbsTime = Time::GetSteadyClockMS();
    tData.psValue = new string(sMessage);
    m_oInQueue.push(tData);

    m_iQueueMemSize += sMessage.size();

    oLock.unlock();

    // 该调动向 EventLoop 中添加一个简单的 Notify 事件，以唤醒可能处于阻塞的事件循环线程。
    JumpoutEpollWait();
    return 0;
}
```

感觉代码写的非常清楚了：TcpClient 中的主要逻辑是为根据消息的目标为待发送的消息选择对应的（不存在则创建）MessageEvent 对象，然后将消息加入到该对象中的发送队列（如果没超过长度或内存使用限制）中，随后利用 Notify 事件提供的接口唤醒可能处于阻塞状态的事件循环线程。

介绍完消息是如何加入队列的，我们来看看队列中的内容如何发送出去的。前面我们提到了，TcpWrite 的线程是用于调用它关联的 EventLoop 对象的，所以核心就在于 EventLoop 的 StartLoop 中，上一节我们提到了 StartLoop 中的 while 循环通过不断地调用 OneLoop 来处理处于 Ready 状态的事件，将它们分发给各自对应的处理函数。所以关键就在于这些事件的来源了。

对于 TcpWrite 的 EventLoop 而言，OneLoop 中的这些事件来源于 TcpClient，所以每次 StartLoop 在执行完 OneLoop 之后，都会调用 TcpClient::DealWithWrite 去检查是否需要往事件循环中添加新的事件，代码如下：

```cpp
void TcpClient :: DealWithWrite()
{
    // 逻辑很简单，调用各个 MessageEvent 的 OpenWrite，由它们自己去
    // 添加所需要进行的写事件。
    size_t iSize = m_vecEvent.size();
    for (size_t i = 0; i < iSize; i++)
    {
        m_vecEvent[i]->OpenWrite();
    }
}

void MessageEvent :: OpenWrite()
{
    // 如果消息队列非空，添加 EPOLLOUT 事件表示有数据要发送，从而当发生缓冲区非满时，
    // epoll_wait 会返回该事件并调用 MessageEvent::OnWrite 开始尝试数据发送。
    if (!m_oInQueue.empty())
    {
        if (IsDestroy())
        {
            // 进行必要的重连。
            ReConnect();
            m_bIsDestroy = false;
        }
        else
        {
            AddEvent(EPOLLOUT);
        }
    }
}
```

在继续描述 OnWrite 中的发送逻辑前，看这段代码的时候我有一点奇怪：**在这两个方法中访问 m\_vecEvent 和 m\_oInQueue 时，没有任何的同步操作，而在其他如 TcpClient::GetEvent 和 MessageEvent::AddMessage 中，我们是可以看到锁操作的**。

m\_oInQueue 这个可能还好，empty 方法如果是直接根据 size 成员变量计算得到结果的话，这里至多因为 size 的更新没有同步而返回一个错误值，最多就是误添加了一个 EPOLLOUT 事件，后续的逻辑应该能够正确处理。

但是 m\_vecEvent 的话，这里是在 TcpWrite 的线程中进行访问，如果此时用户线程调用 AddMessage，是由可能会进入到 CreateEvent 中执行 `m_vecEvent.push_back(poEvent)` 这样一条语句的，这个操作是有可能导致 vector 扩容的，从而 TcpWrite 线程中的访问操作可能会发生异常。

~~不能确定这是否是个潜在 bug，截止我写这篇博客的时候，Github 仓库中的代码依旧是这样。~~

已提交 [Issue](https://github.com/Tencent/phxpaxos/issues/75) 进行了讨论，m\_oInQueue 的后续逻辑有二次加锁检查，所以可以正确处理，m\_vecEvent 则可能由于插入时的扩容带来问题，简单的解决办法是初始化的时候使用 reserve 预留足够大的空间避免扩容行为（因为一般消息发送的目标数量也不会特别夸张）。

抛开上面那个，继续看看 MessageEvent 在被 epoll\_wait 返回并回调 OnWrite 后是如何发送消息的：

```cpp
int MessageEvent :: OnWrite()
{
    // while 循环的两个条件分别表示：发送队列非空、上一次的消息未发送完，
    // 调用 DoOnWrite 进行真实的发送操作。
    int ret = 0;
    while (!m_oInQueue.empty() || m_iLeftWriteLen > 0)
    {
        ret = DoOnWrite();
        if (ret != 0 && ret != 1)
        {
            return ret;
        }
        else if (ret == 1)
        {
            //need break, wait next write
            return 0;
        }
    }

    WriteDone();

    return 0;
}

int MessageEvent :: DoOnWrite()
{
    // 上一次的消息未发送完毕。
    if (m_iLeftWriteLen > 0)
    {
        return WriteLeft();
    }

    // 从队列中取出一条新消息来执行发送。
    m_oMutex.lock();
    if (m_oInQueue.empty())
    {
        m_oMutex.unlock();
        return 0;
    }
    QueueData tData = m_oInQueue.front();
    m_oInQueue.pop();
    m_iQueueMemSize -= tData.psValue->size();
    m_oMutex.unlock();

    // 计算一下消息从入队列到被处理的延时，如果太长就抛弃掉。
    ...
    std::string * poMessage = tData.psValue;
    uint64_t llNowTime = Time::GetSteadyClockMS();
    int iDelayMs = llNowTime > tData.llEnqueueAbsTime ? (int)(llNowTime - tData.llEnqueueAbsTime) : 0;
    BP->GetNetworkBP()->TcpOutQueue(iDelayMs);
    if (iDelayMs > TCP_OUTQUEUE_DROP_TIMEMS)
    {
        delete poMessage;
        return 0;
    }

    // 计算所需的发送缓冲区长度，需要加入一个 4 字节放在头部表示消息长度，
    // 随后申请缓冲区，并将长度和消息内容拷贝到缓冲区中。
    int iBuffLen = poMessage->size();
    int niBuffLen = htonl(iBuffLen + 4);

    // 第二次用户态拷贝，感觉可以优化成记录一个长度，并把 poMessage 的内存管理直接转移到本类。
    // 不过这样实现的话代码可读性会下降，无法用同一段逻辑处理消息长度和消息内容。
    int iLen = iBuffLen + 4;
    m_oWriteCacheBuffer.Ready(iLen);
    memcpy(m_oWriteCacheBuffer.GetPtr(), &niBuffLen, 4);
    memcpy(m_oWriteCacheBuffer.GetPtr() + 4, poMessage->c_str(), iBuffLen);

    m_iLeftWriteLen = iLen;
    m_iLastWritePos = 0;

    delete poMessage;

    // 开始尝试发送消息，因为可能消息过大无法一次递交到内核缓冲区，下面的逻辑需要根据
    // 返回值来更新相关的状态变量。
    int iWriteLen = m_oSocket.send(m_oWriteCacheBuffer.GetPtr(), iLen);
    if (iWriteLen < 0)
    {
        PLErr("fail, write len %d ip %s port %d",
                iWriteLen, m_oAddr.getHost().c_str(), m_oAddr.getPort());
        return -1;
    }

    // 缓冲区满，添加 EPOLLOUT 等待缓冲区非满事件。
    if (iWriteLen == 0)
    {
        //need wait next write
        AddEvent(EPOLLOUT);
        return 1;
    }
    
    if (iWriteLen == iLen)
    {
        m_iLeftWriteLen = 0;
        m_iLastWritePos = 0;
        //write done
    }
    else if (iWriteLen < iLen)
    {
        m_iLastWritePos = iWriteLen;
        m_iLeftWriteLen = iLen - iWriteLen;
    }
    ...
    return 0;
}

void MessageEvent :: WriteDone()
{
    RemoveEvent(EPOLLOUT);
}

int MessageEvent :: WriteLeft()
{
    // 和 DoOnWrite 的后半段类似，向内核缓冲区中添加数据，并更新状态变量。
    int iWriteLen = m_oSocket.send(m_oWriteCacheBuffer.GetPtr() + m_iLastWritePos, m_iLeftWriteLen);
    //PLImp("writelen %d", iWriteLen);
    if (iWriteLen < 0)
    {
        return -1; 
    }

    if (iWriteLen == 0)
    {
        //no buffer to write, wait next epoll_wait
        //need wait next write
        AddEvent(EPOLLOUT);

        return 1;
    }

    m_iLeftWriteLen -= iWriteLen;
    m_iLastWritePos += iWriteLen;

    if (m_iLeftWriteLen == 0)
    {
        m_iLeftWriteLen = 0;
        m_iLastWritePos = 0;
    }

    return 0;
}
```

看起来很复杂，实际上就是为了在 TCP 的流模式上封装得到消息模式：

- 为了记录消息的长度，在每一个消息前都加入了 4 个字节的内容来表示消息的长度。
- 因为发送的消息可能很大，所以 send 操作可能会导致内核的发送缓冲区满而返回 0，所以使用了 m\_iLeftWriteLen 和 m\_iLastWritePos 来记录当前消息的发送状态。
- 在 DoOnWrite 和 WriteLeft 中也都有相应的处理缓冲区满操作：在返回长度为 0 时，添加一个 EPOLLOUT 事件等待下一次的事件循环并返回 1 表示本次不再尝试发送。
- WriteDone 方法中移除 EPOLLOUT 事件，如果还有下一个消息的话，会再次添加 EPOLLIN 事件的。

#### TcpRead
感觉 TcpWrite 写的有点多啊，都快把源码都贴上来了 = =#，这部分就稍微简化下吧。

TcpRead 和 TcpWrite 很类似，成员变量除了 EventLoop 以外有一个与 TcpClient 对应的 TcpAcceptor，再看看 EventLoop 提供的 SetTcpAcceptor 和 StartLoop 方法中的 `m_poTcpAcceptor->CreateEvent();` 语句，就可以很容易想到了它和 TcpWrite 的整个路径是差不多的。

但是，TcpAcceptor 不同于 TcpClient，因为作为 TCP 接收端，有一个很重要的点就是要先接受连接，所以 TcpAcceptor 继承至 Thread，在该线程中结合 poll 来接受对端发来的连接，并将它们构造成 AcceptData，插入到待处理的队列中。而这些数据将在事件循环线程调用 **TcpAcceptor::CreateEvent** 时被处理，过程和 TcpClient::AddMessage 类似：

1. 根据从队列中取出的 AcceptData，创建接收类型（MessageEventType\_RECV）的 MessageEvent 对象。
2. 以该对象注册 EPOLLIN 事件到事件循环中，从而接收数据。

显然，数据的接收过程也被放到了 MessageEvent 中，因为是 EPOLLIN 事件，EventLoop 会回调事件的 OnRead 方法，相似地，存在 ReadLeft 和 ReadDone 这两个方法。

MessageEvent 中读取的过程大致如下（就不贴代码只写逻辑所属的方法名了）：

1. OnRead：读取前 4 个字节以获取消息长度，这里可能会分多次读取，所以 MessageEvent 中使用了 m\_iLastReadHeadPos 这样一个变量来应对这种情况。
2. OnRead：当获取到长度后，准备读取缓冲区，并使用读取到的长度设置 m\_iLeftReadLen 变量。
3. OnRead：尝试进行一次读取，如果未读取完成的话，利用已读到的长度更新 m\_iLeftReadLen 变量。
4. ReadLeft：根据 m\_iLeftReadLen 读取剩余的内容，如果未读完就等待下一次，如果已读完，调用 ReadDone。
5. ReadDone：将完整的缓冲区通过 Network::OnReceiveMessage 接口回调给用户。

不贴代码果然短了很多啊。

## 算法消息接口：MsgTransport & Communicate
可能是出于屏蔽以及方便使用，PhxPaxos 并没有直接为算法层的角色提供网络层，而是通过一个叫 MsgTransport 的接口类提供了一些接口方法，如下：

```cpp
class MsgTransport
{
public:
    virtual ~MsgTransport() {}

    virtual int SendMessage(const nodeid_t iSendtoNodeID, const std::string & sBuffer, 
            const int iSendType = Message_SendType_UDP) = 0;

    virtual int BroadcastMessage(const std::string & sBuffer, 
            const int iSendType = Message_SendType_UDP) = 0;
    
    virtual int BroadcastMessageFollower(const std::string & sBuffer, 
            const int iSendType = Message_SendType_UDP) = 0;
    
    virtual int BroadcastMessageTempNode(const std::string & sBuffer, 
            const int iSendType = Message_SendType_UDP) = 0;
};
```

显然，这些接口可以简化算法层的使用，不过对于 Broadcast 而言，像 Follower 和 TempNode 这些东西就需要由实现者去确定了。

PhxPaxos 内部的 Communicate 类实现了这个接口，该类的构造需要接受一个 Config 对象，该类对象中包含了所有 Broadcast 操作所需要使用的节点信息，这块涉及到算法运行层面，此处就暂时忽略了。

## 结语
完全没想到这篇东西会花这么长时间，昨天晚上开始写的（囧因此忘掉了腾讯的模拟笔试），然后今晚补完了，前后大概用了快 5 个小时吧。可能一方面是因为在写的时候基本又重看了一遍源码来确保不出太大的问题，另一方面感觉是写的过于细了。。。