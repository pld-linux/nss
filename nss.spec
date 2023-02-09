# Conditional build:
%bcond_with	bootstrap	# avoid dependency on nss-tools
%bcond_with	tests		# enable tests

%define	nspr_ver	1:4.35
%define	foover	%(echo %{version} | tr . _)
Summary:	NSS - Network Security Services
Summary(pl.UTF-8):	NSS - Network Security Services
Name:		nss
Version:	3.88
Release:	1
Epoch:		1
License:	MPL v2.0
Group:		Libraries
Source0:	https://ftp.mozilla.org/pub/security/nss/releases/NSS_%{foover}_RTM/src/%{name}-%{version}.tar.gz
# Source0-md5:	9570f728198e1850aa2f2c075ea7cbee
Source1:	%{name}-mozilla-nss.pc
Source2:	%{name}-config.in
Source3:	https://www.cacert.org/certs/root.der
# Source3-md5:	a61b375e390d9c3654eebd2031461f6b
Source4:	nss-softokn.pc.in
# Upstream: https://bugzilla.mozilla.org/show_bug.cgi?id=1083900
URL:		https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS
BuildRequires:	nspr-devel >= %{nspr_ver}
%{!?with_bootstrap:BuildRequires:	nss-tools}
BuildRequires:	perl-base
BuildRequires:	sqlite3-devel
BuildRequires:	zlib-devel
BuildConflicts:	mozilla < 0.9.6-3
Requires:	%{name}-softokn-freebl = %{epoch}:%{version}-%{release}
Requires:	nspr >= %{nspr_ver}
Obsoletes:	libnss3
# needs http2 code update: https://bugzilla.mozilla.org/show_bug.cgi?id=1323209
Conflicts:	firefox < 50.1.0-2
Conflicts:	iceape < 2.46-1
Conflicts:	iceweasel < 51
Conflicts:	mozilla-firefox < 51
Conflicts:	seamonkey < 2.47
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		specflags	-fno-strict-aliasing
%define		signedlibs	libfreebl3.so libfreeblpriv3.so libnssdbm3.so libsoftokn3.so
# signed -  stripped before signing
%define		_noautostrip	.*%{_lib}/\\(%(echo %{signedlibs} | sed 's/ /\\\\|/g')\\)
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
Requires:	nspr-devel >= %{nspr_ver}
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

# http://pki.fedoraproject.org/wiki/ECC_Capable_NSS
for dir in ecc noecc; do
	install -d $dir
	cp -a nss $dir
done

%build
%if %{without bootstrap}
# http://wiki.cacert.org/wiki/NSSLib
addbuiltin -n "CAcert Inc." -t "CT,C,C" < %{SOURCE3} >> nss/lib/ckfw/builtins/certdata.txt
%endif

%ifarch %{x8664} ppc64 sparc64 aarch64
export USE_64=1
%endif

export BUILD_OPT=1
export MOZILLA_CLIENT=1
export NSDISTMODE=copy
export NSPR_INCLUDE_DIR=/usr/include/nspr
export NSS_ENABLE_WERROR=0
export NSS_USE_SYSTEM_SQLITE=1
export USE_PTHREADS=1
export USE_SYSTEM_ZLIB=1
export ZLIB_LIBS="-lz"
%ifarch x32
export USE_X32=1
%endif
%{!?with_tests:export NSS_DISABLE_GTESTS=1}

# https://bugzilla.mozilla.org/show_bug.cgi?id=1084623

# Forcing ecc with this hack would produce broken librares (softoken, freebl etc).
# Thus we also build noecc version (which doesn't require hack) and use these
# libs from there.
%{__sed} -i -e 's|#error|//error|g' ecc/nss/lib/freebl/ecl/ecl-curve.h
%{__make} -C ecc/nss all \
	NSS_ECC_MORE_THAN_SUITE_B=1 \
	CC="%{__cc}" \
	OPTIMIZER="%{rpmcflags} %{rpmcppflags}" \
	OS_TEST="%{_target_cpu}" \
	NS_USE_GCC=1

%{__make} -C noecc/nss all \
	CC="%{__cc}" \
	OPTIMIZER="%{rpmcflags} %{rpmcppflags}" \
	OS_TEST="%{_target_cpu}" \
	NS_USE_GCC=1

# strip and sign again
%{__strip} --strip-unneeded -R.comment -R.note \
	{,no}ecc/dist/Linux*/lib/{%(echo %{signedlibs} | tr ' ' ',')}

