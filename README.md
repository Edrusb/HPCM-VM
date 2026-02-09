# HPCM on VM and for VMs

## Abstract
[HPCM](https://www.hpe.com/psnow/doc/a00044858enw) purpose is to manage Clusters of High Performance Computers, things where
performance means *hardware*... so why using HPCM to manage Virtual Machines (i.e. *software* computers)?

The objective here is to be able to experiment with the HPCM software, when you don't have the hardware and money that goes with
it or want to somehow prepare a big scale operation that will take place later on a real-hardware-powered HPC cluster.

Thus the Performance (the P of HPC - High Performance Computing)
is not the target here, the objectives are rather the ability to use and test as many features of HPCM as possible:
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
- deploy and run some MPI application
- play with HPCM slots
- power management (the ability to boot or reboot a compute node from HPCM) thanks to virtual BMCs

The HPCM features that will not be available in a VM environment are:
- network switch management
- remote console port access
- Slingshot HSN will not be available (well, I have not checked whether a software emulation was exiting, but I doubt it would, correct me if I'm wrong!!!)

## Table of Content

### 1 - [Requirements](doc/1-requirements.md)
### 2 - [VM setup](doc/2-proxmox-setup.md)
### 3 - [HPCM tweeking](doc/3-hpcm-node-setup.md)
### 4 - [Console on Serial Port](doc/4-console-on-serial.md)
### 5 - [Virtual BMC](doc/5-proxmoxbmc.md)
### 6 - [Using Proxmoxbmc with HPCM](doc/6-multibmc.md)
