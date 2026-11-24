[app]
title = THAKTECH
package.name = thaktech
package.domain = org.thaktech
source.dir = .
source.include_exts = py,png,jpg,kv,json,ttf,txt
version = 13.0
requirements = python3==3.11.9,kivy==2.2.1,pyjnius
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/icon.png
android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.archs = armeabi-v7a,arm64-v8a,x86,x86_64
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.allow_backup = False
android.presplash_color = #0A0F1E
p4a.branch = v2024.01.21
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
