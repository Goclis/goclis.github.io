Title: C预处理器宏展开  
Slug: c-preprocessor-macro-expansion  
Tags: 预处理器, 宏  
Date: 2016-04-26 23:21:20  

最近在写一个用于简化生成代码的宏，该宏大致希望达到如下功能：

```c
// macro.h
#if defined(T)

void T ## _func()
{
	// ...
}

#endif
```

这段代码是不能用的，因为预处理符号`##`是不能用在代码中的，这里只是用来表示下宏希望实现的目的，即定义一个T，就为之定义一个对应的方法，比如说：

```c
// 这段代码希望定义一个int_func方法
#define T int
#include "macro.h"
#undef T
```

上面提到了`##`是不能直接写在代码里的，所以我一开始是这样实现的：

```c
// macro.h
#if defined(T)

#define func_m(TN) TN ## _func
#define T_func func_m(T)

void T_func()
{
	// ...
}

#endif
```

但是，这样的写法并不能够正确的定义我们例子中想要的`int_func`方法，而是会定义一个`T_func`方法（这一点可以通过查看VS生成的obj文件中的符号确定，或是设置选项让编译器保留预处理产生的.i文件），下面给出正确的写法：

```c
// macro.h
#if defined(T)

#define concate(A, B) A ## B
#define func_m(TN) concate(TN, _func)
#define T_func func_m(T)

void T_func()
{
	// ...
}

#endif
```

之所以需要这样来实现是因为宏展开的规则，我对于宏展开的规则不是特别熟悉，但在[MSDN][1]上找到了一段可能能够用来解释的内容：

> 如果宏定义中的形参的前面或后面带有 token-pasting 运算符，则会立即将形参替换为未扩展的实参。在替换前将不会对参数执行宏扩展。

token-pasting运算符就是`##`。结合我原先的实现以及这段话，当预处理器在处理`T_func`时，它会替换为`func_m(T)`，这类似于一个函数调用，预处理器查看了一下`func_m`这个宏的内容，发现其中有`##`符号，所以，它直接将形参（即TN）替换成了未扩展的实参（即T），替换前并没有对T进行宏展开，从而导致无论T是什么，`T_func`都是最终结果。

这点通过修改一下代码也可以验证：

```c
#define T_func func_m(B)
```

这里改成了B，所以最后定义的符号是`B_func`，因为不管是啥，预处理器都不会对它展开。

本来想结合生成的obj文件来写的，但写这个的时候不是用的Windows，所以就算了，懒23333。

[1]: https://msdn.microsoft.com/zh-cn/library/09dwwt6y.aspx