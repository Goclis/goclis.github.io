Title: mov 指令与内存  
Slug: mov-with-memory  
Date: 2014-08-08 16:00  
Tags: cs  
Author: Goclis Yao  


今天在啃《深入理解计算机系统》的时候遇到了下面这段代码
```
movl 12(%ebp), %eax
imull 8(%ebp)
movl %eax, (%esp)
movl %edx, 4(%esp)
```
代码的作用就是将两个数的乘积存回栈顶。

代码没有问题，让我疑惑的是书上这两句话

> 存储两个寄存器的位置对小端机器来说是对的——寄存器 %edx 中的高位存在相对于 %eax 的低位偏移量为 4 的地方。
> 栈是向低地址方向增长的，也就是说低位在栈顶。

在考虑这两句话的时候，突然发现自己对 mov 的操作并不是特别的清楚，就去查了查，大致搞明白了一些。

## mov 指令
我们知道 mov 在 IA32 中有基础的三类操作，即 b，w，l。

而 mov 在使用时大致如下
```
movb %al, (%edx)  # 将 al 寄存器的内容放到以 %edx 的值为地址的内存区域
```
这里因为是 b 类型的，只有一个字节，所以直接将该字节放到那个地址对应的地方即可。

然而对于 w 和 l，源不止一个字节，这个时候，一个内存地址只能表示存放开始的地方，想要存储源操作数，需要多个地址，表达可能不清楚，用代码来说明
```
movl %eax, (%edx)
```
我们知道内存是按字节整理的，也就是说 edx 代表的那个地址也就只有 1 个字节，而源操作数 eax 却是 4 个字节，因而，需要多个地址进行存放，我们假设下 %eax = 0x0A0B0C0D，%edx = 4，则内存图如下表

| 地址 | 内容 |
| :-: | :-: |
| 0 | ... |
| 1 | ... |
| 2 | ... |
| 3 | ... |
| 4 | 0D |
| 5 | 0C |
| 6 | 0B |
| 7 | 0A |

这里是假设机器为**小端**

可见，占用了 4~7 的内存地址

所以，mov 指令实际占用内存地址的情况是与源操作数的字节数有关的，而多出来的地方，是通过开始地址（即指令中的目标操作数）往上加的。

## 回归问题
既然知道了 mov 的行为，再回过头来看看那段代码。

假设乘积为 0x010203040A0B0C0D，%esp = 104，小端机器，则该段代码执行后内存应该是如下这样的

| 地址 | 0-7 | 8-15 | 16-23 | 24-31 |
| :-: | :-: | :-: | :-: | :-: |
| ... | ... | ... | ... | .. |
| 104 | 0D | 0B | 0C | 0A |
| 108 | 04 | 03 | 02 | 01 |
| ... | ... | ... | ... | ... |

很明显了，低位 (0D) 在 栈顶 (104)，这就解释了

> 栈是向低地址方向增长的，也就是说低位在栈顶。

但是。。

> %edx 的高位存在相对于 %eax 的低位偏移量为 4 的地方

这句话还是没法解释。。%edx 的高位 (01) 相对于 %eax 的低位 (0D)，偏移量好像不是 4 啊。。