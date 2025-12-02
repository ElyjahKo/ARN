# ARN - Algorithme de Régulation de Nœuds routiers

Ce projet implémente un système de gestion intelligente des feux de circulation utilisant un arbre rouge-noir (ARN) pour optimiser le trafic routier. Il est intégré avec le simulateur de trafic SUMO (Simulation of Urban MObility).

## 🚦 Fonctionnalités

- Gestion intelligente des feux de circulation avec un arbre rouge-noir
- Simulation réaliste du trafic avec SUMO
- Priorisation des véhicules d'urgence et des bus
- Configuration modulaire des routes et des flux de véhicules
- Visualisation en temps réel du trafic

## 🛠️ Prérequis

- Python 3.7+
- SUMO (Simulation of Urban MObility)
- Bibliothèques Python requises :
  ```
  pip install traci
  ```

## 🚀 Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/ElyjahKo/ARN.git
   cd ARN
   ```

2. Assurez-vous que SUMO est installé et que la variable d'environnement `SUMO_HOME` est configurée.

## 🏃‍♂️ Utilisation

1. Lancer la simulation avec l'interface graphique :
   ```bash
   python arn_sumo_integration.py
   ```

2. Pour une simulation en mode console :
   ```bash
   python arn_sumo_integration.py --nogui
   ```

## 📁 Structure des fichiers

- `arn_sumo_integration.py` - Script principal d'intégration avec SUMO
- `setup_sumo.py` - Script de configuration initiale
- `mes_routes.rou.xml` - Définition des routes et flux de véhicules
- `mon_reseau_simple.net.xml` - Configuration du réseau routier simplifié
- `mon_config_simple.sumocfg` - Fichier de configuration principal de SUMO
- `mon_add.xml` - Éléments supplémentaires pour la visualisation

## 🎯 Fonctionnement

1. Le système lit les données de trafic en temps réel depuis SUMO
2. Il utilise un arbre rouge-noir pour déterminer la priorité des voies
3. Les feux de circulation sont ajustés en fonction de la densité du trafic
4. Les véhicules d'urgence et les bus reçoivent une priorité plus élevée

## 📊 Résultats

La simulation génère plusieurs fichiers de sortie :
- `tripinfo.xml` - Informations détaillées sur les trajets
- `detectors.out` - Données des détecteurs de véhicules
- `edge_data.xml` - Statistiques sur les tronçons routiers

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

Développé avec ❤️ par [Votre Nom] - [@ElyjahKo](https://github.com/ElyjahKo)
