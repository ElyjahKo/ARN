"""
setup_complet.py - Génère TOUS les fichiers nécessaires pour SUMO
Lance CE fichier en PREMIER avant tout !
"""
import os

def create_network():
    """Crée mon_reseau.net.xml"""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<net version="1.20" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">

    <location netOffset="0.00,0.00" convBoundary="-500.00,-500.00,500.00,500.00"/>

    <!-- Junctions -->
    <junction id="center" type="traffic_light" x="0.00" y="0.00" incLanes="NtoC_0 StoC_0 EtoC_0 WtoC_0" intLanes=":center_0_0 :center_1_0 :center_2_0 :center_3_0" shape="-3.20,0.00 3.20,0.00 3.20,-3.20 -3.20,-3.20">
        <request index="0" response="0000" foes="1100" cont="0"/>
        <request index="1" response="0000" foes="0100" cont="0"/>
        <request index="2" response="0011" foes="0011" cont="0"/>
        <request index="3" response="0010" foes="0010" cont="0"/>
    </junction>
    
    <junction id="north" type="dead_end" x="0.00" y="300.00" incLanes="CtoN_0" intLanes="" shape="0.00,300.00 3.20,300.00 0.00,300.00"/>
    <junction id="south" type="dead_end" x="0.00" y="-300.00" incLanes="CtoS_0" intLanes="" shape="0.00,-300.00 -3.20,-300.00 0.00,-300.00"/>
    <junction id="east" type="dead_end" x="300.00" y="0.00" incLanes="CtoE_0" intLanes="" shape="300.00,0.00 300.00,-3.20 300.00,0.00"/>
    <junction id="west" type="dead_end" x="-300.00" y="0.00" incLanes="CtoW_0" intLanes="" shape="-300.00,0.00 -300.00,3.20 -300.00,0.00"/>

    <!-- Edges -->
    <edge id="NtoC" from="north" to="center" priority="1">
        <lane id="NtoC_0" index="0" speed="13.89" length="300.00" shape="-1.60,300.00 -1.60,3.20"/>
    </edge>
    
    <edge id="CtoN" from="center" to="north" priority="1">
        <lane id="CtoN_0" index="0" speed="13.89" length="300.00" shape="1.60,3.20 1.60,300.00"/>
    </edge>
    
    <edge id="StoC" from="south" to="center" priority="1">
        <lane id="StoC_0" index="0" speed="13.89" length="300.00" shape="1.60,-300.00 1.60,-3.20"/>
    </edge>
    
    <edge id="CtoS" from="center" to="south" priority="1">
        <lane id="CtoS_0" index="0" speed="13.89" length="300.00" shape="-1.60,-3.20 -1.60,-300.00"/>
    </edge>
    
    <edge id="EtoC" from="east" to="center" priority="1">
        <lane id="EtoC_0" index="0" speed="13.89" length="300.00" shape="300.00,-1.60 3.20,-1.60"/>
    </edge>
    
    <edge id="CtoE" from="center" to="east" priority="1">
        <lane id="CtoE_0" index="0" speed="13.89" length="300.00" shape="3.20,1.60 300.00,1.60"/>
    </edge>
    
    <edge id="WtoC" from="west" to="center" priority="1">
        <lane id="WtoC_0" index="0" speed="13.89" length="300.00" shape="-300.00,1.60 -3.20,1.60"/>
    </edge>
    
    <edge id="CtoW" from="center" to="west" priority="1">
        <lane id="CtoW_0" index="0" speed="13.89" length="300.00" shape="-3.20,-1.60 -300.00,-1.60"/>
    </edge>

    <!-- Internal lanes -->
    <junction id=":center_0" type="internal">
        <lane id=":center_0_0" index="0" speed="13.89" length="6.40" shape="-1.60,3.20 -1.60,-3.20"/>
    </junction>
    <junction id=":center_1" type="internal">
        <lane id=":center_1_0" index="0" speed="13.89" length="6.40" shape="1.60,-3.20 1.60,3.20"/>
    </junction>
    <junction id=":center_2" type="internal">
        <lane id=":center_2_0" index="0" speed="13.89" length="6.40" shape="3.20,-1.60 -3.20,-1.60"/>
    </junction>
    <junction id=":center_3" type="internal">
        <lane id=":center_3_0" index="0" speed="13.89" length="6.40" shape="-3.20,1.60 3.20,1.60"/>
    </junction>

    <!-- Connections -->
    <connection from="NtoC" to="CtoS" fromLane="0" toLane="0" via=":center_0_0" tl="center" linkIndex="0" dir="s" state="O"/>
    <connection from="StoC" to="CtoN" fromLane="0" toLane="0" via=":center_1_0" tl="center" linkIndex="1" dir="s" state="O"/>
    <connection from="EtoC" to="CtoW" fromLane="0" toLane="0" via=":center_2_0" tl="center" linkIndex="2" dir="s" state="O"/>
    <connection from="WtoC" to="CtoE" fromLane="0" toLane="0" via=":center_3_0" tl="center" linkIndex="3" dir="s" state="O"/>

    <connection from=":center_0" to="CtoS" fromLane="0" toLane="0" dir="s" state="M"/>
    <connection from=":center_1" to="CtoN" fromLane="0" toLane="0" dir="s" state="M"/>
    <connection from=":center_2" to="CtoW" fromLane="0" toLane="0" dir="s" state="M"/>
    <connection from=":center_3" to="CtoE" fromLane="0" toLane="0" dir="s" state="M"/>

    <!-- Traffic Light Logic -->
    <tlLogic id="center" type="static" programID="0" offset="0">
        <phase duration="31" state="GGrr"/>
        <phase duration="4"  state="yyrr"/>
        <phase duration="31" state="rrGG"/>
        <phase duration="4"  state="rryy"/>
    </tlLogic>

