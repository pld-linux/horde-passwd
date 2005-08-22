#
%include	/usr/lib/rpm/macros.php
Summary:	passwd - password change module for Horde
Summary(pl):	passwd - modu� do zmieniania hase� w Horde
Name:		horde-passwd
Version:	3.0
Release:	0.1
License:	LGPL
Vendor:		The Horde Project
Group:		Applications/WWW
Source0:	ftp://ftp.horde.org/pub/passwd/passwd-h3-%{version}-beta.tar.gz
# Source0-md5:	9ea299d2822c9d3ca5efca03ce6a23a4
Source1:	%{name}.conf
URL:		http://www.horde.org/passwd/
BuildRequires:	rpm-php-pearprov >= 4.0.2-98
PreReq:		apache
Requires(post):	grep
Requires:	horde >= 3.0
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
Passwd to aplikacja do zmieniania hase� w Horde. Chocia� zosta�a ju�
wydana i jest u�ywana produkcyjnie w wielu serwisach, jest nadal
intensyjwnie rozwijana, aby rozszerzy� mo�liwo�ci i udoskonali� ten
modu�.

%prep
%setup -q -n passwd-h3-%{version}-beta

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{apachedir} $RPM_BUILD_ROOT%{hordedir}/passwd/{themes/graphics,lib,locale,templates,scripts} 
install -d $RPM_BUILD_ROOT%{confdir}/passwd

cp -pR *.php			$RPM_BUILD_ROOT%{hordedir}/passwd
cp -pR config/*.dist		$RPM_BUILD_ROOT%{confdir}/passwd
cp -pR themes/graphics/*	$RPM_BUILD_ROOT%{hordedir}/passwd/themes/graphics
cp -pR lib/*			$RPM_BUILD_ROOT%{hordedir}/passwd/lib
cp -pR locale/*			$RPM_BUILD_ROOT%{hordedir}/passwd/locale
cp -pR templates/*		$RPM_BUILD_ROOT%{hordedir}/passwd/templates
cp -p  config/.htaccess		$RPM_BUILD_ROOT%{confdir}/passwd
cp -p  templates/.htaccess	$RPM_BUILD_ROOT%{hordedir}/passwd/templates

ln -fs %{confdir}/passwd $RPM_BUILD_ROOT%{hordedir}/passwd/config

install %{SOURCE1} $RPM_BUILD_ROOT%{apachedir}

# bit unclean..
cd $RPM_BUILD_ROOT%{confdir}/passwd
for i in *.dist; do cp $i `basename $i .dist`; done

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*%{name}.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/%{name}.conf" >> /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/usr/sbin/apachectl restart 1>&2
	fi
elif [ -d /etc/httpd/httpd.conf ]; then
	ln -sf /etc/httpd/%{name}.conf /etc/httpd/httpd.conf/99_%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/usr/sbin/apachectl restart 1>&2
	fi
fi

%preun
if [ "$1" = "0" ]; then
	umask 027
	if [ -d /etc/httpd/httpd.conf ]; then
		rm -f /etc/httpd/httpd.conf/99_%{name}.conf
	else
		grep -v "^Include.*%{name}.conf" /etc/httpd/httpd.conf > \
			/etc/httpd/httpd.conf.tmp
		mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	fi
	if [ -f /var/lock/subsys/httpd ]; then
		/usr/sbin/apachectl restart 1>&2
	fi
fi

%triggerpostun -- horde-passwd <= 2.2-0.1
for i in backends.php conf.php; do
	if [ -f /home/services/httpd/html/horde/passwd/config/$i.rpmsave ]; then
		mv -f %{confdir}/passwd/$i %{confdir}/passwd/$i.rpmnew
		mv -f /home/services/httpd/html/horde/passwd/config/$i.rpmsave %{confdir}/passwd/$i
	fi
done

%files
%defattr(644,root,root,755)
%doc README docs/*
%dir %{hordedir}/passwd
%attr(640,root,http) %{hordedir}/passwd/*.php
%attr(750,root,http) %{hordedir}/passwd/themes/graphics
%attr(750,root,http) %{hordedir}/passwd/lib
%attr(750,root,http) %{hordedir}/passwd/locale
%attr(750,root,http) %{hordedir}/passwd/templates

%attr(750,root,http) %dir %{confdir}/passwd
%{hordedir}/passwd/config
%attr(640,root,http) %{confdir}/passwd/*.dist
%attr(640,root,http) %{confdir}/passwd/.htaccess
%attr(640,root,http) %config(noreplace) %{confdir}/passwd/*.php
%attr(640,root,http) %{apachedir}/%{name}.conf
