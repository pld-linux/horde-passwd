#
%include	/usr/lib/rpm/macros.php
Summary:	passwd - password change module for Horde
Summary(pl):	passwd - modu³ do zmieniania hase³ w Horde
Name:		horde-passwd
Version:	2.2
Release:	0.2
License:	LGPL
Vendor:		The Horde Project
Group:		Applications/Mail
Source0:	http://ftp.horde.org/pub/passwd/passwd-%{version}.tar.gz
# Source0-md5:	c355ab7ddbb51964e771d523cc08bcd2
URL:		http://www.horde.org/passwd/
BuildRequires:	rpm-php-pearprov >= 4.0.2-98
PreReq:		apache
Requires(post):	grep
Requires:	horde >= 2.0
Requires:	php-xml >= 4.1.0
Obsoletes:	horde-addons-passwd
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		apachedir	/etc/httpd
%define		hordedir	/usr/share/horde
%define		confdir		/etc/horde.org

%description
Passwd is the Horde password changing application. While it has been
released and is in production use at many sites, it is also under
heavy development in an effort to expand and improve the module.

%description -l pl
Passwd to aplikacja do zmieniania hase³ w Horde. Chocia¿ zosta³a ju¿
wydana i jest u¿ywana produkcyjnie w wielu serwisach, jest nadal
intensyjwnie rozwijana, aby rozszerzyæ mo¿liwo¶ci i udoskonaliæ ten
modu³.

%prep
%setup -q -n passwd-%{version}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{apachedir} $RPM_BUILD_ROOT%{hordedir}/passwd/{graphics,lib,locale,templates,scripts}
install -d $RPM_BUILD_ROOT%{confdir}/passwd

cp -pR	*.php			$RPM_BUILD_ROOT%{hordedir}/passwd
cp -pR  config/*.dist           $RPM_BUILD_ROOT%{confdir}/passwd
cp -pR  graphics/*              $RPM_BUILD_ROOT%{hordedir}/passwd/graphics
cp -pR  lib/*                   $RPM_BUILD_ROOT%{hordedir}/passwd/lib
cp -pR  locale/*                $RPM_BUILD_ROOT%{hordedir}/passwd/locale
cp -pR  templates/*             $RPM_BUILD_ROOT%{hordedir}/passwd/templates
cp -p   config/.htaccess        $RPM_BUILD_ROOT%{confdir}/passwd
cp -p   templates/.htaccess     $RPM_BUILD_ROOT%{hordedir}/passwd/templates

ln -fs %{confdir}/passwd $RPM_BUILD_ROOT%{hordedir}/passwd/config

# bit unclean..
cd $RPM_BUILD_ROOT%{confdir}/passwd
for i in *.dist; do cp $i `basename $i .dist`; done

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README docs/*
%dir %{hordedir}/passwd
%attr(640,root,http) %{hordedir}/passwd/*.php
%attr(750,root,http) %{hordedir}/passwd/graphics
%attr(750,root,http) %{hordedir}/passwd/lib
%attr(750,root,http) %{hordedir}/passwd/locale
%attr(750,root,http) %{hordedir}/passwd/templates

%attr(750,root,http) %dir %{confdir}/passwd
%{hordedir}/passwd/config
%attr(640,root,http) %{confdir}/passwd/*.dist
%attr(640,root,http) %{confdir}/passwd/.htaccess
%attr(640,root,http) %config(noreplace) %{confdir}/passwd/*.php
#%{apachedir}/passwd
