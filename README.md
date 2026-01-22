# HPCM on VM

## Abstract
[HPCM](https://www.hpe.com/psnow/doc/a00044858enw) purpose is to manage Clusters of High Performance Computers... so why using HPCM to manage Virtual Machines?

The objective here is to be able to experiment with the HPCM software, when you don't have the hardware and money that goes with
it or want to somehow prepare a big scale operation on a real HPC cluster. Thus the Performance (the P of HPC - High Performance Computing)
is not the target here, the objective is rather the ability to use and test many features of HPCM:
- install HPCM and eventually SU_Leaders in their own VMs
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

The HPCM features that will not be available in a VM environment are:
- power management (the ability to boot or reboot a compute node from HPCM)
- network switch management
- Slingshot HSN will not be available (well, I have not checked whether a software emulation was exiting, but I doubt it would)

## Table of Content

### 1 - [Requirements](doc/requirements.md)
### 2 - [VM setup](doc/proxmox-setup.md)
### 3 - [HPCM tweeking](doc/hpmc-node-setup.md)


