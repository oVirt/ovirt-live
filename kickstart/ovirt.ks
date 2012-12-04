# Maintained by the Fedora Desktop SIG:
# http://fedoraproject.org/wiki/SIGs/Desktop
# mailto:desktop@lists.fedoraproject.org

%include ovirt-live-base.ks

part / --size 16000
rootpw  --iscrypted $1$Idf9Mf5B$lmQBHtDcnO4Xd53vqFWqT.
authconfig --enableshadow --passalgo=sha512 --enablefingerprint
timezone --utc Asia/Jerusalem

%packages
##@sound-and-video
@gnome-desktop
ovirt-engine-setup-plugin-allinone
ovirt-engine-cli
#ovirt-node-iso
spice-xpi
-freeipa-server

# misc
chkconfig
system-config-firewall-base
cyrus-sasl
rpcbind
initscripts
patch
bridge-utils
net-tools
firefox

#missing from vdsBootsrap
m2crypto
seabios
vdsm-cli
vdsm-xmlrpc
ovirt-host-deploy-offline
qemu-kvm-tools
vim
yad
net-tools
bridge-utils
shadow-utils

# FIXME; apparently the glibc maintainers dislike this, but it got put into the
# desktop image at some point.  We won't touch this one for now.
nss-mdns

# This one needs to be kicked out of @base
-smartmontools

# The gnome-shell team does not want extensions in the default spin;
-biosdevname
# rebranding
#-fedora-logos
#-fedora-release
#-fedora-release-notes
#generic-release
#generic-logos
#generic-release-notes

%end

%post #--nochroot --log=/tmp/my-post-log
#!/bin/sh
set -x -v

echo "starting post secion"
echo "adding user"
/sbin/useradd oVirtuser; echo oVirtuser |passwd oVirtuser --stdin
echo "making dir /root/oVirtLiveFiles/"
mkdir /root/oVirtLiveFiles/
echo "making autostart dir"
mkdir -p ~oVirtuser/.config/autostart

cat >> /etc/rc.d/init.d/livesys << EOF

# make the installer show up
if [ -f /usr/share/applications/liveinst.desktop ]; then
  # Show harddisk install in shell dash
  sed -i -e 's/NoDisplay=true/NoDisplay=false/' /usr/share/applications/liveinst.desktop ""
  # need to move it to anaconda.desktop to make shell happy
  mv /usr/share/applications/liveinst.desktop /usr/share/applications/anaconda.desktop
fi

# Turn off PackageKit-command-not-found while uninstalled
if [ -f /etc/PackageKit/CommandNotFound.conf ]; then
  sed -i -e 's/^SoftwareSourceSearch=true/SoftwareSourceSearch=false/' /etc/PackageKit/CommandNotFound.conf
fi

EOF

#configure autologin
sed -i 's/\[daemon\]/\[daemon\]\nAutomaticLoginEnable\=True\nAutomaticLogin\=oVirtuser/g' /etc/gdm/custom.conf

# Add oVirtuser to sudoers
/sbin/usermod -g wheel oVirtuser

sed -i 's/utils.retry(isHostUp, tries=20, timeout=150, sleep=5)/utils.retry(isHostUp, tries=100, timeout=600, sleep=5)/g' /usr/share/ovirt-engine/scripts/plugins/all_in_one_100.py
# No reboot is needed in AIO, so manager should not wait
sed -i "s/'ServerRebootTimeout','300'/'ServerRebootTimeout','0'/g" /usr/share/ovirt-engine/dbscripts/upgrade/pre_upgrade/0000_config.sql
# Allow wlan* on host (as we're running locally)
sed -i -e 's/# hidden_nics = wlan\*,usb\*/hidden_nics = usb\*/' /etc/vdsm/vdsm.conf
sed -i 's/\[vars\]/\[vars\]\nfake_nics\ \=\ \dummy0/g' /etc/vdsm/vdsm.conf
%end

%post --nochroot
cp -r oVirtLiveFiles $INSTALL_ROOT/root/
%end

