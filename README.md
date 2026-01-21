# HPCM on VM
## Abstract
HPCM target is to manage Clusters of High Performance Computers, so why using HPCM to manage Virtual Machines?

The objective here is to be able to "play" with HPCM when you don't have the hardware and money that goes with it, thus the Performance (the P of HPC) is not the target here but rather the ability to use and test the many features of HPCM:
- install HPCM and eventually SU_Leaders in their VMs
- set up a large number of compute nodes (as VM)
- PXE Boot those compute nodes 
- setup repos and repo groups
- setup images
- assign images to compute nodes and SU_Leaders
- connect to VM using clustershell (clush) or pdsh
- monitor the virtual cluster of compute nodes
- setup the different networks including a virtual High Speed Network
- configure the cluster using Ansible
- deploy and run some PMI application
- play with HPCM slots

The HPCM features that will not be available are:
- power management (the ability to boot or reboot a compute node from HPCM)
- network switch management
- Slingshot HSN will not be available (well, I have not checked whether a software emulation was exiting, but I doubt it would)

## Requirement
To setup this type of you will need at least:
- a computer (very minimum 16 GiB, 8 GB for HPCM VM and 8 GB for a single compute node)
- x86_64 CPU (I could run HCPM + a single VM using only 8 cores, and it was not particularly slow)
- Disk/storage at least 300 GiB (can be less but it will difficult to have several slots on the HPCM VM)
- Physical Ethernet Network if more than one hypervisor is used (VLANs/802.1Q will been useful as well as Inter-vlan routing to avoid consuming hypervisor resources for VM to carry this function)
  
## Virtual Environment used - Proxmox
I'm a big fan of [Proxmox](https://www.proxmox.com/en/) since year 2019 (thus long before VMWare was hold up). Proxmox 
is qemu based virtualization wrapped into a nice Web GUI, a CLI interface is also available, which I very rarely use, but can be useful for automation.

## Network Environment used
There is not much constraint here, you'll need VLANs with their subnets on top eventually inter-vlan routing 
(which can be carried by a VM if you have not L3 switches or routers), possibly all can be set inside a single Hypervisor (HPCM, SU_Leaders and Compute nodes) 
leading to a very cheap Lab environment.

In the current lab I have the chance to use the wonderful Plexxi solution (what a pity they've stopped it, it was so cool and cleverly designed!)


