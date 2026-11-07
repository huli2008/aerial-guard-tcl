# Aerial `1.86-guard` 内部结构分析

本文记录我在把视频塞进 Aerial APK 之前做的静态分析。**结论先行：Aerial 不从 APK 内部读取视频**，所以"把 mp4 放进 assets"本身不会让影片出现在电视上。想让它真的播放，请走 `POST /api/videos/send`（见最后一节）。

## 1. 包身份

| 字段 | 值 |
|---|---|
| package | `app.orchard.tv` |
| versionCode / versionName | 118 / `1.86-guard` |
| minSdk / targetSdk | 21 / 34 |
| 主入口 | `app.orchard.tv.MainActivity`（LEANBACK_LAUNCHER + LAUNCHER） |
| 壁纸服务 | `app.orchard.tv.dream.AerialDream`（BIND_DREAM_SERVICE） |
| 原始签名 | v1 + v2，`CN=Android Debug`，SHA-256 `e08962dc…74d6685` |

targetSdk 34 是关键：Android 11+ 要求 targetSdk ≥ 30 的 APK 必须带 **v2/v3** 签名才允许安装。

## 2. 视频从哪来

字符串池里有完整的存储布局线索（DEX 共 19 074 条字符串，UTF-8）：

```
AerialVideos          <- 视频存放目录名
screensaver-videos    <- 设置项
video.mp4             <- 单集影片文件名
poster.jpg            <- 封面
video-frame.jpg       <- 抽帧
getFilms              <- 读取影片的方法名
videoRoom             <- 剩余空间（网页里  / 1e9 显示为 GB）
videos:mine           <- 首页"我的视频"卡片 id
```

配套的日志文案进一步印证这是**运行期收片**而不是 assets：

```
screensaver video upload broke off
could not store a screensaver video
removed a stale upload,
could not keep a video's poster
```

网页端（`assets/web/index.html`，140 KB）里对应的调用：

```js
// 单个文件直接作为 body 发送，电视端边收边落盘
await fetch(base + 'api/videos/send?name=' + encodeURIComponent(file.name),
            { method: 'POST', body: file, headers: pinHeaders() });

// 剩余空间不足就整个跳过
if (!file.size || file.size > (state.videoRoom || 0)) continue;

await api('api/videos/delete', { id: video.id });
```

`base` 取 `location.pathname`，说明这个页面由 App 内嵌 HTTP 服务提供，浏览器只需访问电视的 IP 即可。服务端路由（DEX 字符串）：

```
/api/state  /api/upload  /api/videos/send  /api/videos/delete
/api/wallpaper  /api/screensaver  /api/setting  /api/layout
/api/kids/*  /api/feedback  /api/weather/*  /api/source/*
```

界面文案也写明了容量策略：*"MP4 / MOV, 1080p H.264 recommended. Up to 2 GB each; all films together take at most half the TV's free space."*

## 3. DEX 的"guard"处理

`classes.dex` 头部、`string_ids`、`type_ids`、`method_ids`、`class_defs` 都是合法的，19 074 条字符串可完整解码，但：

- `class_defs` 共 3 555 项，其中只有 **13 项** 的 `class_data_off` 非零；
- 唯一的 `class_data` 段（`data` 区偏移 3 350 527）从第 2 个条目起就超出文件长度；
- 也就是说 **方法体基本被剥离/转移**，无法直接反编译出 `getFilms()` 或 `/api/videos/send` 的实现。

这解释了为什么"只改资源"可行、而"注入代码"很难：没有可编辑的字节码段，注入需要额外挂一个 DEX + ClassLoader，且必须对抗这套保护。**不建议走这条路。**

> 需要说明：以上是静态观察。我没有在电视上做过运行期验证，`AerialVideos` 确切的父目录（内部存储还是外部存储）也未能从被剥离的代码中确认。

## 4. 打包脚本做了什么

`scripts/bundle_videos.py`：

1. 逐条复制原 APK 的所有条目（保持原始压缩方式），未压缩内容逐字节不变；
2. 删除 `META-INF` 下的 v1 签名文件（`MANIFEST.MF` / `*.SF` / `*.RSA`），因为它们无法覆盖新增条目；
3. 把视频以 **`ZIP_STORED`（不压缩）** 写入 `assets/videos/`；
4. 之后必须重新签名（v1 + v2 + v3）。

选择 STORED 的理由：H.264 几乎不可压缩，deflate 只是白耗 CPU；更重要的是**未压缩的 asset 可以用 `AssetManager.openFd()` 拿到文件描述符**，压缩过的大 asset 不行。如果将来真要写代码读取这些影片，这一点是前提。

## 5. 推荐做法：根本不用改包

如果你的目标只是"让电视上有这几个视频"，直接上传即可，**完全不用重新签名**：

1. 电视和手机/电脑连同一个局域网；
2. Aerial 的网页界面在电视 IP 上（`?pin=` 或页面内输入配对码）；
3. 打开 **外观 / 屏保 → 我的视频 → 添加视频**，选择 mp4；
4. 单片上限 2 GB，总量不超过电视剩余空间的一半。

这条路走的是官方通道，签名不变、可以正常升级，也不需要卸载重装。
