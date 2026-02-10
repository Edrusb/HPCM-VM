
# Requirements

## Hardware needed
The environment used for *Proxmox* Lab can be as small as:
- a single computer, (but yes, more or bigger one allows more VMs):
  - very minimum 16 GiB of RAM, 8 GB for HPCM VM and for example 2 GB for a set of four VM having the role of compute node (depending on the workload you plan to run on those)
  - x86_64 CPU (HPCM constraint, for virtual BMC there is no CPU type constaint)
  - Disk/storage at least 300 GiB for HPCM (can be less but it will difficult to have several slots on the HPCM VM and playing with repos and images will be very restrictive)
- Physical (IP/Ethernet) network if more than one hypervisor is to be used. 1 Gbit/s connection to hypervisors is slow but fine, depending on what workload you want to test over this Software "HPC" cluster

## Virtual Environment used - Proxmox
I'm a big fan of [Proxmox Virtual Environment](https://www.proxmox.com/en/). Proxmox can be installed and used at no cost,
it is qemu based virtualization wrapped into a nice (read fully featured) Web GUI. A CLI interface is also available, which I very rarely use, but can be useful for automation.
Proxmox is based on Debian and receive a lot of additional packages to manage the Kernel Virtual Machine (KVM) as well as containers, though the Proxmox/Linux system stays open
and can receive a lot of your own customized software additions if needed (like your own security tools, apparmor, lynis...).

## Network Environment used
There is not many constraints here:
- you'll need few VLANs with their IP subnets on top, which all can reside inside a single hypervisor just using *Proxmox* features. 
  For example, I used three of them:
  - Public VLAN and its IP subnet (what HPCM calls the "home" network), it pre-existed for other purposes in my environment,
  - an HPCM admin network (what HPCM calls the "head" network), VLAN through which HPCM exchanges data with the
    OS of the compute nodes (PXE Boot, Bittorrent imaging, monitoring...)
  - the "head-bmc" network has been created in the infra, to reach the virtual BMCs
  - High Speed Network to emulate a real HSN, but which here is just another vlan 
- *eventually* inter-vlan routing (which can be carried by a Linux VM or a proxmox hypervisor, if you have no physical L3 switch nor router),

If more than one hypervisior is to be used, a physical network will be needed, and the support for 802.1Q (vlan tagging)
will be necessary to propagate VLANs between hypervisors.

>[!Note]
> If you plan to use UDPcast with HPCM, to push images to the compute nodes, you'll need to have support for multicast on
> your network, espetially an IGMP Querier will be needed to query which listener are in which group, this concerns
> the "head" VLAN, mainly. If you do not want to bother with that complexity, keep using the default bittorrent method or try
> the rsync alternative.



| ---              | [top](../README.md)   | [Next](2-proxmox-setup.md) |
|:-----------------|:---------------------:|---------------------------:|

