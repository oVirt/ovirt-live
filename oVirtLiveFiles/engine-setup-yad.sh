#! /bin/bash
# TODO

sudo ifconfig dummy0 10.0.0.1 netmask 255.255.255.0 > /dev/null
sudo ifup ovirtmgmt > /dev/null
sudo brctl addbr ovirtmgmt > /dev/null
sudo brctl addif ovirtmgmt dummy0 > /dev/null

action=$(yad --entry \
    --title "oVirt installation" \
    --text  "oVirt allInOne is going to be installed\nChoose which option you would like to install\nINFO: all passwords on the live system are: \"ovirt\"" \
    --on-top \
    --center\
    --text-align=center \
    --image=/home/oVirtuser/oVirtLiveFiles/images/ovirt-usb-stick.svg \
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
    automatic*) cmd="sudo /usr/bin/engine-setup --answer-file=/home/oVirtuser/oVirtLiveFiles/ovirt-answer" ;;
    interactive*) cmd="gnome-terminal --command=\"sudo /usr/bin/engine-setup\";sleep 20" ;;
    *) exit 1 ;;
esac

echo "excecuting $cmd"
$cmd
if [[ $? -eq 0 ]]; then
    echo "setup ended successfully"
    rm -f ~oVirtuser/.config/autostart/engine-setup.desktop
    yad --text "setup ended successfully\nopening ovirt-engine now on htts://localhost.localdomain" --button="gtk-ok:0"
    /bin/firefox https://localhost.localdomain &
    exit 0
fi
