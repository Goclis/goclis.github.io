Title: openssl-rsa简单使用  
Date: 2015-09-10  
Modified: 2015-12-26  
Tags: openssl, rsa  
Slug: openssl-rsa-basic-use  
Authors: Goclis Yao  

[TOC]

最近需要用到RSA的一些功能，出于方便，打算直接用openssl，但是在不同平台上使用openssl所需要做的工作还不一样，干脆就记个笔记整理一下。

### Windows下使用VS2013编译openssl源码
源码可以去官网下载，先前下过1.0.2d的源码，但是编译老失败，后面换成1.0.1p的就成功了，原因未知。

编译需要用到perl，去官网下个ActivePerl就可以了，为了往后在cmd中操作简单，最好安装时勾上加入PATH的选项。

解压源码包，打开cmd进入该解压后的目录，执行如下命令：

```
perl Configure VC-WIN32 no-asm --prefix=C:\openssl-1.0.1p\VC-WIN32
```

这是编译前必须执行的配置命令，可以自行根据所使用的编译工具以及平台的不同来选择不同的参数（具体可以查看解压后目录中的README以及一系列的INSTALL文件），稍微解释一下：

- VC-WIN32：表示希望使用VS来编译生成WIN32下使用的openssl库，还可以是其他的比如debug-VC-WIN32、VC-WIN64A等等。
- no-asm：表示编译不使用汇编语言文件，这样可以避免出现与NASM相关的错误。
- prefix：此参数后面的值用于指定编译结果的安装目录。

使用VS编译会使用到VS的nmake、cl、link等工具，默认情况下这些工具是不在PATH里的，所以正常打开cmd是没法找到这些工具的，解决方案有两个：

1. 把它们所在的目录加入到PATH环境变量中。在`VS安装目录/VC`文件夹里有个`vcvarsall.bat`的脚本，执行这个脚本就可以了。
2. 使用VS提供的Tools。每个VS基本都提供了相应的命令行工具（从开始菜单里可以找到），启动这些命令行工具后会自动把这些基础工具加入到此次运行的PATH中（实际上它就是运行了1中的脚本，只不过仅在此次cmd中生效）。

简单的配置完毕后开始进行编译。

__静态库__

```
ms\do_ms
nmake -f ms\nt.mak
nmake -f ms\nt.mak install
```

__动态库__

```
ms\do_ms
nmake -f ms\nt.mak
nmake -f ms\nt.mak install
```

`install`表示将生成的内容（头文件及库）安装到使用perl进行配置时指定的目录中。

就我而言，我需要生成debug及release的库，整个过程如下：

```
perl Configure debug-VC-WIN32 no-asm --prefix=c:\openssl-1.0.1p\debug-VC-WIN32
ms\do_ms
nmake -f ms\nt.mak
nmake -f ms\nt.mak install
perl Configure VC-WIN32 no-asm --prefix=c:\openssl-1.0.1p\VC-WIN32
ms\do_ms
nmake -f ms\nt.mak
nmake -f ms\nt.mak install
```

经过简单的测试，发现使用VS的08、10、13来进行编译产生的内容是一样的。

### Linux下安装openssl库
我的发行版是Ubuntu 14.04，但是默认安装的好像只有一个openssl的可执行程序，没有头文件及库文件，需要另外安装`libssl`，如下：

```
sudo apt-get install libssl-dev
```

在编译你的目标文件时指定`-lssl`及`-lcrypto`选项即可使用相关的功能，如果只用到加密库的话，只需要使用后者即可。

暂时没有去研究如何静态链接openssl。

### openssl可执行程序的使用
openssl除了提供编程相关的头文件及库文件外，还有一个应用程序直接提供了相关的功能，这里简单的罗列一些。

__RSA密钥生成__

使用该程序可以直接生成RSA的公私钥：

```
openssl genrsa -out private.pem 2048 && openssl rsa -in private.pem -pubout > public.pem
```

但是需要注意的是，这里的生成是按照PEM格式进行的，所以如果在编程时需要读取这些文件，要使用PEM相关的API。

__提取RSA公钥内容__

我们知道RSA的公钥是由(n,e)组成的，但是openssl生成的公钥为了可读进行了BASE64编码，可以使用如下命令进行提取：

