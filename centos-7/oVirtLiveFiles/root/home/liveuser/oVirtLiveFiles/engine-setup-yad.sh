#! /bin/bash

gsettings set org.gnome.desktop.background picture-uri "file:///usr/share/backgrounds/oVirtLive/default/oVirtLive.xml"
gsettings set org.gnome.desktop.screensaver idle-activation-enabled false
gsettings set org.gnome.settings-daemon.plugins.power active false
gsettings set org.gnome.settings-daemon.plugins.power idle-dim false
gsettings set org.gnome.desktop.session idle-delay 0
xset s 0 0
xset s off

if ! ifconfig ovirtmgmt 2> /dev/null | grep -q 'inet addr'; then
    # network wasn't correctly configured. Attempt to configure.
    # Probably left over workaround from earlier releases.
    # TODO - drop this if not needed
    sudo ip link add name dummy_0 type dummy
    sudo ifconfig dummy_0 10.0.0.1 netmask 255.255.255.0 > /dev/null 2>&1
    sudo ifup ovirtmgmt > /dev/null 2>&1
    sudo brctl addbr ovirtmgmt > /dev/null 2>&1
    sudo brctl addif ovirtmgmt dummy_0 > /dev/null 2>&1
fi

action=$(yad --entry \
    --title "oVirt installation" \
    --text  "oVirt allInOne is going to be installed\nChoose which option you would like to install\nINFO: all passwords on the live system are: \"ovirt\"" \
    --on-top \
    --center\
    --image=/usr/share/pixmaps/oVirtLive/ovirt-usb-stick.svg \
    --skip-taskbar \
    --image-on-top \
    --listen \
    --borders=3 \
    --button="gtk-ok:0" --button="gtk-close:1" \
    --entry-text \
    "automatic" "interactive")
ret=$?

[[ $ret -eq 1 ]] && exit 0

if [[ $ret -eq 2 ]]; then
    gdmflexiserver --startnew &
    exit 0
fi

case $action in
    automatic*) cmd="sudo /usr/bin/engine-setup --offline --config-append=$HOME/oVirtLiveFiles/ovirt-answer" ;;
    interactive*) cmd="sudo /usr/bin/engine-setup --offline" ;;
    *) exit 1 ;;
esac

echo "Excecuting $cmd"
if $cmd; then
    echo "Setup ended successfully."
    rm -f $HOME/.config/autostart/engine-setup.desktop
    echo "Disabling auto-logout from WebAdmin portal."
    sudo engine-config -s UserSessionTimeOutInterval=-1
    sudo ovirt-aaa-jdbc-tool settings set --name MAX_LOGIN_MINUTES --value -1
    echo "Restarting the engine..."
    sudo systemctl restart ovirt-engine
    sleep 10
    . /usr/share/ovirt-engine/bin/engine-prolog.sh
    yad --text "Setup ended successfully\nopening oVirt now on https://${ENGINE_FQDN}" --button="gtk-ok:0"
    firefox -CreateProfile default
    certutil -A -n oVirt-Live -t 'TCu,Cuw,Tuw' -i /etc/pki/ovirt-engine/ca.pem -d ~/.mozilla/firefox/*.default
    firefox https://${ENGINE_FQDN} &
    exit 0
fi
