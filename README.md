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

  参见 [MANUAL.md](MANUAL.md)

## 感谢

* [小众软件](https://www.appinn.com/)
* [python](https://www.python.org/)
* [bottle](https://bottlepy.org/)
* [Paste](https://pypi.org/project/Paste/)
* [PyYAML](https://pyyaml.org/)
* [chardet](https://github.com/chardet/chardet)
* [PyInstaller](https://github.com/pyinstaller/pyinstaller)