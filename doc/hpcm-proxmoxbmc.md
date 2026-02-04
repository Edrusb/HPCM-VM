
# HPCM with virtual BMCs

## Introduction
In this page we will determine the modification to add to our VM template
in HPCM configuration to leverage the vBMC addition we did, for the compute03
VM.

The second paragraph will focus on how to scale efficiently with more VMs and more vBMCs.

## Recording a BMC interface for the compute03 VM

We must add the vBMC as a new NIC to the VM in HPCM using the MAC and IP address the vBMC exposes to the head-bmc network:

>
> cm node nic add -m "bc:24:11:8c:71:9a" -w head-bmc -n compute03 --nic-name bmc0 -c compute03-bmc -i 10.25.255.253
>

Next, we must add the credentials needed to access the BMC:

>
> cadmin --set-bmc-password --node compute03 admin:password
>

```
[root@hpcm1 Documents]# cadmin --set-bmc-password --node compute03 admin:password
Password updated successfully for compute03-bmc
Updating cluster manager configuration files:
=============================================
Configuration manager submitting node configuration.
Populating Dataset...
Populating Dataset complete: 1.275s
0 of 1 nodes completed in 3.8 seconds, averaging 0.0s per node
1 of 1 nodes completed in 6.3 seconds, averaging 1.5s per node
1 of 1 nodes completed in 6.3 seconds, averaging 1.5s per node
Node configuration complete.
Done updating cluster manager configuration files.
==================================================
[root@hpcm1 Documents]# cadmin --get-bmc-password --node compute03
admin
password
[root@hpcm1 Documents]#
```

Last we need to tell HPCM to speak IPMI (and not redfish)

>
> cadmin --set-bmc-protocol --node compute03 ipmi
>

that's all for the power managment of a VM from HPCM:

```
[root@hpcm1 Documents]# cm power status -n compute03
compute03    : Off
[root@hpcm1 Documents]# cm power on -n compute03
compute03: FAILURE:  power on : Unable to get Chassis Power Status

[root@hpcm1 Documents]# cm power status -n compute03
compute03    : On
[root@hpcm1 Documents]# cm power status -n compute03
compute03    : On
[root@hpcm1 Documents]# cm power status -n compute03
compute03    : BOOTED
[root@hpcm1 Documents]#
```


## Scaling Proxmoxbmc

HPCM does not seem to have the ability to connect to a IPMI BMC
on another port than the default UDP/623. While *proxmoxbmc* can
deploy many virtual BMC on an single VM but using different UDP ports.

So we must find a workaround using several IP address on the
Proxmoxbmc VM and add redirection rules to the different UDP ports we will
assign to the different vBMC on that VM.

This is the object of this paragraph.

## creating the additional vBMC on the proxmoxbmc VM

We created three additional VMs (compute01, compute02 and compute04), thus we must
update the proxmoxbmc configuration using the ```bpmc``` commande:

```
(.env) root@vbmc:~# pbmc add --username admin --password password --port 12001 --proxmox-address proxmox-6.ezmeral.edrusb.org --token-user root@pam --token-name vbmc --token-value xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 111
(.env) root@vbmc:~# pbmc add --username admin --password password --port 12002 --proxmox-address proxmox-6.ezmeral.edrusb.org --token-user root@pam --token-name vbmc --token-value xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 112
(.env) root@vbmc:~# pbmc add --username admin --password password --port 12005 --proxmox-address proxmox-6.ezmeral.edrusb.org --token-user root@pam --token-name vbmc --token-value xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 115
(.env) root@vbmc:~# pbmc start 111
(.env) root@vbmc:~# pbmc start 112
(.env) root@vbmc:~# pbmc start 115
(.env) root@vbmc:~# pbmc list
+------+---------+---------+-------+
| VMID | Status  | Address |  Port |
+------+---------+---------+-------+
| 111  | running | ::      | 12001 |
| 112  | running | ::      | 12002 |
| 113  | running | ::      |   623 |
| 115  | running | ::      | 12005 |
+------+---------+---------+-------+
(.env) root@vbmc:~#
```


