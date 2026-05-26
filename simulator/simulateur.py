import paho.mqtt.client as mqtt
import json, time, random, math, ssl
import numpy as np
import requests
from datetime import datetime
from config import ZONES, MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, INTERVALLE, TB_URL
from prediction_ml import ajouter_mesure, predire_risque_24h

# ── Connexion MQTT over TLS ──────────────────────────────────
client = mqtt.Client(client_id="simulateur_mada_v1")
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
client.tls_set_context(ssl_context)

def on_connect(c, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Connecté au broker {MQTT_BROKER}:{MQTT_PORT} (TLS)")
    else:
        print(f"[MQTT] Erreur connexion — code {rc}")

client.on_connect = on_connect
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# ── Envoi vers ThingsBoard ───────────────────────────────────
def envoyer_thingsboard(mesures, token):
    url     = f"{TB_URL}/api/v1/{token}/telemetry"
    payload = {
        "niveau_eau"        : mesures["niveau_eau"],
        "pluviometrie"      : mesures["pluviometrie"],
        "debit_riviere"     : mesures["debit_riviere"],
        "temperature"       : mesures["temperature"],
        "humidite"          : mesures["humidite"],
        "statut"            : mesures["statut"],
        "risque_inondation" : mesures["risque_inondation"],
        "latitude"          : mesures["latitude"],
        "longitude"         : mesures["longitude"],
        "niveau_predit_24h" : mesures.get("niveau_predit_24h"),
        "risque_24h_pct"    : mesures.get("risque_24h_pct"),
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"[TB] Erreur: {e}")
        return False

# ── Génération de données réalistes ─────────────────────────
def generer_mesures(zone):
    heure = datetime.now().hour
    mois  = datetime.now().month

    facteur_heure  = 1.0 + 0.3 * math.sin((heure - 14) * math.pi / 12)
    facteur_saison = 1.8 if mois in [11, 12, 1, 2, 3, 4] else 0.6

    pluie = max(0, (
        zone["base_pluie"]
        * facteur_heure
        * facteur_saison
        + np.random.normal(0, 0.8)
    ))

    variation = pluie * 0.15 + np.random.normal(0, 0.04)
    niveau    = max(0, zone["base_niveau"] + variation + np.random.normal(0, 0.05))

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

    score_niveau = min(100, (niveau / zone["seuil_danger"]) * 60)
    score_pluie  = min(40,  (pluie / 20) * 40)
    risque       = round(score_niveau + score_pluie)

    return {
        "zone_id"           : zone["id"],
        "zone_nom"          : zone["nom"],
        "latitude"          : zone["lat"],
        "longitude"         : zone["lon"],
        "riviere"           : zone["riviere"],
        "timestamp"         : datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "niveau_eau"        : round(niveau, 3),
        "pluviometrie"      : round(pluie, 2),
        "debit_riviere"     : round(debit, 1),
        "temperature"       : temp,
        "humidite"          : round(humidite, 1),
        "statut"            : statut,
        "risque_inondation" : risque,
        "seuil_alerte"      : zone["seuil_alerte"],
        "seuil_danger"      : zone["seuil_danger"],
    }

# ── Boucle principale ────────────────────────────────────────
print("=" * 60)
print("  IoT Flood Detection — Madagascar")
print("  Démarrage simulation + ML prédictif")
print("=" * 60)

while True:
    for zone in ZONES:
        mesures = generer_mesures(zone)

        # Ajouter à l'historique ML
        ajouter_mesure(zone["id"], mesures)

        # Prédiction ML
        niveau_predit, risque_24h = predire_risque_24h(zone["id"])
        mesures["niveau_predit_24h"] = niveau_predit
        mesures["risque_24h_pct"]    = risque_24h

        # Envoi MQTT → Node-RED
        topic   = f"mada/inondation/{zone['id']}/data"
        client.publish(topic, json.dumps(mesures), qos=1)

        # Envoi HTTP → ThingsBoard
        tb_ok     = envoyer_thingsboard(mesures, zone["tb_token"])
        tb_status = "✓" if tb_ok else "✗"

        # Affichage
        predit_str = f"{niveau_predit:.3f}m" if niveau_predit else "calcul..."
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"{zone['nom']:15} | "
            f"Niveau: {mesures['niveau_eau']:.3f}m | "
            f"Statut: {mesures['statut']:6} | "
            f"Risque: {mesures['risque_inondation']:3}% | "
            f"Prédit: {predit_str:9} | "
            f"TB:{tb_status}"
        )

    print("-" * 60)
    time.sleep(INTERVALLE)