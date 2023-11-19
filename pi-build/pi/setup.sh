#!/bin/bash


sudo apt purge wolfram-engine scratch scratch2 nuscratch sonic-pi idle3 -y
sudo apt purge smartsim java-common minecraft-pi libreoffice* -y
sudo apt purge firefox -y

# Remove the low voltage warning widget
sudo apt remove lxplug-ptbatt -y

sudo apt clean
sudo apt autoremove -y

sudo apt update -y
sudo apt upgrade -y


sudo apt install -y xdotool unclutter sed

#sudo apt install -y vim matchbox-window-manager unclutter nitrogen jq chromium-browser xserver-xorg xinit rpd-plym-splash xdotool xrdp ufw cec-utils watchdog unattended-upgrades
sudo apt install -y vim unclutter nitrogen jq chromium-browser xinit rpd-plym-splash xdotool ufw cec-utils watchdog


# Install the firewall
sudo apt-get install ufw
sudo /usr/sbin/ufw default deny
#sudo /usr/sbin/ufw allow ssh
sudo /usr/sbin/ufw limit ssh
#sudo /usr/sbin/ufw allow 22/tcp
sudo /usr/sbin/ufw --force enable
#sudo /usr/sbin/ufw allow 3389/tcp
#sudo /usr/sbin/ufw allow 5900/tcp



# Install the watchdog just in case the pi locks up
sudo modprobe bcm2835_wdt
#echo "bcm2835_wdt" | sudo tee -a /etc/modules

sudo apt-get install watchdog
sudo update-rc.d watchdog defaults

# Get the kiosk service running
sudo cp kiosk.service /lib/systemd/system/kiosk.service
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service

# Update the splash screen
sudo cp splash.png /usr/share/plymouth/themes/pix/splash.png
sudo plymouth-set-default-theme --rebuild-initrd pix


# Cleanup
sudo apt-get clean


# Manual tasks:
# Update the watchdog conf
#sudo vi /etc/watchdog.conf

#sudo raspi-config
## Auto login
## Switch back to X (away from Wayland)

# sudo nano /boot/config.txt
# avoid_warnings=1
# disable_splash=1