for dir in ecc noecc; do
	distdir=$(echo $(pwd)/$dir/dist/Linux*)
	for lib in %{signedlibs}; do
		LD_LIBRARY_PATH="$distdir/lib" "$distdir/bin/shlibsign" -i "$distdir/lib/$lib"
	done
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1,%{_includedir}/nss,/%{_lib},%{_libdir},%{_pkgconfigdir}}

cp -p ecc/dist/private/nss/*	$RPM_BUILD_ROOT%{_includedir}/nss
cp -p ecc/dist/public/dbm/*	$RPM_BUILD_ROOT%{_includedir}/nss
cp -p ecc/dist/public/nss/*	$RPM_BUILD_ROOT%{_includedir}/nss
install -p ecc/dist/Linux*/bin/*	$RPM_BUILD_ROOT%{_bindir}
install -p ecc/dist/Linux*/lib/*	$RPM_BUILD_ROOT%{_libdir}

# non-ECC version, we need only libnssdbm3, libsoftokn3, libfreebl3
install -p noecc/dist/Linux*/lib/libnssdbm3.*	$RPM_BUILD_ROOT%{_libdir}
install -p noecc/dist/Linux*/lib/libsoftokn3.*	$RPM_BUILD_ROOT%{_libdir}
install -p noecc/dist/Linux*/lib/libfreebl3.*	$RPM_BUILD_ROOT%{_libdir}