# Last misc changes here:
%post
mkdir -p /home/oVirtuser
cp -r /root/oVirtLiveFiles /home/oVirtuser
#gsettings set org.gnome.desktop.background picture-uri 'file:////home/oVirtuser/oVirtLiveFiles/ovirt-wallpaper-16:9.jpg'
rm -rf /root/oVirtLiveFiles/
chmod o+x /home/oVirtuser/oVirtLiveFiles/engine-setup-yad.sh
chown -R oVirtuser:oVirtuser /home/oVirtuser/
echo 'user_pref("browser.startup.homepage", "http://localhost.localdomain");' >> /home/oVirtuser/.mozilla/firefox/*.default/prefs.js

find /home/oVirtuser/oVirtLiveFiles/patches -name '*.patch' | sort | while read patch; do
    patch -d /usr/share/ovirt-engine/scripts < "$patch"
done



#configuring autologin
sed -i 's/\[daemon\]/\[daemon\]\nAutomaticLoginEnable\=True\nAutomaticLogin\=oVirtuser/g' /etc/gdm/custom.conf

#settings up vdsm to use a dummy nic
cp /home/oVirtuser/oVirtLiveFiles/50-vdsm-conf-fake-nic.conf /etc/ovirt-host-deploy.conf.d/
echo '10.0.0.1 ovirtlive.localdomain localdomain' >> /etc/hosts

#setting wallapaper
cp /home/oVirtuser/oVirtLiveFiles/images/ovirt-wallpaper-16:9.jpg /usr/share/backgrounds/spherical-cow/default/standard/spherical-cow.png
cp /home/oVirtuser/oVirtLiveFiles/images/ovirt-wallpaper-16:9.jpg /usr/share/backgrounds/spherical-cow/default/wide/spherical-cow.png
cp /home/oVirtuser/oVirtLiveFiles/images/ovirt-wallpaper-16:9.jpg /usr/share/backgrounds/spherical-cow/default/normalish/spherical-cow.png

#copying network files
cp /home/oVirtuser/oVirtLiveFiles/etc/sysconfig/network-scripts/* /etc/sysconfig/network-scripts/

#placing repo file
cp /home/oVirtuser/oVirtLiveFiles/etc/yum.repos.d/ovirt.repo /etc/yum.repos.d/

#copying autostart and desktop shortcuts
cp /home/oVirtuser/oVirtLiveFiles/usr/share/applications/* /usr/share/applications/

#link setup in autostart
/usr/bin/cp /usr/share/applications/engine-setup.desktop ~oVirtuser/.config/autostart/engine-setup.desktop

#setting up autologin
cp /home/oVirtuser/oVirtLiveFiles/etc/gdm/* /etc/gdm/

#overriding glib schemas
cp /home/oVirtuser/oVirtLiveFiles/usr/share/glib-2.0/schemas/* /usr/share/glib-2.0/schemas/

glib-compile-schemas /usr/share/glib-2.0/schemas

#workaround for bz 878119
#echo 'blacklist iTCO_wdt' >> /etc/modprobe.d/blacklist.conf
#echo 'blacklist iTCO_vendor_support' >> /etc/modprobe.d/blacklist.conf
sed -i 's/\#WDMDOPTS/WDMDOPTS/g' /etc/sysconfig/wdmd
yum localinstall -y /home/oVirtuser/oVirtLiveFiles/rpms/*.rpm

#updating patched files
cp /home/oVirtuser/oVirtLiveFiles/ovirt_live_101.py /usr/share/ovirt-engine/scripts/plugins/
cp /home/oVirtuser/oVirtLiveFiles/ovirt_live_101.py /usr/share/ovirt-engine/scripts/


# Manipulate fqdn validation, so that it is possible to setup with answer file
sed -i 's/raise Exception(output_messages.ERR_EXP_VALIDATE_PARAM % param.getKey("CONF_NAME"))/logging.debug("Failed to validate %s with value %s",param,paramValue)/g' /usr/share/ovirt-engine/scripts/engine-setup.py
sed -i -e 's/\(^SELINUX=\).*$/\1permissive/' /etc/selinux/config
#yad script - give some gui to installation

echo "finishing post section"
%end
