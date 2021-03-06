%define		_hordeapp	passwd
#
Summary:	passwd - password change module for Horde
Summary(pl.UTF-8):	passwd - moduł do zmieniania haseł w Horde
Name:		horde-%{_hordeapp}
Version:	3.1.3
Release:	4
License:	ASL
Group:		Applications/WWW
Source0:	ftp://ftp.horde.org/pub/passwd/%{_hordeapp}-h3-%{version}.tar.gz
# Source0-md5:	2094be49e14e94ff66e9304718db7cd6
Source1:	%{name}-apache.conf
Source2:	%{name}-httpd.conf
URL:		http://www.horde.org/passwd/
BuildRequires:	rpm-php-pearprov >= 4.0.2-98
BuildRequires:	rpmbuild(macros) >= 1.264
Requires(post):	sed >= 4.0
Requires:	horde >= 3.0
Requires:	php(core) >= 4.1.0
Requires:	php(ctype)
Requires:	php(xml)
Requires:	webapps
Suggests:	php(ldap)
Suggests:	php(mhash)
Suggests:	php-pear-Crypt_CHAP
Obsoletes:	horde-addons-passwd
Conflicts:	apache-base < 2.4.0-1
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreq_pear	Horde.*

%define		hordedir	/usr/share/horde
%define		_appdir		%{hordedir}/%{_hordeapp}
%define		_webapps	/etc/webapps
%define		_webapp		horde-%{_hordeapp}
%define		_sysconfdir	%{_webapps}/%{_webapp}

%description
Passwd is the Horde password changing application. While it has been
released and is in production use at many sites, it is also under
heavy development in an effort to expand and improve the module.

%description -l pl.UTF-8
Passwd to aplikacja do zmieniania haseł w Horde. Chociaż została już
wydana i jest używana produkcyjnie w wielu serwisach, jest nadal
intensyjwnie rozwijana, aby rozszerzyć możliwości i udoskonalić ten
moduł.

%prep
%setup -q -n %{_hordeapp}-h3-%{version}

rm -f {,*/}.htaccess
for i in config/*.dist; do
	mv $i config/$(basename $i .dist)
done
# considered harmful (horde/docs/SECURITY)
rm -f test.php

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_appdir}/docs}

cp -a *.php $RPM_BUILD_ROOT%{_appdir}
cp -a config/* $RPM_BUILD_ROOT%{_sysconfdir}
echo '<?php ?>' > $RPM_BUILD_ROOT%{_sysconfdir}/conf.php
touch $RPM_BUILD_ROOT%{_sysconfdir}/conf.php.bak
cp -a lib locale templates themes $RPM_BUILD_ROOT%{_appdir}
cp -a docs/CREDITS $RPM_BUILD_ROOT%{_appdir}/docs

ln -s %{_sysconfdir} 	$RPM_BUILD_ROOT%{_appdir}/config
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/conf.php.bak ]; then
	install /dev/null -o root -g http -m660 %{_sysconfdir}/conf.php.bak
fi

# take uids with < 500 and update refused logins in default conf.xml
USERLIST=$(awk -F: '{ if ($3 < 500) print $1 }' < /etc/passwd | xargs | tr ' ' ',')
if [ "$USERLIST" ]; then
	sed -i -e "
	# primitive xml parser ;)
	/configlist name=\"refused\"/s/>.*</>$USERLIST</
	" %{_sysconfdir}/conf.xml
fi

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache-base
%webapp_unregister httpd %{_webapp}

%triggerpostun -- horde-%{_hordeapp} < 3.0-2.1
for i in backends.php conf.php; do
	if [ -f /home/services/httpd/html/horde/passwd/config/$i.rpmsave ]; then
		mv -f %{_sysconfdir}/$i{,.rpmnew}
		mv -f /home/services/httpd/html/horde/passwd/config/$i.rpmsave %{_sysconfdir}/$i
	fi
done

for i in backends.php conf.php; do
	if [ -f /etc/horde.org/%{_hordeapp}/$i.rpmsave ]; then
		mv -f %{_sysconfdir}/$i{,.rpmnew}
		mv -f /etc/horde.org/%{_hordeapp}/$i.rpmsave %{_sysconfdir}/$i
	fi
done

if [ -f /etc/horde.org/apache-%{_hordeapp}.conf.rpmsave ]; then
	mv -f %{_sysconfdir}/apache.conf{,.rpmnew}
	mv -f %{_sysconfdir}/httpd.conf{,.rpmnew}
	cp -f /etc/horde.org/apache-%{_hordeapp}.conf.rpmsave %{_sysconfdir}/apache.conf
	cp -f /etc/horde.org/apache-%{_hordeapp}.conf.rpmsave %{_sysconfdir}/httpd.conf
fi

if [ -L /etc/apache/conf.d/99_horde-%{_hordeapp}.conf ]; then
	/usr/sbin/webapp register apache %{_webapp}
	rm -f /etc/apache/conf.d/99_horde-%{_hordeapp}.conf
	%service -q apache reload
fi
if [ -L /etc/httpd/httpd.conf/99_horde-%{_hordeapp}.conf ]; then
	/usr/sbin/webapp register httpd %{_webapp}
	rm -f /etc/httpd/httpd.conf/99_horde-%{_hordeapp}.conf
	%service -q httpd reload
fi

%files
%defattr(644,root,root,755)
%doc README docs/* scripts
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(660,root,http) %config(noreplace) %{_sysconfdir}/conf.php
%attr(660,root,http) %config(noreplace) %ghost %{_sysconfdir}/conf.php.bak
%attr(640,root,http) %config(noreplace) %{_sysconfdir}/[!c]*.php
%attr(640,root,http) %{_sysconfdir}/conf.xml

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/config
%{_appdir}/docs
%{_appdir}/lib
%{_appdir}/locale
%{_appdir}/templates
%{_appdir}/themes
