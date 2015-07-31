#
# ovirt-engine-setup -- oVirt Live
# Copyright (C) 2015 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

AUTOMAKE_OPTIONS = foreign 1.9
ACLOCAL_AMFLAGS = -I m4

MAINTAINERCLEANFILES = \
	config.log config.status \
	$(srcdir)/Makefile.in \
	$(srcdir)/configure \
	$(srcdir)/install-sh $(srcdir)/missing \
	$(srcdir)/depcomp $(srcdir)/py-compile \
	$(srcdir)/config.guess $(srcdir)/config.sub \
	$(srcdir)/config.rpath \
	$(srcdir)/ABOUT-NLS \
	$(srcdir)/aclocal.m4 \
	$(NULL)

CLEANFILES = \
	POTFILES.in.tmp \
	$(NULL)

SUBDIRS = \
	build \
	po \
	src \
	$(NULL)

dist_noinst_DATA = \
	ovirt-engine-setup-plugin-live.spec \
	NOTICE \
	$(NULL)

dist_doc_DATA = \
	README.md
	$(NULL)

POTFILES.in:
	( cd "$(srcdir)" && \
		find ./src -name '*.py' -or -name '*.py.in' ) | \
		sort | grep -v config.py > POTFILES.in.tmp && \
	cmp -s POTFILES.in.tmp "$(srcdir)/po/POTFILES.in" || \
		cp POTFILES.in.tmp "$(srcdir)/po/POTFILES.in"; \
	rm -f POTFILES.in.tmp

update-po: POTFILES.in
	$(MAKE) -C po update-po
