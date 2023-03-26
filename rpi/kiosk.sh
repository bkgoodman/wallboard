#!/bin/sh
export DISPLAY=:0
#xset -dpms
xset s off
xset s noblank
unclutter &

ipv4=`ip a | grep wlan0 | grep inet | awk -F ' ' '{print \$2}'`
echo "{\"addr\":\"$ipv4\"}" > addr.json


#URL='https://1tz7enzkk9.execute-api.us-east-1.amazonaws.com/TEst1/bkg_esp_iot_mqtt?page=pooltemp.html'
#URL=kiosk.html
URL=/home/bkg/wallboard/rpi/shopbot.html
#URL=XmasKiosk.html
#chromium-browser $URL --force-media-resolution-width 1980 --force-media-resolution-height 1080 --window-size=1920,1080 --start-fullscreen --kiosk --incognito --noerrdialogs --disable-translate --no-first-run --fast --fast-start --disable-infobars --disable-features=TranslateUI --disk-cache-dir=/dev/null  --password-store=basic
chromium-browser $URL --allow-file-access-from-files --force-media-resolution-width 800 --force-media-resolution-height 450 --window-size=800,450 --start-fullscreen --kiosk --incognito --noerrdialogs --disable-translate --no-first-run --fast --fast-start --disable-infobars --disable-features=TranslateUI --disk-cache-dir=/dev/null  --password-store=basic --enable-logging=stderr
