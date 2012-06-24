# TODO
# - check if the signed nss lib data (*.chk) is still valid after rpm stripping
#
%define	foover	%(echo %{version} | tr . _)
Summary:	NSS - Network Security Services
Summary(pl):	NSS - Network Security Services
Name:		nss
Version:	3.11.3
Release:	3
Epoch:		1
License:	GPL
Group:		Libraries
# :pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot mozilla/dbm -r DBM_1_61_RTM
# :pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot mozilla/security/dbm -r DBM_1_61_RTM
# :pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot mozilla/security/coreconf -r NSS_3_9_4_RTM
# :pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot mozilla/security/nss -r NSS_3_9_4_RTM
#Source0:	%{name}-%{version}.tar.bz2
Source0:	ftp://ftp.mozilla.org/pub/mozilla.org/security/nss/releases/NSS_%{foover}_RTM/src/%{name}-%{version}.tar.gz
# Source0-md5:	196c8d2746bd75d3561d129f64bbf9cf
Source1:	%{name}-mozilla-nss.pc
Source2:	%{name}-config.in
Patch0:		%{name}-Makefile.patch
URL:		http://www.mozilla.org/projects/security/pki/nss/
BuildRequires:	nspr-devel >= 1:4.6.3
BuildRequires:	zlib-devel
BuildConflicts:	mozilla < 0.9.6-3
Requires:	nspr >= 1:4.6.3
Obsoletes:	libnss3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		specflags	-fno-strict-aliasing

%description
NSS supports cross-platform development of security-enabled server
applications. Applications built with NSS can support PKCS #5,
PKCS #7, PKCS #11, PKCS #12, S/MIME, TLS, SSL v2 and v3, X.509 v3
certificates, and other security standards.

%description -l pl
NSS wspomaga pisanie wieloplatformowych bezpiecznych serwer�w.
Aplikacja u�ywaj�ca NSS jest w stanie obs�u�y� PKCS #5, PKCS #7,
PKCS #11, PKCS #12, S/MIME, TLS, SSL v2 oraz v3, certyfikaty X.509 v3,
i wiele innych bezpiecznych standard�w.

%package tools
Summary:	NSS command line tools and utilities
Summary(pl):	Narz�dzia NSS
Group:		Applications
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description tools
The NSS Toolkit command line tool.

%description tools -l pl
Narz�dzia NSS obs�ugiwane z linii polece�.

%package devel
Summary:	NSS - header files
Summary(pl):	NSS - pliki nag��wkowe
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}
Obsoletes:	libnss3-devel

%description devel
Development part of NSS library.

%description devel -l pl
Cz�� biblioteki NSS przeznaczona dla programist�w.

%package static
Summary:	NSS - static library
Summary(pl):	NSS - biblioteka statyczna
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}

%description static
Static NSS Toolkit libraries.

%description static -l pl
Statyczne wersje bibliotek z NSS.

%prep
%setup -q
%patch0 -p1

%build
cd mozilla/security/nss

%ifarch %{x8664} ppc64
export USE_64=1
%endif

%{__make} -j1 build_coreconf \
	NSDISTMODE=copy \
	NS_USE_GCC=1 \
	MOZILLA_CLIENT=1 \
	NO_MDUPDATE=1 \
	USE_PTHREADS=1 \
	BUILD_OPT=1 \
	OPTIMIZER="%{rpmcflags}"

%{__make} -j1 build_dbm \
	NSDISTMODE=copy \
	NS_USE_GCC=1 \
	MOZILLA_CLIENT=1 \
	NO_MDUPDATE=1 \
	USE_PTHREADS=1 \
	BUILD_OPT=1 \
	OPTIMIZER="%{rpmcflags}" \
	PLATFORM="pld"

%{__make} -j1 all \
	NSDISTMODE=copy \
	NS_USE_GCC=1 \
	MOZILLA_CLIENT=1 \
	NO_MDUPDATE=1 \
	USE_PTHREADS=1 \
	BUILD_OPT=1 \
	USE_SYSTEM_ZLIB=1 \
	ZLIB_LIBS="-lz" \
	OPTIMIZER="%{rpmcflags}" \
	PLATFORM="pld"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir}/nss,%{_libdir},%{_pkgconfigdir}}

install mozilla/dist/private/nss/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/public/dbm/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/public/nss/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/pld/bin/*		$RPM_BUILD_ROOT%{_bindir}
install mozilla/dist/pld/lib/*		$RPM_BUILD_ROOT%{_libdir}

%{__sed} -e '
	s#libdir=.*#libdir=%{_libdir}#g
	s#includedir=.*#includedir=%{_includedir}#g
	s#VERSION#%{version}#g
' %{SOURCE1} > $RPM_BUILD_ROOT%{_pkgconfigdir}/mozilla-nss.pc
ln -s mozilla-nss.pc $RPM_BUILD_ROOT%{_pkgconfigdir}/nss.pc

NSS_VMAJOR=$(awk '/#define.*NSS_VMAJOR/ {print $3}' mozilla/security/nss/lib/nss/nss.h)
NSS_VMINOR=$(awk '/#define.*NSS_VMINOR/ {print $3}' mozilla/security/nss/lib/nss/nss.h)
NSS_VPATCH=$(awk '/#define.*NSS_VPATCH/ {print $3}' mozilla/security/nss/lib/nss/nss.h)
%{__sed} -e "
	s,@libdir@,%{_libdir},g
	s,@prefix@,%{_prefix},g
	s,@exec_prefix@,%{_prefix},g
	s,@includedir@,%{_includedir}/nss,g
	s,@MOD_MAJOR_VERSION@,$NSS_VMAJOR,g
	s,@MOD_MINOR_VERSION@,$NSS_VMINOR,g
	s,@MOD_PATCH_VERSION@,$NSS_VPATCH,g
" %{SOURCE2} > $RPM_BUILD_ROOT%{_bindir}/nss-config
chmod +x $RPM_BUILD_ROOT%{_bindir}/nss-config

# resolve conflict with squid
mv -f $RPM_BUILD_ROOT%{_bindir}/{,nss-}client

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so
%{_libdir}/lib*.chk

%files devel
%defattr(644,root,root,755)
%{_includedir}/nss
%{_libdir}/libcrmf.a
%{_pkgconfigdir}/*.pc
%attr(755,root,root) %{_bindir}/nss-config

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%exclude %{_bindir}/nss-config

%files static
%defattr(644,root,root,755)
%{_libdir}/lib*.a
%exclude %{_libdir}/libcrmf.a
