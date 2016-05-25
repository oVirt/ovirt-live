#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.60])
define([VERSION_MAJOR], [4])
define([VERSION_MINOR], [0])
define([VERSION_FIX], [0])
define([VERSION_NUMBER], VERSION_MAJOR[.]VERSION_MINOR[.]VERSION_FIX)
define([VERSION_RELEASE], [0.1])
define([VERSION_SUFFIX], [beta1])

AC_INIT([ovirt-engine-setup-plugin-live], [VERSION_NUMBER[-]VERSION_RELEASE[.]VERSION_SUFFIX], [devel@ovirt.org])
PACKAGE_RPM_VERSION="VERSION_NUMBER"
PACKAGE_RPM_RELEASE="VERSION_RELEASE.VERSION_SUFFIX"
AC_SUBST([PACKAGE_RPM_VERSION])
AC_SUBST([PACKAGE_RPM_RELEASE])

AC_CONFIG_AUX_DIR([.])
AC_CONFIG_SRCDIR([src/Makefile.am])
AC_CONFIG_MACRO_DIR([m4])
AM_INIT_AUTOMAKE([1.9 tar-pax])
dnl Fallback definition for gettext.m4 older than 0.19.6.
m4_ifndef([AM_GNU_GETTEXT_REQUIRE_VERSION], [m4_define([AM_GNU_GETTEXT_REQUIRE_VERSION])], [])
dnl Prefer the latest infrastructure, given it is newer than 0.18.2.
AM_GNU_GETTEXT_REQUIRE_VERSION([0.18.2])

dnl This will be ignored if the installed autopoint supports
dnl AM_GNU_GETTEXT_REQUIRE_VERSION.
AM_GNU_GETTEXT_VERSION([0.18.2])
AM_PO_SUBDIRS

AC_ARG_ENABLE(
	[python-syntax-check],
	[AS_HELP_STRING([--disable-python-syntax-check], [disable python syntax check @<:@default=enabled@:>@])],
	,
	[enable_python_syntax_check="yes"]
)

AC_ARG_VAR([PYFLAKES], [path to pyflakes utility])
AC_CHECK_PROGS([PYFLAKES], [pyflakes])
AC_ARG_VAR([PEP8], [path to pep8 utility])
AC_CHECK_PROGS([PEP8], [pep8])

AM_PATH_PYTHON([2.6],, [AC_MSG_ERROR([Cannot find python])])

AM_CONDITIONAL([PYTHON_SYNTAX_CHECK], [test "${enable_python_syntax_check}" = "yes"])

ovirtenginesetupconfdir="\$(sysconfdir)/ovirt-engine-setup.conf.d"
ovirthostdeployconfdir="\$(sysconfdir)/ovirt-host-deploy.conf.d"
ovirtlivelibdir="\$(datadir)/ovirt-engine/setup/ovirt_engine_setup/ovirt_live"
ovirtliveplugindir="\$(datadir)/ovirt-engine/setup/plugins/ovirt-engine-setup/ovirt-engine"
ovirtlivefirewalldtemplatesdir="\$(datadir)/ovirt-engine/firewalld/ovirt-engine"
AC_SUBST([ovirtlivelibdir])
AC_SUBST([ovirtliveplugindir])
AC_SUBST([ovirtlivefirewalldtemplatesdir])
AC_SUBST([ovirtenginesetupconfdir])
AC_SUBST([ovirthostdeployconfdir])

AC_CONFIG_FILES([
	Makefile
        build/Makefile
        conf/Makefile
        conf/ovirt-host-deploy/Makefile
        firewalld/Makefile
        po/Makefile.in
        src/Makefile
        src/ovirt_live/Makefile
        src/plugins/all-in-one/Makefile
        src/plugins/Makefile
        src/plugins/ovirt_live/Makefile
	ovirt-engine-setup-plugin-live.spec
])
AC_OUTPUT
