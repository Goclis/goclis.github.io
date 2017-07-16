Title: Call convention & Name mangling  
Tags: Call convention, 调用约定, Name mangling, ABI  
Date: 2017-04-10 22:29:42  


标题只是为了满足强迫症，文中对于 Call convention 还是使用中文翻译的**调用约定**，但 Name mangling 因为不知道怎么翻译好，就保持吧。

之前同学在聊面试的时候提到被问过调用约定（Call convention）相关的问题，突然想起来自己虽然知道这个东西影响的是方法调用（比如参数如何传递、调用栈清理等），但是并不记得每个类型的调用约定存在的作用以及具体内容，于是查了一下。

## 调用约定（Call convention）
调用约定规定了一个方法在被调用的时候需要遵循的一些内容：

1. 参数如何传递，包括使用寄存器还是堆栈或是混合、从左到右压栈还是从右到左压栈。
2. 调用栈最终由谁负责恢复？调用者（Caller）或被调用者（Callee）。
3. 方法最终在链接时使用的符号名。
4. 更多...

显然，调用约定是 [ABI（Application binary interface）][5] 层面的东西，而且这玩意有很多类型，历史原因在于以前提供机器的那波厂商没有顺带提供操作系统和编译器，而是把这两块交给了市场，于是各家自己玩自己的，弄出来各种自己的标准，所以 ABI 兼容就别想了。虽然也有如 stdcall 这样的标准出来让各家一起遵守，但是至今我好像也没怎么看到关于 ABI 兼容的实例（希望是我没看到吧）。

下面是常见的几种调用约定的规定：

1. cdecl：广泛被 C 编译器使用（Visual Studio 2015 在 Win32 Debug 下默认使用这个），使用栈传递参数、从右到左压栈、栈由调用者清理、符号名如 `_func`（方法名前加下划线）。
2. stdcall：使用栈传递参数、从右到左、栈由被调用者清理、符号名如 `_func@8`（方法名前加下划线，后面使用 @ 拼接调用参数的总大小）。
3. fastcall：类似 stdcall，但会将前两个小于等于 DWORD 的参数使用寄存器 ECX 和 EDX 传递，剩余的使用栈，另外符号名如 `@func@8`（相对于 stdcall，把前面的下划线换成 @）。

可以看到，调用约定对符号名也有一定的规定，这让我想起来 C++ 的 [Name mangling][4]，这个东西同样对符号名有规定，所以我当时好奇当它和调用约定结合起来后会怎么样？

## Name mangling
调用约定在一定程度上告诉了编译器该如何生成一个方法的内容、如何生成调用了这个方法的代码的内容以及链接时该使用怎样的符号。

而 Name mangling 只做一件事，就是一个方法名对应的符号名该是什么，又名 Name decoration。我个人理解 C++ 引入这个是为了对付重载，毕竟允许方法同名后就没办法仅通过名字来在链接时像 C 那样区分各个符号了。不过，查了一些资料后发现，其实 C 的那种在方法名前面加下划线（就是 cdecl 的规定）就是它的 Name mangling，所以不能说 Name mangling 是 C++ 特有的。

瞎扯了一堆，做实验看看两个合起来会对符号名有什么样的影响吧（虽然我觉得这玩意应该又是一件完全由编译器决定的事，不过还是试试看吧）。

## 实验
用的 Visual Studio 2015 Community Edition，Configuration 选择默认的 Win32 Debug，查看符号的方式也比较简单，看生成产生的链接错误即可。

代码如下：

```cpp
// C++ name mangling & cdecl
// unresolved external symbol "void __cdecl F(void)" (?F@@YAXXZ) referenced in function _main
// void F();

// C++ name mangling & stdcall
// unresolved external symbol "void __stdcall F(void)" (?F@@YGXXZ) referenced in function _main
// void __stdcall F(); 

// C++ name mangling & fastcall
// unresolved external symbol "void __fastcall F(void)" (?F@@YIXXZ) referenced in function _main
// void __fastcall F();

// C name mangling & cdecl
// unresolved external symbol _F referenced in function _main
// extern "C" void F();

// C name mangling & stdcall
// unresolved external symbol _F@0 referenced in function _main
// extern "C" void __stdcall F();

// C name mangling & fastcall
// unresolved external symbol @F@0 referenced in function _main
extern "C" void __fastcall  F();

int main()
{
    F();
}
```

代码大概的目的就是测试一下 cdecl、stdcall、fastcall 在混合 C 和 C++ 的 Name mangling 时，会生成怎样的符号，代码里使用 `extern "C"` 来让编译器采用 C Name mangling。

从结果来看，两者会共同影响最终的符号，= =# 好像也没有更多的什么好解释了。如果还对调用栈的清理感兴趣的话，可以增加点参数，实现一下每个方法，然后反汇编看一下即可。

## 写在最后
像这种 ABI 层面的一些规定，我们大多时候可能不会去在意，但是有些地方的开发可能会强制地要求你使用某种特定的规定（比如有个同学提到过他开发驱动的时候好像必须使用 cdecl），所以稍微了解下也没什么坏处吧。

至于 ABI 相关的内容，除了本文提到了两个，还有一个 type representations，大概是指与数据相关的内容，比如数据的大小、对齐等内容？这里就不展开了（懒。

## 参考资料
- [x86 Call convention - Wikipedia][1]
- [Argument Passing and Naming Conventions - MSDN][6]
- [cdecl - MSDN][2]
- [cdecl、stdcall、fastcall 函数调用约定区别 - CSDN][3]
- [Name mangling - Wikipedia][4]
- [Application binary interface - Wikipedia][5]


[1]: https://www.wikiwand.com/en/X86_calling_conventions
[2]: https://msdn.microsoft.com/en-us/library/zkwh89ks.aspx
[3]: http://blog.csdn.net/fly2k5/article/details/544112
[4]: https://www.wikiwand.com/en/Name_mangling
[5]: https://www.wikiwand.com/en/Application_binary_interface
[6]: https://msdn.microsoft.com/en-us/library/984x0h58.aspx
