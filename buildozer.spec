[app]
title = THAKTECH
package.name = thaktech
package.domain = org.thaktech
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 13.0
requirements = python3,kivy==2.3.1
p4a.branch = v2024.01.21
p4a.bootstrap = sdl2
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/icon.png.jpg
android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.allow_backup = True
android.presplash_color = #0A0F1E

[buildozer]
log_level = 2
warn_on_root = 1
