# arn_sumo_integration.py - VERSION FINALE CORRIGÉE
import random
import time
import sys
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict

try:
    import traci
except ImportError:
    print("❌ ERREUR: Module 'traci' non trouvé!")
    print("   Installe SUMO et ajoute-le au PYTHONPATH")
    print("   Ou installe via: pip install traci")
    sys.exit(1)

# =============== CONFIGURATION ===============
SUMO_BINARY = "sumo-gui"  # Change en "sumo" pour mode console
SUMO_CONFIG = "mon_config_simple.sumocfg"  # Utilisation de la configuration simplifiée
TLS_ID = "center"
CYCLE_DELAY = 3.0
SIM_STEPS_PER_CYCLE = 30

# =============== ARBRE ROUGE-NOIR ===============

class Color(Enum):
    RED = 0
    BLACK = 1

@dataclass
class Lane:
    name: str
    sumo_edge_id: str
    num_vehicles: int = 0
    wait_time: float = 0.0
    congestion_level: int = 0
    has_bus: bool = False
    has_emergency: bool = False
    priority_score: float = 0.0
    
    def calculate_score(self):
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

class RBNode:
    def __init__(self, priority_score: float, lane: Optional[Lane]):
        self.priority_score = priority_score
        self.lane = lane
        self.color = Color.RED
        self.left: Optional['RBNode'] = None
        self.right: Optional['RBNode'] = None
        self.parent: Optional['RBNode'] = None

class RedBlackTree:
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
    
    def clear(self):
        self.root = self.NIL

# =============== SYSTÈME DE GESTION ===============

class TrafficLightSystem:
    def __init__(self, lanes: List[Lane]):
        self.lanes = lanes
        self.rbt = RedBlackTree()
        self.current_green: Optional[Lane] = None
        self.cycle_count = 0
        self.edge_to_lane: Dict[str, Lane] = {
            lane.sumo_edge_id: lane for lane in lanes
        }
    
    def update_traffic_data(self):
        """Récupère les données en temps réel depuis SUMO"""
        for lane in self.lanes:
            try:
                # Données SUMO
                vcount = traci.edge.getLastStepVehicleNumber(lane.sumo_edge_id)
                waiting_time = traci.edge.getWaitingTime(lane.sumo_edge_id)
                halting = traci.edge.getLastStepHaltingNumber(lane.sumo_edge_id)
                
                lane.num_vehicles = int(vcount)
                lane.wait_time = waiting_time / max(1, vcount)
                lane.congestion_level = min(10, int((halting / max(1, vcount)) * 10))
                
                # Détection véhicules spéciaux
                lane.has_bus = False
                lane.has_emergency = False
                
                veh_ids = traci.edge.getLastStepVehicleIDs(lane.sumo_edge_id)
                for vid in veh_ids:
                    try:
                        vtype = traci.vehicle.getTypeID(vid)
                        if "bus" in vtype.lower():
                            lane.has_bus = True
                        if "ambulance" in vtype.lower() or "ambulance" in vid.lower():
                            lane.has_emergency = True
                    except:
                        pass
                
            except traci.exceptions.TraCIException as e:
                print(f"⚠️  TraCI error pour {lane.name}: {e}")
                pass
            except Exception as e:
                print(f"⚠️  Erreur inattendue pour {lane.name}: {e}")
                pass
            
            # Calcul du score
            lane.calculate_score()
    
    def rebuild_priority_tree(self):
        self.rbt.clear()
        for lane in self.lanes:
            self.rbt.insert(lane.priority_score, lane)
    
    def get_next_green_light(self) -> Optional[Lane]:
        max_node = self.rbt.find_maximum()
        return max_node.lane if max_node else None
    
    def display_status(self):
        print("\n" + "="*75)
        print(f"🚦 CYCLE #{self.cycle_count:03d} - Carrefour Intelligent (ARN)")
        print("="*75)
        
        sorted_lanes = sorted(self.lanes, key=lambda x: x.priority_score, reverse=True)
        
        for i, lane in enumerate(sorted_lanes, 1):
            status = "🟢 VERT " if lane == self.current_green else "🔴 ROUGE"
            icons = ""
            if lane.has_emergency:
                icons += " 🚑"
            if lane.has_bus:
                icons += " 🚌"
            
            print(f"{i}. {status} | {lane.name:12s} ({lane.sumo_edge_id}){icons}")
            print(f"   📊 Véhicules: {lane.num_vehicles:3d} | "
                  f"Attente: {lane.wait_time:6.1f}s | "
                  f"Congestion: {lane.congestion_level:2d}/10 | "
                  f"Score: {lane.priority_score:6.1f}")
        
        if self.current_green:
            print(f"\n✅ Voie prioritaire: {self.current_green.name}")
        
        print("="*75)
    
    def apply_green_to_sumo(self):
        """Applique la décision ARN aux feux SUMO"""
        if not self.current_green:
            print("⚠️  Aucune voie prioritaire sélectionnée")
            return
        
        try:
            # Méthode simplifiée: utiliser les phases prédéfinies
            target = self.current_green.sumo_edge_id
            
            if target in ["NtoC", "StoC"]:
                # Nord-Sud vert
                traci.trafficlight.setPhase(TLS_ID, 0)
                phase_name = "Nord-Sud"
            else:
                # Est-Ouest vert
                traci.trafficlight.setPhase(TLS_ID, 2)
                phase_name = "Est-Ouest"
            
            print(f"🚦 Feux appliqués: Phase {phase_name}")
            
        except traci.exceptions.TraCIException as e:
            print(f"❌ Erreur TraCI lors de l'application des feux: {e}")
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
    
    def run_cycle(self):
        self.cycle_count += 1
        self.update_traffic_data()
        self.rebuild_priority_tree()
        self.current_green = self.get_next_green_light()
        self.apply_green_to_sumo()
        self.display_status()

