Summary:     Wazuh helps you to gain security visibility into your infrastructure by monitoring hosts at an operating system and application level. It provides the following capabilities: log analysis, file integrity monitoring, intrusions detection and policy and compliance monitoring
Name:        wazuh-agent
Version:     3.5.0
Release:     %{_release}
License:     GPL
Group:       System Environment/Daemons
Source0:     %{name}-%{version}.tar.gz
URL:         https://www.wazuh.com/
BuildRoot:   %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor:      Wazuh, Inc <support@wazuh.com>
Packager:    Wazuh, Inc <support@wazuh.com>
Requires(pre):    /usr/sbin/groupadd /usr/sbin/useradd
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig /sbin/service
Requires(postun): /sbin/service
Conflicts:   ossec-hids ossec-hids-agent wazuh-manager wazuh-local
AutoReqProv: no

Requires: coreutils
%if 0%{?el} >= 6 || 0%{?rhel} >= 6
BuildRequires: coreutils glibc-devel automake autoconf libtool policycoreutils-python
%else
BuildRequires: coreutils glibc-devel automake autoconf libtool policycoreutils
%endif

%if 0%{?fc25}
BuildRequires: perl
%endif

%if 0%{?el5}
BuildRequires: perl
%endif

ExclusiveOS: linux

%description
Wazuh helps you to gain security visibility into your infrastructure by monitoring
hosts at an operating system and application level. It provides the following capabilities:
log analysis, file integrity monitoring, intrusions detection and policy and compliance monitoring

%prep
%setup -q

echo "Vendor is %_vendor"

./gen_ossec.sh conf agent centos %rhel %{_localstatedir} > etc/ossec-agent.conf
./gen_ossec.sh init agent %{_localstatedir} > ossec-init.conf

pushd src
# Rebuild for agent
make clean

%if 0%{?el} >= 6 || 0%{?rhel} >= 6
    make deps
    make -j%{_threads} TARGET=agent USE_SELINUX=yes PREFIX=%{_localstatedir}
%else
    make deps RESOURCES_URL=http://packages.wazuh.com/deps/3.5
    make -j%{_threads} TARGET=agent USE_AUDIT=no USE_SELINUX=yes PREFIX=%{_localstatedir}
%endif

popd

%install
# Clean BUILDROOT
rm -fr %{buildroot}

mkdir -p ${RPM_BUILD_ROOT}%{_initrddir}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/backup
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/active-response/bin
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/agentless
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/bin
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/etc/shared
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/lib
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/logs
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/logs/ossec
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/queue/{agents,alerts,diff,ossec,rids,syscheck}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/var/{run,selinux,wodles,incoming,upgrade}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/.ssh
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/wodles
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/aws
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap/content

