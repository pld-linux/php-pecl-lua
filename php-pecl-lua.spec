#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	lua
Summary:	Embedded LUA interpreter
Name:		%{php_name}-pecl-%{modname}
Version:	1.1.0
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	58bd532957473f2ac87f1032c4aa12b5
URL:		http://pecl.php.net/package/lua/
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel
BuildRequires:	lua52-devel
BuildRequires:	sed >= 4.0
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Provides:	php(lua) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This extension embeds the LUA interpreter and offers an OO-API to LUA
variables and functions.

%prep
%setup -qc
mv %{modname}-%{version}/* .

# should patch config.m4 properly, but i'm lazy
%{__sed} -i -e 's,PHP_LUA/include/lua.h,PHP_LUA/include/lua5.2/lua.h,' config.m4
%{__sed} -i -e 's,LUA_LIB_NAME=liblua.a,LUA_LIB_NAME=liblua5.2.so,' config.m4
%{__sed} -i -e '/PHP_ADD_LIBRARY_WITH_PATH/ s/lua,/lua5.2,/ ' config.m4

%build
CPPFLAGS=-I%{_includedir}/lua5.2
phpize
%configure \
	--with-lua=%{_prefix}
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php}
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc CREDITS EXPERIMENTAL
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
