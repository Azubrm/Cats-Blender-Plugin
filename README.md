# Cats Blender Plugin — Blender 5.2 compatibility fork

This fork targets Blender **5.2.2 LTS**, with an installable version range of
Blender 5.0–5.2. It continues the archived
[Team Neoneko Cats](https://github.com/teamneoneko/Cats-Blender-Plugin)
`blender-5x-dev` branch at `cadc04f1c363c45e2647d874b8c3ef864cdc6245`.

**Status: the user reports that 5.2.1 enables without errors, with extension
namespace warnings. Version 5.2.2 addresses those warnings in source.** No
Blender execution or automated tests were run as part of this adaptation, at
the requester's direction. The version range is the intended target, not a
certification that every inherited Cats feature works.

## 中文界面（5.2.3）

Blender 使用简体中文时，CATS 会自动加载内置中文词库，无需联网下载。
也可以在 CATS → 设置与更新（Settings & Updates）→ Cats 语言（Cats Language）
中选择 **简体中文**。切换后保存工程并完全重启 Blender，使面板名称和按钮提示完整生效。

本版补齐了新功能的中文词条，并汉化此前写死为英文的常用界面与操作提示。
FBX、VRM、MMD 等格式名称及骨骼、形态键的实际数据名称保持原样。
独立安装的第三方插件界面由各自的翻译设置控制。

## Install

1. Disable any older Cats installation, then restart Blender to unload it.
2. Download the [Blender 5.2 branch ZIP](https://github.com/Azubrm/Cats-Blender-Plugin/archive/refs/heads/blender-5.2-compat.zip).
3. In Blender, open **Edit → Preferences → Get Extensions**, open the menu,
   and choose **Install from Disk**. Select the ZIP without extracting it.
4. Enable **Cats Blender Plugin**. The **CATS** sidebar is in the 3D View.

When updating from 5.2.1 or earlier, save your work and fully restart Blender
after installation to clear the old globally loaded MMD Tools modules.

Use the ZIP from the compatibility branch; the upstream `Welcome` branch
contains documentation rather than the extension. This is a Blender extension
with `blender_manifest.toml`, not the older legacy add-on ZIP that used the
unsupported `TESTING` support category.

## Changes in this fork

- Version 5.2.3 fills gaps in Simplified Chinese UI translations, translates
  hard-coded interface text, and fixes first-run language detection without
  a settings file. Blender's `zh_HANS` locale maps to `zh_CN`. Partial cached
  dictionaries keep the bundled entries, and missing translations fall back
  to English. Language changes are saved with a restart notice instead of
  automatically reloading every Blender add-on.
- Version 5.2.2 loads bundled MMD Tools inside the extension namespace and
  removes the `extern_tools` addition to `sys.path`, addressing the reported
  top-level-module and search-path policy warnings. Optional bundled Immersive
  Scaler loading also uses the extension namespace.
- Version 5.2.1 fixes installation errors where a sub-panel's parent is not
  registered yet. All panel parent dependencies are now ordered explicitly.
- Allow Blender 5.1 and 5.2 instead of rejecting everything newer than 5.0.
- Update extension metadata and bundle cross-platform Python dependencies.
- Use the extension package identifier for preferences and the extension user
  directory for mutable settings and translation data.
- Update bone visibility/selection, animation-slot handling, and MMD material
  paths for the Blender 5.x APIs.
- Match shape-key menu registration and unregistration.
- Disable the legacy self-updater so archived upstream builds cannot overwrite
  these changes. Install future ZIPs through Blender's extension installer.
- Stop running the legacy parent-directory cleanup during registration.

See [COMPATIBILITY.md](COMPATIBILITY.md) for scope, known limitations, and API
references. Optional third-party importers, Material Combiner, and Immersive
Scaler remain separate dependencies; they are not bundled here.

## Credits and license

Cats was originally developed by Absolute Quantum and contributors, and later
maintained by Team Neoneko. Original copyright and license notices are retained.
The project is distributed under [GPL-3.0](LICENSE); bundled dependencies retain
their own license files inside their wheels and source directories.
