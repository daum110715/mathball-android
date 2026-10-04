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

# p4a 的 pygame recipe 停在 2.1.0，只支持到 Python 3.10
# （它 include 了 longintrepr.h，而该头文件自 3.11 起被移进 Include/cpython/）
# hostpython3 与 python3 必须同版本，只钉一个会被 p4a 直接拒绝
requirements = hostpython3==3.10.14,python3==3.10.14,pygame

orientation = portrait
fullscreen = 1

icon.filename = %(source.dir)s/icon.png
android.presplash_color = #0F0F1E

# Android 14+ 不再允许只含 32 位原生库的应用
android.archs = arm64-v8a
android.accept_sdk_license = True

p4a.bootstrap = sdl2

log_level = 2
warn_on_root = 0
