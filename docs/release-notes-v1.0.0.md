## 这是什么

一套把本地视频打包进 [Aerial](https://github.com/pengchujin/aerial-tv)（`app.orchard.tv`）
Android TV 桌面 APK 的脚本，附一份对 Aerial `1.86-guard` 包的静态结构分析。

## 先说结论

Aerial **不从 APK 内部读取视频**。它的设计是运行期收片：手机浏览器打开电视上的
Aerial 配置页，视频经 `POST /api/videos/send` 传过去，落到 `AerialVideos` 目录，
再配一张 `poster.jpg`。代码里没有"从 assets 读影片"的路径。

所以：

- **只想让电视上有视频** → 用网页界面直接上传，不用重新打包、不用重新签名。
- **确实需要离线分发内置影片的包** → 用本仓库脚本，但必须接受签名变更。

## 附件说明

| 文件 | 说明 |
|---|---|
| `Aerial-1.86-guard-TCL-MT5879.apk` | **未修改的原版基线包**，仅供对照与作为打包脚本的输入。不含任何视频素材。SHA-256 `bb1e8bc6cab9478035b070f842c4ca37e5737b838e1771bde1e620f20fcd5e36` |

本 Release **不提供**已内置影片的成品 APK：其中的影片素材属于第三方版权，
不适合公开分发。请用 `scripts/bundle_videos.py` 加上你自己有权使用的视频自行打包。

## 重新打包的代价

| 问题 | 说明 |
|---|---|
| 无法覆盖升级 | 上游使用作者的 Android Debug 密钥，私钥不公开；重建包必然换签名，安装前须先卸载旧版 Aerial |
| 必须 v2/v3 签名 | manifest 声明 `targetSdkVersion=34`，Android 11+ 只认 v1 签名会报 `INSTALL_PARSE_FAILED_NO_CERTIFICATES` |
| 体积 | 4K H.264 影片很大：实测 5 个短片共 450 MB，成品 APK 453.5 MB |
| 解码能力 | Aerial 自带说明推荐 1080p H.264；4K High@L5.2 在 MT5879 上不一定流畅 |
| 仍不会自动出现 | 影片虽在包里，仍需代码复制到 `AerialVideos`；而 Aerial 的 DEX 方法体经过剥离保护，注入成本很高 |

## 用法

```bash
python scripts/bundle_videos.py \
    --apk    Aerial-1.86-guard-TCL-MT5879.apk \
    --videos ./myvideos \
    --out    aerial-unsigned.apk
```

接着按 `scripts/sign_apk.ps1` 用 uber-apk-signer 完成 zipalign + v1 + v2 + v3 签名。

## 已验证

- 打包脚本对原包 138 个条目逐字节保留（SHA-256 逐个比对，0 差异）
- 删除 3 个 v1 签名文件后重新签名，v1 + v2 + v3 三方案签名者一致、摘要与实际字节吻合
- 成品 APK 通过 zipalign 校验

## 许可

脚本以 MIT 发布。Aerial 本体版权归 [pengchujin](https://github.com/pengchujin)，同为 MIT。
