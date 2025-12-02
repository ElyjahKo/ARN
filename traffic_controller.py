import os
import sys
import traci
import traci.constants as tc
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

# Importer notre implémentation d'arbre rouge-noir
from arn import RedBlackTree, Lane, Color, RBNode, VehicleType

class TrafficLightController:
    def __init__(self):
        self.tls_id = "0"  # ID du feu de circulation dans SUMO
        self.lanes = self.initialize_lanes()
        self.rbt = RedBlackTree()
        self.current_green_phase = -1
        self.cycle_count = 0
        self.phases = [
            "GGggrrrrGGggrrrr",  # Phase 0: Nord-Sud vert
            "yyggrrrryyggrrrr",  # Phase 1: Nord-Sud jaune
            "rrrrGGggrrrrGGgg",  # Phase 2: Est-Ouest vert
            "rrrryyggrrrryygg"   # Phase 3: Est-Ouest jaune
        ]
        
    def initialize_lanes(self) -> List[Lane]:
        """Initialise les voies avec des valeurs par défaut"""
        return [
            Lane(name="north", num_vehicles=0, wait_time=0, congestion_level=0, 
                 has_bus=False, has_emergency=False),
            Lane(name="south", num_vehicles=0, wait_time=0, congestion_level=0, 
                 has_bus=False, has_emergency=False),
            Lane(name="east", num_vehicles=0, wait_time=0, congestion_level=0, 
                 has_bus=False, has_emergency=False),
            Lane(name="west", num_vehicles=0, wait_time=0, congestion_level=0, 
                 has_bus=False, has_emergency=False)
        ]
    
    def update_traffic_data(self):
        """Met à jour les données de trafic depuis SUMO"""
        # Réinitialiser les compteurs
        for lane in self.lanes:
            lane.num_vehicles = 0
            lane.wait_time = 0
            lane.has_bus = False
            lane.has_emergency = False
            
        # Compter les véhicules par voie
        for veh_id in traci.vehicle.getIDList():
            lane_id = traci.vehicle.getLaneID(veh_id)
            waiting_time = traci.vehicle.getWaitingTime(veh_id)
            
            # Déterminer la direction du véhicule
            if lane_id.startswith("-gneE0"):  # Ouest
                lane = next(l for l in self.lanes if l.name == "west")
            elif lane_id.startswith("gneE0"):  # Est
                lane = next(l for l in self.lanes if l.name == "east")
            elif lane_id.startswith("-gneE1"):  # Sud
                lane = next(l for l in self.lanes if l.name == "south")
            elif lane_id.startswith("gneE1"):  # Nord
                lane = next(l for l in self.lanes if l.name == "north")
            else:
                continue
                
            # Mettre à jour les compteurs
            lane.num_vehicles += 1
            lane.wait_time = max(lane.wait_time, waiting_time)
            
            # Vérifier le type de véhicule
            veh_type = traci.vehicle.getTypeID(veh_id)
            if veh_type == "bus":
                lane.has_bus = True
            elif veh_type == "emergency":
                lane.has_emergency = True
                
        # Mettre à jour les niveaux de congestion (0-10)
        for lane in self.lanes:
            lane.congestion_level = min(10, lane.num_vehicles * 2)
    
    def calculate_priorities(self):
        """Calcule les priorités pour chaque voie"""
        for lane in self.lanes:
            lane.calculate_score()
    
    def update_traffic_lights(self):
        """Met à jour les feux de circulation en fonction des priorités"""
        self.rbt.clear()
        
        # Ajouter les voies à l'arbre rouge-noir
        for lane in self.lanes:
            self.rbt.insert(lane.priority_score, lane)
        
        # Trouver la voie avec la priorité la plus élevée
        max_node = self.rbt.find_maximum()
        if max_node is None or max_node == self.rbt.NIL:
            return
            
        # Déterminer la phase à activer
        if max_node.lane.name in ["north", "south"]:
            new_phase = 0  # Phase Nord-Sud
        else:
            new_phase = 2  # Phase Est-Ouest
        
        # Changer de phase si nécessaire
        if new_phase != self.current_green_phase and self.current_green_phase != -1:
            # D'abord passer à la phase jaune
            traci.trafficlight.setRedYellowGreenState(
                self.tls_id, 
                self.phases[new_phase - 1]  # Phase jaune correspondante
            )
            traci.simulationStep()  # Avancer d'un pas de simulation
            time.sleep(2)  # Attendre 2 secondes pour la phase jaune
            
        # Passer à la nouvelle phase
        traci.trafficlight.setRedYellowGreenState(
            self.tls_id, 
            self.phases[new_phase]
        )
        self.current_green_phase = new_phase
        
        # Afficher les informations de débogage
        print(f"\n=== Cycle {self.cycle_count} ===")
        for lane in self.lanes:
            print(f"Voie {lane.name}: {lane.num_vehicles} véhicules, "
                  f"temps d'attente: {lane.wait_time:.1f}s, "
                  f"priorité: {lane.priority_score:.1f}")
        print(f"Phase active: {'Nord-Sud' if new_phase == 0 else 'Est-Ouest'}")
        
        self.cycle_count += 1

def run():
    """Exécute la simulation avec le contrôleur personnalisé"""
    # Démarrer SUMO avec connexion TraCI
    sumo_binary = "sumo-gui"  # ou "sumo" pour une exécution sans interface graphique
    sumo_cmd = [
        sumo_binary, "-c", "intersection.sumocfg",
        "--tripinfo-output", "tripinfo.xml",
        "--start", "--quit-on-end"
    ]
    
    # Démarrer la simulation
    traci.start(sumo_cmd)
    
    # Initialiser le contrôleur
    controller = TrafficLightController()
    
    try:
        # Boucle principale de simulation
        step = 0
        while traci.simulation.getMinExpectedNumber() > 0 and step < 1000:
            traci.simulationStep()
            
            # Mettre à jour les données toutes les secondes
            if step % 10 == 0:  # Toutes les 10 étapes (1s)
                controller.update_traffic_data()
                controller.calculate_priorities()
                
                # Mettre à jour les feux toutes les 30 secondes
                if step % 300 == 0:  # Toutes les 30 secondes
                    controller.update_traffic_lights()
            
            step += 1
            
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        traci.close()
        print("Simulation terminée.")

if __name__ == "__main__":
    run()