# =============== MAIN ===============

def check_files():
    """Vérifie que les fichiers nécessaires existent"""
    import os
    required = ["mon_reseau.net.xml", "mes_routes.rou.xml", "mon_config.sumocfg"]
    missing = [f for f in required if not os.path.exists(f)]
    
    if missing:
        print("❌ FICHIERS MANQUANTS:")
        for f in missing:
            print(f"   - {f}")
        print("\n💡 Lance d'abord: python setup_complet.py")
        return False
    return True

def main():
    print("\n" + "="*75)
    print("🚀 SYSTÈME DE GESTION INTELLIGENT DES FEUX (ARN + SUMO)")
    print("="*75 + "\n")
    
    # Vérifications préliminaires
    if not check_files():
        sys.exit(1)
    
    # Création des voies
    lanes = [
        Lane(name="Voie Nord",  sumo_edge_id="NtoC"),
        Lane(name="Voie Sud",   sumo_edge_id="StoC"),
        Lane(name="Voie Est",   sumo_edge_id="EtoC"),
        Lane(name="Voie Ouest", sumo_edge_id="WtoC"),
    ]
    
    system = TrafficLightSystem(lanes)
    
    # Démarrage SUMO
    print("🔄 Connexion à SUMO...")
    try:
        sumo_cmd = [SUMO_BINARY, "-c", SUMO_CONFIG, "--start", "--quit-on-end"]
        traci.start(sumo_cmd)
        print("✅ SUMO connecté avec succès!\n")
    except Exception as e:
        print(f"❌ Impossible de démarrer SUMO: {e}")
        print("\n💡 Vérifications:")
        print("   1. SUMO est installé? → sumo --version")
        print("   2. sumo-gui est dans le PATH?")
        print("   3. Change SUMO_BINARY en 'sumo' si pas de GUI")
        sys.exit(1)
    
    # Boucle principale
    print("🎬 Simulation démarrée...\n")
    
    try:
        step = 0
        max_steps = 3600
        
        while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
            # Avance la simulation SUMO
            for _ in range(SIM_STEPS_PER_CYCLE):
                traci.simulationStep()
                step += 1
            
            # Exécute un cycle de décision ARN
            system.run_cycle()
            
            # Pause pour observer
            time.sleep(CYCLE_DELAY)
        
        print("\n✅ Simulation terminée (fin naturelle)")
        
    except KeyboardInterrupt:
        print("\n\n⛔ Simulation interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ ERREUR durant la simulation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Fermeture propre
        try:
            traci.close()
        except:
            pass
        
        # Statistiques finales
        print("\n" + "="*75)
        print("📊 STATISTIQUES FINALES")
        print("="*75)
        print(f"Cycles ARN exécutés: {system.cycle_count}")
        
        if lanes:
            total_wait = sum(l.wait_time for l in lanes)
            avg_wait = total_wait / len(lanes)
            avg_cong = sum(l.congestion_level for l in lanes) / len(lanes)
            
            print(f"Temps d'attente moyen: {avg_wait:.2f}s")
            print(f"Congestion moyenne: {avg_cong:.1f}/10")
            
            print("\n📋 État final des voies:")
            for lane in sorted(lanes, key=lambda x: x.priority_score, reverse=True):
                print(f"  • {lane.name:12s}: {lane.num_vehicles:3d} véhicules, "
                      f"score {lane.priority_score:.1f}")
        
        print("="*75)
        print("👋 Merci d'avoir utilisé le système!")
        print("="*75 + "\n")

if __name__ == "__main__":
    main()