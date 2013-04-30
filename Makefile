#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Makefile for oVirt Live
#
# Make sure you have spin-kickstarts.noarch and livecd-tools installed.

NAME=ovirt-live
VERSION=1.0.0
RELEASE=0.1
SUFFIX="master.$(shell date --utc +%Y%m%d).git$(shell git rev-parse --short HEAD)"

clean:
	rm -rf oVirtLiveFiles/iso *.iso

iso:
	cp -f /usr/share/spin-kickstarts/fedora-live-base.ks kickstart/ovirt-live-base.ks
	sed -i -e 's/selinux \-\-enforcing/selinux \-\-permissive/g' \
            -e 's/services \-\-enabled\=NetworkManager \-\-disabled\=network\,sshd/services \-\-enabled\=NetworkManager\,sshd \-\-disabled\=network\,firewalld\nrepo \-\-name\=ovirt \-\-baseurl\=http:\/\/ovirt.org\/releases\/stable\/rpm\/Fedora\/18/g' \
             -e 's/liveuser/oVirtuser/g' \
             -e 's/firewall \-\-enabled/firewall \-\-disabled/g' \
             -e 's/livedir\=\"LiveOS\"/livedir\=\"LiveoVirt\"/g' \
             -e "s/\(^.*stop.*atd\..*:\)/\1\nmodprobe dummy/g" kickstart/ovirt-live-base.ks

	wget -N http://distro.ibiblio.org/tinycorelinux/4.x/x86/release/TinyCore-current.iso
	wget -N http://download.fedoraproject.org/pub/fedora/linux/releases/18/Live/x86_64/Fedora-18-x86_64-Live-Desktop.iso
	mkdir oVirtLiveFiles/iso

	mv -f *.iso oVirtLiveFiles/iso

	livecd-creator -d -v  \
            --config=kickstart/ovirt.ks \
            --cache=/home \
            --fslabel=$(NAME)-$(VERSION)-$(RELEASE) \
		> $(NAME)-$(VERSION)-$(RELEASE).$(SUFFIX).log 2>&1 || notify-send "Error"
	mv $(NAME)-$(VERSION)-$(RELEASE).iso $(NAME)-$(VERSION)-$(RELEASE).$(SUFFIX).iso
	notify-send "Check ISO"