```
openssl rsa -pubin -inform PEM -text -noout < public.pem
```

### RSA相关编程
#### RSA结构体
RSA结构体在编程中代表RSA的密钥（公钥或私钥），在描述RSA操作之前，先说说RSA的结构体如何构建，也就两种方式：从文件构建或从内存构建。

__文件__

```cpp
RSA *createRSAWithFilename(const char *filename, bool isPub)
{
    BIO *in = NULL;
    in = BIO_new(BIO_s_file());
    if (NULL == in) return 0;
    if (0 == BIO_read_filename(in, filename))
    {
        BIO_free(in);
        return 0;
    }

    RSA *rsa = NULL;
    if (isPub)
    {
        rsa = PEM_read_bio_RSA_PUBKEY(in, 0, 0, 0);
    }
    else
    {
        rsa = PEM_read_bio_RSAPrivateKey(in, 0, 0, 0);
    }

    BIO_free(in);
    return rsa;
}
```

稍微注意一下构造公钥的方法是`*_RSA_PUBKEY`而不是`*_RSAPublicKey`。

PS：对于从文件构建密钥，有一组方法`PEM_read_RSA_PUBKEY`和`PEM_read_RSAPrivateKey`可以直接根据打开的文件构建出对应的RSA结构体，但是在Windows上使用前面那个方法的时候，编译通过，但运行时会提示`Openssl Uplink`，所以改用了openssl内置的BIO。

__内存__

同样利用BIO，代码类似：

```cpp
RSA *createRSAWithMemory(void *buffer, int bufLen, bool isPub)
{
    BIO *in = NULL;
    in = BIO_new_mem_buf(buffer, bufLen);
    if (NULL == in) return 0;

    RSA *rsa = NULL;
    if (isPub)
    {
        rsa = PEM_read_bio_RSA_PUBKEY(in, 0, 0, 0);
    }
    else
    {
        rsa = PEM_read_bio_RSAPrivateKey(in, 0, 0, 0);
    }

    BIO_free(in);
    return rsa;
}
```

#### RSA操作
RSA的使用包括两种基本情况：

- 公钥加密 & 私钥解密
- 私钥签名 & 公钥验签

以下代码省略构造RSA的部分，公钥的RSA为`pubRSA`，私钥的RSA为`priRSA`，处理的内容为`content`，长度为`contentLen`，忽略一些强制转换。

__公钥加密 & 私钥解密__

```cpp
int size = RSA_size(pubRSA);
unsigned char *encrypted = new char[size];
// 返回值表示密文的长度，由于Padding，应该等于size
int ecRet = RSA_public_encrypt(contentLen, content, pubRSA, RSA_PKCS1_PADDING);
if (-1 == ecRet)
{
	// failed
	// ...
}

unsigned char *decrypted = new char[size]; // 加密的内容不能超过RSA密钥的长度
// 返回值即原文的长度
int dcRet = RSA_private_decrypt(ecRet, encrypted, decrypted, priRSA, RSA_PKCS1_PADDING);
if (-1 == dcRet)
{
	// failed
	// ...
}
```

__私钥签名 & 公钥验签__

代码类似，如下：

```cpp
int size = RSA_size(pubRSA);
unsigned char *encrypted = new char[size];
int ecRet = RSA_private_encrypt(contentLen, content, priRSA, RSA_PKCS1_PADDING);
if (-1 == ecRet)
{
	// failed
	// ...
}

unsigned char *decrypted = new char[size];
int dcRet = RSA_public_decrypt(ecRet, encrypted, decrypted, pubRSA, RSA_PKCS1_PADDING);
if (-1 == dcRet)
{
	// failed
	// ...
}
```

#### 大数操作替换RSA
__公钥验签__

```cpp
// 公钥使用(n,e)表示, 验签的内容使用c表示
BigInteger n(nbuf, nlen);
BigInteger e(ebuf, elen);
BigInteger c(cbuf, clen);

// 结果r
BigInteger r = c.modpow(e, n);
```

### 参考资料
1. http://hayageek.com/rsa-encryption-decryption-openssl-c/
2. [Openssl Uplink](http://blog.csdn.net/rabbit729/article/details/3886984)
3. http://developer.covenanteyes.com/building-openssl-for-visual-studio/
4. http://linux.die.net/man/3/bio_new_mem_buf
