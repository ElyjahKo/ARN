import random
import sumolib

def create_routes():
    # Create a route file
    with open("mes_routes.rou.xml", "w") as routes:
        print("""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="50" guiShape="passenger"/>
""", file=routes)

        # Add routes for different directions
        routes_list = [
            ("n1", "n3"),  # bottom to top
            ("n2", "n4"),  # right to left
            ("n3", "n1"),  # top to bottom
            ("n4", "n2")   # left to right
        ]

        # Add 5 vehicles for each route
        for i, (from_edge, to_edge) in enumerate(routes_list):
            for j in range(5):
                depart = i * 10 + j  # Stagger departures
                print(f'    <vehicle id="veh_{i}_{j}" type="car" route="{from_edge}to{to_edge}" depart="{depart}" />', file=routes)
        
        # Add the routes
        for from_edge, to_edge in routes_list:
            print(f'    <route id="{from_edge}to{to_edge}" edges="{from_edge} center {to_edge}" />', file=routes)
        
        print("</routes>", file=routes)
    
    print("Routes created successfully!")

if __name__ == "__main__":
    create_routes()
