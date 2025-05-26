#!/usr/bin/env python3

class Router:
    def __init__(self, name, all_routers):
        self.name = name                    
        self.all_routers = all_routers      
        self.neighbors = {}                 
        self.distance_table = {}            
        
        # Initialize distance table
        for destination in all_routers:
            if destination != self.name:
                self.distance_table[destination] = {}
                for next_hop in all_routers:
                    if next_hop != self.name:
                        self.distance_table[destination][next_hop] = float('inf')

def main():
    # Step 1: Read router names
    router_names = []
    while True:
        line = input().strip()
        if line == "START":
            break
        router_names.append(line)
    
    print(f"Router names: {router_names}")  # Debug print
    
    # Step 2: Read initial topology 
    links = []
    while True:
        line = input().strip()
        if line == "UPDATE":
            break
        # Parse "X Y 3" format
        parts = line.split()
        router1, router2, cost = parts[0], parts[1], int(parts[2])
        links.append((router1, router2, cost))
        
    # Step 3: Create routers
    routers = {}
    for name in router_names:
        routers[name] = Router(name, router_names)
    
    print(f"Created routers: {list(routers.keys())}")  # Debug print
    
    # Step 4: Set up direct connections
    for router1, router2, cost in links:
        # Add bidirectional links
        routers[router1].neighbors[router2] = cost
        routers[router2].neighbors[router1] = cost
        
    print(f"Initial links: {links}")  # Debug print
    
    # Debug: print each router's neighbors
    for name in router_names:
        print(f"Router {name} neighbors: {routers[name].neighbors}")
    
    
    

if __name__ == "__main__":
    main()