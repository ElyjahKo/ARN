import os
import sys
import traci
import sumolib
from sumolib.net import Net
from sumolib.net.node import Node
from sumolib.net.edge import Edge

def create_simple_network():
    # Create a new network
    net = Net("simple_network")
    
    # Create nodes (intersections)
    nodes = [
        ("n1", 0, 0),    # bottom-left
        ("n2", 100, 0),  # bottom-right
        ("n3", 100, 100), # top-right
        ("n4", 0, 100),   # top-left
        ("center", 50, 50) # center
    ]
    
    for node_id, x, y in nodes:
        node = Node(node_id, x, y, "priority")
        net.addNode(node)
    
    # Create edges (roads)
    edges = [
        ("e1", "n1", "center", 1, 13.89),  # 50 km/h
        ("e2", "center", "n2", 1, 13.89),
        ("e3", "n2", "center", 1, 13.89),
        ("e4", "center", "n1", 1, 13.89),
        ("e5", "n3", "center", 1, 13.89),
        ("e6", "center", "n4", 1, 13.89),
        ("e7", "n4", "center", 1, 13.89),
        ("e8", "center", "n3", 1, 13.89)
    ]
    
    for edge_id, from_node, to_node, lanes, speed in edges:
        edge = Edge(edge_id, net.getNode(from_node), net.getNode(to_node), 1, priority=1, numLanes=lanes, speed=speed)
        net.addEdge(edge)
    
    # Save the network
    net.write("mon_reseau.net.xml")
    print("Network created successfully!")

if __name__ == "main__":
    create_simple_network()