# Templates for initscript
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/src/init
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/etc/templates/config/generic
cp -rp  etc/templates/config/generic/* ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/etc/templates/config/generic
install -m 0640 ossec-init.conf ${RPM_BUILD_ROOT}%{_sysconfdir}
install -m 0640 src/init/inst-functions.sh ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/src/init
install -m 0640 src/init/template-select.sh ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/src/init
install -m 0640 src/init/shared.sh ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/src/init
install -m 0640 src/init/replace_manager_ip.sh ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/src/init
install -m 0640 src/LOCATION ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/src
install -m 0640 src/VERSION ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/src
install -m 0640 src/REVISION ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/src
install -m 0640 add_localfiles.sh ${RPM_BUILD_ROOT}%{_localstatedir}/tmp

# AWS wodle
install -m 0750 wodles/aws/aws.py ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/aws

# Wazuh lib
install -m 0750 src/libwazuhext.so ${RPM_BUILD_ROOT}%{_localstatedir}/lib

# Open Scap files
install -m 0750 wodles/oscap/oscap.py ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap
install -m 0750 wodles/oscap/template_oval.xsl ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap
install -m 0750 wodles/oscap/template_xccdf.xsl ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap
install -m 0640 wodles/oscap/content/cve-redhat-7-ds.xml ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap/content
install -m 0640 wodles/oscap/content/ssg-rhel-7-ds.xml ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap/content
install -m 0640 wodles/oscap/content/ssg-centos-7-ds.xml ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap/content
install -m 0640 wodles/oscap/content/cve-redhat-6-ds.xml ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap/content
install -m 0640 wodles/oscap/content/ssg-rhel-6-ds.xml ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap/content
install -m 0640 wodles/oscap/content/ssg-centos-6-ds.xml ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap/content
install -m 0640 wodles/oscap/content/ssg-fedora-24-ds.xml ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap/content

# SELinux file
install -m 0640 src/selinux/wazuh.pp ${RPM_BUILD_ROOT}%{_localstatedir}/var/selinux


cp CHANGELOG.md CHANGELOG
install -m 0755 src/init/ossec-hids-rh.init ${RPM_BUILD_ROOT}%{_initrddir}/wazuh-agent
install -m 0640 etc/wpk_root.pem ${RPM_BUILD_ROOT}%{_localstatedir}/etc
install -m 0640 etc/internal_options* ${RPM_BUILD_ROOT}%{_localstatedir}/etc
install -m 0640 etc/local_internal_options.conf ${RPM_BUILD_ROOT}%{_localstatedir}/etc
install -m 0755 active-response/*.sh ${RPM_BUILD_ROOT}%{_localstatedir}/active-response/bin
install -m 0750 active-response/*.py ${RPM_BUILD_ROOT}%{_localstatedir}/active-response/bin
install -m 0755 active-response/firewalls/*.sh ${RPM_BUILD_ROOT}%{_localstatedir}/active-response/bin
install -m 0644 src/rootcheck/db/*.txt ${RPM_BUILD_ROOT}%{_localstatedir}/etc/shared
install -m 0650 src/agentlessd/scripts/* ${RPM_BUILD_ROOT}%{_localstatedir}/agentless
install -m 0650 src/ossec-logcollector ${RPM_BUILD_ROOT}%{_localstatedir}/bin
install -m 0650 src/ossec-syscheckd ${RPM_BUILD_ROOT}%{_localstatedir}/bin
install -m 0650 src/ossec-execd ${RPM_BUILD_ROOT}%{_localstatedir}/bin
install -m 0650 src/ossec-agentd ${RPM_BUILD_ROOT}%{_localstatedir}/bin
install -m 0650 src/manage_agents ${RPM_BUILD_ROOT}%{_localstatedir}/bin
install -m 0650 src/agent-auth ${RPM_BUILD_ROOT}%{_localstatedir}/bin/
install -m 0650 src/wazuh-modulesd ${RPM_BUILD_ROOT}%{_localstatedir}/bin

install -m 0750 wodles/oscap/oscap.py ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap
install -m 0750 wodles/oscap/template* ${RPM_BUILD_ROOT}%{_localstatedir}/wodles/oscap

cp -pr src/init/ossec-client.sh ${RPM_BUILD_ROOT}%{_localstatedir}/bin/ossec-control
cp -pr contrib/util.sh ${RPM_BUILD_ROOT}%{_localstatedir}/bin/
cp -pr etc/ossec-agent.conf ${RPM_BUILD_ROOT}%{_localstatedir}/etc/ossec.conf

# Copying install scripts to /usr/share
mkdir -p ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/
cp gen_ossec.sh ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/
cp add_localfiles.sh ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/

mkdir -p ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/src
cp src/VERSION ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/src/
cp src/REVISION ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/src/
cp src/LOCATION ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/src/

mkdir -p ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/src/init
cp -r src/init/*  ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/src/init

# Systemd files
mkdir -p ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/src/systemd
cp -r src/systemd/*  ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/src/systemd

mkdir -p ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/etc/templates/config/generic
cp -r etc/templates/config/generic/* ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/etc/templates/config/generic

# Copy scap templates
mkdir -p ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/etc/templates/config/centos
cp -r  etc/templates/config/centos/* ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/etc/templates/config/centos

mkdir -p ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/etc/templates/config/fedora
cp -r  etc/templates/config/fedora/* ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/etc/templates/config/fedora

mkdir -p ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/etc/templates/config/rhel
cp -r  etc/templates/config/rhel/* ${RPM_BUILD_ROOT}/usr/share/wazuh-agent/scripts/tmp/etc/templates/config/rhel

exit 0
%pre

if ! id -g ossec > /dev/null 2>&1; then
  groupadd -r ossec
fi
if ! id -u ossec > /dev/null 2>&1; then
  useradd -g ossec -G ossec       \
        -d %{_localstatedir} \
        -r -s /sbin/nologin ossec
fi

# Delete old service
if [ -f /etc/init.d/ossec ]; then
  rm /etc/init.d/ossec
fi

if [ $1 = 1 ]; then
  if [ -f %{_localstatedir}/etc/ossec.conf ]; then
    echo "====================================================================================="
    echo "= Backup from your ossec.conf has been created at %{_localstatedir}/etc/ossec.conf.rpmorig ="
    echo "= Please verify your ossec.conf configuration at %{_localstatedir}/etc/ossec.conf          ="
    echo "====================================================================================="
    mv %{_localstatedir}/etc/ossec.conf %{_localstatedir}/etc/ossec.conf.rpmorig
  fi
fi
if [ $1 = 2 ]; then
    cp -rp %{_localstatedir}/etc/ossec.conf %{_localstatedir}/etc/ossec.bck
fi
%post

if [ $1 = 1 ]; then
  if [ -f /etc/os-release ]; then
    sles=$(grep "\"sles" /etc/os-release)
    if [ ! -z "$sles" ]; then
      install -m 755 /usr/share/wazuh-agent/scripts/tmp/src/init/ossec-hids-suse.init /etc/rc.d/wazuh-agent
    fi
  fi
  touch %{_localstatedir}/etc/client.keys
  chown root:ossec %{_localstatedir}/etc/client.keys
  chmod 0640 %{_localstatedir}/etc/client.keys
  touch %{_localstatedir}/logs/ossec.log
  chown ossec:ossec %{_localstatedir}/logs/ossec.log
  chmod 660 %{_localstatedir}/logs/ossec.log

  touch %{_localstatedir}/logs/active-responses.log
  chown ossec:ossec %{_localstatedir}/logs/active-responses.log
  chmod 0660 %{_localstatedir}/logs/active-responses.log

  # Generating osse.conf file
  . /usr/share/wazuh-agent/scripts/tmp/src/init/dist-detect.sh
  /usr/share/wazuh-agent/scripts/tmp/gen_ossec.sh conf agent ${DIST_NAME} ${DIST_VER}.${DIST_SUBVER} %{_localstatedir} > %{_localstatedir}/etc/ossec.conf
  chown root:ossec %{_localstatedir}/etc/ossec.conf
  chmod 0640 %{_localstatedir}/etc/ossec.conf

  # Add default local_files to ossec.conf
  %{_localstatedir}/tmp/add_localfiles.sh %{_localstatedir} >> %{_localstatedir}/etc/ossec.conf
  if [ -f %{_localstatedir}/etc/ossec.conf.rpmorig ]; then
      %{_localstatedir}/tmp/src/init/replace_manager_ip.sh %{_localstatedir}/etc/ossec.conf.rpmorig %{_localstatedir}/etc/ossec.conf
  fi

  /sbin/chkconfig --add wazuh-agent
  /sbin/chkconfig wazuh-agent on

fi

if [ ! -d /run/systemd/system ]; then
  update-rc.d wazuh-agent defaults > /dev/null 2>&1
fi

if [ -d /run/systemd/system ]; then
  install -m 644 /usr/share/wazuh-agent/scripts/tmp/src/systemd/wazuh-agent.service /etc/systemd/system/
  systemctl daemon-reload
  systemctl stop wazuh-agent
  systemctl enable wazuh-agent > /dev/null 2>&1
fi

touch %{_localstatedir}/logs/ossec.json
chown ossec:ossec %{_localstatedir}/logs/ossec.json
chmod 660 %{_localstatedir}/logs/ossec.json

chmod 640 %{_sysconfdir}/ossec-init.conf
chown root:ossec %{_sysconfdir}/ossec-init.conf

rm -rf %{_localstatedir}/tmp/etc
rm -rf %{_localstatedir}/tmp/src
rm -f %{_localstatedir}/tmp/add_localfiles.sh
ln -sf %{_sysconfdir}/ossec-init.conf %{_localstatedir}/etc/ossec-init.conf

chown root:ossec %{_localstatedir}/etc/shared/*

if [ $1 = 2 ]; then
  if [ -f %{_localstatedir}/etc/ossec.bck ]; then
      mv %{_localstatedir}/etc/ossec.bck %{_localstatedir}/etc/ossec.conf
  fi
fi

# The check for SELinux is not executed in the legacy OS.
add_selinux="yes"
if [ "${DIST_NAME}" == "centos" -a "${DIST_VER}" == "5" ] || [ "${DIST_NAME}" == "rhel" -a "${DIST_VER}" == "5" ] || [ "${DIST_NAME}" == "suse" -a "${DIST_VER}" == "11" ] ; then
  add_selinux="no"
fi

# Check if SELinux is installed and enabled
if [ ${add_selinux} == "yes" ]; then
  if command -v getenforce > /dev/null 2>&1 && command -v semodule > /dev/null 2>&1; then
    if [ $(getenforce) !=  "Disabled" ]; then
      if ! (semodule -l | grep wazuh > /dev/null); then
        echo "Installing Wazuh policy for SELinux."
        semodule -i %{_localstatedir}/var/selinux/wazuh.pp
        semodule -e wazuh
      else
        echo "Skipping installation of Wazuh policy for SELinux: module already installed."
      fi
    else
      echo "SELinux is disabled. Not adding Wazuh policy."
    fi
  else
    echo "SELinux is not installed. Not adding Wazuh policy."
  fi
elif [ ${add_selinux} == "no" ]; then
  # SELINUX Policy for CentOS 5 and RHEL 5 to use the Wazuh Lib
  if [ "${DIST_NAME}" != "suse" ]; then
    if command -v getenforce > /dev/null 2>&1; then
      if [ $(getenforce) !=  "Disabled" ]; then
        chcon -t textrel_shlib_t  %{_localstatedir}/lib/libwazuhext.so
      fi
    fi
  fi
fi

if cat %{_localstatedir}/etc/ossec.conf | grep -o -P '(?<=<server-ip>).*(?=</server-ip>)' | grep -E '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$' > /dev/null 2>&1; then
   /sbin/service wazuh-agent restart || :
fi

if cat %{_localstatedir}/etc/ossec.conf | grep -o -P '(?<=<server-hostname>).*(?=</server-hostname>)' > /dev/null 2>&1; then
   /sbin/service wazuh-agent restart || :
fi

if cat %{_localstatedir}/etc/ossec.conf | grep -o -P '(?<=<address>).*(?=</address>)' | grep -v 'MANAGER_IP' > /dev/null 2>&1; then
   /sbin/service wazuh-agent restart || :
fi

%preun

if [ $1 = 0 ]; then

  /sbin/service wazuh-agent stop || :
  %{_localstatedir}/bin/ossec-control stop 2>/dev/null
  /sbin/chkconfig wazuh-agent off
  /sbin/chkconfig --del wazuh-agent

  # Check if Wazuh SELinux policy is installed
  if [ -r "/etc/centos-release" ]; then
    DIST_NAME="centos"
    DIST_VER=`sed -rn 's/.* ([0-9]{1,2})\.[0-9]{1,2}.*/\1/p' /etc/centos-release`

  elif [ -r "/etc/redhat-release" ]; then
    DIST_NAME="rhel"
    DIST_VER=`sed -rn 's/.* ([0-9]{1,2})\.[0-9]{1,2}.*/\1/p' /etc/redhat-release`
  elif [ -r "/etc/SuSE-release" ]; then
    DIST_NAME="suse"
    DIST_VER=`sed -rn 's/.*VERSION = ([0-9]{1,2}).*/\1/p' /etc/SuSE-release`
  else
    DIST_NAME=""
    DIST_VER=""
  fi

  add_selinux="yes"
  if [ "${DIST_NAME}" == "centos" -a "${DIST_VER}" == "5" ] || [ "${DIST_NAME}" == "rhel" -a "${DIST_VER}" == "5" ] || [ "${DIST_NAME}" == "suse" -a "${DIST_VER}" == "11" ] ; then
    add_selinux="no"
  fi

  # If it is a valid system, remove the policy if it is installed
  if [ ${add_selinux} == "yes" ]; then
    if command -v getenforce > /dev/null 2>&1 && command -v semodule > /dev/null 2>&1; then
      if [ $(getenforce) !=  "Disabled" ]; then
        if (semodule -l | grep wazuh > /dev/null); then
          semodule -r wazuh
        fi
      fi
    fi
  fi