### additional IPs

The current proxmoxbmc configuration is the following:
```
(.env) root@vbmc:~# ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute
       valid_lft forever preferred_lft forever
2: ens18: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether bc:24:11:78:6b:4a brd ff:ff:ff:ff:ff:ff
    altname enp0s18
    inet 10.13.25.134/24 brd 10.13.25.255 scope global ens18
       valid_lft forever preferred_lft forever
    inet6 fe80::be24:11ff:fe78:6b4a/64 scope link
       valid_lft forever preferred_lft forever
3: ens19: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether bc:24:11:8c:71:9a brd ff:ff:ff:ff:ff:ff
    altname enp0s19
    inet 10.25.255.253/16 brd 10.25.255.255 scope global ens19
       valid_lft forever preferred_lft forever
    inet6 fe80::be24:11ff:fe8c:719a/64 scope link
       valid_lft forever preferred_lft forever
(.env) root@vbmc:~#
```

- ens18 is the interface toward the proxmox hypervisors
- ens19 is the interface connected to the head-bmc, thus HPCM

We add tree new IPs on that later interface using this command:

>
> ip addr add <IP>/<mask> dev ens19
>

```
(.env) root@vbmc:~# ip addr add 10.25.255.252/16 dev ens19
(.env) root@vbmc:~# ip addr add 10.25.255.251/16 dev ens19
(.env) root@vbmc:~# ip addr add 10.25.255.250/16 dev ens19
(.env) root@vbmc:~# ip address show dev ens19
3: ens19: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether bc:24:11:8c:71:9a brd ff:ff:ff:ff:ff:ff
    altname enp0s19
    inet 10.25.255.253/16 brd 10.25.255.255 scope global ens19
       valid_lft forever preferred_lft forever
    inet 10.25.255.252/16 scope global secondary ens19
       valid_lft forever preferred_lft forever
    inet 10.25.255.251/16 scope global secondary ens19
       valid_lft forever preferred_lft forever
    inet 10.25.255.250/16 scope global secondary ens19
       valid_lft forever preferred_lft forever
    inet6 fe80::be24:11ff:fe8c:719a/64 scope link
       valid_lft forever preferred_lft forever
(.env) root@vbmc:~#
```

So we are good, let's try to ping them from HPCM:

```
[root@hpcm1 ~]# ping -c 1 10.25.255.250 -q
PING 10.25.255.250 (10.25.255.250) 56(84) bytes of data.

--- 10.25.255.250 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.741/0.741/0.741/0.000 ms
[root@hpcm1 ~]# ping -c 3 10.25.255.250 -q
PING 10.25.255.250 (10.25.255.250) 56(84) bytes of data.

--- 10.25.255.250 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2034ms
rtt min/avg/max/mdev = 0.444/0.492/0.560/0.049 ms
[root@hpcm1 ~]# ping -c 3 10.25.255.251 -q
PING 10.25.255.251 (10.25.255.251) 56(84) bytes of data.

--- 10.25.255.251 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2056ms
rtt min/avg/max/mdev = 0.437/0.555/0.791/0.168 ms
[root@hpcm1 ~]# ping -c 3 10.25.255.252 -q
PING 10.25.255.252 (10.25.255.252) 56(84) bytes of data.

--- 10.25.255.252 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2071ms
rtt min/avg/max/mdev = 0.547/0.639/0.819/0.127 ms
[root@hpcm1 ~]# ping -c 3 10.25.255.253 -q
PING 10.25.255.253 (10.25.255.253) 56(84) bytes of data.

--- 10.25.255.253 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2079ms
rtt min/avg/max/mdev = 0.460/0.501/0.580/0.058 ms
[root@hpcm1 ~]#
```

and this is really the same interface / MAC address behind:

