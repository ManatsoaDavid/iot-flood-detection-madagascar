import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import collections

# Buffer circulaire des 48 dernières mesures par zone
historique = collections.defaultdict(lambda: collections.deque(maxlen=48))

def ajouter_mesure(zone_id, mesures):
    """Ajoute une mesure à l'historique de la zone."""
    historique[zone_id].append({
        "niveau_eau"   : mesures["niveau_eau"],
        "pluviometrie" : mesures["pluviometrie"],
        "debit_riviere": mesures["debit_riviere"],
        "humidite"     : mesures["humidite"],
    })

def predire_risque_24h(zone_id):
    """
    Prédit le niveau d'eau futur via régression linéaire.
    Retourne (niveau_predit, risque_24h_pct) ou (None, None)
    si données insuffisantes.
    """
    hist = list(historique[zone_id])

    if len(hist) < 10:
        return None, None

    # Features : [niveau, pluie, débit, humidité]
    X = np.array([[
        h["niveau_eau"],
        h["pluviometrie"],
        h["debit_riviere"],
        h["humidite"]
    ] for h in hist])

    # Target : niveau_eau décalé (prédire t+1 depuis t)
    y = np.array([h["niveau_eau"] for h in hist])

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LinearRegression()
    model.fit(X_scaled[:-1], y[1:])

    # Prédire depuis la dernière mesure
    derniere   = X_scaled[-1].reshape(1, -1)
    prediction = model.predict(derniere)[0]
    prediction = max(0, round(float(prediction), 3))

    # Score de risque 0-100%
    risque_24h = min(100, max(0, round((prediction / 2.5) * 100, 1)))

    return prediction, risque_24h