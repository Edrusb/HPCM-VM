

# Proxmox BMC

## Presentation

[Proxmoxbmc](https://github.com/agnon/proxmoxbmc) is a project that inherits from
VirtualBMC which was active on Openstack.

In turn *Proxmoxbmc* relies on [proxmoxer](https://github.com/proxmoxer/proxmoxer) which
is a wrapper of the Proxmox Virtual Environment (PVE in the following) REST API for the Python language.

## Architecture consideration

As the fundation is the PVE REST API, it's only necessary to install *proxmoxer* and *proxmoxbmc* on
a single node that has access, on one side, to all the PVE hypervisor, and on the other side
is accessible from HPCM and the eventual SU_leader(s) node(s).

Here the *node* means a VM, of course.

From HPCM point of view, the vBMC node should be reachable through the head-bmc network

## Proxmoxer

We just have to install it, no daemon to run:

```
pip install proxmoxer

pip install requests

pip install paramiko

pop install openssh_wrapper
```

Debian provides packages from the official distributions which is more secured than replying
on PyPI:

```
apt-get install python3-proxmoxer
```


## Proxmoxbmc

### Installation

We will stick to Debian OS to install *proxmoxbmc* and follow the short doc provided for its installation:

```
   apt-get install python3-pip python3-venv git -y

   apt-get update && apt-get install python3-pip python3-venv
   cd ~
   git clone https://github.com/agnon/proxmoxbmc.git
   cd proxmoxbmc
   python3 -m venv .env
   source .env/bin/activate
   pip install -r requirements.txt
   python -m setup install
```

### Running the *pbmcd* daemon

Proxmoxbmc relies an a daemon, named **pbmcd** we can run manually this way:

```
   cd ~/proxmoxbmc
   source .env/bin/activate
   pbmcd # starts the server
```

### Automatic launch of *pbmcd*

A this *pbmcd* daemn should be fired each time the VM boots, we have to
create a systemctl service:

```
cat > /etc/systemd/system/pbmcd.service <<EOF
[Unit]
Description = pbmcd service
After = syslog.target
After = network.target

[Service]
ExecStart = /root/proxmoxbmc/.env/bin/pbmcd --foreground
Restart = on-failure
RestartSec = 2
TimeoutSec = 120
Type = simple
q
[Install]
WantedBy = multi-user.target

EOF
```

then we can activate the service with:
```
systemctl enable --now pbcmd
```

check the service is running as expected:
```
root@vbmc:~# systemctl status pbmcd
● pbmcd.service - pbmcd service
     Loaded: loaded (/etc/systemd/system/pbmcd.service; enabled; preset: enabled)
     Active: active (running) since Fri 2026-01-23 12:21:09 CET; 1min 50s ago
   Main PID: 909 (pbmcd)
      Tasks: 3 (limit: 2314)
     Memory: 20.5M
        CPU: 238ms
     CGroup: /system.slice/pbmcd.service
             └─909 /root/proxmoxbmc/.env/bin/python /root/proxmoxbmc/.env/bin/pbmcd --foreground

janv. 23 12:21:09 vbmc systemd[1]: Started pbmcd.service - pbmcd service.
janv. 23 12:21:10 vbmc pbmcd[909]: 2026-01-23 12:21:10,222 909 INFO ProxmoxBMC [-] Started pBMC server on port 50891
root@vbmc:~#
```

## Proxmox VE authentication

To access PVE API we need to authenticate with a token. This has to be created first.

First, we define a role having access to the:
- VM Power managment
- VM console
- VM Monitoring

Go to menu ```Datacenter | Permissions | Roles``` and add a new role as illustrated below:

![PVE role definition](../pictures/role-definition.png)


Then go to the menu ```Datacenter | Permissions | API Tokens```and add a new token
checking the box ```privilege separation```:

![token creation](../pictures/token-definition.png)

Once validated, a new window show the token secret, copy it in a secured place, it will not
show again (you'll be good to delete this token an create a new one in case of loss).

![token secret](../pictures/token-value.png)

Checking the box ```privilege separation``` means that this token has not been assigned
any privilege (privilege separated from the user account it has been created on). We must
thus here assigne the role we defined earlier to the token we just created:

![token permission](../pictures/token-permission.png)


## Proxmoxbmc Configuration

To a give a BMC feature to a given VM the *pbmcd* daemon must also be configured.
This is done in the save virtuel environement (venv) using the **pbmc** command (still in
the venv):

```
cd ~/proxmoxbmc
source .env/bin/activate
(.env) root@vbmc:~/proxmoxbmc# pbmc add --username admin --password password --port 9001 --proxmox-address proxmox-6.ezmeral.edrusb.org --token-user root@pam --token-name vbmc-token --token-value xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 113
````

In the previous output:
- we assigned TCP port 9001 to the BMC of the compute03 we created for HPCM PXE boot. This
  VM has a VMID of 113, where from the last argument on the command-line
- the username and password are the one to use to connect to the virtual BMC service on this port
- the proxmox-address is the hostname/IP address of one of the hypervisor of the PVE cluster, if a Virtual IP is available on the different hypervisor constituing this PVE cluster, this would be more robust to use it instead of the one of a particular hypervisor.
- the token user, token name and token value are to be fetched from the token we just
  created above.

```
(.env) root@vbmc:~/proxmoxbmc# pbmc list
+------+--------+---------+------+
| VMID | Status | Address | Port |
+------+--------+---------+------+
| 113  | down   | ::      | 9001 |
+------+--------+---------+------+
(.env) root@vbmc:~/proxmoxbmc#
```

in the previous output we see our virtual BMC for the VM which ID is 113.
The status ```down``` is not those of the VM but of the virtual BMC, so we
must first start it:

```
(.env) root@vbmc:~/proxmoxbmc# pbmc start 113
(.env) root@vbmc:~/proxmoxbmc# pbmc list
+------+---------+---------+------+
| VMID | Status  | Address | Port |
+------+---------+---------+------+
| 113  | running | ::      | 9001 |
+------+---------+---------+------+
(.env) root@vbmc:~/proxmoxbmc#
```


## Updating HPCM

we can now add the BMC parameter to the compute03 node in HPCM

---- TO BE CONTINUED ----

cm node set --bmc-password password --bmc-username admin -n compute03
cm node set --conserver-logging yes -n compute03







| [Prev](console-on-seiral.md) | [top](../README.md)   |                        --- |
|:-----------------------------|:---------------------:|---------------------------:|
