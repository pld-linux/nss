%define	foover	%(echo %{version} | tr . _)
Summary:	NSS - Network Security Services
Summary(pl.UTF-8):	NSS - Network Security Services
Name:		nss
Version:	3.15.4
Release:	1
Epoch:		1
License:	MPL v1.1 or GPL v2+ or LGPL v2.1+
Group:		Libraries
Source0:	http://ftp.mozilla.org/pub/mozilla.org/security/nss/releases/NSS_%{foover}_RTM/src/%{name}-%{version}.tar.gz
# Source0-md5:	74738d89615665e3547dc2c0602ab0e6
Source1:	%{name}-mozilla-nss.pc
Source2:	%{name}-config.in
Source3:	http://www.cacert.org/certs/root.der
# Source3-md5:	a61b375e390d9c3654eebd2031461f6b
Patch0:		%{name}-Makefile.patch
Patch1:		hasht-dont-include-prtypes.patch
URL:		http://www.mozilla.org/projects/security/pki/nss/
BuildRequires:	nspr-devel >= 1:4.10.2
BuildRequires:	nss-tools
BuildRequires:	perl-base
BuildRequires:	sqlite3-devel
BuildRequires:	zlib-devel
BuildConflicts:	mozilla < 0.9.6-3
Requires:	nspr >= 1:4.10.2
Requires:	%{name}-softokn-freebl = %{epoch}:%{version}-%{release}
Obsoletes:	libnss3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		specflags	-fno-strict-aliasing
# signed -  stripped before signing
%define		_noautostrip	.*%{_libdir}/libfreebl3.so\\|.*%{_libdir}/libsoftokn3.so
%define		_noautochrpath	.*%{_libdir}/libfreebl3.so\\|.*%{_libdir}/libsoftokn3.so

%description
NSS supports cross-platform development of security-enabled server
applications. Applications built with NSS can support PKCS #5,
PKCS #7, PKCS #11, PKCS #12, S/MIME, TLS, SSL v2 and v3, X.509 v3
certificates, and other security standards.

%description -l pl.UTF-8
NSS wspomaga pisanie wieloplatformowych bezpiecznych serwerów.
Aplikacja używająca NSS jest w stanie obsłużyć PKCS #5, PKCS #7,
PKCS #11, PKCS #12, S/MIME, TLS, SSL v2 oraz v3, certyfikaty X.509 v3,
i wiele innych bezpiecznych standardów.

%package tools
Summary:	NSS command line tools and utilities
Summary(pl.UTF-8):	Narzędzia NSS obsługiwane z linii poleceń
Group:		Applications
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description tools
The NSS Toolkit command line tool.

%description tools -l pl.UTF-8
Narzędzia NSS obsługiwane z linii poleceń.

%package devel
Summary:	NSS - header files
Summary(pl.UTF-8):	NSS - pliki nagłówkowe
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	nspr-devel >= 1:4.10.2
Obsoletes:	libnss3-devel

%description devel
Development part of NSS library.

%description devel -l pl.UTF-8
Część biblioteki NSS przeznaczona dla programistów.

%package static
Summary:	NSS - static library
Summary(pl.UTF-8):	NSS - biblioteka statyczna
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}

%description static
Static NSS Toolkit libraries.

%description static -l pl.UTF-8
Statyczne wersje bibliotek z NSS.

%package softokn-freebl
Summary:	Freebl library for the Network Security Services
Summary(pl.UTF-8):	Biblioteka freebl dla bibliotek NSS
Group:		Libraries

%description softokn-freebl
Freebl cryptographic library for the Network Security Services.

%description softokn-freebl -l pl.UTF-8
Biblioteka kryptograficzna freebl dla bibliotek NSS.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%if 0%{!?debug:1}
# strip before signing
%{__sed} -i -e '/export ADDON_PATH$/a\    echo STRIP \; %{__strip} --strip-unneeded -R.comment -R.note ${5}' nss/cmd/shlibsign/sign.sh
%endif

%build
cd nss

# http://wiki.cacert.org/wiki/NSSLib
addbuiltin -n "CAcert Inc." -t "CT,C,C" < %{SOURCE3} >> lib/ckfw/builtins/certdata.txt

%ifarch %{x8664} ppc64 sparc64
export USE_64=1
%endif

