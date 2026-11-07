# Aerial 定制桌面 · 雷鸟 / TCL 电视

适用于**雷鸟（FFALCON）**与 **TCL** 电视的定制版 Aerial 桌面。
Aerial 是一个参照 tvOS 设计的 Android TV 桌面：没有广告，开机自动接管，主页即桌面。

本仓库只做两件事：**分发适配雷鸟 / TCL 固件的 guard 版安装包**，以及**说明怎么把它装进电视**。
Aerial 本体由 [pengchujin/aerial-tv](https://github.com/pengchujin/aerial-tv) 开发，本仓库不修改其代码。

## 为什么需要 guard 版

雷鸟 / TCL 固件在 PackageManager 层做了限制：

- 直接 `adb install` 会失败，报 `INSTALL_FAILED_VERIFICATION_FAILURE`
  或 `install apk has be disabled from pm by system default!`；
- 安装器**拒绝声明了 HOME category 的 APK**。

普通版 Aerial 因为要接管主页键，必然声明 HOME，于是被 TCL 安装器挡掉。
guard 版就是针对这个固件行为做的适配版本。

## 适用机型

| 机型 / 平台 | 状态 |
|---|---|
| **雷鸟 FFALCON MT5879**（`tcl_mt5879_cn`，Android 11） | ✅ 实机已验证 |
| **TCL m7642**（Android 9） | ✅ 实机已验证 |
| 其他装了 Aerial 的 Android TV | ⚠️ 大部分可用；「推送安装」仅 TCL / 雷鸟系固件可用 |

## 下载

**[⬇ Aerial-1.86-guard-TCL-MT5879.apk](https://github.com/huli2008/aerial-guard-tcl/releases/latest)**（Release 附件）

| 项 | 值 |
|---|---|
| 包名 | `app.orchard.tv` |
| 版本 | `1.86-guard`（versionCode 118） |
| 最低 / 目标 SDK | 21 / 34 |
| 大小 | 3,159,168 字节 |
| SHA-256 | `bb1e8bc6cab9478035b070f842c4ca37e5737b838e1771bde1e620f20fcd5e36` |
| 签名 | v1 + v2，`CN=Android Debug`，指纹 `e08962dc…74d6685` |

### 校验下载（可选但推荐）

```powershell
# Windows
certutil -hashfile Aerial-1.86-guard-TCL-MT5879.apk SHA256
```

```bash
# macOS / Linux
shasum -a 256 Aerial-1.86-guard-TCL-MT5879.apk
# 或
sha256sum Aerial-1.86-guard-TCL-MT5879.apk
```

输出应当等于上表的 SHA-256；不一致就不要安装。

## 安装

`adb install` 和 `pm install` 在雷鸟 / TCL 上都被固件禁用，所以要走电视自带的**「多屏互动」（T-Cast）**通道——
它由系统以 system 身份安装，能绕过这两道限制。

### 方式一：Aerial 管家（推荐）

配合 [huli2008/aerial-buddy](https://github.com/huli2008/aerial-buddy)（手机端 App，374 KB）：

1. 手机与电视连**同一个 Wi-Fi**，手机装好 Aerial 管家；
2. 管家首页点「扫描」，列表里出现这台电视（状态「待授权」）→ 点它，拍电视「控制中心 → 个性化」页右侧的二维码完成绑定；
3. 点该电视卡片的「安装 APK」→ 选择本页下载的 guard 包 → 电视弹出「安装 Aerial」时按遥控器**右键选「同意」**；
4. 装好后在电视应用列表打开 Aerial，按提示把它设为默认桌面。

装完后同一台电视不用再扫码，以后升级、换壁纸、传屏保视频、打开管理页都在管家卡片上操作。

### 方式二：手动走多屏互动

电视上打开「多屏互动」，手机端选「投屏 / 安装应用」，把 APK 推过去，电视上确认安装。

> 装好后如果主页键仍跳回原桌面，去电视「应用 → 默认应用」把 Aerial 设为桌面；
> 必要时在管家「管理」页里确认桌面守护已开启。

## 与 Aerial 管家组合使用

两个仓库是**上下游关系**，各管一段：

| 仓库 | 负责 | 不负责 |
|---|---|---|
| **aerial-guard-tcl**（本仓库） | 提供 guard 安装包、版本与哈希、机型适配说明 | 传输、安装动作 |
| **[aerial-buddy](https://github.com/huli2008/aerial-buddy)** | 手机端：扫描绑定、T-Cast 推送安装、壁纸/屏保/应用管理 | 提供 Aerial 安装包 |

组合后的链路：

```
手机 Aerial 管家  ──选择/下载──▶  guard APK（本仓库 Release）
        │                              │
        │  T-Cast：TCP 6553            │ 约 3 MB
        ▼                              ▼
     雷鸟 / TCL 电视  ──系统身份安装──▶ Aerial 接管桌面
        ▲
        │  扫码绑定（8790 + token）
        └── 之后：换壁纸、开关屏保、进管理页传照片/视频
```

| 场景 | 操作 |
|---|---|
| 第一次装 Aerial | 管家「安装 APK」→ 选本仓库的 guard 包 |
| 升级 Aerial | 下载新 tag 的 guard 包 → 管家再推一次（同签名可直接覆盖） |
| 日常管理 | 管家卡片：换壁纸 / 管理页 / 刷新状态 |
| 换电视 | 管家「扫描」→ 点新电视 → 扫一次二维码 |

## 升级与覆盖安装

- 新版本请**继续使用本仓库的官方 guard 包**：签名一致才能覆盖安装、保留数据。
- 若混用其他渠道改签名的包，覆盖会失败（`INSTALL_FAILED_UPDATE_INCOMPATIBLE`），必须卸载重装，桌面配置会丢失。
- 卸载 Aerial 会同时清掉它的壁纸/图标/布局设置；升级前可在管家「管理」页导出需要的题库之外内容（Aerial 本身不提供整体导出）。

## 说明

- 本包为**未修改的官方 guard 构建**，原样分发，便于校验与回退；没有加壳、没有改签名。
- 因为是 Android Debug 签名，新版覆盖安装时若签名不一致，需要先卸载旧版。
- 首次接管主页键后，如果系统仍跳回原桌面，请检查电视的「应用 → 默认应用」里 Aerial 是否被设为桌面。

## 版本记录

| 版本 | 内容 |
|---|---|
| v1.0.0 | 首发：Aerial 1.86-guard，适配雷鸟 MT5879 / TCL m7642 |

## 致谢与许可

Aerial 由 [pengchujin](https://github.com/pengchujin) 开发，以 **MIT** 协议发布：
<https://github.com/pengchujin/aerial-tv>。本仓库仅针对雷鸟 / TCL 固件做分发与说明，
不修改其源码。相关文档与脚本同样以 MIT 发布，见 [LICENSE](LICENSE)。
