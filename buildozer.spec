[app]

title = 数学球
package.name = mathball
package.domain = com.daum110715

source.dir = .
source.include_exts = py,png,jpg,ogg,wav,mp3,ttf,json
source.exclude_dirs = bin,.buildozer,.github,.git
source.exclude_patterns = *.pyc,*.pyo,buildozer.spec,README.md

version = 0.1.0
android.numeric_version = 1

# pygame 2.1.0 是 distutils 时代的产物，Python 3.12+ 已移除 distutils，必须钉在 3.11
requirements = python3==3.11.9,pygame

orientation = portrait
fullscreen = 1

icon.filename = %(source.dir)s/icon.png
android.presplash_color = #0F0F1E

# Android 14+ 不再允许只含 32 位原生库的应用
android.arch = arm64-v8a
android.accept_sdk_license = True

p4a.bootstrap = sdl2

log_level = 2
warn_on_root = 0
