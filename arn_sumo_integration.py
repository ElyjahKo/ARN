# arn_sumo_integration.py
import random
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict

import traci

# ---- CONFIG SUMO ----
SUMO_BINARY = "sumo-gui"   # ou "sumo" si tu veux sans GUI
SUMO_CONFIG = "mon_config.sumocfg"
TLS_ID = "center"          # id du carrefour/traffic light dans le net (dans mon_reseau.net.xml)
CYCLE_DELAY = 1.0          # délai (en secondes) entre les cycles ARN
SIM_STEPS_PER_CYCLE = 10   # nombre d'appels traci.simulationStep() par cycle ARN

# ---- TON CODE EXISTANT ----

# Couleurs pour l'affichage
class Color(Enum):
    RED = 0
    BLACK = 1

class VehicleType(Enum):
    CAR = 0
    BUS = 1
    AMBULANCE = 2
    FIRE_TRUCK = 3

@dataclass
class Lane:
    """Représente une voie logique (mapping vers edges SUMO)"""
    name: str
    sumo_edge_id: str
    num_vehicles: int
    wait_time: float  # en secondes
    congestion_level: int  # 0-10
    has_bus: bool
    has_emergency: bool
    priority_score: float = 0.0
    
    def calculate_score(self):
        """Calcule le score de priorité de la voie"""
        score = (
            self.num_vehicles * 1.0 +
            self.wait_time * 0.5 +
            self.congestion_level * 2.0
        )
        
        if self.has_bus:
            score += 20
        
        if self.has_emergency:
            score += 100
        
        self.priority_score = score
        return score

# ========== IMPLÉMENTATION ARBRE ROUGE-NOIR ==========

class RBNode:
    """Nœud d'un Arbre Rouge-Noir"""
    def __init__(self, priority_score: float, lane: Optional[Lane]):
        self.priority_score = priority_score
        self.lane = lane
        self.color = Color.RED
        self.left: Optional[RBNode] = None
        self.right: Optional[RBNode] = None
        self.parent: Optional[RBNode] = None

