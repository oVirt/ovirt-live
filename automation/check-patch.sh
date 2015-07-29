#!/bin/bash -xe

# check artwork rpm
pushd ovirt-live-artwork
autoreconf -ivf
./configure
make distcheck
popd

# check python code on centos-7, skipping fedora for now
pyflakes `find centos-7 -name "*.py"`
pep8 `find centos-7 -name "*.py"`

