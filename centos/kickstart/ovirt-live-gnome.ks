########################################################################
#
#  LiveCD with gnome desktop
#
#  Urs Beyerle, ETHZ
#
########################################################################

# Based on
# https://svn.iac.ethz.ch/websvn/pub/websvn-pub/wsvn/livecd/trunk/SL6/livecd-config/sl65-livecd-gnome.ks

#{ ovirt
#part / --size 4096 --fstype ext4
# 16GB are needed because the ramdisk running the live instance must have at least
# 10GB free for the storage domain.
part / --size 16000 --fstype ext4
#}

########################################################################
# Include kickstart files
########################################################################

#{ovirt
#%include sl65-live-base.ks
#%include sl65-extra-software.ks
%include ovirt-live-base.ks
#}

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

@basic-desktop
# package removed from @basic-desktop
-gok

@desktop-platform
# packages removed from @desktop-platform
-redhat-lsb

#{ovirt
#@dial-up
#}

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

### SL LiveCD specific changes

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
-system-config-printer
-system-config-printer-udev
-system-config-printer-libs
-samba-common
-samba-client
-cifs-utils
-gvfs-smb
-gnome-vfs2-smb
-libsmbclient
-samba-winbind
-samba-winbind-clients
-mousetweaks
-foomatic-db-ppds
-redhat-lsb-printing
-eog
-qt
-gcalctool
-gnome-system-monitor
-nc
-minicom
#gnome-utils-libs
#gnome-utils

#brasero
-brasero-nautilus
-brasero-libs
-brasero
-libburn
-vorbis-tools
-libisofs

# pidgin
-pidgin
-gssdp
-farsight2
-gupnp
-gupnp-igd
-libnice
-libpurple
-gtkspell
-meanwhile

## remove some fonts and input methods
# remove Chinese font (Ming face) (8.9 MB)
# we still have wqy-zenhei-fonts
-cjkuni-fonts-common
-cjkuni-uming-fonts
# remove Korean input method (2.1 MB)
-ibus-hangul
-libhangul

## packages to add
#{ovirt
#thunderbird
-thunderbird
#}
xorg-x11-fonts-100dpi
xorg-x11-fonts-ISO8859-1-100dpi
xorg-x11-fonts-Type1
nautilus-sendto

## packages which are no longer included
# @openafs-client
# system-config-printer
# system-config-printer-udev
# phonon-backend-gstreamer
# cups
# cups-pk-helper
# lftp
# spice-client

%end


########################################################################
# Post installation
########################################################################

%post

# remove folders/files that use a lot of diskspace
# and are not really needed for LiveCD
rm -rf /usr/share/doc/openafs-*
rm -rf /usr/share/doc/testdisk-*

%end
