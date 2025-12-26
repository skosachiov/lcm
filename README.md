# Linux Configuration Manager (LCM)

[![debian-12](https://github.com/skosachiov/lcm/actions/workflows/debian-12.yml/badge.svg)](https://github.com/skosachiov/lcm/actions/workflows/debian-12.yml)
[![debian-13](https://github.com/skosachiov/lcm/actions/workflows/debian-13.yml/badge.svg)](https://github.com/skosachiov/lcm/actions/workflows/debian-13.yml)
[![ubuntu-22.04](https://github.com/skosachiov/lcm/actions/workflows/ubuntu-22.04.yml/badge.svg)](https://github.com/skosachiov/lcm/actions/workflows/ubuntu-22.04.yml)
[![ubuntu-24.04](https://github.com/skosachiov/lcm/actions/workflows/ubuntu-24.04.yml/badge.svg)](https://github.com/skosachiov/lcm/actions/workflows/ubuntu-24.04.yml)
[![rocky-9](https://github.com/skosachiov/lcm/actions/workflows/rocky-9.yml/badge.svg)](https://github.com/skosachiov/lcm/actions/workflows/rocky-9.yml)
[![rocky-10](https://github.com/skosachiov/lcm/actions/workflows/rocky-10.yml/badge.svg)](https://github.com/skosachiov/lcm/actions/workflows/rocky-10.yml)

<img src="https://github.com/skosachiov/lcm/blob/main/lcm.png" width="200" height="250">

# License

This file is part of Linux Configuration Manager (LCM).

Linux Configuration Manager (LCM) is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Linux Configuration Manager (LCM) is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Linux Configuration Manager (LCM).  If not, see <https://www.gnu.org/licenses/>.

<a name="Introduction"></a>
# Introduction

## Briefly

*The objective of the project is to provide management capabilities (similar to SCCM) for various types of devices operating in a corporate environment. Information security is the primary focus of development. Roles come with default settings that can be dynamically overridden using rules from the "inventories" folder based on subnet, host group (organizational unit or branch), operating system, etc. Git enables lifecycle management through a GitOps approach. [Roles](#Roles) (policies) can also be used separately.*

## More details

Consider the challenge of managing an extensive fleet of user devices. For example, the French National Gendarmerie oversees 100,000 workstations, and the government of Schleswig-Holstein has approved migrating 30,000 computers to Linux and LibreOffice. This project proposes using only two simple yet widely adopted tools for this purpose: Git and Ansible. Several arguments support this approach:

* The job market offers many Ansible specialists whose salaries are not excessively high.
* Ansible includes an ansible-pull mode, which drastically reduces the load on the management server. A single server can manage tens of thousands of devices.
* Adherence to the KISS principle (Unix philosophy).
* Git provides version control and GitOps-style management.

While numerous solutions exist for specific workstation administration tasks (e.g., Ansible Galaxy), a comprehensive solution is lacking. Systems such as Foreman and Saltstack are available, but Puppet is outdated, and Salt is complex and not yet widely adopted. AWX (Ansible Tower) is suitable for servers in push mode. This project offers a complete solution reminiscent of SCCM in the Windows world, where Ansible replaces PowerShell DSC, with the added benefit of Git version control.

Additionally, the project includes inventory templates, which are essential for implementing dynamic device inventory in ansible-pull mode. These templates are designed to suit the needs of most enterprises.

Security tasks are partially derived from ComplianceAsCode and OpenSCAP but have been adapted to allow administrators to refine the code in Git as part of their daily routines. The roles feature user-readable templates and variables, distinguishing them from ComplianceAsCode.

Security, as a top priority, is addressed comprehensively. Information leakage is mitigated by the "dlp" role, which includes USBGuard and disabling WiFi and Bluetooth modules. A broad range of configurations is applied—from remounting "tmp" and "home" with noexec and nodev options to verifying repository lists using key fingerprints. The most valuable feature is mandatory access control, ensuring the integrity and signing of executable files.

Ideally, the enterprise security administrator receives a daily report with "Changed = 0" for each workstation, indicating that all hosts remain in their desired state with no modifications required. "Changed != 0" warrants further investigation.

Profiling is accomplished through a defined set of roles compiled into playbooks:

* workstation (a standard workstation within the enterprise domain)
* mobile-device (a laptop for accessing corporate resources over the internet)
* flash-drive (a bootable USB drive for BYOD)
* distribution-point (a distribution point within an enterprise unit)
* server (a general-purpose server), etc.

Profiles support security flags, such as:

* mandatory-access (AppArmor, SELinux)
* administrative-workstation (restricted group access)
* network-auditd (sending auditd data to a log server)
* always-on-display (disabling display lock and shutdown)
* devel-workstation (switching the host to test workstation mode)
* unrestricted-os (users may boot other operating systems)
* fs-userspace (file systems accessible to the user)
* thin-client (thin client mode)
* flash-drive (thin client mode on a USB drive)
* dist-upgrade (host forcibly updates all packages), etc.

For security specialists, numerous opportunities exist to coordinate changes and oversee management workflows: code reviews, merge requests, and pull requests. For instance, only a security specialist may commit to the master branch (see Lifecycle). Ansible-pull agents retrieve playbooks from the master branch. Large enterprise divisions have room for creativity—branches and units can address their specific needs in separate Git repositories without compromising baseline security configurations. On-premise solutions like GitLab or Forgejo are well-suited for collaboration.

Initially, several roles handled connections to proprietary systems such as Citrix and ESET antivirus. These roles have been removed from this repository as they are not relevant to most administrators seeking independence from proprietary software. Details for connecting to Microsoft AD domain controllers and Exchange have been retained, as many organizations are still transitioning from MS AD to FreeIPA. Moreover, these roles are also applicable to SambaAD-based controllers.

The project is designed for development in internet environments, with or without corporate repositories. Corporate resource availability is determined dynamically, and roles adjust accordingly.

<a name="Folder structure"></a>
# Folder structure

    ├── inventories         # vars based on various parameters
    │   ├── all             #
    │   │    ├─ group_vars  # vars for certain hosts, for example, for distribution-points
    │   │        └── dp     #
    │   ├── branches        # vars based on Company
    │   ├── ou              # vars based on OU membership
    │   ├── distribution    # vars based on OS distribution
    │   └── subnets         # vars based on Subnet
    │                       #
    ├── roles               # roles
    │   ├── ad-client       #
    │   ├── ansible-client  #
    │   ├── antivirus       #
    │   ├── ...             #
    ├── tests               # test automation
    └── utils               # utilities, git hooks

<a name="Roles"></a>
# Roles

## ad-client

The role prepares a workstation to join a SambaDC or MS AD domain. If you have domain join credentials, you can get full automation. The script for manual attachment is located in /root/realm.sh. FreeIPA client has its own connection mechanism. The role provides additional kerberos logging.

## ansible-client

Ansible-client creates a special user with an authorized key, sets up a sudoers entry, adds a cron job to regularly contact the main ansible git repository.

## antivirus

This role installs and configures a free antivirus suite to run in on-access scan mode and to regularly scan specific folders. The static clamav-dada package is not available in current versions of Ubuntu, and server-side freshclam may require the most recent clamav, so we had to provide the script with an rpm installation. In addition, the script installs onAccess scanning systemd service.

## apt

Apt role controls all packagets on a workstation or mobile device, installs Security task checks repos fingerprints.

## audit

A fairly large role is devoted to setting up an audit. Information security audit is configured in immutable mode, that is, changes require reboot. Additional control is exercised by counting active rules. If the rules are not loaded, the information security officer receives a warning message.

## base-security

Basic device security settings are provided by this role. Corporate and mobile devices are checked and configured daily. Tasks include setting grub security, sudoers, access to various folders and files, checking suid files, and the like.

## base-system

Many small tasks are reduced to one role for setting up the system and the user's working environment. Among them are the installation of corporate certificates, proxy settings, time service, user profile.

## browser

Browser settings moved to a separate role.

## desktop

For convenience, the administrative setting of the user's graphical environment has been moved to a separate role. Here you can pin favorite applications, set desktop wallpaper, set or hide icons in all apps.

## distribution-point

This role is designed to configure and manage regional content distribution points and collect security events.

## dlp

Obviously, the resources of a large enterprise must be protected from leaks. The default dlp setting allows you to connect a keyboard, mouse, headphones, cameras, but blocks any flash drives. The dlp role disables wireless communication modules and some keyjacks radio keyboards. You can always add the necessary devices to the white list.

## fapolicyd

The ansible-controlled version of fapolisyd is an analogue of Applocker on the Windows platform. In addition to the Applocker functions Fapolicy can use file digital signature in combination with IMA/SELinux. In this project, the default fapolicyd role behavior is:
- install fapolicyd
- use whitelist executables using dpkg or rpm database
- use whitelist executables using ansible updated fapolicyd.trust
- prohibit execution of non-whitelisted binary files for regular users
- prevent bytecode and source code from running in runtime environments (OpenJDK, Python, Wine etc.) from the home and tmp folders
- make an exception for root and ansible user
- add executable files from installed deb or rpm to the whitelist daily

## firewall

The firewall role replaces the uncomplicated ufw with the more advanced firewalld, defines multiple zones based on outgoing ip addresses. In addition, the role performs various checks, for example, for suspicious open ports. Configuring the netfilter-persistent package makes it possible to override the default ACCEPT mode for INPUT chains.

## flatpak

Flatpak replaces snap and gives users access to self-contained applications with additional isolation from the file system and the network. In this way, untrusted proprietary applications can be used on the corporate network. In the near future, a role will be added for mirroring external flatpak resources to the corporate network.

## integrity-check

The role configures and controls file integrity checking.

## inventory

The role inventories devices, monitors the health of equipment based on SMART and various voltage and temperature sensors.

## laps

The role of laps is similar to the LAPS service from Microsoft. The difference is that local admin passwords are always encrypted with gpg keys. You can add several gpg keys of information security officers, for example, a master key and a key of a local branch employee. In addition, the data (encrypted passwords) is not stored in the MS AD, but in the network syslog. The role is applied as part of additional security profiles. You may lose access to the device if you don't have network log working and don't have gpg keys to decrypt passwords. If you are absolutely sure, choose: var_laps_dryrun: false.

## mail-client

Evolution is currently being configured to work with EWS services.

## mandatory-access

The SELinux role will be introduced later.

## office

The role is intended for installing and configuring the current version of Libreoffice. Setting and control of macro security level. Choice of Ribbon user interface for all libreoffice applications.

## openvpn-client

The role is designed to securely configure a VPN connection to a corporate network and will be introduced later.

## polkit-restrictions

Events transmitted over d-bus are filtered by this role. The role is related to security.

## pre-tasks

Technical role for dynamic definition of variables.

## print

For each subnet role, connect your own set of printers. See definition of variables.

## remote-assistance

Ansible role produces desktop files in the /usr/share/applications/ folder and creates server no-shell user. Desktop files contain one-liners bash scripts. Desktop files allow to connect in automatic mode reverse forward and direct forward ports over ssh for telework and helpdesk. See https://github.com/skosachiov/linux-remote-assistance repo.

## scap

The role allows information security officers to scan packages installed on users' computers against CVE databases. If the OS distribution is not in a hurry to release fixes for vulnerabilities, you can switch to using self-contained flatpak versions of the software.

## security-modules

At the moment, the role checks the active state of the simplified MAC system apparmor.

## smb-client

For each subnet, network file shares are automatically configured with Kerberos authentication. These can be Samba shares or Windows-based legacy DFS.

## ssh

The secure configuration of the important SSH service has been moved to a separate role.

## terminal-server

The terminal service is provided through XRDP. The role configures accesses, disables insecure protocols, and changes logos.

<a name="Deploy"></a>
# Deploy

## Pre tasks for push mode

1. See inventories/distribution/<distribution>/<major_version>/vars for a list of supported platforms.
2. Create deploy user: `groupadd ansible; useradd -m -g ansible ansible`
3. Set password: `passwd ansible`
4. Add ansible to sudoers: `echo "ansible ALL=(ALL) EXEC:ALL, NOPASSWD:ALL" >> /etc/sudoers`
5. (Ubuntu/Debian) apt install openssh-server

## Deploy Master Distribution Point

IP of the master DP must be in vars to avoid errors. It is advisable to perform the configuration in manual mode.

## Deploy Slave Distribution Points

Create host flag: `touch /etc/ansible/distribution-point`
Slave DP have no ansible gits. IPs of slaves must be in lists to avoid errors.

## Deploy Workstation in install mode

Set the kernel option at the time of installation:
`auto url=<distribution-point-fqdn>`

## Deploy Workstation in push mode

`ANSIBLE_HOST_KEY_CHECKING=False sshpass -p password ansible-playbook -vv --ask-pass -b -i 192.168.122.230, -u ansible workstation.yml`
Regular cron procedures will be configured automatically by default.

If you have not created an ansible user:
`ANSIBLE_HOST_KEY_CHECKING=False sshpass -p password ansible-playbook -vv --ask-pass -e "ansible_become_password=password" -b -i 192.168.122.230, -u admin workstation.yml`

## Deploy workstation in pull mode
```
wget http://example.test/git/lcm/late-script.sh
sh late-script.sh
```

## Deploy administrative workstation in pull mode

Create host flag: `touch /etc/ansible/administrative-workstation`
```
wget http://example.test/git/lcm/late-script.sh
sh late-script.sh
```

## Deploy workstation mandatory access in pull mode

Create host flag: `touch /etc/ansible/mandatory-access`
```
wget http://example.test/git/lcm/late-script.sh
sh late-script.sh
```

## Deploy non-domain PC in push mode

`ansible-pull -i localhost -d /root/.ansible/pull/lcm -t mob -U https://example.test/git/lcm mobile-device.yml`

## Deploy non-domain PC in pull mode
```
wget http://example.test/git/lcm/late-script-mob.sh
sh late-script-mob.sh
```

## Install workstation with preseed.cfg (all data on the disk will be lost)

`auto=true priority=critical url=https://github.com/skosachiov/lcm/raw/main/assets/preseed.cfg`

## Check Workstation security in push mode

For information security purpose (check only).
`ANSIBLE_HOST_KEY_CHECKING=no sshpass -p password ansible-playbook -vv --check --ask-pass -e "ansible_become_password=password" -b -i 192.168.122.230, -u admin workstation.yml`

## Get changed only tasks in push mode

`ANSIBLE_DISPLAY_OK_HOSTS=no ANSIBLE_DISPLAY_SKIPPED_HOSTS=no sshpass -p password ansible-playbook -v --ask-pass -e "ansible_become_password=password" -b -i 192.168.122.174, -u ansible workstation.yml`

## Set dist-upgrade flag

Create flag: `touch /etc/ansible/dist-upgrade`

<a name="Lifecycle"></a>
# Lifecycle

## All participants

- Clone github repo (once)
`git clone git@github.com:skosachiov/lcm.git`
 or local repo (see man gitolite3)
`git clone gitolite3@ansible.si.mi:lcm`

- Change folder
`cd lcm`

- Edit git config (once)
`git config --global user.email absolon.faucher@si.mi`
`git config --global user.name "Absolon Faucher"`

- Get changes (every time)
`git pull --all`

- View various statuses
`git diff; git log; git status; git branch --all`

## Developer

- The developer needs to make sure it works on the *devel* branch
`git branch -a`
`git checkout devel`

- Make changes
`codium <git folder>` or `vim <file>.yml`

- Commit
`git commit -a -m "some fix"`

- Push changes
`git push --all origin`

## Information security auditor

- The auditor must make sure that he works in the devel branch
`git branch -a`
`git checkout devel`

- Get changes (every time)
`git pull --all`

- Examine the changes in the devel branch relative to the master branch
`git diff master..devel`

- Examine changes at the patch level, if necessary
`git log --patch | less`

- Switch to master branch
`git checkout master`

- Merge devel changes to the current branch (master)
`git merge --no-ff devel`

- Push to the git repo. After that, the tasks will be received and executed by all workstations through the ansible-pull mechanism.
`git push --all origin`
