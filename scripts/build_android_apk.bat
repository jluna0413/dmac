@echo off
echo Building DMac Android APK...

cd flutter-app

echo Cleaning previous build...
flutter clean

echo Getting dependencies...
flutter pub get

echo Building APK...
flutter build apk --release

echo APK built successfully!
echo You can find the APK at: build\app\outputs\flutter-apk\app-release.apk

echo Copying APK to the root directory...
copy build\app\outputs\flutter-apk\app-release.apk ..\dmac-release.apk

echo Done! The APK is now available at: dmac-release.apk
