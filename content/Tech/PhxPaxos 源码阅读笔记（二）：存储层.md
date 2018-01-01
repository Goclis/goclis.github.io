Title: PhxPaxos 源码阅读笔记（二）：存储层  
Tags: LevelDB, PhxPaxos  
Date: 2017-09-07 21:38:00


[TOC]

**我原以为本篇不需要很多前置内容，但越写越发现还是需要，毕竟存储层存的内容已经和算法及实现息息相关了，所以建议还是先补充前置内容。**

类似网络层，PhxPaxos 对存储层也进行了抽象，给用户留下了自行扩展的能力。本篇将对 PhxPaxos 内部实现的默认存储层进行介绍，方便有自行实现需求的用户可以将官方的设计作为参考。我大概理了一遍设计后，发现并不是太复杂，所以篇幅应该不会太长。

## 接口
在 include/phxpaxos/storage.h 中定义了存储层所需要提供的一些接口，如下：

```cpp
class LogStorage
{
public:
    virtual ~LogStorage() {}

    virtual const std::string GetLogStorageDirPath(const int iGroupIdx) = 0;

    virtual int Get(const int iGroupIdx, const uint64_t llInstanceID, std::string & sValue) = 0;
    virtual int Put(const WriteOptions & oWriteOptions, const int iGroupIdx, const uint64_t llInstanceID, const std::string & sValue) = 0;
    virtual int Del(const WriteOptions & oWriteOptions, int iGroupIdx, const uint64_t llInstanceID) = 0;

    virtual int GetMaxInstanceID(const int iGroupIdx, uint64_t & llInstanceID) = 0;

    virtual int SetMinChosenInstanceID(const WriteOptions & oWriteOptions, const int iGroupIdx, const uint64_t llMinInstanceID) = 0;
    virtual int GetMinChosenInstanceID(const int iGroupIdx, uint64_t & llMinInstanceID) = 0;

    // 清除指定组下的所有实例数据。
    virtual int ClearAllLog(const int iGroupIdx) = 0;

    // 设置/获取系统变量。
    virtual int SetSystemVariables(const WriteOptions & oWriteOptions, const int iGroupIdx, const std::string & sBuffer) = 0;
    virtual int GetSystemVariables(const int iGroupIdx, std::string & sBuffer) = 0;

    // 设置/获取 Master 变量。
    virtual int SetMasterVariables(const WriteOptions & oWriteOptions, const int iGroupIdx, const std::string & sBuffer) = 0;
    virtual int GetMasterVariables(const int iGroupIdx, std::string & sBuffer) = 0;
}
```

根据命名能够大概猜到相关的含义，这里简要补充下：

- GetLogStorageDirPath：获取存储的根目录。这个接口主要是为 Checkpoint 服务，PhxPaxos 会将一些临时文件存储到此目录中。
- Get/Put/Del：实例数据的相关持久化访问接口。
    - 三个接口的参数基本一致，都包含**组 ID、实例 ID 和实例值**这三部分，组和实例是 PhxPaxos 引入的概念（这里不多介绍）。简单理解，在每个组内，我们可以把存储的实例数据当做**一连串有序的键值对**，可以把实例 ID 当作键，该实例对应的数据作为值。
    - Put/Del 方法多了个 WriteOptions 参数，主要是用来控制修改操作时的一些行为，目前仅有 sync 这样一个标识用来指导本次修改操作是否要同步到磁盘（这里的同步是指磁盘缓冲到真正的落盘）。
- GetMaxInstanceID：获取当前存储的最大实例 ID。实例数据是根据实例 ID 有序的，也就不难理解最大这个概念了。
- Set/GetMinChosenInstanceID：存储层允许 PhxPaxos 内部设置一个称为**最小选择实例 ID** 的概念，我还没有完全确定它的含义，目前猜测是和 Checkpoint 相关，在完成一次 Checkpoint 后，之前的实例数据对应的日志应该就可以删除，从而我们可以设置一个 MinChosenInstanceID 来告知 PhxPaxos 算法层本节点目前拥有的实例日志的范围。
- ClearAllLog：完全清除存储的所有日志。
- Set/GetSystemVariables：后文解释。
- Set/GetMasterVariables：后文解释。

