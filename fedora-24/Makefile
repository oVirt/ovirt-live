all:		\
		prereq \
		packages \
		kickstart \
		livecd \
		$(NULL)

clean:
	rm -fr downloads/*.tmp
	rm -fr *.tmp
	rm -f kickstart/ovirt-live-ovirt-custom.ks
	rm -rf oVirtLiveFiles/iso

dist-clean:	clean

maintainer-clean:	dist-clean
	rm -fr downloads

prereq:
	if [ $$(id -u) != 0 ]; then echo "You must be root"; exit 1; fi

download: 	\
		downloads/TinyCore-current.iso \
		$(NULL)

_download:
	mkdir -p downloads
	rm -f "downloads/$(OUT)"
	curl "$(URL)" > "downloads/$(OUT).tmp"
	mv "downloads/$(OUT).tmp" "downloads/$(OUT)"

downloads/TinyCore-current.iso:
	$(MAKE) _download URL="http://distro.ibiblio.org/tinycorelinux/7.x/x86/release/TinyCore-current.iso" OUT="TinyCore-current.iso"

packages:
	rpm -ql livecd-tools > /dev/null 2>&1 || \
		dnf install -y livecd-tools python-imgcreate hfsplus-tools
	rpm -ql fedora-kickstarts  > /dev/null 2>&1 || \
		dnf install -y fedora-kickstarts

kickstart/fedora-live-workstation.ks: packages
	ln -s \
		/usr/share/spin-kickstarts/fedora-live-base.ks \
		/usr/share/spin-kickstarts/fedora-live-workstation.ks \
		/usr/share/spin-kickstarts/fedora-workstation-packages.ks \
		/usr/share/spin-kickstarts/fedora-repo.ks \
		/usr/share/spin-kickstarts/fedora-repo-not-rawhide.ks \
		kickstart/
	mkdir -p kickstart/snippets
	ln -s \
		/usr/share/spin-kickstarts/snippets/packagekit-cached-metadata.ks \
		kickstart/snippets/

.SUFFIXES:
.SUFFIXES: .in
.in:
	sed \
		-e "s#@PATH@#$$(pwd)#g" \
		"$<" > "$@"

livecd:		\
		downloads/TinyCore-current.iso \
		kickstart/ovirt-live-ovirt-custom.ks \
		kickstart/fedora-live-workstation.ks \
		$(NULL)
	mkdir -p oVirtLiveFiles/iso
	cp downloads/TinyCore-current.iso oVirtLiveFiles/iso/
	livecd-creator -d -v -p --config=kickstart/ovirt-live-ovirt-custom.ks --fslabel=ovirt-live-master-fc.$(shell date -u +%y%m%d%H) 2>&1 | tee iso.log
