import paho.mqtt.client as mqtt
import json, time, random, math
import numpy as np
from datetime import datetime
from config import ZONES, MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, INTERVALLE

# ── Connexion MQTT ───────────────────────────────────────────
client = mqtt.Client(client_id="simulateur_mada_v1")
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

def on_connect(c, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Connecté au broker {MQTT_BROKER}:{MQTT_PORT}")
    else:
        print(f"[MQTT] Erreur connexion — code {rc}")

def on_publish(c, userdata, mid):
    pass

client.on_connect = on_connect
client.on_publish  = on_publish
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# ── Génération de données réalistes ─────────────────────────
def generer_mesures(zone):
    heure = datetime.now().hour
    mois  = datetime.now().month

    facteur_heure   = 1.0 + 0.3 * math.sin((heure - 14) * math.pi / 12)
    facteur_saison  = 1.8 if mois in [11, 12, 1, 2, 3, 4] else 0.6

    pluie = max(0, (
        zone["base_pluie"]
        * facteur_heure
        * facteur_saison
        + np.random.normal(0, 0.8)
    ))

    variation = pluie * 0.15 + np.random.normal(0, 0.04)
    niveau    = max(0, zone["base_niveau"] + variation + np.random.normal(0, 0.05))

    # Simulation cyclone — 1% de chance
    if random.random() < 0.01:
        niveau *= random.uniform(2.5, 4.0)
        pluie  *= random.uniform(5.0, 10.0)
        print(f"[CYCLONE] Simulé sur {zone['nom']} !")

    debit    = max(0, niveau * 85 + np.random.normal(0, 5))
    temp     = round(26 + np.random.normal(0, 2), 1)
    humidite = min(100, max(40, 75 + pluie * 2 + np.random.normal(0, 3)))

    statut = (
        "DANGER" if niveau >= zone["seuil_danger"] else
        "ALERTE" if niveau >= zone["seuil_alerte"] else
        "NORMAL"
    )

    return {
        "zone_id"        : zone["id"],
        "zone_nom"       : zone["nom"],
        "latitude"       : zone["lat"],
        "longitude"      : zone["lon"],
        "riviere"        : zone["riviere"],
        "timestamp"      : datetime.utcnow().isoformat() + "Z",
        "niveau_eau"     : round(niveau, 3),
        "pluviometrie"   : round(pluie, 2),
        "debit_riviere"  : round(debit, 1),
        "temperature"    : temp,
        "humidite"       : round(humidite, 1),
        "statut"         : statut,
        "seuil_alerte"   : zone["seuil_alerte"],
        "seuil_danger"   : zone["seuil_danger"],
    }

# ── Boucle principale ────────────────────────────────────────
print("=" * 55)
print("  IoT Flood Detection — Madagascar")
print("  Démarrage de la simulation...")
print("=" * 55)

while True:
    for zone in ZONES:
        mesures = generer_mesures(zone)
        topic   = f"mada/inondation/{zone['id']}/data"
        payload = json.dumps(mesures)

        result = client.publish(topic, payload, qos=1)

        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"{zone['nom']:15} | "
            f"Niveau: {mesures['niveau_eau']:.3f}m | "
            f"Pluie: {mesures['pluviometrie']:.1f}mm/h | "
            f"Statut: {mesures['statut']}"
        )

    print("-" * 55)
    time.sleep(INTERVALLE)