## 存储层用来做啥？
在简单地过了一遍接口后，我们先来想一个问题：为什么 PhxPaxos 需要一个存储层，用它来存些什么？我个人的理解是，存储 Paxos 日志，更具体些，存储每一轮 Paxos（在 PhxPaxos 可以看成每一个实例）所确定下来的数据。而保存它们的原因也很简单：这些数据需要被其他的 Paxos 节点所学习以使得各个 Paxos 节点上的实例都尽量保持一致，按照 PhxPaxos 的设计，大多数落后的话可就没法继续推进实例了。

除了最基本的实例数据外，各个实现可以按照自己的需要，存储一些额外的辅助信息。在 PhxPaxos 中，存储层负责了三类数据的存储：

1. 实例数据。对应于通过 Paxos 算法确定下来的值，包括实例 ID、此实例对应的数据等。**可以当做是日志数据**。
2. System Variables：使用 Protobuf 定义（见 src/comm/paxos_msg.proto），应该是用来存储一些在节点间共享的内容的，更多需要去进一步了解内部的 SystemVSM。
3. Master Variables：类似 System Variables，用于记录 Master 信息，相关的也有 MasterStateMachine。

## 存储层的设计
PhxPaxos 的存储层包括两部分：

1. 利用文件系统：以文件形式存储实例数据。
2. 利用 LevelDB：构建实例 ID 到其数据的索引。

PhxPaxos 将每个组的存储内容进行了划分，分别对应于文件系统上的不同目录和 LevelDB 中的不同名数据库，后续内容我将只描述组内的存储情况。

### 文件系统
我们先抛开索引，当要为一个实例去维护日志时，很显然，需要保存至少两部分内容：该实例的 ID 以及该实例所确定下来的数据。实例 ID 是定长的，但是实例的数据可能是变长的，从而在将多个实例序列化存储到一个文件时，为了能够区分各个实例，我们至少还需要一个长度来表示每个实例所占用的文件范围。

上面的推理基本就是 PhxPaxos 在文件中存储实例数据的格式，由三部分组成：

1. 四字节的长度，表示该实例后续数据的字节数。
2. 实例 ID，八字节。
3. 实例数据，变长。

以实例 ID 为 1，实例数据为 Hello 为例，在文件中持久化成（小端机器）：

```
06 00 00 00 01 00 00 00 00 00 00 00 48 65 6c 6c 6f
```

PhxPaxos 在存储前并没有进行任何的端序转换，可能是因为生产环境基本都是小端机器或是这些数据只会被同一节点读取，不需要这种转换。

PhxPaxos 采用了类似于 Kafka 段文件的存储方法，单个文件中存储多个实例数据，但每个文件有一个大小上限，当一个文件存不下时，创建一个新的文件进行存储。这些数据文件之间使用有序递增的**文件 ID**来进行命名。为了快速定位最大实例，PhxPaxos 增加了一个额外的 meta 文件，该文件中保存着存储层的最大实例以及该实例的索引信息，索引的结构我们放到下一节讲。

### 索引
从上一节的内容中我们得知，一个文件中是存储着多个实例数据的，这虽然提高了存储效率，但为我们定位特定实例的数据带来了麻烦，所以 PhxPaxos 引入了 LevelDB 来进行索引（了解过 Kafka 的读者可以将这样的设计与 Kafka 中的 .index 文件进行类比）。

我们知道，LevelDB 是一个键值数据库，所以了解了 PhxPaxos 将什么作为键，什么作为值就可以明白这个索引的设计了。

键，很明显是实例 ID，因为 Paxos 算法层面的大多数操作都要求按实例去存储或者获取数据。

值，作为索引，值需要方便我们定位实例数据的位置，可以稍微想一下这个查找的过程：从一堆文件中找到该实例 ID 所在的文件，然后从该文件中找到实例数据。所以，很容易想到索引结构至少有**文件 ID**和**文件内偏移**这两个部分。为了避免磁盘错误，PhxPaxos 在索引中加入了额外的 CRC 校验码，即索引内容由三部分构成。这三部分都是定长的，PhxPaxos 将它们依次转换成字符串然后拼接在一起，就构成了 LevelDB 中的值。

**索引键**

这里额外提一下，PhxPaxos 中所有的实例 ID 均未自然数，顺序也自然是基于自然顺序的，实例 ID 也是各个实例 LevelDB 中的键值。

在之前的内容中，我们曾经提到过 System Variables 和 Master Variables，它们两者并不存储文件系统中，而是以特殊的键存储在 LevelDB 中，这里的特殊体现在它们是负值，所以不会和 PhxPaxos 的实例 ID 发生冲突。类似地，MinChosenInstanceID 也是以特殊键的方式存储在 LevelDB 中。三者的定义如下：

