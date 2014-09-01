########################################################################
#
#  LiveCD with gnome desktop
#
#  Urs Beyerle, ETHZ
#
########################################################################

part / --size 16000 --fstype ext4

########################################################################
# Include kickstart files
########################################################################

%include ovirt-live-base.ks
rootpw  ovirt

########################################################################
# Packages
########################################################################

%packages
# packages removed from @base
-bind-utils
-ed
-kexec-tools
-system-config-kdump
-libaio
-libhugetlbfs
-microcode_ctl
-psacct
-quota
-autofs
-smartmontools
yad

@basic-desktop
# package removed from @basic-desktop
-gok

@desktop-platform
# packages removed from @desktop-platform
-redhat-lsb


@fonts

@general-desktop
# package removed from @general-desktop
-gnome-backgrounds
-gnome-user-share
-nautilus-sendto
-orca
-rhythmbox
-vino
-compiz
-compiz-gnome
-evince-dvi
-gnote
-sound-juicer

# @input-methods

@internet-applications
# package added to @internet-applications
# xchat
# packages removed from @internet-applications
-ekiga

@internet-browser

## packages to remove to save diskspace
-evolution
-evolution-help
-evolution-mapi
-scenery-backgrounds
-redhat-lsb-graphics
-qt3
-xinetd
-openswan
-pinentry-gtk
-seahorse
-hunspell-*
-words
-nano
-pinfo
-vim-common
-vim-enhanced
-samba-common
-samba-client
-mousetweaks
patch
ovirt-engine
ovirt-engine-setup-plugin-allinone
bridge-utils
net-tools
firefox
m2crypto
seabios
vdsm-cli
vdsm-xmlrpc
ovirt-host-deploy-offline
vim
net-tools
bridge-utils
shadow-utils
apr
httpd
ovirt-log-collector

## remove some fonts and input methods
# remove Chinese font (Ming face) (8.9 MB)
# we still have wqy-zenhei-fonts 
-cjkuni-fonts-common
-cjkuni-uming-fonts
# remove Korean input method (2.1 MB)
-ibus-hangul
-libhangul

## packages to add
lftp
-thunderbird
#@openafs-client
cups
cups-pk-helper
system-config-printer
system-config-printer-udev
xorg-x11-fonts-100dpi
xorg-x11-fonts-ISO8859-1-100dpi
xorg-x11-fonts-Type1
nautilus-sendto
spice-client
spice-xpi
phonon-backend-gstreamer

%end


########################################################################
# Post installation
########################################################################

%post --nochroot
cp -r oVirtLiveFiles $INSTALL_ROOT/root/
%end


%post

mkdir -p /home/liveuser/oVirtLiveFiles

cp -r /root/oVirtLiveFiles /home/liveuser

yum localinstall -y /home/liveuser/oVirtLiveFiles/rpms/*.rpm

echo '10.0.0.1 livecd.localdomain localdomain' >> /etc/hosts

# remove folders/files that use a lot of diskspace
# and are not really needed for LiveCD
rm -rf /usr/share/doc/openafs-*
rm -rf /usr/share/doc/testdisk-*

#workaround for bz 878119
#echo 'blacklist iTCO_wdt' >> /etc/modprobe.d/blacklist.conf
#echo 'blacklist iTCO_vendor_support' >> /etc/modprobe.d/blacklist.conf
sed -i 's/\#WDMDOPTS/WDMDOPTS/g' /etc/sysconfig/wdmd

#configuring autostart
mkdir -p /home/liveuser/.config/autostart

umask 0027

# Updating patched files
cp -r /home/liveuser/oVirtLiveFiles/root/* /

chmod 666 /etc/xdg/autostart/engine-setup.desktop

#setting up wallpaper
su -c "gconftool-2 -t str -s /desktop/gnome/background/picture_filename /home/liveuser/oVirtLiveFiles/images/ovirt-wallpaper-16:9.jpg" - liveuser

sed -i 's/pc-0.14/rhel6.4.0/' /usr/share/ovirt-engine/dbscripts/upgrade/pre_upgrade/0000_config.sql

%end