</net>"""
    
    with open("mon_reseau.net.xml", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ mon_reseau.net.xml créé")


def create_routes():
    """Crée mes_routes.rou.xml"""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    
    <!-- Vehicle Types -->
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5.0" minGap="2.5" maxSpeed="13.89" guiShape="passenger" color="1,1,0"/>
    <vType id="bus" accel="1.2" decel="4.5" sigma="0.5" length="12.0" minGap="3.0" maxSpeed="12.0" guiShape="bus" color="0,1,0"/>
    <vType id="ambulance" accel="3.0" decel="5.0" sigma="0.3" length="6.0" minGap="2.0" maxSpeed="20.0" guiShape="emergency" color="1,0,0"/>

    <!-- Routes -->
    <route id="north_south" edges="NtoC CtoS"/>
    <route id="south_north" edges="StoC CtoN"/>
    <route id="east_west" edges="EtoC CtoW"/>
    <route id="west_east" edges="WtoC CtoE"/>

    <!-- Traffic Flows -->
    <flow id="flow_ns_cars" type="car" route="north_south" begin="0" end="3600" vehsPerHour="300"/>
    <flow id="flow_sn_cars" type="car" route="south_north" begin="0" end="3600" vehsPerHour="300"/>
    <flow id="flow_ew_cars" type="car" route="east_west" begin="0" end="3600" vehsPerHour="300"/>
    <flow id="flow_we_cars" type="car" route="west_east" begin="0" end="3600" vehsPerHour="300"/>

    <!-- Buses -->
    <flow id="flow_ns_bus" type="bus" route="north_south" begin="0" end="3600" vehsPerHour="30"/>
    <flow id="flow_ew_bus" type="bus" route="east_west" begin="0" end="3600" vehsPerHour="30"/>

    <!-- Emergency Vehicles -->
    <vehicle id="ambulance_1" type="ambulance" route="south_north" depart="10" color="1,0,0"/>
    <vehicle id="ambulance_2" type="ambulance" route="east_west" depart="150" color="1,0,0"/>
    <vehicle id="ambulance_3" type="ambulance" route="north_south" depart="300" color="1,0,0"/>
    
</routes>"""
    
    with open("mes_routes.rou.xml", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ mes_routes.rou.xml créé")


def create_config():
    """Crée mon_config.sumocfg"""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">

    <input>
        <net-file value="mon_reseau.net.xml"/>
        <route-files value="mes_routes.rou.xml"/>
    </input>

    <time>
        <begin value="0"/>
        <end value="3600"/>
        <step-length value="1"/>
    </time>

    <processing>
        <time-to-teleport value="-1"/>
        <max-depart-delay value="1"/>
        <ignore-route-errors value="true"/>
    </processing>

    <report>
        <verbose value="false"/>
        <no-step-log value="true"/>
        <no-warnings value="false"/>
    </report>

</configuration>"""
    
    with open("mon_config.sumocfg", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ mon_config.sumocfg créé")


def main():
    print("\n" + "="*70)
    print("🚀 CRÉATION DES FICHIERS SUMO")
    print("="*70 + "\n")
    
    create_network()
    create_routes()
    create_config()
    
    print("\n" + "="*70)
    print("✅ TOUS LES FICHIERS SONT CRÉÉS !")
    print("="*70)
    print("\n📋 Fichiers générés:")
    print("  ✓ mon_reseau.net.xml")
    print("  ✓ mes_routes.rou.xml")
    print("  ✓ mon_config.sumocfg")
    print("\n🎯 Prochaine étape:")
    print("  python arn_sumo_integration.py")
    print("\n💡 Pour tester SUMO seul:")
    print("  sumo-gui -c mon_config.sumocfg")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()