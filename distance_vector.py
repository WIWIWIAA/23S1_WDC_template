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
    # This is where your program starts
    pass

if __name__ == "__main__":
    main()