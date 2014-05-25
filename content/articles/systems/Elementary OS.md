Title: Elementary OS  
Date: 2014-04-24  
Catagory: 系统配置  
Tags: linux  
Author: Goclis Yao  

记录一下对Elementary OS的每一步配置，持续更新。

###系统安装
省略。。

###源的修改
去网上查查相应的源，修改
```
/etc/apt/source.list
```
记得备份一下
```
cp /etc/apt/source.list /etc/apt/source.list.bak
```
163的源
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

###语言支持
因为选择的是英文安装，并没有中文模块

System Settings -> Language Support 里面可以安装，选择 Chinese (Simplified)，
安装完后选择 Keyboard-Input-Helper 为 ibus

这里得启动ibus才能使用中文输入法，这里顺便讲讲设置ibus为开机启动

首先找到ibus-daemon的路径
```
which ibus-daemon # /usr/bin/ibus-daemon
```
然后在 System Settings -> Startup Applications 里添加一项， 路径为 /usr/bin/ibus-daemon 即可

接着要对ibus进行下配置（preference），添加一项中文输入法，设置下字体和大小，再共享到全局就好了

###安装Chrome
Chrome占了Web开发狗生活的一大部分。。

去官网或者自己以前留下的.deb包

```
sudo dpkg -i ****.deb
```

ok

####插件
其他插件基本都会被同步，主要是配置下GAE就好了

拿到GAE的安装包（之前用的就可以），然后放到home目录下就好了，假设路径为
```
/home/user/gae/
```
同ibus一样设置开机启动，不过命令改为
```
python /home/user/gae/local/proxy.py
```

####chrome app
```
google-chrome-stable --app=http://stackedit.io
```

###Sublime Text 2
__源安装__

```
add-apt-repository ppa:webupd8team/sublime-text-2
apt-get update
apt-get install sublime-text
```

__包安装__

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


__配置Sublime__

在Sublime中按Ctrl+`调出console，输入以下代码后回车
```
import urllib2,os;pf='Package Control.sublime-package';ipp=sublime.installed_packages_path();os.makedirs(ipp) if not os.path.exists(ipp) else None;open(os.path.join(ipp,pf),'wb').write(urllib2.urlopen('http://sublime.wbond.net/'+pf.replace(' ','%20')).read())
```
重启Sublime Text 2，如果在Perferences->package settings中看到package control这一项，则安装成功，按下Ctrl+Shift+P调出命令面板，输入install 调出 Install Package 选项并回车，然后在列表中选中要安装的插件  

**一些插件：**  

- HTMLBeautify  
- [InputHelper](https://github.com/xgenvn/InputHelper)（为了输入中文。。。自行打开~/.config/sublime-text-2/Packages/InputHelper/Default(Linux).sublime-keymap修改快捷键）  

**个人的配置：**
打开Preference->Key Bindings - User，在[]里添加以下内容
```
{ "keys": ["ctrl+2"], "command": "move_to", "args": {"to": "eol", "extend": false} }
```
即使用ctrl+2来使光标移到本行末尾  

Preference->Settings-Default里
```
"translate_tabs_to_spaces": true, // 把这项设置了
```

__Problems__

= =# inputhelper弹不出来。。

手动使用shift+ctrl+p调用后发现
```
Traceback (most recent call last):
  File "./sublime_plugin.py", line 362, in run_
  File "./inputhelper.py", line 22, in run
  File ".\subprocess.py", line 633, in __init__
  File ".\subprocess.py", line 1139, in _execute_child
OSError: [Errno 13] Permission denied
```
大概就是权限不够吧。。

然后就自己跑到InputHelper的安装目录（~/.config/sublime text 2/Packages/InputHelper/

真正被调用的是这个目录下lib里的linux_text_input_gui.py
```
python linux_text_input_gui.py
```
OK，确实弹出来了。。

这里我大概猜测是调用了subprocess.py的进程没有权限执行linux_text_input_gui.py，所以改它的权限吧
```
chmod 777 linux_text_input_gui.py  # 不知道多少好。就给全部了。。755 is enough
```
然后再到shift+ctrl+p里执行，成功弹出！！快捷键也OK～～～

###Dropbox
.deb安装

###Mysql
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

###Nginx+phpmyadmin
网上找来的[教程](http://hi.baidu.com/sudoer/item/479347788e7364376e29f6f8)，很不错，可用。。  

__安装nginx__
```
sudo add-apt-repository ppa:nginx/stable
sudo apt-get update
sudo apt-get install nginx
```

__安装php__
```
sudo apt-get install php5-cli php5-cgi php5-fpm php5-mcrypt php5-mysql
```

__配置Nginx__
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

__安装phpmyadmin__
```
sudo apt-get install phpmyadmin
```
安装完后执行
```
sudo ln -s /usr/share/phpmyadmin /var/www/phpmyadmin
```
注意，phpmyadmin后面没有"/"  
然后在浏览器中输入http://localhost/phpmyadmin即可

###安装python pip
[安装指南](http://www.pip-installer.org/en/latest/installing.html)
```
sudo apt-get install python-pip
```

###管理启动项
使用update-rc.d关掉服务器类型的软件的启动项
```
sudo update-rc.d -f nginx remove
sudo update-rc.d -f apache2 remove
sudo update-rc.d -f php-fpm5 remove
```
另外有个gui界面的bum，不知道怎么用。。。。  

###安装System monitor & System load Indicator
软件中心就有，后者可以加到系统启动

###安装Node.js
下载源码包
```
tar -xzvf node-v0.10.26.tar.gz
cd node-v0.10.26
sudo make  # 前提安装了g++
sudo make install 
```

###安装新立得
```
sudo apt-get install synaptic
```

###安装git
```
sudo apt-get install git

git config --global user.name "Goclis Yao"
git config --global user.email "goclisyyh@gmail.com"
```

###安装atom-text-editor
```
sudo add-apt-repository ppa:webupd8team/atom
sudo apt-get update
sudo apt-get install atom
```