```cpp
#define MINCHOSEN_KEY ((uint64_t)-1)
#define SYSTEMVARIABLES_KEY ((uint64_t)-2)
#define MASTERVARIABLES_KEY ((uint64_t)-3)
```

## 源码
写了一堆，我们以 LogStorage::Put 和 LogStorage::Get 的流程为例来看一下相关的代码（src/logstorage）吧。

![](https://ws1.sinaimg.cn/large/006tKfTcgy1fjbfpvp74lj30oe0gkabb.jpg)

先参照类图大体上讲一下，PhxPaxos 内部的 LogStorage 接口实现类为 MultiDatabase，它负责管理所有 Group 的存储层，内部使用一个 vector 来为各个 Group 维护一个 Database 对象，对接口的实现也是简单的转发到 Database 类对象中。显然，Database 类内部需要维护文件系统和 LevelDB 这两部分的操作，PhxPaxos 将文件系统相关的操作封装到类 LogStore 中，LevelDB 的操作直接在 Database 中使用 LevelDB 的 API 完成。

简单介绍完毕，后续的内容将从 Database 类开始。

### LogStorage::Put
调用转发到 Database::Put，其中的内容分为两部操作：首先调用 ValueToFileID 将实例数据存储到文件中，并获取相应的索引信息；随后以实例 ID 作为键，上一步得到的索引信息作为值存储到 LevelDB 中。

让我们来看看 ValueToFileID 的相关代码：

```cpp
int Database :: ValueToFileID(const WriteOptions & oWriteOptions, const uint64_t llInstanceID, const std::string & sValue, std::string & sFileID)
{
    int ret = m_poValueStore->Append(oWriteOptions, llInstanceID, sValue, sFileID);
    ...
}

int LogStore :: Append(const WriteOptions & oWriteOptions, const uint64_t llInstanceID, const std::string & sBuffer, std::string & sFileID)
{
    m_oTimeStat.Point();
    std::lock_guard<std::mutex> oLock(m_oMutex);

    int iFd = -1;
    int iFileID = -1;
    int iOffset = -1;

    int iLen = sizeof(uint64_t) + sBuffer.size();
    int iTmpBufferLen = iLen + sizeof(int);

    // 获取存储此实例数据的文件信息，因为当前文件不一定放的下此实例数据，
    // 所以本方法中包含着开启一个新文件的逻辑。
    int ret = GetFileFD(iTmpBufferLen, iFd, iFileID, iOffset);
    if (ret != 0)
    {
        return ret;
    }

    m_oTmpAppendBuffer.Ready(iTmpBufferLen);

    // 每条实例数据在文件中由三部分组成：
    // 1. 4 字节长度（包括实例 ID 的 8 字节和数据内容两部分）。
    // 2. 实例 ID。
    // 3. 数据内容。
    memcpy(m_oTmpAppendBuffer.GetPtr(), &iLen, sizeof(int));
    memcpy(m_oTmpAppendBuffer.GetPtr() + sizeof(int), &llInstanceID, sizeof(uint64_t));
    memcpy(m_oTmpAppendBuffer.GetPtr() + sizeof(int) + sizeof(uint64_t), sBuffer.c_str(), sBuffer.size());

    size_t iWriteLen = write(iFd, m_oTmpAppendBuffer.GetPtr(), iTmpBufferLen);

    if (iWriteLen != (size_t)iTmpBufferLen)
    {
        return -1;
    }

    if (oWriteOptions.bSync)
    {
        int fdatasync_ret = fdatasync(iFd);
        if (fdatasync_ret == -1)
        {
            PLG1Err("fdatasync fail, writelen %zu errno %d", iWriteLen, errno);
            return -1;
        }
    }

    m_iNowFileOffset += iWriteLen;

    int iUseTimeMs = m_oTimeStat.Point();
    BP->GetLogStorageBP()->AppendDataOK(iWriteLen, iUseTimeMs);

    // checksum 只包含数据内容部分，忽略实例数据开头的 4 字节长度部分。
    uint32_t iCheckSum = crc32(0, (const uint8_t*)(m_oTmpAppendBuffer.GetPtr() + sizeof(int)), iTmpBufferLen - sizeof(int), CRC32SKIP);

    // 根据实例数据存储的文件 ID、在该文件中的 offset 以及数据内容的 checksum 生成作为 LevelDB 值，以
    // out 参数的形式返回给调用者。
    GenFileID(iFileID, iOffset, iCheckSum, sFileID);

    return 0;
}
```

可以看到，ValueToFileID 也仅仅是将调用转换到 LogStore::Append 中，后者中的逻辑主要分为几部分：

1. GetFileFD：获取一个**可以放的下**本实例数据的文件描述符。回想一下前面的设计，我们曾提到每一个文件的大小是有限制的，所以此方法内部是需要考虑当前文件的剩余空间是否能够放的下本实例数据的，如果不能的话，需要打开一个新的文件。总之，该方法会返回一个文件描述符供后续操作写入数据，一个文件 ID 以及偏移量。
2. 序列化：准备空间并紧跟一系列的 memcpy，通过 memcpy 我们可以确定实例数据在文件中的存储格式正如之前设计中所述。
3. 写入：注意此处会根据 WriteOptions 来决定是否要 sync。
4. GenFileID：最后这部分计算了内容的 CRC 校验码，随后结合文件 ID 和偏移量生成了最终存储到 LevelDB 中的 sFileID。

### LogStorage::Get
调用转发到 Database::Get，其中的内容同样分为两部分，不过和 Put 的相反：首先根据实例 ID 从 LevelDB 中查询实例数据的索引信息；随后根据索引信息，调用 FileIDToValue 从文件系统中获取实例数据。

从 LevelDB 中取值的过程就略过了，我们来看看 FileIDToValue 的相关代码：

```cpp
int Database :: FileIDToValue(const std::string & sFileID, uint64_t & llInstanceID, std::string & sValue)
{
    int ret = m_poValueStore->Read(sFileID, llInstanceID, sValue);
    ...
}

int LogStore :: Read(const std::string & sFileID, uint64_t & llInstanceID, std::string & sBuffer)
{
    // 从索引信息中提取文件 ID、偏移量和校验码
    int iFileID = -1;
    int iOffset = -1;
    uint32_t iCheckSum = 0;
    ParseFileID(sFileID, iFileID, iOffset, iCheckSum);
    
    int iFd = -1;
    int ret = OpenFile(iFileID, iFd);
    if (ret != 0)
    {
        return ret;
    }
    
    off_t iSeekPos = lseek(iFd, iOffset, SEEK_SET);
    if (iSeekPos == -1)
    {
        return -1;
    }
    
    int iLen = 0;
    ssize_t iReadLen = read(iFd, (char *)&iLen, sizeof(int));
    if (iReadLen != (ssize_t)sizeof(int))
    {
        close(iFd);
        return -1;
    }
    
    std::lock_guard<std::mutex> oLock(m_oReadMutex);

    m_oTmpBuffer.Ready(iLen);
    iReadLen = read(iFd, m_oTmpBuffer.GetPtr(), iLen);
    if (iReadLen != iLen)
    {
        close(iFd);
        return -1;
    }

    close(iFd);

    // 重新计算校验码，比较是否出错
    uint32_t iFileCheckSum = crc32(0, (const uint8_t *)m_oTmpBuffer.GetPtr(), iLen, CRC32SKIP);

    if (iFileCheckSum != iCheckSum)
    {
        return -2;
    }

    memcpy(&llInstanceID, m_oTmpBuffer.GetPtr(), sizeof(uint64_t));
    sBuffer = string(m_oTmpBuffer.GetPtr() + sizeof(uint64_t), iLen - sizeof(uint64_t));

    return 0;
}
```

可以看到，FileIDToValue 也仅仅是将调用转换到 LogStore::Read 中，后者的逻辑主要分为以下几部分：

1. ParseFileID：根据传入的索引信息，提取文件 ID、文件内偏移以及校验码。
2. 读取：打开上一步得到的文件，利用偏移定位到指定位置，根据格式读取长度以及内容。
3. 校验：根据读取的内容重新计算校验码，检查是否存在磁盘错误。
4. 反序列化：从读取到的内容中提取实例 ID 和实例数据，赋值给返回参数。

### 其他
其他的操作的实现都类似，都或多或少利用了 LevelDB 的一些特性，比如 GetMaxInstanceID 的实现中使用了 leveldb::Iterator::SeekToLast 方法来快速定位到最大的键。

## 结语
这篇基本写完了，不长，但是因为加班，空闲时间略少，所以一直托到很晚才开始写。开始写的时候发现已经快把源码忘光了，又花了一些时间来重新过一遍。

内容中有些略过了，待我把整个系列写完（如果没太监 = =#）后再回过头来看看，尽量补的详实些。
