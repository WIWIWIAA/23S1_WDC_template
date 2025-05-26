#!/usr/bin/env python3

class Router:
    def __init__(self, name, all_routers):
        self.name = name                    
        self.all_routers = all_routers      
        self.neighbors = {}                 
        self.distance_table = {}
        # Store complete distance vectors received from neighbors
        self.stored_distance_vectors = {}
        
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
                        if destination in self.neighbors and destination == next_hop:
                            # Direct connection: cost to reach neighbor via itself
                            self.distance_table[destination][next_hop] = self.neighbors[destination]
                        else:
                            # Everything else starts as infinity
                            self.distance_table[destination][next_hop] = float('inf')
                            
    def print_distance_table(self, step):
        """Print distance table in required format"""
        print(f"Distance Table of router {self.name} at t={step}:")
        
        # Header with destination names
        destinations = sorted([d for d in self.all_routers if d != self.name])
        
        # Print header with proper spacing
        header = "     " + "    ".join(f"{dest}" for dest in destinations) + "    "
        print(header)
        
        for next_hop in destinations:
            row = f"{next_hop}    "
            for dest in destinations:
                # Access as distance_table[next_hop][dest] for correct format
                cost = self.distance_table[next_hop][dest]
                if cost == float('inf'):
                    row += "INF  "
                else:
                    row += f"{int(cost)}    "
            print(row)
        print()
    
    def get_distance_vector_for_neighbor(self, neighbor_name):
        """Get distance vector with poisoned reverse for specific neighbor"""
        distance_vector = {}
        for dest in self.all_routers:
            if dest != self.name:
                # Find best path to dest
                best_cost = float('inf')
                best_next_hop = None
                
                for next_hop in self.all_routers:
                    if next_hop != self.name:
                        cost = self.distance_table[dest][next_hop]
                        if cost < best_cost:
                            best_cost = cost
                            best_next_hop = next_hop
                
                # POISONED REVERSE: If we route to dest via this neighbor,
                # advertise infinity to that neighbor
                if best_next_hop == neighbor_name:
                    distance_vector[dest] = float('inf')  # Poison the reverse!
                else:
                    distance_vector[dest] = best_cost
                    
        return distance_vector
    
    def update_from_neighbor(self, neighbor_name, neighbor_distances):
        """Update distance table based on neighbor's distance vector"""
        if neighbor_name not in self.neighbors:
            return False  # Not a direct neighbor
        
        # Store the complete distance vector from this neighbor
        self.stored_distance_vectors[neighbor_name] = neighbor_distances.copy()
        
        changed = False
        neighbor_cost = self.neighbors[neighbor_name]
        
        # Update costs to all destinations via this neighbor
        for dest in self.all_routers:
            if dest != self.name and dest in neighbor_distances:
                # Cost via this neighbor = cost to neighbor + neighbor's cost to dest
                neighbor_dist = neighbor_distances[dest]
                if neighbor_dist == float('inf'):
                    new_cost = float('inf')
                else:
                    new_cost = neighbor_cost + neighbor_dist
                
                # Update cost to reach dest via neighbor_name
                old_cost = self.distance_table[dest][neighbor_name]
                
                if new_cost != old_cost:
                    self.distance_table[dest][neighbor_name] = new_cost
                    changed = True
        
        return changed
    
    def recalculate_after_topology_change(self):
        """Recalculate distance table after topology changes - COMPLETE FIX"""
        
        # Step 1: Remove stored distance vectors for neighbors that no longer exist
        neighbors_to_remove = []
        for stored_neighbor in self.stored_distance_vectors:
            if stored_neighbor not in self.neighbors:
                neighbors_to_remove.append(stored_neighbor)
        
        for neighbor in neighbors_to_remove:
            del self.stored_distance_vectors[neighbor]
        
        # Step 2: Update distance table
        for dest in self.all_routers:
            if dest != self.name:
                for next_hop in self.all_routers:
                    if next_hop != self.name:
                        
                        if dest == next_hop:
                            # Direct connection case
                            if dest in self.neighbors:
                                # Update direct link cost
                                self.distance_table[dest][next_hop] = self.neighbors[dest]
                            else:
                                # Link was removed
                                self.distance_table[dest][next_hop] = float('inf')
                        
                        elif next_hop in self.neighbors:
                            # Indirect path via existing neighbor
                            if next_hop in self.stored_distance_vectors:
                                # Recalculate using stored distance vector
                                neighbor_cost = self.neighbors[next_hop]
                                stored_dv = self.stored_distance_vectors[next_hop]
                                
                                if dest in stored_dv:
                                    if stored_dv[dest] == float('inf'):
                                        self.distance_table[dest][next_hop] = float('inf')
                                    else:
                                        # KEY: Recalculate entire column using stored DV
                                        self.distance_table[dest][next_hop] = neighbor_cost + stored_dv[dest]
                                else:
                                    self.distance_table[dest][next_hop] = float('inf')
                            else:
                                # No stored DV, reset to infinity (will be recalculated in next exchange)
                                self.distance_table[dest][next_hop] = float('inf')
                        
                        else:
                            # Next hop is no longer a neighbor
                            self.distance_table[dest][next_hop] = float('inf')
    
    def print_routing_table(self):
        """Print final routing table in required format"""
        print(f"Routing Table of router {self.name}:")
        
        destinations = sorted([d for d in self.all_routers if d != self.name])
        for dest in destinations:
            # Find best next hop for this destination
            best_cost = float('inf')
            best_next_hop = None
            
            for next_hop in sorted(self.all_routers):
                if next_hop != self.name:
                    cost = self.distance_table[dest][next_hop]
                    if cost < best_cost:
                        best_cost = cost
                        best_next_hop = next_hop
            
            if best_cost == float('inf'):
                print(f"{dest},INF,INF")
            else:
                print(f"{dest},{best_next_hop},{int(best_cost)}")
        print()

