# $Revision: 1.27.2.2 $ $Date: 2002-09-28 23:25:45 $
%define		snap	20020929

Summary:	NSS - Network Security Services
Summary(pl):	NSS - Network Security Services
Name:		nss
Version:	3.4.2
Release:	3.%{snap}
Epoch:		1
License:	GPL
Group:		Libraries
#Source0:	ftp://ftp.mozilla.org/pub/security/nss/releases/NSS_3_4_2_RTM/src/%{name}-%{version}.tar.gz
Source0:	%{name}-%{snap}.tar.bz2
Patch0:		%{name}-Makefile.patch
Patch1:		%{name}-system-zlib.patch
BuildRequires:  nspr-devel >= 4.1.2-3
BuildRequires:	zip >= 2.1
BuildConflicts:	mozilla < 0.9.6-3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	libnss3

%description
NSS supports cross-platform development of security-enabled server
applications. Applications built with NSS can support PKCS #5, PKCS
#7, PKCS #11, PKCS #12, S/MIME, TLS, SSL v2 and v3, X.509 v3
certificates, and other security standards.

%description -l pl
NSS wspomaga pisanie wieloplatformowych bezpiecznych serwer�w.
Aplikacja u�ywaj�ca NSS jest w stanie obs�u�y� PKCS #5, PKCS #7, PKCS
#11, PKCS #12, S/MIME, TLS, SSL v2 oraz v3, certyfikaty X.509 v3, i
wiele innych bezpiecznych standard�w.

%package tools
Summary:	NSS command line tools and utilities
Summary(pl):	Narz�dzia NSS
Group:		Applications
Requires:	%{name} = %{version}

%description tools
The NSS Toolkit command line tool.

%description tools -l pl
Narz�dzia NSS obs�ugiwane z linii polece�.

%package devel
Summary:	NSS - header files
Summary(pl):	NSS - pliki nag��wkowe
Group:		Development/Libraries
Requires:	%{name} = %{version}
Obsoletes:	libnss3-devel

%description devel
Development part of NSS library.

%description devel -l pl
Cz�� biblioteki NSS przeznaczona dla programist�w.

%package static
Summary:	NSS - static library
Summary(pl):	NSS - biblioteka statyczna
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}

%description static
Static NSS Toolkit libraries.

%description static -l pl
Statyczne wersje bibliotek z NSS.

%prep
%setup -q -n %{name}-%{snap}
%patch0 -p1
%patch1 -p1

%build
cd mozilla/security/nss

%{__make} build_coreconf \
	NSDISTMODE=copy \
	NS_USE_GCC=1 \
	MOZILLA_CLIENT=1 \
	NO_MDUPDATE=1 \
	USE_PTHREADS=1 \
	BUILD_OPT=1 \
	OPTIMIZER="%{rpmcflags}"

%{__make} build_dbm \
	NSDISTMODE=copy \
	NS_USE_GCC=1 \
	MOZILLA_CLIENT=1 \
	NO_MDUPDATE=1 \
	USE_PTHREADS=1 \
	BUILD_OPT=1 \
	OPTIMIZER="%{rpmcflags}" \
	PLATFORM="pld"

%{__make} all \
	NSDISTMODE=copy \
	NS_USE_GCC=1 \
	MOZILLA_CLIENT=1 \
	NO_MDUPDATE=1 \
	USE_PTHREADS=1 \
	BUILD_OPT=1 \
	OPTIMIZER="%{rpmcflags}" \
	PLATFORM="pld"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir}/nss,%{_libdir}}

install mozilla/dist/private/nss/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/public/dbm/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/public/seccmd/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/public/nss/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/pld/bin/*		$RPM_BUILD_ROOT%{_bindir}
install mozilla/dist/pld/lib/*		$RPM_BUILD_ROOT%{_libdir}

# resolve conflict with squid
mv -f $RPM_BUILD_ROOT%{_bindir}/{,nss-}client

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so

%files devel
%defattr(644,root,root,755)
%{_includedir}/nss
%{_libdir}/libcrmf.a

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*

%files static
%defattr(644,root,root,755)
%{_libdir}/lib[^c]*.a
%{_libdir}/libc[^r]*.a
%{_libdir}/libcr[^m]*.a