cp -p nss/doc/nroff/*.1		$RPM_BUILD_ROOT%{_mandir}/man1

%{__sed} -e '
	s#libdir=.*#libdir=%{_libdir}#g
	s#includedir=.*#includedir=%{_includedir}#g
	s#VERSION#%{version}#g
' %{SOURCE1} > $RPM_BUILD_ROOT%{_pkgconfigdir}/nss.pc
# compatibility symlink
ln -s nss.pc $RPM_BUILD_ROOT%{_pkgconfigdir}/mozilla-nss.pc

cat %{SOURCE4} | \
sed -e "s,%%libdir%%,%{_libdir},g" \
	-e "s,%%prefix%%,%{_prefix},g" \
	-e "s,%%exec_prefix%%,%{_prefix},g" \
	-e "s,%%includedir%%,%{_includedir}/nss,g" \
	-e "s,%%NSPR_VERSION%%,$(echo %{nspr_ver} | sed -e 's#.*:##g'),g" \
	-e "s,%%NSS_VERSION%%,%{version},g" \
	-e "s,%%SOFTOKEN_VERSION%%,%{version},g" > \
	$RPM_BUILD_ROOT%{_pkgconfigdir}/nss-softokn.pc

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

%{__mv} $RPM_BUILD_ROOT%{_libdir}/libfreebl3.so $RPM_BUILD_ROOT/%{_lib}
ln -s /%{_lib}/libfreebl3.so $RPM_BUILD_ROOT%{_libdir}/libfreebl3.so
%{__mv} $RPM_BUILD_ROOT%{_libdir}/libfreebl3.chk $RPM_BUILD_ROOT/%{_lib}
ln -s /%{_lib}/libfreebl3.chk $RPM_BUILD_ROOT%{_libdir}/libfreebl3.chk
%{__mv} $RPM_BUILD_ROOT%{_libdir}/libfreeblpriv3.so $RPM_BUILD_ROOT/%{_lib}
ln -s /%{_lib}/libfreeblpriv3.so $RPM_BUILD_ROOT%{_libdir}/libfreeblpriv3.so
%{__mv} $RPM_BUILD_ROOT%{_libdir}/libfreeblpriv3.chk $RPM_BUILD_ROOT/%{_lib}
ln -s /%{_lib}/libfreeblpriv3.chk $RPM_BUILD_ROOT%{_libdir}/libfreeblpriv3.chk

# conflict with openssl-static
%{__mv} $RPM_BUILD_ROOT%{_libdir}/libssl{,3}.a

# unit tests
%if %{with tests}
%{__rm} $RPM_BUILD_ROOT%{_bindir}/{certdb,certhigh,cryptohi,der,pk11,softoken,smime,ssl,util}_gtest
%{__rm} $RPM_BUILD_ROOT%{_bindir}/nss_bogo_shim
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libgtest*
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libpkcs11testmodule.*
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libcpputil.*
%endif
%{__rm} $RPM_BUILD_ROOT%{_bindir}/fbectest
%{__rm} $RPM_BUILD_ROOT%{_bindir}/pk11ectest
%{__rm} $RPM_BUILD_ROOT%{_bindir}/pk11importtest
%{__rm} $RPM_BUILD_ROOT%{_bindir}/rsapoptst
%{__rm} $RPM_BUILD_ROOT%{_bindir}/sdbthreadtst
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libnss*-testlib.so

if [ ! -f "$RPM_BUILD_ROOT%{_includedir}/nss/nsslowhash.h" ]; then
	echo >&2 "ERROR: %{_includedir}/nss/nsslowhash.h not installed. Needed by glibc"
	exit 1
fi

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
# COPYING beside MPL v2.0 text contains GPL/LGPL compatibility notes
%doc nss/{COPYING,trademarks.txt}
%attr(755,root,root) %{_libdir}/libfreebl3.so
%attr(755,root,root) %{_libdir}/libfreeblpriv3.so
%attr(755,root,root) %{_libdir}/libnss3.so
%attr(755,root,root) %{_libdir}/libnssckbi.so
%attr(755,root,root) %{_libdir}/libnssdbm3.so
%attr(755,root,root) %{_libdir}/libnssutil3.so
%attr(755,root,root) %{_libdir}/libsmime3.so
%attr(755,root,root) %{_libdir}/libsoftokn3.so
%attr(755,root,root) %{_libdir}/libssl3.so
%{_libdir}/libfreebl3.chk
%{_libdir}/libfreeblpriv3.chk
%{_libdir}/libnssdbm3.chk
%{_libdir}/libsoftokn3.chk

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/nss-config
%{_libdir}/libcrmf.a
%{_libdir}/libfreebl.a
%{_includedir}/nss
%{_pkgconfigdir}/mozilla-nss.pc
%{_pkgconfigdir}/nss.pc
%{_pkgconfigdir}/nss-softokn.pc

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/addbuiltin
%attr(755,root,root) %{_bindir}/atob
%attr(755,root,root) %{_bindir}/baddbdir
%attr(755,root,root) %{_bindir}/bltest
%attr(755,root,root) %{_bindir}/btoa
%attr(755,root,root) %{_bindir}/certutil
%attr(755,root,root) %{_bindir}/chktest
%attr(755,root,root) %{_bindir}/cmsutil
%attr(755,root,root) %{_bindir}/conflict
%attr(755,root,root) %{_bindir}/crlutil
%attr(755,root,root) %{_bindir}/crmftest
%attr(755,root,root) %{_bindir}/dbtest
%attr(755,root,root) %{_bindir}/derdump
%attr(755,root,root) %{_bindir}/dertimetest
%attr(755,root,root) %{_bindir}/digest
%attr(755,root,root) %{_bindir}/ecperf
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
%attr(755,root,root) %{_bindir}/nss-policy-check
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
%attr(755,root,root) %{_bindir}/validation
%attr(755,root,root) %{_bindir}/vfychain
%attr(755,root,root) %{_bindir}/vfyserv
%{_mandir}/man1/certutil.1*
%{_mandir}/man1/cmsutil.1*
%{_mandir}/man1/crlutil.1*
%{_mandir}/man1/derdump.1*
%{_mandir}/man1/modutil.1*
%{_mandir}/man1/pk12util.1*
%{_mandir}/man1/pp.1*
%{_mandir}/man1/signtool.1*
%{_mandir}/man1/signver.1*
%{_mandir}/man1/ssltap.1*
%{_mandir}/man1/vfychain.1*
%{_mandir}/man1/vfyserv.1*

%files static
%defattr(644,root,root,755)
%{_libdir}/libcertdb.a
%{_libdir}/libcerthi.a
%{_libdir}/libcryptohi.a
%{_libdir}/libdbm.a
%{_libdir}/libjar.a
%{_libdir}/libnss.a
%{_libdir}/libnssb.a
%{_libdir}/libnssckfw.a
%{_libdir}/libnssdbm.a
%{_libdir}/libnssdev.a
%{_libdir}/libnsspki.a
%{_libdir}/libnssutil.a
%{_libdir}/libpk11wrap.a
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
%{_libdir}/libsmime.a
%{_libdir}/libsoftokn.a
%{_libdir}/libssl3.a

%files softokn-freebl
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/libfreebl3.so
%attr(755,root,root) /%{_lib}/libfreeblpriv3.so
/%{_lib}/libfreebl3.chk
/%{_lib}/libfreeblpriv3.chk
