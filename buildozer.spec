[app]
title = THAKTECH
package.name = thaktech
package.domain = org.thaktech
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 12.1
requirements = python3,kivy
p4a.fork = kivy/python-for-android
p4a.branch = v2024.01.21
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,NFC
android.archs = arm64-v8a,armeabi-v7a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.allow_backup = True
[buildozer]
log_level = 2
warn_on_root = 1
