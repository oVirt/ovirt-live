all:		\
		prereq \
		packages \
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
		downloads/yad-0.27.0-1.el6.x86_64.rpm \
		downloads/TinyCore-current.iso \
		$(NULL)

_download:
	mkdir -p downloads
	rm -f "downloads/$(OUT)"
	curl "$(URL)" > "downloads/$(OUT).tmp"
	mv "downloads/$(OUT).tmp" "downloads/$(OUT)"

downloads/yad-0.27.0-1.el6.x86_64.rpm:
	$(MAKE) _download URL="http://kojipkgs.fedoraproject.org/packages/yad/0.27.0/1.el6/x86_64/yad-0.27.0-1.el6.x86_64.rpm" OUT="yad-0.27.0-1.el6.x86_64.rpm"

downloads/TinyCore-current.iso:
	$(MAKE) _download URL="http://distro.ibiblio.org/tinycorelinux/4.x/x86/release/TinyCore-current.iso" OUT="TinyCore-current.iso"

repo:		\
		downloads/yad-0.27.0-1.el6.x86_64.rpm \
		$(NULL)
	rm -fr repo
	mkdir -p repo.tmp
	ln -s ../downloads/yad-0.27.0-1.el6.x86_64.rpm repo.tmp/yad-0.27.0-1.el6.x86_64.rpm
	createrepo repo.tmp
	mv repo.tmp repo

packages:
	rpm -ql epel-release > /dev/null 2>&1 || yum install -y http://www.mirrorservice.org/sites/dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
	rpm -ql livecd-tools > /dev/null 2>&1 || yum install -y livecd-tools
	rpm -ql createrepo > /dev/null 2>&1 || yum install -y createrepo


.SUFFIXES:
.SUFFIXES: .in
.in:
	sed \
		-e "s#@PATH@#$$(pwd)#g" \
		"$<" > "$@"

livecd:		\
		repo \
		downloads/TinyCore-current.iso \
		kickstart/ovirt-live-ovirt-custom.ks \
		$(NULL)
	mkdir -p oVirtLiveFiles/iso
	cp downloads/TinyCore-current.iso oVirtLiveFiles/iso/
	setenforce 0
	livecd-creator -d -v  --config=kickstart/ovirt-live-ovirt-custom.ks --cache=/home --fslabel=ovirt-live-el6-3.5.0_rc5 2>&1 | tee iso.log