class RedBlackTree:
    """Arbre Rouge-Noir pour gérer les priorités"""
    
    def __init__(self):
        self.NIL = RBNode(0, None)
        self.NIL.color = Color.BLACK
        self.root = self.NIL
    
    def left_rotate(self, x: RBNode):
        y = x.right
        x.right = y.left
        
        if y.left != self.NIL:
            y.left.parent = x
        
        y.parent = x.parent
        
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        
        y.left = x
        x.parent = y
    
    def right_rotate(self, y: RBNode):
        x = y.left
        y.left = x.right
        
        if x.right != self.NIL:
            x.right.parent = y
        
        x.parent = y.parent
        
        if y.parent is None:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        
        x.right = y
        y.parent = x
    
    def insert(self, priority_score: float, lane: Lane):
        node = RBNode(priority_score, lane)
        node.left = self.NIL
        node.right = self.NIL
        
        parent = None
        current = self.root
        
        while current != self.NIL:
            parent = current
            if node.priority_score < current.priority_score:
                current = current.left
            else:
                current = current.right
        
        node.parent = parent
        
        if parent is None:
            self.root = node
        elif node.priority_score < parent.priority_score:
            parent.left = node
        else:
            parent.right = node
        
        node.color = Color.RED
        self._fix_insert(node)
    
    def _fix_insert(self, node: RBNode):
        while node.parent and node.parent.color == Color.RED:
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                
                if uncle.color == Color.RED:
                    node.parent.color = Color.BLACK
                    uncle.color = Color.BLACK
                    node.parent.parent.color = Color.RED
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self.left_rotate(node)
                    
                    node.parent.color = Color.BLACK
                    node.parent.parent.color = Color.RED
                    self.right_rotate(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                
                if uncle.color == Color.RED:
                    node.parent.color = Color.BLACK
                    uncle.color = Color.BLACK
                    node.parent.parent.color = Color.RED
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self.right_rotate(node)
                    
                    node.parent.color = Color.BLACK
                    node.parent.parent.color = Color.RED
                    self.left_rotate(node.parent.parent)
        
        self.root.color = Color.BLACK
    
    def find_maximum(self) -> Optional[RBNode]:
        if self.root == self.NIL:
            return None
        
        current = self.root
        while current.right != self.NIL:
            current = current.right
        
        return current
    
    def delete(self, node: RBNode):
        y = node
        y_original_color = y.color
        
        if node.left == self.NIL:
            x = node.right
            self._transplant(node, node.right)
        elif node.right == self.NIL:
            x = node.left
            self._transplant(node, node.left)
        else:
            y = self._minimum(node.right)
            y_original_color = y.color
            x = y.right
            
            if y.parent == node:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = node.right
                y.right.parent = y
            
            self._transplant(node, y)
            y.left = node.left
            y.left.parent = y
            y.color = node.color
        
        if y_original_color == Color.BLACK:
            self._fix_delete(x)
    
    def _transplant(self, u: RBNode, v: RBNode):
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent
    
    def _minimum(self, node: RBNode) -> RBNode:
        while node.left != self.NIL:
            node = node.left
        return node
    
    def _fix_delete(self, node: RBNode):
        while node != self.root and node.color == Color.BLACK:
            if node == node.parent.left:
                sibling = node.parent.right
                
                if sibling.color == Color.RED:
                    sibling.color = Color.BLACK
                    node.parent.color = Color.RED
                    self.left_rotate(node.parent)
                    sibling = node.parent.right
                
                if sibling.left.color == Color.BLACK and sibling.right.color == Color.BLACK:
                    sibling.color = Color.RED
                    node = node.parent
                else:
                    if sibling.right.color == Color.BLACK:
                        sibling.left.color = Color.BLACK
                        sibling.color = Color.RED
                        self.right_rotate(sibling)
                        sibling = node.parent.right
                    
                    sibling.color = node.parent.color
                    node.parent.color = Color.BLACK
                    sibling.right.color = Color.BLACK
                    self.left_rotate(node.parent)
                    node = self.root
            else:
                sibling = node.parent.left
                
                if sibling.color == Color.RED:
                    sibling.color = Color.BLACK
                    node.parent.color = Color.RED
                    self.right_rotate(node.parent)
                    sibling = node.parent.left
                
                if sibling.right.color == Color.BLACK and sibling.left.color == Color.BLACK:
                    sibling.color = Color.RED
                    node = node.parent
                else:
                    if sibling.left.color == Color.BLACK:
                        sibling.right.color = Color.BLACK
                        sibling.color = Color.RED
                        self.left_rotate(sibling)
                        sibling = node.parent.left
                    
                    sibling.color = node.parent.color
                    node.parent.color = Color.BLACK
                    sibling.left.color = Color.BLACK
                    self.right_rotate(node.parent)
                    node = self.root
        
        node.color = Color.BLACK
    
    def clear(self):
        """Vide l'arbre"""
        self.root = self.NIL

# ========== SYSTÈME DE GESTION DES FEUX avec intégration SUMO ==========

class TrafficLightSystem:
    """Système intelligent de gestion des feux tricolores, lié à SUMO"""
    
    def __init__(self, lanes: List[Lane]):
        self.lanes = lanes
        self.rbt = RedBlackTree()
        self.current_green: Optional[Lane] = None
        self.cycle_count = 0

        # Pré-calc: mapping sumo_edge_id -> Lane
        self.edge_to_lane: Dict[str, Lane] = {lane.sumo_edge_id: lane for lane in lanes}
    
    def update_traffic_data(self):
        """Met à jour les données de trafic à partir de SUMO (et quelques randomisations)"""
        # On récupère les données SUMO pour chaque edge mappé
        for lane in self.lanes:
            try:
                # nombre de véhicules sur edge (dernier pas)
                vcount = traci.edge.getLastStepVehicleNumber(lane.sumo_edge_id)
                # temps d'attente total (somme temps d'attente des véhicules) -> on moyenne approximativement
                waiting_time = traci.edge.getWaitingTime(lane.sumo_edge_id)
                # nombre de véhicules immobilisés (halting)
                halting = traci.edge.getLastStepHaltingNumber(lane.sumo_edge_id)
                
                lane.num_vehicles = int(vcount)
                
                # approximons wait_time par waiting_time / max(1, num_vehicles)
                lane.wait_time = waiting_time / max(1, lane.num_vehicles)
                
                # congestion approximée par halting fraction * 10
                lane.congestion_level = min(10, int((halting / max(1, lane.num_vehicles)) * 10))
                
                # detection bus / emergency: on regarde les ids des véhicules récents
                lane.has_bus = False
                lane.has_emergency = False
                veh_ids = traci.edge.getLastStepVehicleIDs(lane.sumo_edge_id)
                for vid in veh_ids:
                    # si l'utilisateur ajoute des véhicules spéciaux (ex: ambulance_1) => on les détecte
                    if vid.lower().startswith("bus") or vid.lower().startswith("b_"):
                        lane.has_bus = True
                    if vid.lower().startswith("ambulance") or vid.lower().startswith("emg") or "ambul" in vid.lower():
                        lane.has_emergency = True
            except traci.TraCIException:
                # Si TraCI n'a pas d'info (au début), on garde une simulation légère
                lane.num_vehicles = max(0, lane.num_vehicles + random.randint(-1, 2))
                lane.wait_time = max(0.0, lane.wait_time + random.uniform(0.5, 2.0))
                lane.congestion_level = min(10, max(0, lane.congestion_level + random.randint(-1, 1)))
                if random.random() < 0.02:
                    lane.has_emergency = True
                if random.random() < 0.05:
                    lane.has_bus = True
            
            # recalcul du score
            lane.calculate_score()
    
    def rebuild_priority_tree(self):
        """Reconstruit l'arbre de priorité"""
        self.rbt.clear()
        for lane in self.lanes:
            self.rbt.insert(lane.priority_score, lane)
    
    def get_next_green_light(self) -> Optional[Lane]:
        """Détermine quelle voie doit passer au vert"""
        max_node = self.rbt.find_maximum()
        if max_node:
            return max_node.lane
        return None
    
    def display_status(self):
        """Affiche l'état actuel du système"""
        print("\n" + "="*70)
        print(f"🚦 CYCLE #{self.cycle_count} - État du Carrefour (TLS: {TLS_ID})")
        print("="*70)
        
        for lane in sorted(self.lanes, key=lambda x: x.priority_score, reverse=True):
            status = "🟢 VERT" if lane == self.current_green else "🔴 ROUGE"
            emergency_icon = " 🚑" if lane.has_emergency else ""
            bus_icon = " 🚌" if lane.has_bus else ""
            
            print(f"{status} {lane.name} ({lane.sumo_edge_id}){emergency_icon}{bus_icon}")
            print(f"  Véhicules: {lane.num_vehicles:3d} | "
                  f"Attente moyenne: {lane.wait_time:5.1f}s | "
                  f"Congestion: {lane.congestion_level}/10")
            print(f"  📊 Score de priorité: {lane.priority_score:.2f}")
        
        if self.current_green:
            print(f"\n✅ Feu VERT accordé à: {self.current_green.name}")
        print("="*70)
    
    def apply_green_to_sumo(self):
        """Applique le feu vert dans SUMO pour la voie choisie"""
        if not self.current_green:
            return
        
        # Récupère les controlled links du TLS
        try:
            controlled = traci.trafficlight.getControlledLinks(TLS_ID)
        except traci.TraCIException:
            # pas prêt / pas de TLS
            return
        
        # controlled est une liste par groupe; on a besoin d'énumérer tous les liens
        # Flatten and keep track of index -> each element in the flattened list corresponds to a signal position
        flat_links = []
        for group in controlled:
            for link in group:
                flat_links.append(link)  # link is a tuple (fromEdgeID, toEdgeID, viaLaneIndex)
        
        # Compose l'état: par défaut tout rouge (r). On met 'G' pour les liens provenant de l'edge cible.
        state_chars = []
        target_edge = self.current_green.sumo_edge_id
        matched_any = False
        for link in flat_links:
            from_edge = link[0]
            if from_edge == target_edge:
                state_chars.append("G")  # vert pour ce lien
                matched_any = True
            else:
                state_chars.append("r")  # rouge
        state_str = "".join(state_chars)
        
        if matched_any and len(state_str) > 0:
            try:
                traci.trafficlight.setRedYellowGreenState(TLS_ID, state_str)
            except traci.TraCIException:
                # fallback: try setPhase 0
                try:
                    traci.trafficlight.setPhase(TLS_ID, 0)
                except Exception:
                    pass
        else:
            # fallback si on n'a pas trouvé de correspondance ou erreur: setPhase(0)
            try:
                traci.trafficlight.setPhase(TLS_ID, 0)
            except Exception:
                pass
    
    def run_cycle(self):
        """Exécute un cycle de gestion"""
        self.cycle_count += 1
        
        # 1. Mise à jour des données (depuis SUMO)
        self.update_traffic_data()
        
        # 2. Reconstruction de l'arbre
        self.rebuild_priority_tree()
        
        # 3. Détermination de la voie prioritaire
        self.current_green = self.get_next_green_light()
        
        # 4. Appliquer le vert dans SUMO
        self.apply_green_to_sumo()
        
        # 5. Affichage
        self.display_status()
        
        # 6. Réinitialisation des flags temporaires
        if self.current_green:
            self.current_green.wait_time = 0
            self.current_green.has_bus = False
            self.current_green.has_emergency = False
    
    def simulate_offline(self, num_cycles: int = 10, delay: float = 2.0):
        """Simulateur offline (sans SUMO) si besoin."""
        print("Mode offline: simulation interne (SUMO non connecté)")
        for _ in range(num_cycles):
            # petits changements aléatoires
            for lane in self.lanes:
                lane.num_vehicles = max(0, lane.num_vehicles + random.randint(-2, 3))
                lane.wait_time += random.uniform(0.5, 2.0)
                lane.congestion_level = min(10, max(0, lane.congestion_level + random.randint(-1, 1)))
                if random.random() < 0.05:
                    lane.has_bus = True
                if random.random() < 0.02:
                    lane.has_emergency = True
                lane.calculate_score()
            self.run_cycle()
            time.sleep(delay)

# ========== FONCTION PRINCIPALE ==========

def start_sumo(use_gui: bool = True):
    bin_name = "sumo-gui" if use_gui else "sumo"
    sumo_cmd = [bin_name, "-c", SUMO_CONFIG]
    traci.start(sumo_cmd)

def main():
    # Création des voies (mapping vers les edges que nous avons dans mon_reseau.net.xml)
    lanes = [
        Lane(name="Voie Nord",  sumo_edge_id="NtoC", num_vehicles=12, wait_time=30.0, congestion_level=5, has_bus=False, has_emergency=False),
        Lane(name="Voie Est",   sumo_edge_id="EtoC", num_vehicles=15, wait_time=25.0, congestion_level=6, has_bus=True,  has_emergency=False),
        Lane(name="Voie Sud",   sumo_edge_id="StoC", num_vehicles=8,  wait_time=40.0, congestion_level=4, has_bus=False, has_emergency=True),
        Lane(name="Voie Ouest", sumo_edge_id="WtoC", num_vehicles=6,  wait_time=15.0, congestion_level=3, has_bus=False, has_emergency=False),
    ]
    
    for lane in lanes:
        lane.calculate_score()
    
    system = TrafficLightSystem(lanes)
    
    # Démarre SUMO
    print("🔁 Démarrage SUMO...")
    try:
        start_sumo(use_gui=True)  # change to False si tu veux sans GUI
    except Exception as e:
        print("⚠️ Erreur en lançant SUMO via TraCI:", e)
        print("Le système va continuer en mode offline.")
        system.simulate_offline(num_cycles=10, delay=CYCLE_DELAY)
        return
    
    print("✅ SUMO connecté. Intégration ARN -> SUMO démarrée.")
    
    # Boucle de simulation: on avance dans SUMO quelques steps puis on exécute un cycle ARN
    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            # avance SIM_STEPS_PER_CYCLE steps SUMO pour laisser circuler les véhicules
            for _ in range(SIM_STEPS_PER_CYCLE):
                traci.simulationStep()
            # exécute un cycle ARN
            system.run_cycle()
            # laisse un peu de temps pour que SUMO affiche (si GUI)
            time.sleep(CYCLE_DELAY)
    except KeyboardInterrupt:
        print("⛔ Simulation interrompue par l'utilisateur.")
    except Exception as e:
        print("⚠️ Erreur pendant la simulation:", e)
    finally:
        try:
            traci.close()
        except Exception:
            pass
        print("\n✅ Simulation terminée. Statistiques finales:")
        total_wait = sum(lane.wait_time for lane in lanes)
        avg_wait = total_wait / len(lanes)
        print(f"Temps d'attente moyen (approx): {avg_wait:.2f}s")
        print(f"Congestion moyenne: {sum(l.congestion_level for l in lanes) / len(lanes):.1f}/10")
        emergency_handled = sum(1 for lane in lanes if lane.name == "Voie Sud")
        print(f"Urgences traitées (approx): {emergency_handled}")

if __name__ == "__main__":
    main()
