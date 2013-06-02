#! /bin/bash
# TODO

gconftool-2 -t str -s /desktop/gnome/background/picture_filename /home/liveuser/oVirtLiveFiles/images/ovirt-wallpaper-16:9.jpg
sudo ifconfig dummy0 10.0.0.1 netmask 255.255.255.0 > /dev/null
sudo ifup ovirtmgmt > /dev/null
sudo brctl addbr ovirtmgmt > /dev/null
sudo brctl addif ovirtmgmt dummy0 > /dev/null

action=$(yad --entry \
    --title "oVirt installation" \
    --text  "oVirt allInOne is going to be installed\nChoose which option you would like to install\nINFO: all passwords on the live system are: \"ovirt\"" \
    --on-top \
    --center\
    --image=/home/liveuser/rhevLiveFiles/images/ovirt-usb-stick.svg \
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
    automatic*) cmd="sudo /usr/bin/engine-setup --answer-file=/home/liveuser/oVirtLiveFiles/ovirt-answer" ;;
    interactive*) cmd="gnome-terminal --command=\"sudo /usr/bin/engine-setup\";sleep 20" ;;
    *) exit 1 ;;
esac

echo "Excecuting $cmd"
if $cmd; then
    echo "Setup ended successfully"
    rm -f ~liveuser/.config/autostart/engine-setup.desktop
    yad --text "Setup ended successfully\nopening ovirt now on htts://localhost.localdomain" --button="gtk-ok:0"
    /usr/bin/firefox https://localhost.localdomain &
    exit 0
fi
