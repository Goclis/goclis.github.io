Title: 重装之路  
Slug: the-way-to-reinstall-system  
Date: 2013-12-14  
Tag: windows, linux, reinstall   
Author: Goclis Yao  

### 背景

今天手贱把引导玩坏了。。  
虽然用WinPE重写了MBR成功进入了Win7，但搞了好久都无法引导进Linux。。。
于是决定把系统重装清理一番。。  
（虽然把引导弄好了，但是还是决定先把Win7给重装一番）


### 准备工作

#####备份文件  
这个不用说了，如果头脑发热重装后发现重要的东西都没备份，那就。。。  
我的是双系统，虽然现在只重装Windows，但还是都一起备份了，备份内容大致如下：  

Linux的home目录，暂时只有这个，因为不是服务器，而且自己也没再机子上做很多的配置，所以不在意那些各种目录下的配置文件了，另外还有数据库的备份，使用sql语句导出就好了  
Windows主要备份的是驱动以及一些临时到上面办公产生的文档，下载的软件之类的  

**--Update--**  
突然想到了Linux还有一系列的配置文件需要备份。。比如说mysql的my.cnf文件，nginx的default最好也备份一下，以后直接拿来用  

Ok， 备份完毕，开始干活


### Windows的安装

首先，烧个U盘启动盘。。在Linux下用dd命令试了一发。。但是失败了。。所以默默地滚回Windows使用Ultraiso进行烧录，轻松惬意  
插上U盘，重启进入安装界面，我的电脑只用在开机的时候狂按ESC就可以选择U盘启动进入安装界面了  
有些电脑可能需要按F2，DEL之类的进入BIOS进行修改，不得不说，这ESC真的很方便  

这次安装只给Windows划了80G左右，觉得够系统安装以及一些日常软件使用了，毕竟不是主系统，自己也不是啥升级控。。。  
至于分区，没分，就一个C盘（还一个D盘是之前的E盘，因为上面还有些数据懒得处理，以后会在重装Linux时把它合并到Linux系统下），没分的原因是因为感觉没啥必要，知乎上也有个关于系统是否要分区的文章，不过不了解也不知道是否正确，再做一回跟风汪。。  
接下来，就按步骤安装就行了。。。

装完了，先激活一发吧。。穷孩子只能盗版了T T  
激活完后开始安装一些基础的软件，至于软件哪来。。  
个人是建议自己日常中收集一些装机必备的软件的，比如驱动精灵，文本编辑器（Sublime），压缩工具，还有一些不大不小但是又挺有用的软件  
往移动硬盘里建个文件夹，丢里面，也不会太占内容，没移动硬盘的话在机子硬盘上划一块，烧完U盘后再把它们拷进去  

开始装软件（突然发现个问题。。。系统没自带USB3.0的驱动，还好破机子有2.0的接口，否则移动硬盘还没法开了）。。。

**Ps: Win7刚安装完成后，在安装软件（绝大部分）时会弹出个框问你是否，这是在Vista引入的一个为了安全起见的机制，防止某些软件偷偷地在背后做些坏事，但是对我这种不懂得区分安全与否的人比较鸡肋，还会妨碍在系统盘进行的操作（比如不以管理员模式打开解压缩软件无法解压到C盘），所以先关掉它了。。在控制面板找找应该有（- -#我懒得找所以随便点开个软件触发它，然后在框框里面会有设置，跳过去改了就行了）** 

-【好压】  
先装个解压缩软件是为了把Sublime解压开来记录。。  

-【搜狗输入法】  
不解释  

-【驱动精灵】  
恢复之前备份的驱动，直接驱动管理里面还原就好了。。然后重启电脑吧。。  
果然又一次失败了。。。就没直接从备份里还原成功过！！！次噢！！！  
= =# 先恢复网卡驱动吧，然后再去下吧。。。  
把备份的驱动文件解压了，然后打开设备管理器（计算机-属性），点开网络适配器，如果其中没有无线网卡的话，从**其他设备**中找，然后右键-更新驱动软件程序，手动选择本机的驱动程序，然后定位到解压出来的驱动文件里无线网卡的那个文件夹，然后下一步即可安装驱动  
Ok了，下驱动吧。。。实在不明白为什么备份的驱动无法恢复。。。  
**怒下驱动中。。。。。。。。。**

-【Chrome+Sougou】  
= =# 没浏览器不幸福  
Sougou只是为了它的兼容模式。。。。  

-【Ultraiso】  
烧启动盘用

-【Linux Reader】  
Windows下访问linux文件

