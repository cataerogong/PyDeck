v0.2.0
===
* 配置增加 `Pre-action` 和 `Post-action`，在执行命令前后运行
* Pre-action、Post-action、command、workdir 中支持宏：`{PYDECK_PATH}`、`{APPID}`
* 配置增加 `Theme` ，支持换主题
* 配置增加特殊 app id (`<RELOAD>`, `<BR>`)，可以简单自定义客户端布局
* 引入 `jQuery-1.12.4`
* 特定功能实现：执行命令后连续截屏并在前端显示
  - 凑合着能用
  - 通过 Post-action 和前端页面配合实现
  - 服务端需要 `nircmd.exe`
  - 代码注释了，默认不启用

v0.1.0
===
* 显示客户端页面
* 客户端点击图标，服务端执行程序
* 配置文件
* 页面模板
