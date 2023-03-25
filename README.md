# domo-androidtv
Domoticz AndroidTV plugin

## Installation

### Prerequisite on AndroidTV

Do not forget to go to Settings > About. Click 7 times on "Build" to activate developper mode.
Then go to Developper tools and set usb debug mode on.

If you want to use Wake-On-Lan capability, enable it on the TV network menu, and add the TV network card MAC address to the plugin settings!

### Plugin installation

    sudo apt-get install git adb
    cd ~/domoticz/plugins/
    git clone https://github.com/enesbcs/domo-androidtv.git
    service domoticz restart

AndroidTV plugin now should be appear on Domoticz Hardware list.
After starting AndroidTV plugin in Domoticz, enable remote access on the TV screen.

## Customization

App starting and Source selection commands configured for my Blaupunkt Android TV, other models might need other commands, which can be customized by editing database.ini file next to plugin.py.

