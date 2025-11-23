import random
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional

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
    """Représente une voie du carrefour"""
    name: str
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
    def __init__(self, priority_score: float, lane: Lane):
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
        """Rotation gauche"""
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
        """Rotation droite"""
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
        """Insère une nouvelle voie dans l'arbre"""
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
        """Corrige l'arbre après insertion"""
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
        """Trouve le nœud avec la priorité maximale (le plus à droite)"""
        if self.root == self.NIL:
            return None
        
        current = self.root
        while current.right != self.NIL:
            current = current.right
        
        return current
    
    def delete(self, node: RBNode):
        """Supprime un nœud de l'arbre"""
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
        """Remplace un sous-arbre par un autre"""
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent
    
    def _minimum(self, node: RBNode) -> RBNode:
        """Trouve le minimum dans un sous-arbre"""
        while node.left != self.NIL:
            node = node.left
        return node
    
    def _fix_delete(self, node: RBNode):
        """Corrige l'arbre après suppression"""
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

# ========== SYSTÈME DE GESTION DES FEUX ==========

class TrafficLightSystem:
    """Système intelligent de gestion des feux tricolores"""
    
    def __init__(self, lanes: list[Lane]):
        self.lanes = lanes
        self.rbt = RedBlackTree()
        self.current_green = None
        self.cycle_count = 0
    
    def update_traffic_data(self):
        """Met à jour les données de trafic (simulation)"""
        for lane in self.lanes:
            # Simulation de changements
            lane.num_vehicles = max(0, lane.num_vehicles + random.randint(-2, 3))
            lane.wait_time += random.uniform(1, 3)
            lane.congestion_level = min(10, max(0, lane.congestion_level + random.randint(-1, 1)))
            
            # Simulation bus/ambulance
            if random.random() < 0.05:
                lane.has_bus = True
            if random.random() < 0.02:
                lane.has_emergency = True
            
            # Recalcul du score
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
        print("\n" + "="*80)
        print(f"🚦 CYCLE #{self.cycle_count} - État du Carrefour")
        print("="*80)
        
        for lane in sorted(self.lanes, key=lambda x: x.priority_score, reverse=True):
            status = "🟢 VERT" if lane == self.current_green else "🔴 ROUGE"
            emergency_icon = " 🚑" if lane.has_emergency else ""
            bus_icon = " 🚌" if lane.has_bus else ""
            
            print(f"\n{status} {lane.name}{emergency_icon}{bus_icon}")
            print(f"  Véhicules: {lane.num_vehicles:3d} | "
                  f"Attente: {lane.wait_time:5.1f}s | "
                  f"Congestion: {lane.congestion_level}/10")
            print(f"  📊 Score de priorité: {lane.priority_score:.2f}")
        
        if self.current_green:
            print(f"\n✅ Feu VERT accordé à: {self.current_green.name}")
        print("="*80)
    
    def run_cycle(self):
        """Exécute un cycle de gestion"""
        self.cycle_count += 1
        
        # 1. Mise à jour des données
        self.update_traffic_data()
        
        # 2. Reconstruction de l'arbre
        self.rebuild_priority_tree()
        
        # 3. Détermination de la voie prioritaire
        self.current_green = self.get_next_green_light()
        
        # 4. Affichage
        self.display_status()
        
        # 5. Réinitialisation des flags temporaires
        if self.current_green:
            self.current_green.wait_time = 0
            self.current_green.has_bus = False
            self.current_green.has_emergency = False
    
    def simulate(self, num_cycles: int = 10, delay: float = 2.0):
        """Simule le fonctionnement pendant plusieurs cycles"""
        print("🚀 Démarrage du système de feux intelligents avec ARN")
        print(f"Nombre de voies: {len(self.lanes)}")
        
        for _ in range(num_cycles):
            self.run_cycle()
            time.sleep(delay)
        
        print("\n✅ Simulation terminée")
        print(f"Total de cycles: {self.cycle_count}")

# ========== FONCTION PRINCIPALE ==========

def main():
    """Point d'entrée du programme"""
    
    # Création du carrefour avec 4 voies
    lanes = [
        Lane(
            name="Voie Nord",
            num_vehicles=12,
            wait_time=30.0,
            congestion_level=5,
            has_bus=False,
            has_emergency=False
        ),
        Lane(
            name="Voie Est",
            num_vehicles=15,
            wait_time=25.0,
            congestion_level=6,
            has_bus=True,
            has_emergency=False
        ),
        Lane(
            name="Voie Sud",
            num_vehicles=8,
            wait_time=40.0,
            congestion_level=4,
            has_bus=False,
            has_emergency=True
        ),
        Lane(
            name="Voie Ouest",
            num_vehicles=6,
            wait_time=15.0,
            congestion_level=3,
            has_bus=False,
            has_emergency=False
        )
    ]
    
    # Calcul initial des scores
    for lane in lanes:
        lane.calculate_score()
    
    # Création et lancement du système
    system = TrafficLightSystem(lanes)
    system.simulate(num_cycles=10, delay=1.5)
    
    # Statistiques finales
    print("\n📊 STATISTIQUES FINALES")
    print("-" * 50)
    total_wait = sum(lane.wait_time for lane in lanes)
    avg_wait = total_wait / len(lanes)
    print(f"Temps d'attente moyen: {avg_wait:.2f}s")
    print(f"Congestion moyenne: {sum(l.congestion_level for l in lanes) / len(lanes):.1f}/10")
    
    emergency_handled = sum(1 for lane in lanes if lane.name == "Voie Sud")
    print(f"Urgences traitées: {emergency_handled}")

if __name__ == "__main__":
    main()