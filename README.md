# domo-androidtv
Domoticz AndroidTV plugin

This is a fork of enesbcs/domo-androidtv.
Thanks for the work he has done.

## Installation

### Prerequisite on AndroidTV

Do not forget to go to Settings > About. Click 7 times on "Build" to activate developper mode.
Then go to Developper tools and set usb debug mode on.

If you want to use Wake-On-Lan capability, enable it on the TV network menu, and add the TV network card MAC address to the plugin settings!

### Plugin installation

    sudo apt-get install git adb
    cd ~/domoticz/plugins/
    git clone https://github.com/wvries/Domoticz-AndroidTV.git
    service domoticz restart

AndroidTV plugin now should be appear on Domoticz Hardware list.
After starting AndroidTV plugin in Domoticz, enable remote access on the TV screen.
Install plugin for each Android TV you want to control.

## Customization

In the database.ini file you can change the settings / codes for the specific TV you have.
Generic ADB codes and commands are used in this app.