def main():
    # Step 1: Read router names
    router_names = []
    while True:
        line = input().strip()
        if line == "START":
            break
        router_names.append(line)
    
    # Step 2: Read initial topology 
    links = []
    while True:
        line = input().strip()
        if line == "UPDATE":
            break
        parts = line.split()
        router1, router2, cost = parts[0], parts[1], int(parts[2])
        links.append((router1, router2, cost))
        
    # Step 3: Create routers
    routers = {}
    for name in router_names:
        routers[name] = Router(name, router_names)
    
    # Step 4: Set up direct connections
    for router1, router2, cost in links:
        routers[router1].neighbors[router2] = cost
        routers[router2].neighbors[router1] = cost
        
    # Step 5: Initialize distance tables
    for router in routers.values():
        router.initialize_distance_table()
        
    # Step 6: Print initial distance tables (t=0)
    for name in sorted(router_names):
        routers[name].print_distance_table(0)
        
    # Step 7: Run Distance Vector algorithm until convergence
    step = 0
    last_distance_vectors = {}
    
    while True:
        step += 1
        
        # Collect all distance vectors that will be sent this round
        distance_vectors = {}
        for name in router_names:
            distance_vectors[name] = routers[name].get_distance_vector()
        
        # Check if converged
        if step > 1 and distance_vectors == last_distance_vectors:
            break
            
        # Each router updates based on what it receives from neighbors
        for name in router_names:
            router = routers[name]
            for neighbor_name in router.neighbors:
                if neighbor_name in distance_vectors:
                    router.update_from_neighbor(neighbor_name, distance_vectors[neighbor_name])
        
        # Print distance tables for this step
        for name in sorted(router_names):
            routers[name].print_distance_table(step)
            
        # Save for convergence check
        last_distance_vectors = distance_vectors
    
    # Step 8: Print final routing tables
    for name in sorted(router_names):
        routers[name].print_routing_table()
        
    # Step 9: Handle updates
    updates = []
    while True:
        try:
            line = input().strip()
            if line == "END":
                break
            if line:
                parts = line.split()
                router1, router2, cost = parts[0], parts[1], int(parts[2])
                updates.append((router1, router2, cost))
        except EOFError:
            break
    
    # Apply updates if any
    if updates:
        # Apply topology changes
        for router1, router2, cost in updates:
            if cost == -1:
                # Remove link
                if router2 in routers[router1].neighbors:
                    del routers[router1].neighbors[router2]
                if router1 in routers[router2].neighbors:
                    del routers[router2].neighbors[router1]
            else:
                # Add/update link
                routers[router1].neighbors[router2] = cost
                routers[router2].neighbors[router1] = cost
        
        # Recalculate all distance tables after topology change
        for router in routers.values():
            router.recalculate_after_topology_change()
        
        step = 3  # Start at t=3 after topology change
        for name in sorted(router_names):
            routers[name].print_distance_table(step)
        
        # Run algorithm again until convergence
        last_distance_vectors = {}
        
        while True:
            # Collect distance vectors
            distance_vectors = {}
            for name in router_names:
                distance_vectors[name] = routers[name].get_distance_vector()
            
            # Check if converged
            if step > 3 and distance_vectors == last_distance_vectors:
                break
                
            # Each router updates based on what it receives from neighbors
            for name in router_names:
                router = routers[name]
                for neighbor_name in router.neighbors:
                    if neighbor_name in distance_vectors:
                        router.update_from_neighbor(neighbor_name, distance_vectors[neighbor_name])
            
            # Increment step and print tables for this step
            step += 1
            for name in sorted(router_names):
                routers[name].print_distance_table(step)
                
            # Save for convergence check
            last_distance_vectors = distance_vectors
        
        # Print final routing tables after updates
        for name in sorted(router_names):
            routers[name].print_routing_table()

if __name__ == "__main__":
    main()