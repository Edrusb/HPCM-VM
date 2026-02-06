#!/usr/bin/python3

import json
import sys
import os

#
# local error raise ValueError exception
#

DEBUG = False

def os_system(cmd):
    if DEBUG:
        print("would execute: {}".format(cmd))
        return 0
    else:
        return os.system(cmd)

####
# class vbmc holds attributes associated to a VMID: IP/mask/UDP
#

class vbmc:
    def __init__(self,
                 ipv4addr: str = "",
                 masklen: int = 0,
                 udp_port: int = 0):

        # constants strings to dump() and load() the object as a dictionnary
        self.ipv4addr = ipv4addr
        self.masklen  = masklen
        self.udp_port = udp_port

    def dump(self):
        """
        return a dictionnary of the datastructure

        used to dump this data into a json file
        """
        ret = {}
        ret[self.IPV4ADDR] = self.ipv4addr
        ret[self.MASKLEN]  = self.masklen
        ret[self.UDP_PORT] = self.udp_port

        return ret

    def load(self, data: dict):
        """
        set the object fields with the provided dictionnary

        used to load data from json structure
        """
        try:
            self.ipv4addr = data[self.IPV4ADDR]
            self.masklen  = data[self.MASKLEN]
            self.udp_port = data[self.UDP_PORT]
        except:
            self.ipv4addr = ""
            self.masklen  = 0
            self.udp_port = 0
            raise ValueError("Missing value in dictionnary to load a vbmc structure")

    # class/static fields
    IPV4ADDR = "IPV4"
    MASKLEN  = "MASK"
    UDP_PORT = "UDP"



####
# class vbmcclass holds all vBMC sharing a given network interface and UDP range
#
#

