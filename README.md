# [RDS - 2425 Task #2] - Simple L3 Switch
This P4 task involves developing a simple L3 Switch that implements essential packet processing functions. Specifically, the switch decrements the TTL and rewrites MAC addresses based on the IP destination address to ensure proper forwarding across networks.


## **Objectives**
- Understand how packet forwarding works between different networks
- Comprehend the parser state machine
- Examine the structure and function of the IPv4 header
- Explore the various types of table lookups permitted in v1model
- How to compute checksums in P4
- Manage more than one P4 device


## Topology:
`h1——r1——r2——h2`

### Network Configuration

| Device    | Interface   | IP Address       | MAC Address            |
|-----------|-------------|------------------|------------------------|
| **h1**    | `h1-eth0`   | `10.0.1.1/24`    | `00:04:00:00:00:01`    |
| **r1**    | `r1-eth1`   | `10.0.1.254/24`  | `aa:00:00:00:01:01`    |
|           | `r1-eth2`   | `10.0.3.1/30`    | `aa:00:00:00:01:02`    |
| **r2**    | `r2-eth1`   | `10.0.3.2/30`    | `aa:00:00:00:02:01`    |
|           | `r2-eth2`   | `10.0.2.254/24`  | `aa:00:00:00:02:02`    |
| **h2**    | `h2-eth0`   | `10.0.2.1/24`    | `00:04:00:00:00:02`    |

## Task Description
### **Create the Topology**
- Create the network topology in Mininet, ensuring that each P4 device is instantiated correctly.
- Assign a unique Thrift port to each P4 device to prevent any conflicts during runtime.
- Since the exercise does not implement ARP, manually configure the ARP table for each host to correctly map gateway IP addresses to their MAC addresses.
- Set the default route manually on the host so that traffic is correctly forwarded through the designated gateway.

### **l3switch.p4 headers and parser**
- Define a IPv4 header
- Create a state for ipv4 parsing
### **l3switch.p4 ingress**
- Create a table that performs a longest prefix match on the IPv4 destination address. This table should output two critical pieces of information—a designated egress port and the corresponding next-hop MAC address—when a match is found, or drop the packet otherwise.
- Implement an action that receives the egress port and next-hop MAC address from the routing lookup. This action should set the packet's egress port, store the next-hop MAC address in a metadata field for later use, and decrement the IPv4 TTL by one.
- Construct a second table that uses an exact match on the egress port (or other suitable field) to trigger an action that rewrites the Ethernet header. This action must update the source MAC address (to a predetermined value) and the destination MAC address using the metadata containing the next-hop MAC.
- In the ingress processing block, first verify that the IPv4 header is valid. If it is, apply the routing lookup stage; upon a successful match, invoke the MAC rewriting stage. If either the IPv4 header is not valid or no match is found, drop the packet.
### **l3switch.p4 compute checksum**
- Investigate which IPv4 header fields are used in the checksum calculation.
- Modify the existing compute checksum function by adding the identified IPv4 header fields so that the checksum reflects any changes—particularly the decremented TTL.

### **Rules**
   - Extend `flows/r1-flows.txt` to define the necessary flow rules for populating the tables of your `r1` L3 switch.
   - Extend `flows/r2-flows.txt` to define the necessary flow rules for populating the tables of your `r2` L3 switch.
   - Syntax: 
   - `table_add <table_name> <action_name> <key> => <arguments_for_the_action>`

### **Test your setup**
1. **Compile the P4 code**
```bash
p4c-bm2-ss --std p4-16  p4/l3switch.p4 -o json/l3switch.json
```
2. **Run Mininet script**
```bash
sudo python3 mininet/task2-topo.py --json json/l3switch.json
```
3. **Inject the flows rules for each device**
```bash
simple_switch_CLI --thrift-port 9090 < flows/r1-flows.txt
simple_switch_CLI --thrift-port 9091 < flows/r2-flows.txt
``` 
4. **Test**
```bash
mininet> h1 ping h2 -c 5
```
5. **Exit and Clean**
```bash
mininet> exit
$ sudo mn -c
```

## Debugging Tips

Here are some useful commands to help troubleshoot and verify your topology:

### 1. **Wireshark (Packet Capture)**

### 2. **ARP Table Inspection**
   - **Command:** `arp -n`
   - **Usage:** Check the ARP table on any Mininet host to ensure proper IP-to-MAC Default gateway resolution.
   - Example:
     ```bash
     mininet> h1 arp -n
     ```

### 3. **Interface Information**
   - **Command:** `ip link`
   - **Usage:** Display the state and configuration of network interfaces for each host or router.
   - Example:
     ```bash
     mininet> r1 ip link
     ```

### 4. **P4 Runtime Client for Monitoring**
   - **Command:** `sudo ./tools/nanomsg_client.py --thrift-port <r1_port or r2_port>`
   - **Usage:** Interact with the P4 runtime to inspect flow tables and rules loaded on each router.
   - Example:
     ```bash
     sudo ./tools/nanomsg_client.py --thrift-port 9090
     ```

These commands will help you inspect network traffic, verify ARP entries, check interface states, and interact directly with the P4 routers.
