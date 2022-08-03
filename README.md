# PyDeck

让老手机老平板老Kindle发挥余热，给电脑增加功能键 - 极端低配/无售后/功能全靠DIY版 StreamDeck

## 缘起

[小众软件论坛](http://meta.appinn.net/) 的一个帖子：[能代StreamDeck！免费、开源软件macro deck](https://meta.appinn.net/t/topic/34615)。

看了之后，感觉极端低配版的 StreamDeck 很容易实现，就是写个 Web 服务器，根据用户点击链接在后台执行相应的程序。

小众论坛的 @dog 写了不少有趣又有用的小工具，我也用过，也学到了不少。

他在这个贴子里感叹自己之前搞的手机电脑交互不好用。

家里正好新装一台长期开机的小电脑，不接显示器键盘，每次操作都要开电脑连远程桌面。

于是就有了这个。

## **警告**

因为是一天手搓的极端低配版，没有任何安全防护措施，只能在家里局域网内使用，服务器千万不能开放到互联网上，否则别人连上来就可以点击启动电脑内的程序，更别说高手说不定就能黑入电脑了。

## 免责

既然叫 `极端低配/无售后/功能全靠DIY版`，那肯定是 `使用后果自负` 啦！:P

我写这个是为了自己家里长期开机的电脑用，一些常用的操作就不用连显示器键盘或者连远程桌面了。

## 使用说明

* `PyDeck.yaml`

  ```yaml
  Port: Web 服务侦听端口，防火墙要开放这个端口，否则其他设备无法连接 Web 服务。
  Title: 面板名称
  Theme: 页面主题，对应 static\css 下的 css 文件名，不包含后缀 (.css)
  Icons Per Line: 每行应用图标个数
  Show Label: 是否显示应用名称，true|false
  Pre-action: 启动 app 前执行命令，可有可无可为空。
  Post-action: 启动 app 后执行命令，可有可无可为空。
  Apps: 应用列表
  -   id: 应用ID，纯英文字符串
      name: 应用显示名称
      icon: 应用图标文件名，存放目录：PyDeck\icon
      command: 应用实际执行命令
      workdir: 应用起始路径
  ```
  + App id 有两个特殊值：

     `<RELOAD>` : 重新载入后台设置按钮，点击可以重新载入 PyDeck.yaml 和 PyDeck.stpl，对应 URL: `/reload`

     `<BR>` : 强制换行

  + 所有字符串值最好都加英文单引号(')，字符串里有双引号 (") 的一定要加单引号。

  + Pre-action、Post-action、command、workdir 中，如果文件名或路径中有空格，需要加双引号。

  + command 和 workdir 的正确格式：

    可以认为在 PyDeck 服务器中有一个隐藏的 cmd 窗口，执行
    
    ```shell
    START "[PyDeck] CMD" /I /D workdir command
    ```

    因此，如果将 command 和 workdir 填入其中后，在普通 cmd 窗口中可以运行成功，那么基本上 PyDeck 也可以成功执行命令。

  + Pre-action、Post-action、command、workdir 支持以下宏：

    `{PYDECK_PATH}` : 运行时会替换成 PyDeck 根目录

    `{APPID}` : 运行时会替换成相应的 appid

* `PyDeck.stpl`

  Deck 页面模板 (HTML)，可以自己修改。

  > 注意： `{{ }}` 中和 `%` 后的是 Python 代码。

* `icon\` 目录

  子目录 `icon` 里放的是应用图标文件，浏览器支持显示的格式都行，最好是正方形图片。

  > `icon\RELOAD.png` 是 PyDeck 自用的，不要删除，除非修改了 `PyDeck.stpl`。

* `static\` 目录

  会映射到 `http:\\IP:Port\static\`，包括下面**所有**子目录和文件。

* 客户端浏览器要求

  页面用了 jQuery 1.12.4 和简单的 CSS，至少在我的 **iPad 1 (iOS 5.1.1)** 的 Safari 浏览器上没问题。

## 感谢

* [小众软件](https://www.appinn.com/)
* [python](https://www.python.org/)
* [bottle](https://bottlepy.org/)
* [Paste](https://pypi.org/project/Paste/)
* [PyYAML](https://pyyaml.org/)
* [chardet](https://github.com/chardet/chardet)
* [PyInstaller](https://github.com/pyinstaller/pyinstaller)