class vbmcbase:

    def __init__(self):
        """
        The class constructor

        two constructors with different signature would be needed but
        python does not support this, thus once constructed there are
        two ways to "initialize" the object:
        - set_to() method from the given parameters in argument
        - load() from a json file feeded by a previous call to the dump() method
        """
        self._reset()

    def set_to(self,
               net_dev: str,
               udp_min: int,
               udp_max: int,
               bmc_login: str,
               bmc_pass: str,
               venv_path: str,
               api_token_user: str,
               api_token_name: str,
               api_token_secret: str,
               proxmox_ip: str):
        """
        initialize the vbmcbase

        net_dev: is the interface name on the local machine to be used to expose vBMCs
        udp_min: lowest UDP port to use for vBMCs
        udp_max: highest UDP port to use for vBMCs
        bmc_login: login the vBMCs will require
        bmc_pass: password the vBMCs will require
        venv_path: virtual env where pbmc command is available, this is the full path of the 'active' file
        api_token_user: username by which the API token has been created
        api_token_name: name of the API token created by api_token_user
        api_token_secret: secret of the API token
        proxmox_ip: ip address of a proxmox hypervisor of the proxmox cluster
        """

        # first, some sanity checks on inputs
        if udp_min >= udp_max:
            raise ValueError("udp_min should be strictly less than udp_max")

        self._reset()
        self.net_dev = net_dev
        self.udp_min = udp_min
        self.udp_max = udp_max
        self.bmc_login = bmc_login
        self.bmc_pass = bmc_pass
        self.venv_path = venv_path
        self.api_user = api_token_user
        self.token_name = api_token_name
        self.token_secret = api_token_secret
        self.proxmox_ip = proxmox_ip
        self.vbmcs = {}

    def load(self,
             filename: str):
        """
        loads a vbmc base from a configuration file

        filename: name of the file to read
        the content of file should be the result of
        vbmcbase.dump(filename)
        """

        with open(filename, "r") as f:
            jsonized = json.loads(f.read())
        self._reset()

        try:

            version = jsonized[self.VERSION]
            if version > self.supported_version:
                raise ValueError("Unsupported format version: {}. Max supported version is {}".format(version, self.supported_version))

            # for now only version 1 exist
            # this we have no special condition
            # to check based in the version
            # we read from...

            params = jsonized[self.GPARAMS];
            self.net_dev = params[self.NET_DEV]
            self.udp_min = params[self.UDP_MIN]
            self.udp_max = params[self.UDP_MAX]
            self.bmc_login = params[self.BMC_LOGIN]
            self.bmc_pass = params[self.BMC_PASS]
            self.venv_path = params[self.VENV_PATH]
            self.api_user = params[self.API_USER]
            self.token_name = params[self.TOKEN_NAME]
            self.token_secret = params[self.TOKEN_SECRET]
            self.proxmox_ip = params[self.PROXMOX_IP]

            vbmc_dico = jsonized[self.VBMCS]
            self.vbmcs = {}
            for x in vbmc_dico:
                tmp = vbmc()
                tmp.load(vbmc_dico[x])
                self.vbmcs[x] = tmp

        except Exception as e:
            self._reset()
            raise ValueError("Failed loading vBMC base from file {}: {}".format(filename, e))


    def dump(self, filename: str):
        """
        building json structure and write it to the given file (overwriting the content, no backup file for now)

        """

        self._check_initialized()
        # this is the overall level of what will be the json structure
        jsonized = {}

        jsonized[self.VERSION] = self.supported_version

        # all global params are set as a dictionnary inder the GPARAMS entry
        params = {}
        params[self.NET_DEV]      = self.net_dev
        params[self.UDP_MIN]      = self.udp_min
        params[self.UDP_MAX]      = self.udp_max
        params[self.BMC_LOGIN]    = self.bmc_login
        params[self.BMC_PASS]     = self.bmc_pass
        params[self.VENV_PATH]    = self.venv_path
        params[self.API_USER]     = self.api_user
        params[self.TOKEN_NAME]   = self.token_name
        params[self.TOKEN_SECRET] = self.token_secret
        params[self.PROXMOX_IP]   = self.proxmox_ip
        jsonized[self.GPARAMS] = params

        # VBMCS entry holds a list of vbmcs object
        vbmc_dico = {}
        for obj in self.vbmcs:
            vbmc_dico[obj] = self.vbmcs[obj].dump()
        jsonized[self.VBMCS] = vbmc_dico;

        with open(filename, "w") as f:
            f.write(json.dumps(jsonized))


    def add(self, vmid, ip, masklen):
        """
        create a new vBMC, adds an IP and create iptable rules

        """

        self._check_os_stuff()
        if self._has_vmid(vmid):
            raise ValueError("VM ID {} already has a configuration set".format(vmid))
        udp = self._find_free_udp()
        self._add_to_base(vmid, ip, masklen, udp)
        self._add_to_system(vmid)


    def delete(self, vmid):
        """
        remove an vBMC from the system and database

        """
        self._check_os_stuff()
        if not self._has_vmid(vmid):
            raise ValueError("VM ID {} has no configuration set".format(vmid))
        self._del_from_system(vmid)
        self._del_from_base(vmid)

    def list(self):
        """
        List the current base content

        Note that this does not mean the base has been applied
        to the system, see the clear_system() and set_system()
        methods to do or undo that part of the work.
        """

        self._check_initialized()
        print("")
        print("Global parameters")
        print("------------------")
        print("Net device  : {}".format(self.net_dev))
        print("UDP range   : {} - {}".format(self.udp_min, self.udp_max))
        print("BMC login   : {}".format(self.bmc_login))
        print("BMC password: {}".format(self.bmc_pass))
        print("venv path   : {}".format(self.venv_path))
        print("API user    : {}".format(self.api_user))
        print("Token name  : {}".format(self.token_name))
        print("Token secret: {}".format(self.token_secret))
        print("Proxmox host: {}".format(self.proxmox_ip))
        print("")
        print("Configured BMCs:")
        print("------------------")
        if len(self.vbmcs) == 0:
            print("None")
        else:
            print("+--------+---------------------+-------+")
            print("|  VM ID |     IP address      | UDP   |")
            print("+--------+---------------------+-------+")
            for x in self.vbmcs:
                print("| {:>6} | {:>16}/{:<2} | {:>5} |".format(x, self.vbmcs[x].ipv4addr, self.vbmcs[x].masklen, self.vbmcs[x].udp_port))
            print("+--------+---------------------+-------+")
        print("")

    def check(self):
        """
        Checks that the system has all IPs and iptables rules applied

        """
        pass

    def clear_system(self):
        """
        Removes from the system the BMCs, extra IPs and iptables rules defined in the base

        """

        self._check_os_stuff()
        for x in self.vbmcs:
            self._del_from_system(x)

    def set_system(self):
        """
        Apply to the system the iptables rules, extra IPs and creates the BMCs according to the base content

        """

        self._check_os_stuff()
        for x in self.vbmcs:
            self._add_to_system(x)

        #### class "private" equivalent methods
        # not be called from outside the object itself

    def _reset(self):
        """
        Reset the object to uninitialized state

        """

        # object fields
        self.net_dev = None
        self.udp_min = None
        self.udp_max = None
        self.bmc_login = None
        self.bmc_pass = None
        self.venv_path = None
        self.api_user = None
        self.token_name = None
        self.token_secret = None
        self.proxmox_ip = None

        # vbmc will hold dictionnary associating the VMID to a vbmc objects
        self.vbmcs = None

    def _check_initialized(self):
        """
        Checks whether the object has been initialized

        """

        if self.vbmcs == None:
            raise ValueError("vbmcbase object has not been initialized")

    def _find_free_udp(self):
        """
        Return the first unassigned UDP port in the range

        Throw ValueError exception if range is full
        """

        self._check_initialized()

        found = False
        ret = self.udp_min

        used = []
        for x in self.vbmcs:
            used.append(self.vbmcs[x].udp_port)

        used.sort()
        i_used = 0
        max_used = len(used)
        while i_used < max_used and not found and ret <= self.udp_max:
            if ret < used[i_used]:
                found = True
            else:
                if ret > used[i_used]:
                   raise ValueError("BUG, list was not sorted as expected!!!")
                i_used += 1
                ret += 1
        if i_used == max_used and not found and ret <= self.udp_max:
            found = True

        if found:
            return ret
        else:
            raise ValueError("No more UDP port available in the provided range")

    def _add_to_base(self, vmid, ip, masklen, udp):
        """
        Adds a new vBMC association to the base

        """

        self._check_initialized()
        coord = vbmc(ip, masklen, udp)
        exists = False
        try:
            tmp = self.vbmcs[vmid]
            exists = True
        except:
            pass

        if exists:
            raise ValueError("Configuration for VM ID {} already exists".format(vmid))
        else:
            self.vbmcs[vmid] = coord

    def _add_to_system(self, vmid):
        """
        Adds a new vBMC configuration IP rules and extra IPs to the system

        """

        self._check_initialized()

        # adding a new IP address
        cmd = "ip addr add {}/{} dev {} label {}".format(self.vbmcs[vmid].ipv4addr, self.vbmcs[vmid].masklen, self.net_dev, vmid)
        if os_system(cmd) != 0:
            raise ValueError("shell command failed: {}".format(cmd))
            
        # adding an iptable rule
        cmd = "iptables -t nat -A PREROUTING -i {} -p udp --dport 623 -d {} -j REDIRECT --to-ports {}".format(self.net_dev, self.vbmcs[vmid].ipv4addr, self.vbmcs[vmid].udp_port)
        if os_system(cmd) != 0:
            raise ValueError("shell command failed: {}".format(cmd))

    def _add_to_pbmc(self, vmid):
        """
        Update pbmcd configuration

        # adding a new bmc
        cmd = "source {} 2> /dev/null || . {} 2> /dev/null ; pbmc add --username {} --password {} --port {} --proxmox-address {} --token-user {} --token-name {} --token-value {} {}".format(
            self.venv_path, self.venv_path, self.bmc_login, self.bmc_pass, self.vbmcs[vmid].udp_port, self.proxmox_ip, self.api_user, self.token_name, self.token_secret, vmid)
        if os_system(cmd) != 0:
            raise ValueError("shell command failed: {}".format(cmd))

        # activating the new bmc
        cmd = "source {} 2> /dev/null || . {} 2> /dev/null ; pbmc start {}".format(self.venv_path, self.venv_path, vmid)
        if os_system(cmd) != 0:
            raise ValueError("shell command failed: {}".format(cmd))


    def _del_from_system(self, vmid):
        """
        Remove system configuration relative to the given VM ID

        """

        self._check_initialized()

        error = []

        # removing iptable rule
        cmd = "iptables -t nat -D PREROUTING -i {} -p udp --dport 623 -d {} -j REDIRECT --to-ports {}".format(self.net_dev, self.vbmcs[vmid].ipv4addr, self.vbmcs[vmid].udp_port)
        if os_system(cmd) != 0:
            error.append(cmd)

        # removing the extra IP
        cmd = "ip addr delete {}/{} dev {} label {}".format(self.vbmcs[vmid].ipv4addr, self.vbmcs[vmid].masklen, self.net_dev, vmid)
        if os_system(cmd) != 0:
            error.append(cmd)

        if len(error) > 0:
            print("the following command failed:")
            for cmd in error:
                print(cmd)
            raise ValueError("shell command failed")

    def _del_from_pbmc(self, vmid):
        """
        unconfiguring pbmc for the given VM ID

        
        """
        # removing the vBMC instance
        cmd = "source {} 2> /dev/null || . {} 2> /dev/null ; pbmc del {}".format(self.venv_path, self.venv_path, vmid)
        if os_system(cmd) != 0:
            raise ValueError("pbmc command failed: {}".format(cmd))


    def _has_vmid(self, vmid):
        """
        check whether a configuration exists for the provided VM ID

        """

        return self.vbmcs.get(vmid) != None

    def _del_from_base(self, vmid):
        """
        Delete vmid entry from the base

        """

        self._check_initialized()
        self.vbmcs.pop(vmid)

    def _check_os_stuff(self):
        x = os_system("iptables -V > /dev/null")
        if x != 0:
            raise ValueError("no iptables command available, aborting the operation")
        x = os_system("ip a > /dev/null")
        if x != 0:
            raise ValueError("no ip command available, aborting the operation")

        # we assume the default shell is bourn shell (not a ksh/tcsh/csh...)
        x = os_system("source {} 2> /dev/null || . {} 2> /dev/null ; pbmc --version > /dev/null".format(self.venv_path, self.venv_path))
        if x != 0:
            raise ValueError("pbmc command not found in venv activated by {}".format(self.venv_path))

    ### class static fields

    # max version of the file format we know and version we save as
    supported_version = 1

    # constants used as key in saved json structured file
    VERSION      = "version"
    GPARAMS      = "global"

    NET_DEV      = "netdev"
    UDP_MIN      = "udpmin"
    UDP_MAX      = "udpmax"
    BMC_LOGIN    = "bmclogin"
    BMC_PASS     = "bmcpass"
    VENV_PATH    = "venv"
    API_USER     = "apiuser"
    TOKEN_NAME   = "tokenname"
    TOKEN_SECRET = "tokensecret"
    VBMCS        = "vbmcs"
    PROXMOX_IP   = "proxmox_ip"



####
# Usage
#
#

def usage(argv0):
    print("usage: {} init <configfile> <net device> <udp min> <udp max> <bmcs login> <bmcs pass> <pbmc venv path> <api_user> <token name> <token secret> <proxmox IP/FQDN>".format(argv0))
    print("usage: {} run  <configfile>".format(argv0))
    print("usage: {} stop <configfile>".format(argv0))
    print("usage: {} add  <configfile> <VMID> <IP> <mask len>".format(argv0))
    print("usage: {} del  <configfile> <VMID>".format(argv0))
    print("usage: {} list <configfile>".format(argv0))
    print("")
    print("The *add* and *del* command take effect immediately no need to *stop* and *run* the program.")
    print("*run* and *stop* are to be used from the init process to system initial setup")
    print("Before any command on a <configfile> the *init* command must be run which will create/overwrite the given file")
    print("")
    exit(1)

####
# command line parsing
#
#

def cli_parser():
    argv = sys.argv
    if len(argv) < 3:
        usage(argv[0])
    else:
        base = vbmcbase()
        if argv[1] != "init":
            base.load(argv[2])

        match argv[1]:
            case "init":
                if len(argv) != 13:
                    usage(argv[0])
                else:
                    base.set_to(argv[3], int(argv[4]), int(argv[5]), argv[6], argv[7], argv[8], argv[9], argv[10], argv[11], argv[12])
                    base.dump(argv[2])
            case "run":
                if len(argv) != 3:
                    usage(argv[0])
                else:
                    base.set_system()
            case "stop":
                if len(argv) != 3:
                    usage(argv[0])
                else:
                    base.clear_system()
            case "add":
                if len(argv) != 6:
                    usage(argv[0])
                else:
                    base.add(argv[3], argv[4], argv[5])
                    base.dump(argv[2])
            case "del":
                if len(argv) != 4:
                    usage(argv[0])
                else:
                    base.delete(argv[3])
                    base.dump(argv[2])
            case "list":
                if len(argv) != 3:
                    usage(argv[0])
                else:
                    base.list()
            case _:
                usage(argv[0])


####
# exception and exit code handling
#
#

if __name__ == "__main__":
    try:
        cli_parser()
        exit(0)
    except Exception as e:
        print("{}: {}".format(sys.argv[0], e))
        exit(2)

# exit code:
# 0 - OK
# 1 - syntax error (usage() routine)
# 2 - other error
#
