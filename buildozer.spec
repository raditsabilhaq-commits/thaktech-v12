[app]
title = THAKTECH
package.name = thaktech
package.domain = org.thaktech
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 13.0
requirements = python3,kivy
p4a.branch = master
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/icon.png
android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.archs = arm64-v8a,armeabi-v7a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.allow_backup = True
android.gradle_dependencies = 

[buildozer]
log_level = 2
warn_on_root = 1
