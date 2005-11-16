%define		_hordeapp	passwd
#define		_snap	2005-09-10
#define		_rc		rc1
%define		_rel	2
#
%include	/usr/lib/rpm/macros.php
Summary:	passwd - password change module for Horde
Summary(pl):	passwd - modu³ do zmieniania hase³ w Horde
Name:		horde-%{_hordeapp}
Version:	3.0
Release:	%{?_rc:0.%{_rc}.}%{?_snap:0.%(echo %{_snap} | tr -d -).}%{_rel}
License:	ASL
Group:		Applications/WWW
#Source0:	ftp://ftp.horde.org/pub/snaps/%{_snap}/%{_hordeapp}-HEAD-%{_snap}.tar.gz
Source0:	ftp://ftp.horde.org/pub/passwd/%{_hordeapp}-h3-%{version}.tar.gz
# Source0-md5:	ca5612500c91c4ef3c838e8e94376332
Source1:	%{name}.conf
URL:		http://www.horde.org/passwd/
BuildRequires:	rpm-php-pearprov >= 4.0.2-98
BuildRequires:	rpmbuild(macros) >= 1.226
BuildRequires:	tar >= 1:1.15.1
Requires(post):	sed >= 4.0
Requires:	apache(mod_access)
Requires:	horde >= 3.0
Requires:	php-xml >= 4.1.0
Requires:	webserver = apache
Obsoletes:	horde-addons-passwd
Conflicts:	apache < 1.3.33-2
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# horde accesses it directly in help->about
%define		_noautocompressdoc  CREDITS
%define		_noautoreq	'pear(Horde.*)'

%define		hordedir	/usr/share/horde
%define		_sysconfdir	/etc/horde.org
%define		_appdir		%{hordedir}/%{_hordeapp}

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
%setup -q -c -T -n %{?_snap:%{_hordeapp}-%{_snap}}%{!?_snap:%{_hordeapp}-%{version}%{?_rc:-%{_rc}}}
tar zxf %{SOURCE0} --strip-components=1

rm -f scripts/.htaccess
# considered harmful (horde/docs/SECURITY)
rm -f test.php

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{_hordeapp} \
	$RPM_BUILD_ROOT%{_appdir}/{docs,lib,locale,scripts,templates,themes}

cp -pR	*.php			$RPM_BUILD_ROOT%{_appdir}
for i in config/*.dist; do
	cp -p $i $RPM_BUILD_ROOT%{_sysconfdir}/%{_hordeapp}/$(basename $i .dist)
done
echo '<?php ?>' > $RPM_BUILD_ROOT%{_sysconfdir}/%{_hordeapp}/conf.php
cp -p config/conf.xml $RPM_BUILD_ROOT%{_sysconfdir}/%{_hordeapp}/conf.xml
touch					$RPM_BUILD_ROOT%{_sysconfdir}/%{_hordeapp}/conf.php.bak

cp -pR	lib/*			$RPM_BUILD_ROOT%{_appdir}/lib
cp -pR	locale/*		$RPM_BUILD_ROOT%{_appdir}/locale
cp -pR	templates/*		$RPM_BUILD_ROOT%{_appdir}/templates
cp -pR	themes/*		$RPM_BUILD_ROOT%{_appdir}/themes

ln -s %{_sysconfdir}/%{_hordeapp} 	$RPM_BUILD_ROOT%{_appdir}/config
ln -s %{_docdir}/%{name}-%{version}/CREDITS $RPM_BUILD_ROOT%{_appdir}/docs

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache-%{_hordeapp}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/%{_hordeapp}/conf.php.bak ]; then
	install /dev/null -o root -g http -m660 %{_sysconfdir}/%{_hordeapp}/conf.php.bak
fi

# take uids with < 500 and update refused logins in default conf.xml
USERLIST=$(awk -F: '{ if ($3 < 500) print $1 }' < /etc/passwd | xargs | tr ' ' ',')
if [ "$USERLIST" ]; then
	sed -i -e "
	# primitive xml parser ;)
	/configlist name=\"refused\"/s/>.*</>$USERLIST</
	" %{_sysconfdir}/%{_hordeapp}/conf.xml
fi

%triggerin -- apache1 >= 1.3.33-2
%apache_config_install -v 1 -c %{_sysconfdir}/apache-%{_hordeapp}.conf

%triggerun -- apache1 >= 1.3.33-2
%apache_config_uninstall -v 1

%triggerin -- apache >= 2.0.0
%apache_config_install -v 2 -c %{_sysconfdir}/apache-%{_hordeapp}.conf

%triggerun -- apache >= 2.0.0
%apache_config_uninstall -v 2

%triggerpostun -- horde-passwd <= 2.2-0.1
for i in backends.php conf.php; do
	if [ -f /home/services/httpd/html/horde/passwd/config/$i.rpmsave ]; then
		mv -f %{confdir}/passwd/$i %{confdir}/passwd/$i.rpmnew
		mv -f /home/services/httpd/html/horde/passwd/config/$i.rpmsave %{confdir}/passwd/$i
	fi
done

%files
%defattr(644,root,root,755)
%doc README docs/* scripts
%attr(750,root,http) %dir %{_sysconfdir}/%{_hordeapp}
%attr(640,root,root) %config(noreplace) %{_sysconfdir}/apache-%{_hordeapp}.conf
%attr(660,root,http) %config(noreplace) %{_sysconfdir}/%{_hordeapp}/conf.php
%attr(660,root,http) %config(noreplace) %ghost %{_sysconfdir}/%{_hordeapp}/conf.php.bak
%attr(640,root,http) %config(noreplace) %{_sysconfdir}/%{_hordeapp}/[!c]*.php
%attr(640,root,http) %{_sysconfdir}/%{_hordeapp}/conf.xml

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/config
%{_appdir}/docs
%{_appdir}/lib
%{_appdir}/locale
%{_appdir}/templates
%{_appdir}/themes