fi

%triggerin -- glibc
[ -r %{_sysconfdir}/localtime ] && cp -fpL %{_sysconfdir}/localtime %{_localstatedir}/etc
 chown root:ossec %{_localstatedir}/etc/localtime
 chmod 0640 %{_localstatedir}/etc/localtime

%clean
rm -fr %{buildroot}

%files
%defattr(-,root,root)
%doc BUGS CONFIG CONTRIBUTORS INSTALL LICENSE README.md CHANGELOG
%attr(640,root,ossec) %verify(not md5 size mtime) %{_sysconfdir}/ossec-init.conf
%attr(750,root,ossec) %dir %{_localstatedir}
%attr(750,root,ossec) %dir %{_localstatedir}/backup
%attr(750,root,ossec) %dir %{_localstatedir}/wodles
%attr(750,root,ossec) %dir %{_localstatedir}/wodles/aws
%attr(750,root,ossec) %dir %{_localstatedir}/wodles/oscap
%attr(750,root,ossec) %dir %{_localstatedir}/wodles/oscap/content
%attr(700,root,ossec) %dir %{_localstatedir}/.ssh
%attr(750,root,ossec) %dir %{_localstatedir}/active-response
%attr(750,root,ossec) %dir %{_localstatedir}/active-response/bin
%attr(770,root,ossec) %dir %{_localstatedir}/etc/shared
%attr(750,root,root) %dir %{_localstatedir}/lib
%attr(770,ossec,ossec) %dir %{_localstatedir}/logs
%attr(750,ossec,ossec) %dir %{_localstatedir}/logs/ossec
%attr(750,root,ossec) %dir %{_localstatedir}/queue
%attr(750,ossec,ossec) %dir %{_localstatedir}/queue/agents
%attr(770,ossec,ossec) %dir %{_localstatedir}/queue/ossec
%attr(750,ossec,ossec) %dir %{_localstatedir}/queue/diff
%attr(770,ossec,ossec) %dir %{_localstatedir}/queue/alerts
%attr(750,ossec,ossec) %dir %{_localstatedir}/queue/rids
%attr(750,ossec,ossec) %dir %{_localstatedir}/queue/syscheck
%attr(750,root,root) %dir %{_localstatedir}/bin
%attr(770,ossec,ossec) %dir %{_localstatedir}/etc
%attr(750,root,ossec) %dir %{_localstatedir}/var
%attr(770,root,ossec) %dir %{_localstatedir}/var/incoming
%attr(770,root,ossec) %dir %{_localstatedir}/var/run
%attr(770,root,ossec) %dir %{_localstatedir}/var/selinux
%attr(770,root,ossec) %dir %{_localstatedir}/var/wodles
%attr(770,root,ossec) %dir %{_localstatedir}/var/upgrade
%attr(750,root,ossec) %{_localstatedir}/active-response/bin/*
%attr(750,root,ossec) %{_localstatedir}/agentless
%attr(750,root,root) %{_localstatedir}/bin/*
%{_initrddir}/*
%attr(640,root,ossec) %{_localstatedir}/etc/internal_options*
%attr(640,root,ossec) %{_localstatedir}/etc/wpk_root.pem
%attr(640,root,ossec) %config(noreplace) %{_localstatedir}/etc/local_internal_options.conf
%attr(640,root,ossec) %{_localstatedir}/etc/ossec.conf
%attr(660,root,ossec) %config(missingok,noreplace) %{_localstatedir}/etc/shared/*
%attr(750,root,root) %{_localstatedir}/lib/*
%attr(1750,root,ossec) %dir %{_localstatedir}/tmp
%attr(750,root,ossec) %{_localstatedir}/wodles/aws/*
%attr(640,root,ossec) %{_localstatedir}/var/selinux/*
%attr(750,root,ossec) %{_localstatedir}/wodles/oscap/oscap.py
%attr(750,root,ossec) %{_localstatedir}/wodles/oscap/template*
%attr(640,root,ossec) %{_localstatedir}/wodles/oscap/content/*

#Template files
%attr(750,root,root) %config(missingok)%{_localstatedir}/tmp/src/*
%attr(750,root,root) %config(missingok) %{_localstatedir}/tmp/add_localfiles.sh
%attr(750,root,root) %config(missingok) %{_localstatedir}/tmp/etc/templates/config/generic/*

/usr/share/wazuh-agent/scripts/tmp/*

%if %{_debugenabled} == "yes"
/usr/lib/debug/%{_localstatedir}/*
/usr/src/debug/%{name}-%{version}/*
%endif


%changelog
* Wed Jul 25 2018 support <support@wazuh.com> - 3.5.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Jul 11 2018 support <support@wazuh.com> - 3.4.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Jun 18 2018 support <support@wazuh.com> - 3.3.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Jun 11 2018 support <support@wazuh.com> - 3.3.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed May 30 2018 support <support@wazuh.com> - 3.2.4
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu May 10 2018 support <support@wazuh.com> - 3.2.3
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Apr 09 2018 support <support@wazuh.com> - 3.2.2
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Feb 21 2018 support <support@wazuh.com> - 3.2.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Feb 07 2018 support <support@wazuh.com> - 3.2.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu Dec 21 2017 support <support@wazuh.com> - 3.1.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Nov 06 2017 support <support@wazuh.com> - 3.0.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon May 29 2017 support <support@wazuh.com> - 2.0.1
- Changed random data generator for a secure OS-provided generator.
- Changed Windows installer file name (depending on version).
- Linux distro detection using standard os-release file.
- Changed some URLs to documentation.
- Disable synchronization with SQLite databases for Syscheck by default.
- Minor changes at Rootcheck formatter for JSON alerts.
- Added debugging messages to Integrator logs.
- Show agent ID when possible on logs about incorrectly formatted messages.
- Use default maximum inotify event queue size.
- Show remote IP on encoding format errors when unencrypting messages.
- Fix permissions in agent-info folder
- Fix permissions in rids folder.
* Fri Apr 21 2017 Jose Luis Ruiz <jose@wazuh.com> - 2.0
- Changed random data generator for a secure OS-provided generator.
- Changed Windows installer file name (depending on version).
- Linux distro detection using standard os-release file.
- Changed some URLs to documentation.
- Disable synchronization with SQLite databases for Syscheck by default.
- Minor changes at Rootcheck formatter for JSON alerts.
- Added debugging messages to Integrator logs.
- Show agent ID when possible on logs about incorrectly formatted messages.
- Use default maximum inotify event queue size.
- Show remote IP on encoding format errors when unencrypting messages.
- Fixed resource leaks at rules configuration parsing.
- Fixed memory leaks at rules parser.
- Fixed memory leaks at XML decoders parser.
- Fixed TOCTOU condition when removing directories recursively.
- Fixed insecure temporary file creation for old POSIX specifications.
- Fixed missing agentless devices identification at JSON alerts.
- Fixed FIM timestamp and file name issue at SQLite database.
- Fixed cryptographic context acquirement on Windows agents.
- Fixed debug mode for Analysisd.
- Fixed bad exclusion of BTRFS filesystem by Rootcheck.
- Fixed compile errors on macOS.
- Fixed option -V for Integrator.
- Exclude symbolic links to directories when sending FIM diffs (by Stephan Joerrens).
- Fixed daemon list for service reloading at ossec-control.
- Fixed socket waiting issue on Windows agents.
- Fixed PCI_DSS definitions grouping issue at Rootcheck controls.
