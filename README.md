# Aerial 视频整合工具 / Aerial video bundling toolkit

把本地视频打包进 [Aerial](https://github.com/pengchujin/aerial-tv)（`app.orchard.tv`）
Android TV 桌面 APK 的小工具，外加一份对 Aerial `1.86-guard` 包结构的静态分析。

配套 App：[Aerial 管家 aerial-buddy](https://github.com/huli2008/aerial-buddy)
（手机端扫码绑定、换壁纸、推送安装 Aerial）。

> 与 Aerial 作者无关，是非官方脚本集合。Aerial 本体以 MIT 协议发布。

## 重要结论（请先读这段）

**把 mp4 放进 `assets/` 不会让影片出现在电视上。** Aerial 的设计是运行期收片：
手机浏览器打开电视上的 Aerial 网页界面，视频经 `POST /api/videos/send` 传过去，
落到内部的 `AerialVideos` 目录，再配一张 `poster.jpg`。代码里没有任何
"从 APK assets 读取影片"的路径。

所以：

- **只想让电视上有视频** → 走网页上传，几秒钟搞定，**不用重新打包、不用重新签名**，
  详见 [`docs/analysis.md`](docs/analysis.md) 第 5 节。
- **确实需要离线分发一个内置影片的 APK**（比如给不会用手机上传的人）→ 用本仓库的脚本，
  但要接受下面的代价。

## 重新打包的代价

| 问题 | 说明 |
|---|---|
| **无法覆盖升级** | 上游用作者自己的 Android Debug 密钥签名，私钥不公开，重建包必然换签名。安装前必须先卸载旧版 Aerial，设置会被清空。 |
| **必须 v2/v3 签名** | manifest 声明 `targetSdkVersion=34`，Android 11+ 只认 v1 签名会报 `INSTALL_PARSE_FAILED_NO_CERTIFICATES`。 |
| **体积** | 4K H.264 影片很大。示例：5 个 4K 短片共 450 MB，成品 APK 453.5 MB。 |
| **解码能力** | Aerial 界面自述推荐 1080p H.264；4K High@L5.2 在 MT5879 这类电视芯片上不一定流畅播放。 |
| **仍然不会自动出现** | 即使影片就在包里，也还需要一段代码把它们复制到 `AerialVideos`。而 Aerial 的 DEX 方法体被剥离保护过，注入成本很高（见分析文档第 3 节）。 |

## 用法

```bash
python scripts/bundle_videos.py \
    --apk   Aerial-1.86-guard-TCL-MT5879.apk \
    --videos ./myvideos \
    --out   aerial-unsigned.apk
```

脚本会保留原包每一个条目的未压缩内容（逐字节一致），只删除 `META-INF` 下的 v1 签名文件，
并把视频以 `ZIP_STORED`（不压缩）写入 `assets/videos/`。

接着签名（PowerShell，需要 JDK 17）：

```powershell
# 详见 scripts/sign_apk.ps1
java -jar uber-apk-signer-1.3.0.jar --apks aerial-unsigned.apk --overwrite `
     --ks aerial.keystore --ksAlias aerial --ksPass YOURPASS --ksKeyPass YOURPASS
```

## 仓库结构

```
scripts/bundle_videos.py   打包脚本（纯标准库，无第三方依赖）
scripts/sign_apk.ps1       签名步骤与说明（zipalign + v1 + v2 + v3）
docs/analysis.md           Aerial 1.86-guard 的静态结构分析
```

## 版权说明

本仓库**不包含** Aerial 的 APK、二进制或任何第三方影片素材。请自行从
[官方 Releases](https://github.com/pengchujin/aerial-tv/releases) 获取 Aerial，
并使用你有权使用的视频文件。修改后的包仅供个人使用，请遵守 Aerial 的 MIT 协议
（保留版权声明）以及你所使用视频素材的授权条款。

## 许可

脚本部分以 MIT 协议发布，见 [LICENSE](LICENSE)。
Aerial 本身版权归 [pengchujin](https://github.com/pengchujin) 所有，同样为 MIT 协议。
