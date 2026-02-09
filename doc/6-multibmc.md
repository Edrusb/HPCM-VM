
# Multibmc program

## Introduction

[Multibmc](../Multibmc/multibm.py) is a Object Oriented python program
we created on top of *proxmoxbmc* to enhance
its features and let it provide a standard
BMC (listening on the standard 623/UDP port) for **all** VMs (not only one).

It is to be considered as a wrapper around *proxmoxbmc* in the followin way:
- it sets stores once and for all the many common parameters needed to setup
a single vBMC using *proxmoxbmc*
- eases the addition and remove a vBMC for a given VM
- persists accross reboots when called from the init process (sysV init, systemd...)

It is expected to be ran on a VM where *proxmoxbmc* is installed, VM from where at least
one hypervisor of the *proxmox* cluster is available and eventually having a second (or
more network interface) where vBMC will be reachable.

## Usage

>
> ./multibmc.py /etc/multibmc.json ens19 11000 11999 admin password /root/proxmoxbmc/.env/bin/activate root@pam vbmc-token xxxxxx-xx-xxx-xxxxx proxmox-6
>

This command create the */etc/multibmc.json* configuration file and stores:
- **ens19** the interface to expose the vBMC one
- **11000** to **11999** is the UDP range of ports where *proxmoxbmc* will bind its vBMC
- **admin** is the login to use to connect to the BMCs (same login for all, but room has been made for it can be enhanced to login/password per BMC in the future)
- **password** the password to use to connect to the BMCs
- **/root/.../active** is the *venv* where the pbmc command is available (*proxmoxbmc*)
- **root@pam** the user owning the token on the proxmox RESTFUL API
- **vbmc-token** the token name as created on the proxmox environment
- **xxx-x...xxx** the token secret as obtained at its creation time
- **proxmox-6** the hostname or the IP address of one of the proxmox hypervisor of the cluster

>
> ./multibmc.py /etc/multibmc.json add 111 10.25.255.250 16
>

Using this command we create a new vBMC and store its configuration in /etc/multibmc.json configuration file
- **111** is the VM ID of the VM to be controlled by this vBMC
- **10.25.255.250** and **16** define the IP/mask of the IP address to create for this vBMC. This IP address will be added to the **ens19** network interface (interface provided in rhe previous step).

>[!Note]
> The IP/mask should be reachable by the expected IPMI client (like ipmitool or HPCM).
> The easiest way choose such IP is to take a free IP in the existing subnet assigned
> to the selected network interface.

>
> ./multibmc.py /etc/multibmc.json list
>

Gives content visibility of the /etc/multibmc.json configuration file (You could also
use the *jq* program, but would have to interprete the meaning of the different fields)


>
> ./multibmc.py /etc/multibmc.json start
>
> ./multibmc.py /etc/multibmc.json stop
>

this form is to run from the *init* process, like systemd for example (see below for
a systemd configuration file).

>
> ./multibmc.py /etc/multibmc.josn del 111
>

will remove the vBMC for the VM having the ID 111 (and no need to restart the
*multibmc* service for it takes effect, same thing when adding a new vBMC as seen
above).


## Requirement

**multibmc.py** only requires:
- proxmoxbmc installed in particular pbmcd should be ran from the init process
- python3

In this page we will determine the modification to add to our VM template
in HPCM configuration to leverage the vBMC addition we did, for the compute03
VM.

## Systemd configuration file

---- TO BE ADDED ---

# Integration with HPCM

## Multibmc configuration

Continuing with our example, we cloned the compute03 node as compute01, compute02 and
compute04. So we now have four VMs. Cleaning all previous vBMC on the VM hosting **proxmoxbmc** we just create the following commands:

```
root@vbmc:~/Multibmc# ./multibmc.py /etc/multibmc.json init ens19 11000 11999 admin password  /root/proxmoxbmc/.env/bin/activate root@pam vbmc-token ef883eba-8027-4ab6-8466-a37f3e08babc proxmox-6
root@vbmc:~/Multibmc#
root@vbmc:~/Multibmc# ./multibmc.py /etc/multibmc.json add 111 10.25.100.1 16
root@vbmc:~/Multibmc# ./multibmc.py /etc/multibmc.json add 112 10.25.100.2 16
root@vbmc:~/Multibmc# ./multibmc.py /etc/multibmc.json add 113 10.25.100.3 16
root@vbmc:~/Multibmc# ./multibmc.py /etc/multibmc.json add 115 10.25.100.4 16
root@vbmc:~/Multibmc#
```

For reference, VMID 111, 112, 113 and 115 are respectively the VM compute01, compute02, compute03 and compute04[^1]

[^1]:yes, VM ID 115 not 114 as it was already used, but this has no importance

Now we can check the *multibmc* configuration:

