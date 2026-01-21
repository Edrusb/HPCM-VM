# HPCM on VM
## Abstract
[HPCM](https://www.hpe.com/psnow/doc/a00044858enw) purpose is to manage Clusters of High Performance Computers... so why using HPCM to manage Virtual Machines?

The objective here is to be able to experiment with the HPCM software, when you don't have the hardware and money that goes with 
it or want to somehow prepare a big scale operation on a real HPC cluster. Thus the Performance (the P of HPC - High Performance Computing) 
is not the target here, but rather the ability to use and test many features of HPCM:
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

The HPCM features that will not be available in VM a environment are:
- power management (the ability to boot or reboot a compute node from HPCM)
- network switch management
- Slingshot HSN will not be available (well, I have not checked whether a software emulation was exiting, but I doubt it would)

## Requirement
To setup this type of you will need at least:
- a single computer (very minimum 16 GiB, 8 GB for HPCM VM and 8 GB for a single compute node)
- x86_64 CPU (I could run HCPM + a single compte node VM using only 8 cores, and it was not particularly slow)
- Disk/storage at least 300 GiB (can be less but it will difficult to have several slots on the HPCM VM and to play with repos and images)
- Physical Ethernet Network if more than one hypervisor is used (VLANs/802.1Q will been useful as well as Inter-vlan routing to avoid consuming hypervisor resources for VM to carry this function)
  
### Virtual Environment used - Proxmox
I'm a big fan of [Proxmox](https://www.proxmox.com/en/) since year 2019 (thus long before VMWare was hold up). Proxmox 
is qemu based virtualization wrapped into a nice (read fully featured) Web GUI. A CLI interface is also available, which I very rarely use, but can be useful for automation.
Proxmox is based on Debian and receive a lot of additional packages to manage the Kernel Virtual Machine of the Linux kernel, though the Linux system stays open
and can receive a lot of customized software and kernel tweeking if needed.

### Network Environment used
There is not much constraint here, you'll need VLANs with their subnets on top eventually inter-vlan routing 
(which can be carried by a VM if you have not L3 switches or routers), possibly all can be set inside a single Hypervisor (HPCM, SU_Leaders and Compute nodes) 
leading to a very cheap Lab environment.

In the current lab I have the chance to use the wonderful Plexxi solution (what a pity they've stopped it, it was so cool and cleverly designed!)

## Implementation

### Installing HPCM from an HPE provided ISO
The VM to create should have:
- at least 2 network interfaces
    - one for the public network,
    - one for the HPC admin (aka "head" network)
- at least 100 GiB of disk per slot (if you want to play with slots set a virtual disk of at least 250 GiB)
- 16 GiB or RAM seems OK, I used 32 GiB but have more than 16 GiB unused (all monitoring setup, but no SU_Leaders)
- 8 cores seems OK, more if possible to speedup compression operation (image creation for example)
- a virtual CD/DVD Drive to boot on the ISO image during the HPCM installation process
- UEFI Boot is mandatory (proxmox will require the creation of a tiny virtual disk to store the EFI parameters)
- Virtio Random Number Generator is mandatory for UEFI boot

Here below the VM configuration I used for HPCM VM
![HPCM Virtual hardware](pictures/hpcm-vm.png)

  


