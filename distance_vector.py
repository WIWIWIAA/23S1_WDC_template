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
                        
    def initialize_distance_table(self):
        """Set up initial distance table with direct neighbor costs"""
        for destination in self.all_routers:
            if destination != self.name:
                for next_hop in self.all_routers:
                    if next_hop != self.name:
                        if destination == next_hop and next_hop in self.neighbors:
                            # Direct connection: cost to reach neighbor via itself
                            self.distance_table[destination][next_hop] = self.neighbors[next_hop]
                        else:
                            # Everything else starts as infinity
                            self.distance_table[destination][next_hop] = float('inf')
                            
    def print_distance_table(self, step):
        """Print distance table in required format"""
        print(f"Distance Table of router {self.name} at t={step}:")
        
        # Header with destination names
        destinations = [d for d in self.all_routers if d != self.name]
        header = "     " + "".join(f"{dest:<5}" for dest in destinations)
        print(header)
        
        # Rows for each next hop
        for next_hop in destinations:
            row = f"{next_hop:<4} "
            for dest in destinations:
                cost = self.distance_table[dest][next_hop]
                if cost == float('inf'):
                    row += "INF  "
                else:
                    row += f"{cost:<4} "
            print(row.rstrip())
        print()  # Blank line after each table
    
    def get_distance_vector(self):
        """Get current best distances to each destination"""
        distance_vector = {}
        for dest in self.all_routers:
            if dest != self.name:
                # Find minimum cost across all next hops
                min_cost = float('inf')
                for next_hop in self.distance_table[dest]:
                    if self.distance_table[dest][next_hop] < min_cost:
                        min_cost = self.distance_table[dest][next_hop]
                distance_vector[dest] = min_cost
        return distance_vector
    
    def update_from_neighbor(self, neighbor_name, neighbor_distances):
        """Update distance table based on neighbor's distance vector"""
        if neighbor_name not in self.neighbors:
            return False  # Not a direct neighbor
        
        changed = False
        neighbor_cost = self.neighbors[neighbor_name]
        
        for dest, neighbor_dist in neighbor_distances.items():
            if dest != self.name:  # Don't update routes to ourselves
                # Cost via this neighbor = cost to neighbor + neighbor's cost to dest
                new_cost = neighbor_cost + neighbor_dist
                old_cost = self.distance_table[dest][neighbor_name]
                
                if new_cost != old_cost:
                    self.distance_table[dest][neighbor_name] = new_cost
                    changed = True
        
        return changed
    
    def print_routing_table(self):
        """Print final routing table in required format"""
        print(f"Routing Table of router {self.name}:")
        
        destinations = [d for d in self.all_routers if d != self.name]
        for dest in sorted(destinations):  # Alphabetical order
            # Find best next hop for this destination
            best_cost = float('inf')
            best_next_hop = None
            
            for next_hop in sorted(self.all_routers):  # Alphabetical for tie-breaking
                if next_hop != self.name:
                    cost = self.distance_table[dest][next_hop]
                    if cost < best_cost:
                        best_cost = cost
                        best_next_hop = next_hop
            
            if best_cost == float('inf'):
                print(f"{dest},INF,INF")
            else:
                print(f"{dest},{best_next_hop},{best_cost}")
        print()

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
        
    # Step 5: Initialize distance tables
    for router in routers.values():
        router.initialize_distance_table()
    
    # Debug: print Router X's initial distance table
    print(f"\nRouter X initial distance table:")
    for dest in routers['X'].distance_table:
        print(f"  To {dest}: {routers['X'].distance_table[dest]}")
        
    for name in sorted(router_names):  # Alphabetical order
        routers[name].print_distance_table(0)
        
    step = 0
    converged = False
    
    while not converged:
        step += 1
        converged = True  # Assume converged unless we see changes
        
        # Collect all distance vectors that will be sent this round
        distance_vectors = {}
        for name in router_names:
            distance_vectors[name] = routers[name].get_distance_vector()
        
        # Each router updates based on what it receives from neighbors
        for name in router_names:
            router = routers[name]
            for neighbor_name in router.neighbors:
                # Router receives distance vector from this neighbor
                changed = router.update_from_neighbor(neighbor_name, distance_vectors[neighbor_name])
                if changed:
                    converged = False  # Something changed, not converged yet
        
        # Print distance tables for this step (only if something changed)
        if not converged:
            for name in sorted(router_names):
                routers[name].print_distance_table(step)
    
    print("Algorithm converged!")
    
    for name in sorted(router_names):
        routers[name].print_routing_table()
    
    
if __name__ == "__main__":
    main()