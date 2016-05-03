Title: Git  
Date: 2014-01-01  
Tags: Git  

[TOC]

### 1. 本地初始化git项目并添加远程仓库
```bash
cd newProject
git init
git remote add origin url # url为项目的远程仓库路径
git push master origin
```


### 2. Git设置
全局设置（--global）：

```bash
git config --global user.name "Goclis Yao"
git config --global user.email "goclisyyh@gmail.com"
git config --global branch.master.remote origin
git config --global branch.master.merge refs/heads/master
```

本地设置：

```bash
git config branch.master.remote origin
```

查看设置：

```bash
git config --list
```


### 3. Git Bash生成公私钥访问内网git仓库
打开Git Bash，输入如下命令：

```bash
ssh-keygen -t rsa -C "goclisyyh@gmail.com"  # -C后的参数为注释，一般为开发者的email，后面有个步骤会让你输入密码
```

将 ~/.ssh/id_rsa.pub 交给管理员，就可以clone服务器的仓库了。

```bash
git clone user@hostname:gitname.git  # ssh仓库
git clone git@192.168.1.1:Blog.git  # eg
```


### 4. git subtree
当一个项目需要用到另一个项目，并且可能会修改那个项目时，用此命令即可实现。

假设情境如下：

- some-lib：服务器上的某个项目仓库，要在新项目上引入的。
- pro：服务器上的新项目仓库。

下面的操作在本地进行：

```bash
git clone url1 pro    # 将pro项目拷贝到本地，url1为服务器上pro仓库的地址
cd pro
git remote add -f remote-lib url2    # 从服务器上把要引入的仓库加入进来，命名为remote-lib，url2为服务器上some-lib仓库的地址
git subtree add -P lib remote-lib master    # 将外部仓库的master分支变为本地的文件夹，-P指定文件夹名
cd lib
...    # 修改了外部仓库lib的内容，准备提交
git add .
git commit -m "modify lib"
git subtree push -P lib remote-lib master    # 将修改提交到外部仓库的远程仓库的master分支
git subtree pull -P lib remote-lib master    # 如果服务器上的some-lib修改了，用这句命令进行修改，拉下来会设计到合并问题。
```

Over，服务器上的some-lib已经被修改了，其他引用了some-lib的地方pull下来即可发现。

git subtree的本质上是将另一个仓库的某个commit与本仓库进行合并，所以会产生commit提交，而在选择对方的commit的时候可以使用branch、tag等来指代，比如将对方的develop分支合（或更新）进来，如下：

```bash
git subtree add -P remote-develop remote-lib/develop  # 假设先前已remote add了remote-lib
git subtree pull -P remote-develop remote-lib/develop
```


### 5. Git补充提交内容
__Reference__: [git commit --amend](https://www.atlassian.com/git/tutorials/rewriting-history/git-commit--amend)

有时候在提交的时候会遗漏一些文件，可以通过命令来弥补，以下假设遗漏`todo.txt`。

```bash
git add todo.txt
git commit --amend
```

重新修改commit message后提交即可。


### 6. Git clone指定文件夹名
```bash
git clone url your-folder-name
```


### 7. 重命名当前分支
```
git branch -m new-name
```
