# $Revision: 1.13 $ $Date: 2002-02-18 21:24:51 $
Summary:	NSS - Network Security Services
Summary(pl):	NSS - Network Security Services
Name:		nss
Version:	3.3.1
Release:	3
License:	GPL
Group:		Libraries
Group(de):	Libraries
Group(es):	Bibliotecas
Group(fr):	Librairies
Group(pl):	Biblioteki
Group(pt_BR):	Bibliotecas
Group(ru):	‚…¬Ã…œ‘≈À…
Group(uk):	‚¶¬Ã¶œ‘≈À…
Source0:	ftp://ftp.mozilla.org/pub/security/nss/releases/NSS_3_3_1_RTM/src/%{name}-%{version}.tar.gz
Patch0:		%{name}-Makefile.patch
BuildRequires:	nspr-devel
BuildRequires:	zip
BuildConflicts:	mozilla < 0.9.6-3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	libnss3

%description
NSS supports cross-platform development of security-enabled server
applications. Applications built with NSS can support PKCS #5, PKCS
#7, PKCS #11, PKCS #12, S/MIME, TLS, SSL v2 and v3, X.509 v3
certificates, and other security standards.

%description -l pl
NNS wspomaga pisanie wieloplatformowych bezpiecznych serwerÛw.
Aplikacja uøywaj±ca NSS jest w stanie obs≥uøyÊ PKCS #5, PKCS #7, PKCS
#11, PKCS #12, S/MIME, TLS, SSL v2 oraz v3, certyfikaty X.509 v3, i
wiele innych bezpiecznych standardÛw.

%package devel
Summary:	NSS - header files
Summary(pl):	NSS - pliki nag≥Ûwkowe
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(es):	Desarrollo/Bibliotecas
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Group(pt_BR):	Desenvolvimento/Bibliotecas
Group(ru):	Ú¡⁄“¡¬œ‘À¡/‚…¬Ã…œ‘≈À…
Group(uk):	Úœ⁄“œ¬À¡/‚¶¬Ã¶œ‘≈À…
Requires:	%{name} = %{version}
Obsoletes:	libnss3-devel

%description devel
Development part of NSS library.

%description devel -l pl
CzÍ∂Ê biblioteki NSS przeznaczona dla programistÛw.

%package tools
Summary:	NSS command line tools and utilities
Summary(pl):	NarzÍdzia NSS
Group:		Applications
Group(de):	Applikationen
Group(es):	Aplicaciones
Group(fr):	Utilitaires
Group(pl):	Aplikacje
Group(pt):	AplicaÁıes
Group(pt_BR):	AplicaÁıes
Requires:	%{name} = %{version}

%description tools
The NSS Toolkit command line tool.

%description tools -l pl
NarzÍdzia NSS obs≥ugiwane z linii poleceÒ.

%package static
Summary:	NSS - static library
Summary(pl):	NSS - biblioteka statyczna
Group:		Development/Libraries
Group(de):	Entwicklung/Libraries
Group(es):	Desarrollo/Bibliotecas
Group(fr):	Development/Librairies
Group(pl):	Programowanie/Biblioteki
Group(pt_BR):	Desenvolvimento/Bibliotecas
Group(ru):	Ú¡⁄“¡¬œ‘À¡/‚…¬Ã…œ‘≈À…
Group(uk):	Úœ⁄“œ¬À¡/‚¶¬Ã¶œ‘≈À…
Requires:	%{name}-devel = %{version}

%description static
Static NSS Toolkit libraries.

%description static -l pl
Statyczne wersje bibliotek z NSS.

%prep
%setup -q
%patch0 -p1

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

install mozilla/dist/private/security/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/public/dbm/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/public/seccmd/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/public/security/*	$RPM_BUILD_ROOT%{_includedir}/nss
install mozilla/dist/pld/bin/*		$RPM_BUILD_ROOT%{_bindir}
install mozilla/dist/pld/lib/*		$RPM_BUILD_ROOT%{_libdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so

%files devel
%defattr(644,root,root,755)
%{_includedir}/nss

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*

%files static
%defattr(644,root,root,755)
%{_libdir}/*.a
