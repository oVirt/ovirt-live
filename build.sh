#!/usr/bin/sh
yum install -y spin-kickstarts.noarch
yum install -y livecd-tools
cp -f /usr/share/spin-kickstarts/fedora-live-base.ks ./kickstart/ovirt-live-base.ks
sed -i 's/selinux \-\-enforcing/selinux \-\-permissive/g' ./kickstart/ovirt-live-base.ks
sed -i 's/services \-\-enabled\=NetworkManager \-\-disabled\=network\,sshd/services \-\-enabled\=NetworkManager\,sshd \-\-disabled\=network\,firewalld\nrepo \-\-name\=ovirt \-\-baseurl\=http:\/\/ovirt.org\/releases\/stable\/rpm\/Fedora\/18/g' ./kickstart/ovirt-live-base.ks
sed -i 's/liveuser/oVirtuser/g' ./kickstart/ovirt-live-base.ks
sed -i 's/firewall \-\-enabled/firewall \-\-disabled/g' ./kickstart/ovirt-live-base.ks
sed -i 's/livedir\=\"LiveOS\"/livedir\=\"LiveoVirt\"/g' ./kickstart/ovirt-live-base.ks
sed -i "s/\(^.*stop.*atd\..*:\)/\1\nmodprobe dummy/g" ./kickstart/ovirt-live-base.ks
wget -N http://kojipkgs.fedoraproject.org//packages/sanlock/2.6/7.fc18/x86_64/sanlock-2.6-7.fc18.x86_64.rpm
wget -N http://kojipkgs.fedoraproject.org//packages/sanlock/2.6/7.fc18/x86_64/sanlock-lib-2.6-7.fc18.x86_64.rpm
wget -N http://kojipkgs.fedoraproject.org//packages/sanlock/2.6/7.fc18/x86_64/sanlock-python-2.6-7.fc18.x86_64.rpm
wget -N http://distro.ibiblio.org/tinycorelinux/4.x/x86/release/TinyCore-current.iso
wget -N http://download.fedoraproject.org/pub/fedora/linux/releases/18/Live/x86_64/Fedora-18-x86_64-Live-Desktop.iso
mkdir ./oVirtLiveFiles/rpms/
mkdir ./oVirtLiveFiles/iso/
mv -f *.rpm ./oVirtLiveFiles/rpms/
mv -f *.iso ./oVirtLiveFiles/iso/
livecd-creator -d -v  --config=kickstart/ovirt.ks --cache=/home --fslabel=ovirt-live-`cat VERSION` > iso.log 2>&1 || notify-send "Error"
notify-send "Check ISO"
