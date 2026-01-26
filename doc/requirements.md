
# Requirements

## Hardware needed
To experiment with HPCM and VMs of you will need at least:
- a single computer, more or bigger one is better:
  - very minimum 16 GiB of RAM, 8 GB for HPCM VM and for example 8 GB for a single compute node
  - x86_64 CPU (I could run HCPM + a single compute node VM using only 8 cores, and it was not particularly slow)
  - Disk/storage at least 300 GiB (can be less but it will difficult to have several slots on the HPCM VM and playing with repos and images will be very restrictive)
- Physical (IP/Ethernet) network if more than one hypervisor is to be used. 1 Gbit/s connection to hypervisors is slow but fine, depending on what workload you want to test over the Software "HPC" cluster

## Virtual Environment used - Proxmox
I'm a big fan of [Proxmox Virtual Environment](https://www.proxmox.com/en/). Proxmox can be installed and used at no cost,
it is qemu based virtualization wrapped into a nice (read fully featured) Web GUI. A CLI interface is also available, which I very rarely use, but can be useful for automation.
Proxmox is based on Debian and receive a lot of additional packages to manage the Kernel Virtual Machine (KVM) of the Linux kernel, though the Proxmox/Linux system stays open
and can receive a lot of customized software additions if needed.

I will thus focus on this virtualization environment.

## Network Environment used
There is not many constraints here:
- you'll need few VLANs with their IP subnets on top.
  For example, I used three of them:
  - Public VLAN and its IP subnet (what HPCM calls the "home" network), it pre-existed for other purposes in my environment,
  - an HPCM admin network (what HPCM calls the "head" network), VLAN through which HPCM exchanges data with the
    OS of the compute nodes (PXE Boot, Bittorrent imaging, monitoring...)
  - the "head-bmc" network has been created in the infra, but as VMs do not have BMC or iLO by default,
    we will not use until we find and test a [virtual BMC for proxmox](https://github.com/agnon/proxmoxbmc)
    though from HPCM stand point, this VLAN exists and is ready for use
- *eventually* inter-vlan routing (which can be carried by a Linux VM or a proxmox hypervisor, if you have no L3 switch nor router),

If more than one hypervisior is to be used, a physical network will be needed, and the support for 802.1Q (vlan tagging)
will be necessary to propagate VLANs between hypervisors.

>[!Note]
> If you plan to use UDPcast to push images to the compute nodes, you'll need to have support for multicast on
> your network, espetially an IGMP Querier will be needed to query which listener are in which group, this concerns
> the "head" VLAN, mainly. If you do not want to bother with that complexity, keep using the default bittorrent method or try
> the rsync alternative.



| ---              | [top](../README.md)   | [Next](proxmox-setup.md) |
|:-----------------|:---------------------:|-------------------------:|

