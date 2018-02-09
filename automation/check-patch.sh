#!/bin/bash -xe

pushd ovirt-live-artwork
autoreconf -ivf
./configure
make distcheck
popd

automation/build-artifacts.sh
