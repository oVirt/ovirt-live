#!/bin/sh
if [ $(id -u) != 0 ]; then
    echo "Please run as root"
    exit 1
fi
if ! rpm -q livecd-tools >  /dev/null; then 
    yum install -y livecd-tools
fi
wget -N http://distro.ibiblio.org/tinycorelinux/4.x/x86/release/TinyCore-current.iso
mkdir -p oVirtLiveFiles/rpms/ oVirtLiveFiles/iso/
wget -N http://kojipkgs.fedoraproject.org//packages/yad/0.14.2/1.fc14/x86_64/yad-0.14.2-1.fc14.x86_64.rpm
mv -f *.rpm oVirtLiveFiles/rpms
mv -f *.iso oVirtLiveFiles/iso
createrepo oVirtLiveFiles/rpms
sed -e "s#@PATH@#$(pwd)#g" kickstart/ovirt-live-base.ks.in > kickstart/ovirt-live-base.ks
livecd-creator -d -v  --config=kickstart/ovirt-live-gnome.ks --cache=/home --fslabel=ovirt-live-el6 > iso.log 2>&1
