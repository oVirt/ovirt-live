#!/bin/bash -xe

for package in ovirt-live-artwork ovirt-engine-setup-plugin-live
do
    pushd ${package}
    autoreconf -ivf
    ./configure
    make distcheck
    popd
done

# check python code on centos-7, skipping fedora for now
pyflakes `find centos-7 -name "*.py"`
pep8 `find centos-7 -name "*.py"`