```
root@vbmc:~/Multibmc# ./multibmc.py /etc/multibmc.json list

Global parameters
------------------
Net device  : ens19
UDP range   : 11000 - 11999
BMC login   : admin
BMC password: password
venv path   : /root/proxmoxbmc/.env/bin/activate
API user    : root@pam
Token name  : vbmc-token
Token secret: ef883eba-8027-4ab6-8466-a37f3e08babc
Proxmox host: proxmox-6

Configured BMCs:
------------------
+--------+---------------------+-------+
|  VM ID |     IP address      | UDP   |
+--------+---------------------+-------+
|    111 |      10.25.100.1/16 | 11000 |
|    112 |      10.25.100.2/16 | 11001 |
|    113 |      10.25.100.3/16 | 11002 |
|    115 |      10.25.100.4/16 | 11003 |
+--------+---------------------+-------+

root@vbmc:~/Multibmc#
```

And see that the correct IP address have been assigned to each VM. The UDP port
colomn is the port *proxmoxbmc* uses, but this is hidden by *multibmc* as you will
use the standard 623/UDP port.


## updating the VM template in HPCM

the VM template can be updated to include the IPMI credentials and some
network informations, we will use this [template3.txt](../resources/template3.txt)

>
> cm node template update -c template3.txt
>

## recording the new VM in HPCM

The template we created above includes all the networks (hsn, head-bmc, head), this might not be
the best approach as this implies us to provide the MAC addresses of these new VM when setting
up the configfile (here [three-new-nodes.txt](../resources/three-new-nodes.txt)) of the nodes to add:

>
> cm node add -c three-new-nodes.txt --allow-duplicate-macs-and-ips
>

But that was not sufficient, we also needed to specify as we did for compute03, the ipmi protocol

```
[root@hpcm1 Documents]# cadmin --set-bmc-protocol --node compute01 ipmi
[root@hpcm1 Documents]# cadmin --set-bmc-protocol --node compute02 ipmi
[root@hpcm1 Documents]# cadmin --set-bmc-protocol --node compute04 ipmi
[root@hpcm1 Documents]#
```

## Using the new BMC IP for compute03
we used the IP address of the vBMCs VM for compute03 when using *proxmoxbmc* without
*multibmc*, we must now change this VM BMC IP to the one we assigned above:

```
[root@hpcm1 ~]# cm node nic show -n compute03
ID  NAME  IP             MAC                IPV6  BOND_MASTER  BOND_MODE      INTERFACE_NAME  MANAGED  TYPE      NETWORK_NAME
7   ens19 None           bc:24:11:11:6b:f4  None  bond0        active-backup  compute03       True     mgmt      head
8   ens18 10.26.0.2      bc:24:11:30:57:d2  None  bond0        active-backup  compute03       True     mgmt      head
9   bmc0  10.25.255.249  bc:24:11:8c:71:9a  None  None         None           compute03-bmc   True     mgmt-bmc  head-bmc
12  ens20 10.27.0.2      bc:24:11:99:48:35  None  None         None           compute03-hsn   True     data      hsn
[root@hpcm1 ~]# cm node nic set -n compute03 -I 9 -i 10.25.100.3
Configuration manager submitting node configuration.
Populating Dataset...
Populating Dataset complete: 1.299s
0 of 1 nodes completed in 3.8 seconds, averaging 0.0s per node
0 of 1 nodes completed in 6.3 seconds, averaging 0.0s per node
1 of 1 nodes completed in 8.8 seconds, averaging 1.7s per node
1 of 1 nodes completed in 8.8 seconds, averaging 1.7s per node
Node configuration complete.
[root@hpcm1 ~]#
```


## Playing with HPCM

Let's see how this works now:

```
[root@hpcm1 ~]# cm power on -n compute01
direct node compute01 power ON
[root@hpcm1 ~]# cm power status -t system
compute01    : On
compute02    : Off
compute03    : BOOTED
compute04    : Off
[root@hpcm1 ~]#
```

Let's continue:

```
[root@hpcm1 ~]# cm power on -n compute02,compute04
direct node compute04 power ON
direct node compute02 power ON
[root@hpcm1 Documents]# cm power status -t system
compute01    : BOOTED
compute02    : On
compute03    : BOOTED
compute04    : On
[root@hpcm1 Documents]#
```

Let's see the final stage:

```
[root@hpcm1 Documents]# cm power status -t system
compute01    : BOOTED
compute02    : BOOTED
compute03    : BOOTED
compute04    : BOOTED
[root@hpcm1 Documents]# ssh compute01
Last login: Wed Feb  4 18:07:25 2026 from 10.26.255.254
[root@compute01 ~]# hostname
compute01
[root@compute01 ~]#
```

| [Prev](proxmoxbmc.md) | [top](../README.md)   |  --- |
|:----------------------|:---------------------:|-----:|