%{__make} -C coreconf -j1 \
	NSDISTMODE=copy \
	NS_USE_GCC=1 \
	MOZILLA_CLIENT=1 \
	NO_MDUPDATE=1 \
	USE_PTHREADS=1 \
	BUILD_OPT=1 \
	CC="%{__cc}" \
	OPTIMIZER="%{rpmcflags}"

%{__make} -j1 \
	NSDISTMODE=copy \
	NS_USE_GCC=1 \
	MOZILLA_CLIENT=1 \
	NO_MDUPDATE=1 \
	USE_PTHREADS=1 \
	USE_SYSTEM_ZLIB=1 \
	ZLIB_LIBS="-lz" \
	BUILD_OPT=1 \
	CC="%{__cc}" \
	OPTIMIZER="%{rpmcflags}" \
	PLATFORM="pld"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir}/nss,/%{_lib},%{_libdir},%{_pkgconfigdir}}

install dist/private/nss/*	$RPM_BUILD_ROOT%{_includedir}/nss
install dist/public/dbm/*	$RPM_BUILD_ROOT%{_includedir}/nss
install dist/public/nss/*	$RPM_BUILD_ROOT%{_includedir}/nss
install dist/pld/bin/*		$RPM_BUILD_ROOT%{_bindir}
install dist/pld/lib/*		$RPM_BUILD_ROOT%{_libdir}

%{__sed} -e '
	s#libdir=.*#libdir=%{_libdir}#g
	s#includedir=.*#includedir=%{_includedir}#g
	s#VERSION#%{version}#g
' %{SOURCE1} > $RPM_BUILD_ROOT%{_pkgconfigdir}/nss.pc
# compatibility symlink
ln -s nss.pc $RPM_BUILD_ROOT%{_pkgconfigdir}/mozilla-nss.pc

NSS_VMAJOR=$(awk '/#define.*NSS_VMAJOR/ {print $3}' nss/lib/nss/nss.h)
NSS_VMINOR=$(awk '/#define.*NSS_VMINOR/ {print $3}' nss/lib/nss/nss.h)
NSS_VPATCH=$(awk '/#define.*NSS_VPATCH/ {print $3}' nss/lib/nss/nss.h)
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

mv $RPM_BUILD_ROOT%{_libdir}/libfreebl3.so $RPM_BUILD_ROOT/%{_lib}
ln -s /%{_lib}/libfreebl3.so $RPM_BUILD_ROOT%{_libdir}/libfreebl3.so
mv $RPM_BUILD_ROOT%{_libdir}/libfreebl3.chk $RPM_BUILD_ROOT/%{_lib}
ln -s /%{_lib}/libfreebl3.chk $RPM_BUILD_ROOT%{_libdir}/libfreebl3.chk

if [ ! -f "$RPM_BUILD_ROOT%{_includedir}/nss/nsslowhash.h" ]; then
	echo "ERROR: %{_includedir}/nss/nsslowhash.h not installed. Needed by glibc" >&2
	exit 1
fi

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfreebl3.so
%attr(755,root,root) %{_libdir}/libnss3.so
%attr(755,root,root) %{_libdir}/libnssckbi.so
%attr(755,root,root) %{_libdir}/libnssdbm3.so
%attr(755,root,root) %{_libdir}/libnssutil3.so
%attr(755,root,root) %{_libdir}/libsmime3.so
%attr(755,root,root) %{_libdir}/libsoftokn3.so
%attr(755,root,root) %{_libdir}/libssl3.so
%{_libdir}/libfreebl3.chk
%{_libdir}/libnssdbm3.chk
%{_libdir}/libsoftokn3.chk

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/nss-config
%{_libdir}/libcrmf.a
%{_includedir}/nss
%{_pkgconfigdir}/mozilla-nss.pc
%{_pkgconfigdir}/nss.pc

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/addbuiltin
%attr(755,root,root) %{_bindir}/atob
%attr(755,root,root) %{_bindir}/baddbdir
%attr(755,root,root) %{_bindir}/bltest
%attr(755,root,root) %{_bindir}/btoa
%attr(755,root,root) %{_bindir}/certcgi
%attr(755,root,root) %{_bindir}/certutil
%attr(755,root,root) %{_bindir}/checkcert
%attr(755,root,root) %{_bindir}/chktest
%attr(755,root,root) %{_bindir}/cmsutil
%attr(755,root,root) %{_bindir}/conflict
%attr(755,root,root) %{_bindir}/crlutil
%attr(755,root,root) %{_bindir}/crmftest
%attr(755,root,root) %{_bindir}/dbtest
%attr(755,root,root) %{_bindir}/derdump
%attr(755,root,root) %{_bindir}/dertimetest
%attr(755,root,root) %{_bindir}/digest
%attr(755,root,root) %{_bindir}/encodeinttest
%attr(755,root,root) %{_bindir}/fipstest
%attr(755,root,root) %{_bindir}/httpserv
%attr(755,root,root) %{_bindir}/listsuites
%attr(755,root,root) %{_bindir}/lowhashtest
%attr(755,root,root) %{_bindir}/makepqg
%attr(755,root,root) %{_bindir}/mangle
%attr(755,root,root) %{_bindir}/modutil
%attr(755,root,root) %{_bindir}/multinit
%attr(755,root,root) %{_bindir}/nonspr10
%attr(755,root,root) %{_bindir}/ocspclnt
%attr(755,root,root) %{_bindir}/ocspresp
%attr(755,root,root) %{_bindir}/oidcalc
%attr(755,root,root) %{_bindir}/p7content
%attr(755,root,root) %{_bindir}/p7env
%attr(755,root,root) %{_bindir}/p7sign
%attr(755,root,root) %{_bindir}/p7verify
%attr(755,root,root) %{_bindir}/pk11gcmtest
%attr(755,root,root) %{_bindir}/pk11mode
%attr(755,root,root) %{_bindir}/pk12util
%attr(755,root,root) %{_bindir}/pk1sign
%attr(755,root,root) %{_bindir}/pkix-errcodes
%attr(755,root,root) %{_bindir}/pp
%attr(755,root,root) %{_bindir}/pwdecrypt
%attr(755,root,root) %{_bindir}/remtest
%attr(755,root,root) %{_bindir}/rsaperf
%attr(755,root,root) %{_bindir}/sdrtest
%attr(755,root,root) %{_bindir}/secmodtest
%attr(755,root,root) %{_bindir}/selfserv
%attr(755,root,root) %{_bindir}/shlibsign
%attr(755,root,root) %{_bindir}/signtool
%attr(755,root,root) %{_bindir}/signver
%attr(755,root,root) %{_bindir}/ssltap
%attr(755,root,root) %{_bindir}/strsclnt
%attr(755,root,root) %{_bindir}/symkeyutil
%attr(755,root,root) %{_bindir}/tstclnt
%attr(755,root,root) %{_bindir}/vfychain
%attr(755,root,root) %{_bindir}/vfyserv

%files static
%defattr(644,root,root,755)
%{_libdir}/libcertdb.a
%{_libdir}/libcerthi.a
%{_libdir}/libcryptohi.a
%{_libdir}/libdbm.a
%{_libdir}/libfreebl3.a
%{_libdir}/libjar.a
%{_libdir}/libnss3.a
%{_libdir}/libnssb.a
%{_libdir}/libnssckfw.a
%{_libdir}/libnssdbm3.a
%{_libdir}/libnssdev.a
%{_libdir}/libnsspki3.a
%{_libdir}/libnssutil3.a
%{_libdir}/libpk11wrap3.a
%{_libdir}/libpkcs12.a
%{_libdir}/libpkcs7.a
%{_libdir}/libpkixcertsel.a
%{_libdir}/libpkixchecker.a
%{_libdir}/libpkixcrlsel.a
%{_libdir}/libpkixmodule.a
%{_libdir}/libpkixparams.a
%{_libdir}/libpkixpki.a
%{_libdir}/libpkixresults.a
%{_libdir}/libpkixstore.a
%{_libdir}/libpkixsystem.a
%{_libdir}/libpkixtop.a
%{_libdir}/libpkixutil.a
%{_libdir}/libsectool.a
%{_libdir}/libsmime3.a
%{_libdir}/libsoftokn3.a
%{_libdir}/libssl3.a

%files softokn-freebl
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/libfreebl3.so
/%{_lib}/libfreebl3.chk
