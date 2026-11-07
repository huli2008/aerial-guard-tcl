# Aerial 定制桌面 · 雷鸟 / TCL 电视

适用于**雷鸟（FFALCON）**与 **TCL** 电视的定制版 Aerial 桌面。
Aerial 是一个参照 tvOS 设计的 Android TV 桌面：没有广告，开机自动接管，主页即桌面。

本仓库提供适配这两类固件的 **guard 版**安装包。

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

**[⬇ Aerial-1.86-guard-TCL-MT5879.apk](https://github.com/huli2008/aerial-guard-tcl/releases/latest)**

| 项 | 值 |
|---|---|
| 包名 | `app.orchard.tv` |
| 版本 | `1.86-guard`（versionCode 118） |
| 最低 / 目标 SDK | 21 / 34 |
| 大小 | 3,159,168 字节 |
| SHA-256 | `bb1e8bc6cab9478035b070f842c4ca37e5737b838e1771bde1e620f20fcd5e36` |
| 签名 | v1 + v2，`CN=Android Debug`，指纹 `e08962dc…74d6685` |

## 安装

`adb install` 和 `pm install` 在雷鸟 / TCL 上都被固件禁用，所以要走电视自带的**「多屏互动」（T-Cast）**通道——
它由系统以 system 身份安装，能绕过这两道限制。

两种方式：

1. **用 [Aerial 管家 aerial-buddy](https://github.com/huli2008/aerial-buddy)（推荐）**
   手机与电视同一 Wi-Fi → 扫描或扫码绑定 → 「安装 APK」选择本页下载的包 →
   电视上按「右键 → 同意」即装。
2. **手动走多屏互动**：电视上打开多屏互动，手机端选「投屏 / 安装应用」，把 APK 推过去。

装完后在电视的应用列表里打开 Aerial，按提示把它设为默认桌面。

## 说明

- 本包为**未修改的官方 guard 构建**，原样分发，便于校验与回退；没有加壳、没有改签名。
- 因为是 Android Debug 签名，新版覆盖安装时若签名不一致，需要先卸载旧版。
- 首次接管主页键后，如果系统仍跳回原桌面，请检查电视的「应用 → 默认应用」里
  Aerial 是否被设为桌面。

## 致谢与许可

Aerial 由 [pengchujin](https://github.com/pengchujin) 开发，以 **MIT** 协议发布：
<https://github.com/pengchujin/aerial-tv>。本仓库仅针对雷鸟 / TCL 固件做分发与说明，
不修改其源码。相关文档与脚本同样以 MIT 发布，见 [LICENSE](LICENSE)。
