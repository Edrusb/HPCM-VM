
# Requirements

## Hardware needed
To setup this type of you will need at least:
- a single computer (very minimum 16 GiB, 8 GB for HPCM VM and 8 GB for a single compute node)
- x86_64 CPU (I could run HCPM + a single compte node VM using only 8 cores, and it was not particularly slow)
- Disk/storage at least 300 GiB (can be less but it will difficult to have several slots on the HPCM VM and playing with repos and images will be very restrictive)
- Physical (IP/Ethernet) network if more than one hypervisor is to be used.

## Virtual Environment used - Proxmox
I'm a big fan of [Proxmox](https://www.proxmox.com/en/) since year 2019 (thus long before VMWare was hold up). Proxmox
is qemu based virtualization wrapped into a nice (read fully featured) Web GUI. A CLI interface is also available, which I very rarely use, but can be useful for automation.
Proxmox is based on Debian and receive a lot of additional packages to manage the Kernel Virtual Machine of the Linux kernel, though the Linux system stays open
and can receive a lot of customized software and kernel tweeking if needed.

I will thus here only described what was necessary to setup in that context

## Network Environment used
There is not many constraints here:
- you'll need VLANs with their IP subnets on top
  I used three of them:
  - Public VLAN and its IP subnet (what HPCM calls the "home" network) pre-existed for other purposes
  - an HPCM admin network (what HPCM calls the "head" network) through which HPCM exchange data with the
    OS of the compute nodes (PXE Boot, Bittorrent imaging, monitoring, ...)
  - the "head-bmc" network has been created in the infra, but as VMs do not have BMC or iLO it is not used,
    though from HPCM stand point it exists and is configured
- **eventually** inter-vlan routing (which can be carried by a Linux VM or a proxmox hypervisor, if you have no L3 switch nor router),

If more than one hypervisior is to be used, a physical network will be needed, and the support for 802.1Q (vlan tagging)
will be necessary to propagate VLANs between hypervisors.

>[!Note]
> If you plan to use UDPcast to push images to the compute nodes, you'll need to have support for multicast on
> your network, espetially an IGMP Querier will be needed to query which listener are in which group, this concerns
> the "head" VLAN. If you do not want to bother with that complexity, keep using the default bittorrent method or try
> the rsync alternative.



| ---              | [top](../README.md)   | [Next](proxmox-setup.md) |
|:-----------------|:---------------------:|-------------------------:|

w
