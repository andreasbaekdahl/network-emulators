import ipaddress

class Router:
    RIB = []
    FIB = []

    def __init__(self, hostname):
        self.hostname = hostname
        print(f"Router {self.hostname} is booting...")
    
    def add_route(self, network, prefix_length, next_hop):
        new_route = {
            "network": network,
            "prefix_length": prefix_length,
            "next_hop": next_hop
        }
        self.RIB.append(new_route)
        self.calculate_fib()
    
    def calculate_fib(self):
        print(f"💭 Calculating FIB for router {self.hostname}")
        print("  ❌ Clearing existing FIB")
        self.FIB = []
        for route in self.RIB:
            new_fib_entry = {
                "prefix": ipaddress.IPv4Network(f"{route['network']}/{route['prefix_length']}"),
                "next_hop": ipaddress.IPv4Address(route["next_hop"])
            }
            print(f"  ⚙️ Populating FIB entry: {new_fib_entry}")
            self.FIB.append(new_fib_entry)

    def show_ip_route(self):
        sh_ip_route_banner = """
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area 
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2

"""
        print(sh_ip_route_banner)
        for route in self.RIB:
            print(f"S    {route['network']}/{route['prefix_length']} via {route['next_hop']}")
    
    def find_next_hop_address(self, dst_addr):
        addr_obj = ipaddress.IPv4Address(dst_addr)
        print(f"Size of FIB: {len(self.FIB)}")
        best_candidate = None
        for fib_entry in self.FIB:
            if addr_obj in fib_entry["prefix"]:
                print(f"  🟡 Found candidate prefix: {fib_entry['prefix']}")
                if not best_candidate:
                    best_candidate = fib_entry
                elif fib_entry['prefix'].prefixlen > best_candidate['prefix'].prefixlen:
                    best_candidate = fib_entry
        if best_candidate:
            print(f"  🟢 Longest prefix match for {dst_addr} is {best_candidate}")
            return best_candidate["next_hop"]
        else:
            print(f"  🔴 No matching route")
    
    def incoming_packet(self, dst_addr):
        print(f"⚠️ Received IP packet for {dst_addr}")
        next_hop_address = self.find_next_hop_address(dst_addr)
        if next_hop_address:
            print(f"  🟢 Forwarding to {next_hop_address}")
        else:
            print("  🔴 Dropping packet")

corerouter = Router("core-01")

corerouter.add_route("10.5.16.0", 23, "192.0.2.1")
corerouter.add_route("10.5.17.64", 28, "192.0.2.3")
corerouter.add_route("10.5.0.0", 16, "192.0.2.4")
corerouter.add_route("10.10.20.0", 24, "192.0.2.1")

corerouter.show_ip_route()

while True:
    destination = input("Send packet to IP address: ")

    try:
        ipaddress.IPv4Address(destination)
        corerouter.incoming_packet(destination)
    except:
        print("Invalid IPv4 address")