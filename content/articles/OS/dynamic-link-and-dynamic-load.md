Title: 动态链接和动态载入的区别  
Slug: difference-between-dynamic-link-and-dynamic-load  
Date: 2014-05-21 15:32
Tags: os  
Author: Goclis Yao    


大致的理解如下，不一定正确，确认后会更新：

按照一般的步骤，用户程序在执行前会经历以下几个步骤：

 - 编译汇编
 - 链接（将编译出来的模块和其他引用了的模块合并）
 - 加载（从硬盘加载到内存中）
 - 执行（在内存中执行）

动态加载和动态链接是打破以上所描述的常规行为的。

###动态加载
硬盘上存储了一个已经生成好的目标模块，但是这个目标模块是由许多子程序组成的。每时每刻，不一定所有的子程序都需要在内存中，所以，在使用到相应子程序时再把其加载到内存中来使用，这要求用户在编写程序时合理地编写子程序，不需要操作系统提供特别的支持。

###动态链接
它与动态加载的概念相似，但是，它不是将加载延迟到了执行时，而是将链接延迟到执行时。主要的问题就在于理解这句话。对于动态链接，磁盘上存储着的目标模块中包含着一部分它并未链接的模块（但是它迟早要用，所以动态链接嘛~）。而使用动态加载技术时，你动态加载的模块是经过链接之后的，也就是该模块已经结合了所有它会用到的模块，只是在你程序的不同地方使用了，所以在不同的地方动态加载需要的代码。

动态链接的实现是依赖于存根（stub）的，目标模块中在使用需要动态链接的模块的地方使用存根来代替，存根能够指出如何装入以及装入后的程序在内存的哪。

动态链接的好处在于多个程序使用到了一个相同的模块时，不需要将该模块都像常规步骤或者动态加载那样合并到目标模块中，而是在执行时再动态链接，这样在内存中就只用存在一份该模块的代码了，即实现了共享库。


###Update at 2014-05-26
问了老师之后，再自己查了查wiki之后有了更深的理解。

首先，上面的理解依旧是正确的，只是不那么准确，看看wiki的吧

__动态加载__
> Dynamic loading is a mechanism by which a computer program can, at run time, load a library (or other binary) into memory, retrieve the addresses of functions and variables contained in the library, execute those functions or access those variables, and unload the library from memory. Unlike static linking and loadtime linking, this mechanism allows a computer program to start up in the absence of these libraries, to discover available libraries, and to potentially gain additional functionality. [^1]

大致的意思就是说动态加载是在运行时把一个library或者二进制文件调入内存，取出其中的functions或者variables来使用。

再看看动态链接。

__动态链接__
> In computing, a dynamic linker is the part of an operating system (OS) that loads (copies from persistent storage to RAM) and links (fills jump tables and relocates pointers) the shared libraries needed by an executable at run time, that is, when it is executed. The specific operating system and executable format determine how the dynamic linker functions and how it is implemented. Linking is often referred to as a process that is performed at compile time of the executable while a dynamic linker is in actuality a special loader that loads external shared libraries into a running process and then binds those shared libraries dynamically to the running process. This is also called dynamic or late linking. The specifics of how a dynamic linker functions is operating-system dependent. [^2]

看上去比起动态加载貌似只多了一个共享吧？

实际上，动态链接做的不止是动态加载，还有链接的工作。回想我们在一开始说的那个常规步骤就可以明白了。

其实，这两个概念在现在操作系统的实现上已经混合了，没有纯粹的**动态加载**了，都是基于动态链接做的了，比如windows的dll和linux的.so都是如此。






[^1]:[Dynamic Loading](http://en.wikipedia.org/wiki/Dynamic_loading)

[^2]:[Dynamic Linker](http://en.wikipedia.org/wiki/Dynamic_linker)