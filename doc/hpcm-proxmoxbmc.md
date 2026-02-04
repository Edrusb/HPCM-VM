
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


---- TO BE CONTINUED ----



| [Prev](../proxmoxbmc.md) | [top](../README.md)   |  --- |
|:-------------------------|:---------------------:|-----:|
