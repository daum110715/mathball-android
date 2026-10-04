# 数学球 · Mathball

用数学数列砸砖块的 pygame 竖屏小游戏,通过 python-for-android 打包成 Android APK。

球从顶部落下,砖块的需求值是 `10^exp`,球值是所选数列的第 n 项。球值够大就砸碎砖块、`n` 加一;不够就按比例扣血、被弹回,同样 `n` 加一 —— 所以球会越滚越大,直到砸穿。

30 条数列分三档(慢速 / 中速 / 快速增长),每条配一个专属技能。支持单人演示和双人对战。

## 构建 APK

由 GitHub Actions 构建,工作流见 [.github/workflows/build.yml](.github/workflows/build.yml)。

```bash
gh workflow run build.yml      # 手动触发
gh run watch                   # 看进度
gh run download --name mathball-debug-apk   # 取产物
```

`requirements` 可以用工作流参数临时覆盖,方便换 Python / pygame 版本重试:

```bash
gh workflow run build.yml -f requirements="python3==3.11.9,pygame"
```

## 本地运行

```bash
pip install pygame
python main.py
```

## 打包相关的改动

相对原始单文件版本,`main.py` 为了跑在 Android 上改了三处:

- **入口改名 `main.py`** —— buildozer 固定找这个文件名,中文模块名在 p4a 里不可靠。
- **`IS_MOBILE` 增加 `ANDROID_ARGUMENT` 判断** —— p4a 编出来的 CPython 里 `sys.platform` 是 `linux` 而不是 `android`,只按 `sys.platform` 判断的话全屏永远不生效。
- **`settings.json` 改写 `ANDROID_PRIVATE`** —— APK 内的脚本目录只读,原先写同目录会静默失败,导致音量、解锁球、砖块指数每次启动重置。

`buildozer.spec` 里另外钉了两处:`android.arch = arm64-v8a`(Android 14 起拒绝只含 32 位原生库的应用,而 buildozer 默认正是 32 位),以及 `python3==3.11.9`(p4a 的 pygame recipe 是 2.1.0,属于 distutils 时代,Python 3.12+ 已移除 distutils)。

## 已知缺失

音频资源(`bgm.ogg`、`sfx_destroy.wav`、`sfx_bounce.wav`)不在仓库里,游戏会静默降级为无声运行。
