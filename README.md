Logging
============

### 初始化
因为把源码和最终生成内容都维护在了一个仓库中，在一台新设备上需要进行一些基本的初始化：

```bash
git clone git@github.com:Goclis/goclis.github.io.git
git checkout source
git clone git@github.com:Goclis/goclis.github.io.git output
cd output
git checkout master
cd ..
```

使用两个目录来维护两个分支，根目录为 source 分支，维护源码，output 目录为 master 分支，负责推生成内容。

在根目录下生成新内容放到 output 目录，然后进入 output 目录将修改提交到 master 分支。

安装 pelican 以及插件的依赖（Windows 下考虑使用 pip2）：

```bash
pip install 'pelican==3.6.3'
pip install bs4
```

### 文章规则
文件名、方法名、变量名、路径等使用``包裹，其他的英文均直接写且不加任何的空格。
