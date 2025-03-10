#!/usr/bin/env python3
"""
P4 Mininet Integration Script

Description:
This script sets up a Mininet topology with a P4-enabled software switch. 
It parses command-line arguments to configure the switch architecture, 
Thrift communication, and JSON configuration for P4 execution.

Usage:
python script.py --json <path_to_compiled_p4_json> [--behavioral-exe <switch_exe>] [--thrift-port <port_number>]

Arguments:
- --json: Path to the compiled P4 JSON configuration file (required).
- --behavioral-exe: Software switch executable (default: 'simple_switch').
- --thrift-port: Thrift server port for runtime switch communication (default: 9090).

Dependencies:
- Mininet
- P4 (BMv2, Thrift)
- Python 3.x

Author: jfpereira
Date: 10-02-2025
"""

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI

from p4_mininet import P4Switch, P4Host

import argparse
from time import sleep

# This parser identifies three arguments:  
#  
# --behavioral-exe (default: 'simple_switch')  
## Specifies the architecture of our software switch as 'simple_switch'.  
## Any P4 program targeting this architecture must be compiled against 'v1model.p4'.  
#  
# --thrift-port (default: 9090)  
## Defines the default server port for a Thrift server.  
## The P4Switch instantiates a Thrift server, enabling runtime communication with the software switch.  
#  
# --json (required)  
## Specifies the path to the JSON configuration file, which is the output of the P4 program compilation.  
## This is the only mandatory argument needed to run the script.
parser = argparse.ArgumentParser(description='Task 1')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", default='simple_switch')
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)

args = parser.parse_args()

# Mininet assigns MAC addresses automatically, but we need to control this process  
# to ensure that the MAC addresses match our network design.  
# This is crucial because the rules we set in the data plane tables must use  
# the exact MAC addresses of the network.

# In Mininet, IP addresses are assigned only to hosts.  
# Any other IP-related tasks, if required, are handled by the controller.


class SingleSwitchTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        
        # In Mininet, we create switches, hosts, and links.  
        # Every network device — whether it's an L2 switch, L3 switch, firewall, or load balancer — is treated as a switch in Mininet.        
        
        # Adding a P4Switch  
        # Refer to the P4Switch class in p4_mininet.py for more details.  
        r1 = self.addSwitch('r1',
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thrift_port)
        
        # Adding a host with the correct MAC and IP addresses. 
        h1 = self.addHost('h1',
                          ip = "10.0.1.1/24",
                          mac = "00:04:00:00:00:01") 
        
        # When declaring a link, using addr2=sw_mac assigns the specified MAC address  
        # to the second argument in the link, which in this case is the switch port.
        # the same logic is applyed to port2=1
        self.addLink(h1, r1, port2 = 1, addr2 = "aa:00:00:00:01:01")
        
        # TASK: follow the topology presented in the README.md

def main():
    # The 'topo' instance represents the network topology in Mininet.
    # It defines the structure of switches, hosts, and links in the simulation.
    topo = SingleSwitchTopo(args.behavioral_exe,
                            args.json,
                            args.thrift_port)

    # The host class used in this topology is P4Host.  
    # The switch class used is P4Switch.  
    # 'net' is the instance that represents our Mininet simulation.  
    net = Mininet(topo = topo,
                  host = P4Host,
                  switch = P4Switch,
                  controller = None)

    net.start()

    # Allow time for the host and switch configurations to take effect.
    sleep(1)

    # In this setup, we're not implementing the ARP protocol. Therefore, we manually configure the ARP entry
    # so that host h1 can correctly resolve the MAC address for the gateway when sending packets.

    # Retrieve the host 'h1' from the network topology.
    h1 = net.get('h1')
    # Manually set the ARP entry for the gateway IP 10.0.1.254 with its corresponding MAC address.
    h1.setARP("10.0.1.254", "aa:00:00:00:01:01")
    # Configure the default route for h1 to direct traffic through interface eth0 via the gateway 10.0.1.254.
    h1.setDefaultRoute("dev eth0 via 10.0.1.254")


    print("Ready !")

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
    