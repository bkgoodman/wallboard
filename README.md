# wallboard
Resource room TV Display


# Raspberry Pi

`apt install unclutter`

## raspi-config
Under ("Advanced Options")
### Set "Composter" to "No"
Make sure GL driver is set to "Full KMS" (?)

# raspi-config

* Make sure wayland is DISABLED
* Set auto login to "desktop" and user account "bkg"

In /etc/lightdm/lightdm.conf make sure you comment out:

```
#user-session=
#autologin-session=
```


I think you want to see:
```autologin-user=bkg```

Help with auto login: https://forums.raspberrypi.com/viewtopic.php?t=340632

Some people say `/usr/share/dispsetup.sh` should be 755 and:
```
#!/bin/sh
exit 0
```

Add the following to `/etc/xdg/lxsession/LXDE-pi/autostart`

```
#@xscreensaver -no-splash
@xset s off
@xset -dpms
@xset s noblank
```

## DEBIAN 12

`sudo tasksel`


Install LXDE

# More info

https://blockdev.io/raspberry-pi-2-and-3-chromium-in-kiosk-mode/
