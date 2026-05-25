import os
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER   = os.getenv("MQTT_BROKER", "34.57.103.138")
MQTT_PORT     = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER     = os.getenv("MQTT_USER", "iot_user")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "MadaIoT2025!")
INTERVALLE    = int(os.getenv("INTERVALLE_SECONDES", 30))

TB_URL = "http://34.57.103.138:8080"

ZONES = [
    {
        "id"           : "zone_antananarivo",
        "nom"          : "Antananarivo",
        "lat"          : -18.9101,
        "lon"          : 47.5362,
        "riviere"      : "Ikopa",
        "seuil_alerte" : 1.8,
        "seuil_danger" : 2.5,
        "base_niveau"  : 0.8,
        "base_pluie"   : 2.0,
        "tb_token"     : "m1IC2hWygMy636U5200W",
    },
    {
        "id"           : "zone_toamasina",
        "nom"          : "Toamasina",
        "lat"          : -18.1492,
        "lon"          : 49.4023,
        "riviere"      : "Ivondro",
        "seuil_alerte" : 2.0,
        "seuil_danger" : 3.0,
        "base_niveau"  : 1.1,
        "base_pluie"   : 5.0,
        "tb_token"     : "2DDjUpvXT23Slctb332U",
    },
    {
        "id"           : "zone_fianarantsoa",
        "nom"          : "Fianarantsoa",
        "lat"          : -21.4527,
        "lon"          : 47.0863,
        "riviere"      : "Matsiatra",
        "seuil_alerte" : 1.5,
        "seuil_danger" : 2.2,
        "base_niveau"  : 0.6,
        "base_pluie"   : 1.5,
        "tb_token"     : "0g5lHgpZpXVEJuUBTyHQ",
    },
    {
        "id"           : "zone_mahajanga",
        "nom"          : "Mahajanga",
        "lat"          : -15.7162,
        "lon"          : 46.3175,
        "riviere"      : "Betsiboka",
        "seuil_alerte" : 2.5,
        "seuil_danger" : 4.0,
        "base_niveau"  : 1.4,
        "base_pluie"   : 3.0,
        "tb_token"     : "WC3k0B9KqGCno5sWxWh1",
    },
    {
        "id"           : "zone_toliara",
        "nom"          : "Toliara",
        "lat"          : -23.3516,
        "lon"          : 43.6854,
        "riviere"      : "Fiherenana",
        "seuil_alerte" : 1.2,
        "seuil_danger" : 1.8,
        "base_niveau"  : 0.4,
        "base_pluie"   : 0.8,
        "tb_token"     : "nqO41HvAF6IrYE27jBFa",
    },
]