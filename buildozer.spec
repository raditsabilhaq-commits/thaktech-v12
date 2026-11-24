[app]
title = THAKTECH
package.name = thaktech
package.domain = org.thaktech
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas
version = 13.0
requirements = python3,kivy==2.3.1,pyjnius
p4a.branch = v2024.01.21
p4a.bootstrap = sdl2
orientation = portrait
fullscreen = 0

# INI UDAH GUA BENERIN PAKE FILE LU
icon.filename = %(source.dir)s/Icon.jpg

android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.archs = armeabi-v7a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.allow_backup = False
android.presplash_color = #0A0F1E

[buildozer]
log_level = 2
warn_on_root = 1
