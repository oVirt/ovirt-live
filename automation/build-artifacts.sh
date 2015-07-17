#!/bin/bash -xe

SUFFIX=".git$(git rev-parse --short HEAD)"

# remove any previous artifacts
rm -rf output
rm -f ./*tar.gz


# build artwork rpm
pushd ovirt-live-artwork
autoreconf -ivf
./configure
make clean
make dist
mv ovirt-live-artwork-*.tar.gz ../
popd

# create the src.rpm
rpmbuild \
    -D "_srcrpmdir $PWD/output" \
    -D "_topmdir $PWD/rpmbuild" \
    -D "release_suffix ${SUFFIX}" \
    -ts ovirt-live-artwork-*.tar.gz

# install any build requirements
yum-builddep output/ovirt-live-artwork-*src.rpm

# create the rpms
rpmbuild \
    -D "_rpmdir $PWD/output" \
    -D "_topmdir $PWD/rpmbuild" \
    -D "release_suffix ${SUFFIX}" \
    --rebuild output/ovirt-live-artwork-*.src.rpm

# Store any relevant artifacts in exported-artifacts for the ci system to
# archive
[[ -d exported-artifacts ]] || mkdir -p exported-artifacts
find output -iname \*rpm -exec mv "{}" exported-artifacts/ \;
mv ./*tar.gz exported-artifacts/
