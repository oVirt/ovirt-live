#!/bin/bash
yum install -y livecd-tools
wget -N http://distro.ibiblio.org/tinycorelinux/4.x/x86/release/TinyCore-current.iso
mkdir oVirtLiveFiles/rpms/
mkdir oVirtLiveFiles/iso/
wget -N http://kojipkgs.fedoraproject.org//packages/yad/0.14.2/1.fc14/x86_64/yad-0.14.2-1.fc14.x86_64.rpm
mv -f *.rpm oVirtLiveFiles/rpms
mv -f *.iso oVirtLiveFiles/iso
PWD=$(pwd)
sed -i '/name=local/d' kickstart/ovirt-live-base.ks
awk -v n=20 -v s="repo \-\-name=local \-\-baseurl=file://${PWD}/oVirtLiveFiles\/rpms\/" 'NR == n {print s} {print}' kickstart/ovirt-live-base.ks > kickstart/ovirt-live-base.temp
mv kickstart/ovirt-live-base.temp kickstart/ovirt-live-base.ks
rm -f kickstart/ovirt-live-base.temp
livecd-creator -d -v  --config=kickstart/ovirt-live-gnome.ks --cache=/home --fslabel=ovirt-live-el6 > iso.log 2>&1
