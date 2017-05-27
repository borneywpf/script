# logcat

logcat是简化的android adb logcat，美观而且方便，可以用logcat -h查看用法，如下:
```
logcat [option] [arguments]
-t (TAG1|TAG2|...) 通过grep方式过滤tag 例如: logcat -t "Log|xxx"

-v (TAG1|TAG2|...) 过滤掉无用的tag日志 例如: logcat -v "Log|xxx"

-p (packageName)   通过进程Id过滤日志 例如: logcat -p processName
-b (buffer)        抓取events等日志
-s (TAG1|TAG2|...) 通过adb -s 命令过滤tag
```

# adbshellpull

在平时开发中，如果用的时user版的手机，这时又想查看应用数据，是不是一脸懵逼，这个脚步可以帮到你
```
名称:adbshellpull
概述:android调试过程中，user版本的手机应用数据因为权限的限制无法通过adb shell pull到本地，该脚步的作用就是在user版本的手机中，pull出应用的数据
用法:adbshellpull <应用包名> <本地路径>
例如:adbshellpull com.gionee.bbs /home/borney/tmp 就会将com.gione.bbs data/data中的数据pull到本地/home/borney/tmp目录
```

# slint.py

这个脚步是一个将lint终端检查结果美化和分类的工具，具体可以查看我的[blog](http://thinkdevos.net/blog/20170526/androidzhong-duan-ke-jiao-hu-de-lintjiao-bu-slint/)

# javaswitch

如果在系统中如果安装了多个jdk版本，切换时是不是很麻烦，该脚步就是帮你简化这个切换过程的，将脚步中的PASSWORD改成你自己的用户密码，其中java和javac的编号改成自己的编号就可以随意切换了，比如javaswitch 7就切换到jdk7；java或javac编号查看方法如下:
```
sudo update-alternatives --config java
```

# unusecomponent.py

该脚步主要是查询在AndroidManifest中注册了代码中不存在的组件，放置用户恶意启动，导致应用报错
```
脚本用途：用于检查在manifest中注册了没有实现的android组件
使用方法：第一个参数指定manifest文件，第二个参数指定code目录
```

# psk

有时在终端下想杀死一个进程，但是还要查询进程的pid，有点麻烦，用psk就可以根据关键字杀掉自己想杀掉的进程了，例如:psk java就杀掉了系统中的java进程

# gitreset.py

该脚步对git log的结果进行二次解析，然后查看，并可以将代码恢复到自己想要的版本，例如:gitreset.py 10查看git最近10次修改，然后可以选择自己想恢复的代码版本