-【开发环境】  
JDK  
需要配置[Java环境](http://blog.csdn.net/tianshuai1111/article/details/7367700)  

Python2.7  
直接安装即可  

-【MacType】  
美化字体（个人感觉不错，因为习惯了Linux的字体）

-【Adobe Flash Player】

-【QQ Intl】

-【有道词典(FULL)】

-【Putty+FileZilla】  
服务器开发必备

-【Dropbox】  
上传一些比较小但是重要的文档和代码

-【MdCharm】  
一款markdown编辑器，可视化

差不多都搞定了。。。最后把Linux的引导修复回来就好了，使用LiveCD的方法见Notebook中的Goclis-Linux.md  


### Linux的安装。。。
Linux虽然安装软件配置开发环境相对Windows来说很方便，但是还是有少配置由于不熟悉的原因并不是特别的好进行，所以打算借着这次机会一并记录下来，现在先列出一些要装的软件，以备更换成Elementary OS时安装  
**软件列表：**  
【必备浏览器】Google Chrome & Firefox  
【文本编辑器】Sublime Text 2 & MdCharm  
【IDE】Eclipse & Codeblocks  
【服务器工具】Filezilla & Putty & Remote  
【磁盘管理】Disks（Ubuntu13.04是预装的，不确定Elementary有没有预装）  
【BT下载】Transmission（兼容学校PT站）  
【开发环境】Python & Java & MySQL & Nginx  
【电源管理】Bumblebee  

大概就上面这些，准备开始安装。。先规划下分区。。因为仍旧不是特别明确各个分区的作用，决定如下进行：  
/  
/home  
swap  

OK，开始！！！  

= =# 装完了。。。蛋疼才真正的开始。。。  
因为没注意现在装的是64bit的系统，直接把32位的.deb包拿来安装。。结果导致apt-get直接被搞得乱七八糟。。没办法，使用apt-get install -f修复吧。。才发现更新源没有换。。慢的一米。。受不了终止了上网试着手动更换源。。。  

#####更换软件源
```bash
sudo cp /etc/apt/source.list /etc/apt/source.list.bak # 备份原先的软件源
sudo scratch-text-editor /etc/apt/source.list # 使用文本编辑器打开(Elementary OS预装Scratch)
```
把文本替换成下面的文本(163 ubuntu 12.04的源)
```
deb http://mirrors.163.com/ubuntu/ precise main restricted
deb-src http://mirrors.163.com/ubuntu/ precise main restricted
deb http://mirrors.163.com/ubuntu/ precise-updates main restricted
deb-src http://mirrors.163.com/ubuntu/ precise-updates main restricted
deb http://mirrors.163.com/ubuntu/ precise universe
deb-src http://mirrors.163.com/ubuntu/ precise universe
deb http://mirrors.163.com/ubuntu/ precise-updates universe
deb-src http://mirrors.163.com/ubuntu/ precise-updates universe
deb http://mirrors.163.com/ubuntu/ precise multiverse
deb-src http://mirrors.163.com/ubuntu/ precise multiverse
deb http://mirrors.163.com/ubuntu/ precise-updates multiverse
deb-src http://mirrors.163.com/ubuntu/ precise-updates multiverse
deb http://mirrors.163.com/ubuntu/ precise-backports main restricted universe multiverse
deb-src http://mirrors.163.com/ubuntu/ precise-backports main restricted universe multiverse
deb http://mirrors.163.com/ubuntu/ precise-security main restricted
deb-src http://mirrors.163.com/ubuntu/ precise-security main restricted
deb http://mirrors.163.com/ubuntu/ precise-security universe
deb-src http://mirrors.163.com/ubuntu/ precise-security universe
deb http://mirrors.163.com/ubuntu/ precise-security multiverse
deb-src http://mirrors.163.com/ubuntu/ precise-security multiverse
deb http://extras.ubuntu.com/ubuntu precise main
deb-src http://extras.ubuntu.com/ubuntu precise main
```
保存后更新源
```bash
sudo apt-get update
```
更多的源可以上网查。。。[更新源的参考资料](http://my.oschina.net/rockbaby/blog/14711)

= =# 搞定源了。。把apt先修复后继续装东西。。为了写文本先装个[Sublime](http://www.sublimetext.com/2)，出于移植性考虑。。这次下的是解压包，而不是直接使用.deb包，安装也查了一定的[资料](http://www.sublimetext.com/2)，如下：
#####安装配置Sublime Text 2
在官网下载解压包后，解压并移到/opt目录下
```bash
tar -xf sublime.tar.bz2 # 不一定是这个名字。。
mv sublime/ /opt # 名字也不一定
sudo ln -s /opt/sublime/sublime_text /usr/bin/sublime # 建立硬链以便在terminal中使用
```
现在在Terminal中打sublime已经可以启动了，为了下一步添加到Dock上，得先在/usr/share/applications下创一个.desktop
```
sudo sublime /usr/share/applications/sublime.desktop
```
输入以下内容，注意自行替换Icon的目录，即图标
```
[Desktop Entry]
Version=1.0
Name=Sublime Text 2
GenericName=Text Editor

Exec=sublime
Terminal=false
Icon=/opt/Sublime/Icon/48×48/sublime_text.png
Type=Application
Categories=TextEditor;IDE;Development
X-Ayatana-Desktop-Shortcuts=NewWindow

[NewWindow Shortcut Group]
Name=New Window
Exec=sublime -n
TargetEnvironment=Unity
```
现在就可以在Applications里看到Sublime了。。  
接下来创建**右键启动**，即选择文件点击右键时可选择使用Sublime来打开，具体如下：
```
sudo sublime ~/.local/share/applications/mimeapps.list
```
在最后一行加上
```
text/plain=sublime.desktop
```
在终端中
```
sudo sublime /usr/share/applications/defaults.list
```
将原先的默认编辑器(比如gedit.desktop)全部替换为sublime.desktop即可  

至于**添加到dock**上，直接从applications上拖到dock上添加即可(对Elementary可行)

最后配置一下Sublime的Package Control  
在Sublime中按Ctrl+`调出console，输入以下代码后回车
```
import urllib2,os;pf='Package Control.sublime-package';ipp=sublime.installed_packages_path();os.makedirs(ipp) if not os.path.exists(ipp) else None;open(os.path.join(ipp,pf),'wb').write(urllib2.urlopen('http://sublime.wbond.net/'+pf.replace(' ','%20')).read())
```
重启Sublime Text 2，如果在Perferences->package settings中看到package control这一项，则安装成功，按下Ctrl+Shift+P调出命令面板，输入install 调出 Install Package 选项并回车，然后在列表中选中要安装的插件  
**一些插件：**  
HTMLBeautify  
[InputHelper](https://github.com/xgenvn/InputHelper)（为了输入中文。。。自行打开~/.config/sublime-text-2/Packages/Users/Default(Linux).sublime-keymap修改快捷键）  

**个人的配置：**
打开Preference->Key Bindings - User，在[]里添加以下内容
```
{ "keys": ["ctrl+2"], "command": "move_to", "args": {"to": "eol", "extend": false} }
```
即使用ctrl+2来使光标移到本行末尾  


搞定编辑器后继续装一些软件吧  
#####Chrome  
直接在官网下.deb包，然后使用sudo dpki -i xxx.deb安装即可，注意下64位的包，即**amd64**  

#####Haroopad
一款markdown的编辑器，还不错，安装同chrome  

#####Dropbox
同Chrome安装  

#####安装JDK
0.0 不确定是不是这个。。。
```
sudo apt-get install openjdk-7-jdk
```

#####安装Bumblebee
```
sudo add-apt-repository ppa:bumblebee/stable
sudo apt-get update
sudo apt-get install bumblebee-nvidia primus
sudo reboot

lspci grep | VGA
```
如果显示如下则成功了。。
```
00:02.0 VGA compatible controller: Intel Corporation 2nd Generation Core Processor Family Integrated Graphics Controller (rev 09)
01:00.0 VGA compatible controller: NVIDIA Corporation Device 1058 (rev ff)
```
ff表示已经关闭  

#####安装Virtualbox
Software Center里搜索Install就行了。。。

#####安装Firefox
Software Center里搜索Install就行了。。。  
主要还是要装一些**插件(Add-ons)**开发使用，如下：  
Httpfox  
Firebug  
XPather  
Firecookie  
Vimium  

#####安装Android开发环境
从[Google官网](http://developer.android.com/sdk/index.html#download)直接下的集成包，里面包含Eclipse和SDK  
下载后解压即可使用，打开新建一个项目时发现下面的问题
```
error while loading shared libraries: libz.so.1: cannot open shared object file: No such file or directory
```
上网搜索解决方案。。是因为系统是64位的原因，[解决方案](http://askubuntu.com/questions/147400/problems-with-eclipse-and-android-sdk)如下:
```
sudo apt-get update
sudo apt-get install ia32-libs
```
Ok，解决问题。。由于是.zip包，所以得自己建desktop了。。参照sublime.desktop的建立
```
sudo mv adt-bundle-linux-x86_64-20131030/ /opt/eclipse(with\ android)
ln -s /opt/eclipse\(with\ android\)/eclipse/
sudo sublime /usr/share/applications/eclipse.desktop
#Content
[Desktop Entry]
Version=1.0
Name=Eclipse
GenericName=IDE

Exec=eclipse
Terminal=false
Icon=/opt/eclipse(with android)/eclipse/icon.xpm
Type=Application
Categories=TextEditor;IDE;Development
X-Ayatana-Desktop-Shortcuts=NewWindow

[NewWindow Shortcut Group]
Name=New Window
Exec=eclipse -n
TargetEnvironment=Unity
```
这样就可以在Applications里看到Eclipse了。。打开后要在Preference里**修改SDK的目录**

#####安装fcitx
= =# 一直都用的ibus，但是确实很多地方不如人意。。。也尝试过很多次更换成fcitx，但是都失败了。。这次再来一发试试。。。  
按[教程](http://ningyubuaa.sinaapp.com/2012/10/23/ubuntu-12-04-%E5%AE%89%E8%A3%85fcitx%E8%BE%93%E5%85%A5%E6%B3%95/)来。。。  
```
sudo apt-get install fcitx
im-switch #调出输入法管理器选择界面，选择fcitx
```
注销后再登录即可，接下来配置fcitx，在Terminal输入
```
fcitx-configtool
```
首先修改置顶的输入法，在Input Method Configuration这一栏，将pinyin置顶  
其次修改些基本配置，在Global Config->Hotkey里面将第三栏Htokey of Swtiching Chinese and English Mode改为L_SHIFT，即左shift切换中英文  
还有Global Config->Program里面将Default Input Method Mode修改为Active好像就可以让fcitx自启动第一个输入法了。。。  
然后点击Apply注销再登录后即可生效。。。  
其他配置自己改吧。。  

竟然安装成功了。。。

#####Filezilla & Putty & Remote & Transmission & Disk Utility
Software Center就有。。

#####Mysql
不想折腾就在Software Center里装吧。。  
不过正规地还是从官网下载源码，编译安装，不过麻烦。。  
0.0 竟然没提示设置密码。。。。按下面的法子破。。
```
mysqladmin -u root password
New password:
Confirm new password: 
```
OK，密码已设置完毕，用它登录就好了
= =#编码实在没折腾出来。。。打算用phpmyadmin来修改了。。。

#####Nginx+phpmyadmin
网上找来的[教程](http://hi.baidu.com/sudoer/item/479347788e7364376e29f6f8)，很不错，可用。。  

安装nginx
```
sudo add-apt-repository ppa:nginx/stable
sudo apt-get update
sudo apt-get install nginx
```

安装php
```
sudo apt-get install php5-cli php5-cgi php5-fpm php5-mcrypt php5-mysql
```

配置Nginx
```
sudo sublime /etc/nginx/site-available/default
```
进行如下修改
```
server {
	listen 80 default_server;
	listen [::]:80 default_server ipv6only=on;

	root /var/www;
	index index.html index.htm index.php index;

	# Make site accessible from http://localhost/
	server_name localhost;

	location / {
		# First attempt to serve request as file, then
		# as directory, then fall back to displaying a 404.
		try_files $uri $uri/ =404;
		# Uncomment to enable naxsi on this location
		# include /etc/nginx/naxsi.rules
	}

	# Only for nginx-naxsi used with nginx-naxsi-ui : process denied requests
	#location /RequestDenied {
	#	proxy_pass http://127.0.0.1:8080;    
	#}

	#error_page 404 /404.html;

	# redirect server error pages to the static page /50x.html
	#
	#error_page 500 502 503 504 /50x.html;
	#location = /50x.html {
	#	root /usr/share/nginx/html;
	#}

	# pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
	#
	location ~ \.php$ {
		fastcgi_split_path_info ^(.+\.php)(/.+)$;
	#	# NOTE: You should have "cgi.fix_pathinfo = 0;" in php.ini
	#
	#	# With php5-cgi alone:
		fastcgi_pass 127.0.0.1:9000;
	#	# With php5-fpm:
	#	fastcgi_pass unix:/var/run/php5-fpm.sock;
		fastcgi_index index.php;
		include fastcgi_params;
	}

	# deny access to .htaccess files, if Apache's document root
	# concurs with nginx's one
	#
	#location ~ /\.ht {
	#	deny all;
	#}
}
```
修改完后nginx就会将/var/www目录(可能需要手动创建)下的文件进行相应的处理了，当然有相应规则，比如
```
location ~ \.php$ {
	# ...
}
```
这段就是处理.php脚本的  

安装phpmyadmin
```
sudo apt-get install phpmyadmin
```
安装完后执行
```
sudo ln -s /usr/share/phpmyadmin /var/www/phpmyadmin
```
注意，phpmyadmin后面没有"/"  
然后在浏览器中输入http://localhost/phpmyadmin即可

#####安装python pip
[安装指南](http://www.pip-installer.org/en/latest/installing.html)
```
sudo apt-get install python-pip
```

#####管理启动项
使用update-rc.d关掉服务器类型的软件的启动项
```
sudo update-rc.d -f nginx remove
sudo update-rc.d -f apache2 remove
sudo update-rc.d -f php-fpm5 remove
```
另外有个gui界面的bum，不知道怎么用。。。。  


基本搞定了～～有啥以后再加～