```
[root@hpcm1 ~]# arp -an | grep 10.25.255.25[0-3]
? (10.25.255.252) at bc:24:11:8c:71:9a [ether] on ens21
? (10.25.255.250) at bc:24:11:8c:71:9a [ether] on ens21
? (10.25.255.253) at bc:24:11:8c:71:9a [ether] on ens21
? (10.25.255.251) at bc:24:11:8c:71:9a [ether] on ens21
[root@hpcm1 ~]#
```


### IP/port redirection

Now as HPCM is only able to speak with BMC using the standard default UDP/623 port, we
have to add three IP address to the VM and configure iptables to redirect connection
to UDP/623 on each of these new IPs to be redirected to UDP/12001, UDP/12002 and UDP/12005
respectively.

>
> iptables -t nat -A PREROUTING -i ens19 -p udp --dport 623 -d <IP> -j REDIRECT --to-ports <local UDP Port>
>

```
(.env) root@vbmc:~#  iptables -t nat -A PREROUTING -i ens19 -p udp --dport 623 -d 10.25.255.250 -j REDIRECT --to-ports  12001
(.env) root@vbmc:~#  iptables -t nat -A PREROUTING -i ens19 -p udp --dport 623 -d 10.25.255.251 -j REDIRECT --to-ports  12002
(.env) root@vbmc:~#  iptables -t nat -A PREROUTING -i ens19 -p udp --dport 623 -d 10.25.255.252 -j REDIRECT --to-ports  12005
(.env) root@vbmc:~# iptables -t nat -L PREROUTING -v
Chain PREROUTING (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
    0     0 REDIRECT   udp  --  ens19  any     anywhere             10.25.255.250        udp dpt:asf-rmcp redir ports 12001
    0     0 REDIRECT   udp  --  ens19  any     anywhere             10.25.255.251        udp dpt:asf-rmcp redir ports 12002
    0     0 REDIRECT   udp  --  ens19  any     anywhere             10.25.255.252        udp dpt:asf-rmcp redir ports 12005
(.env) root@vbmc:~#
```

### Non-volatile configuration
All the configuration we've setup above (iptables and IP addresses) will be lost if the proxmoxbmc VM is rebooted.
For that reason, we have to consider making a tool to automate the process of management of
these IP/UDP port associations.

---- TO BE DONE ----


## updating the template

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

## Final Check

Let's see how this works now:

```
[root@hpcm1 Documents]# cm power on -n compute01
compute01: FAILURE:  power on : Unable to get Chassis Power Status

[root@hpcm1 Documents]# cm power status -t system
compute01    : On
compute02    : Off
compute03    : BOOTED
compute04    : Off
[root@hpcm1 Documents]#
```

At first it seemd the powering up of compute01 failed, but as before
this is the "Chassis" of compute01 that HPCM failes to obtain the
power information from. This is weird as using *ipmitool* this information
is available and is identical to the compute power status.

Let's continue:

```
[root@hpcm1 Documents]# cm power on -n compute02,compute04
compute02: FAILURE:  power on : Unable to get Chassis Power Status

compute04: FAILURE:  power on : Unable to get Chassis Power Status

[root@hpcm1 Documents]# cm power status -t system
compute01    : BOOTED
compute02    : On
compute03    : BOOTED
compute04    : On
[root@hpcm1 Documents]#
```

Same thing here regard the false alarm, the compute node properly
got powered up, and we see that in the meantime compute01 has now
completed its booting process and is operational!

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

For the sake of completness, the HSN network IP are not
assigned on the new nodes, this has to be done in complement:

>
> cm node nic add -w hsn -N ens20 -c hsn -n compute01 --compute-next-ip -m bc:24:11:59:94:d3
>
> cm node nic add -w hsn -N ens20 -c hsn -n compute02 --compute-next-ip -m BC:24:11:47:98:E3
>
> cm node nic add -w hsn -N ens20 -c hsn -n compute04 --compute-next-ip -m BC:24:11:75:A8:2A
>


| [Prev](../proxmoxbmc.md) | [top](../README.md)   |  --- |
|:-------------------------|:---------------------:|-----:|
