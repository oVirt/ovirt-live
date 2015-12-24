#! /bin/bash

gsettings set org.gnome.desktop.background picture-uri "file:///usr/share/backgrounds/oVirtLive/default/oVirtLive.xml"

if ! ifconfig ovirtmgmt 2> /dev/null | grep -q 'inet addr'; then
    # network wasn't correctly configured. Attempt to configure.
    # Probably left over workaround from earlier releases.
    # TODO - drop this if not needed
    sudo ifconfig dummy0 10.0.0.1 netmask 255.255.255.0 > /dev/null 2>&1
    sudo ifup ovirtmgmt > /dev/null 2>&1
    sudo brctl addbr ovirtmgmt > /dev/null 2>&1
    sudo brctl addif ovirtmgmt dummy0 > /dev/null 2>&1
fi

sudo exportfs -r
sudo systemctl restart nfs-server

action=$(yad --entry \
    --title "oVirt installation" \
    --text  "oVirt allInOne is going to be installed\nChoose which option you would like to install\nINFO: all passwords on the live system are: \"ovirt\"" \
    --on-top \
    --center\
    --image=$HOME/oVirtLiveFiles/images/ovirt-usb-stick.svg \
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

do_interactive() {
    gnome-terminal --disable-factory --command='sh -c "sudo /usr/bin/engine-setup --offline; sleep 20"'
}

case $action in
    automatic*) cmd="sudo /usr/bin/engine-setup --offline --config-append=$HOME/oVirtLiveFiles/ovirt-answer" ;;
    interactive*) cmd="do_interactive" ;;
    *) exit 1 ;;
esac

echo "Excecuting $cmd"
if $cmd; then
    echo "Setup ended successfully"
    rm -f $HOME/.config/autostart/engine-setup.desktop
    yad --text "Setup ended successfully\nopening oVirt now on https://localhost.localdomain" --button="gtk-ok:0"
    firefox https://localhost.localdomain &
    exit 0
fi
