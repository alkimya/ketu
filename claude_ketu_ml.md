# Conversation Claude 2025-12-08

Loc : Pour étudier des cycles, avec des séries temporellesv mettre en relations des courbes de prix d'une crypto comme Solana avec des cycles d'aspects planétaires, quelles sont les meilleures librairies Python de ML, Deep Learning ?

Claude : Pour étudier les corrélations entre les cycles de prix des cryptomonnaies et les aspects planétaires, voici les meilleures librairies Python selon différents besoins :

## Librairies de Machine Learning / Deep Learning

**Pour l'analyse de séries temporelles :**

- **Prophet** (Meta) : excellent pour détecter des cycles et tendances, gère automatiquement la saisonnalité
- **statsmodels** : pour les modèles classiques (ARIMA, SARIMA, analyse spectrale)
- **TensorFlow / Keras** : pour construire des réseaux LSTM, GRU adaptés aux séries temporelles
- **PyTorch** : plus flexible pour des architectures personnalisées
- **sktime** : spécialisé dans le ML pour séries temporelles, avec de nombreux algorithmes

**Pour la détection de cycles et corrélations :**

- **scipy** : transformée de Fourier (FFT), corrélations croisées, analyse spectrale
- **PyWavelets** : analyse par ondelettes pour détecter des cycles à différentes échelles
- **hurst** : pour analyser la persistance des séries

## Librairies pour les données astronomiques

- **ephem** ou **skyfield** : calcul précis des positions planétaires et aspects
- **astropy** : pour des calculs astronomiques plus avancés

## Approche recommandée

Pour votre cas spécifique, je suggérerais de commencer avec :

1. **Extraction des données** : `ccxt` pour les prix Solana, `ephem` pour les aspects planétaires
2. **Prétraitement** : `pandas` + `numpy` pour aligner les séries temporelles
3. **Analyse exploratoire** : scipy.signal pour détecter les périodicités, corrélations croisées
4. **Modélisation** :
    - **Prophet** pour une première approche (peut intégrer des régresseurs externes)
    - **LSTM/GRU** avec TensorFlow/PyTorch pour capturer des dépendances complexes
    - **XGBoost/LightGBM** avec features engineered des aspects planétaires

Voulez-vous que je vous montre un exemple de code pour commencer l'analyse ?

Loc : Pour l'astro, je développe ma propre librairie `ketu` <https://github.com/alkimya/ketu>, bientôt dans une version pure numpy. Cette librairie permet de générer et calculer les aspects entre des planètes dans le zodiaque. Comment mettre en place un framework permettant de mettre en place des analyses de corrélations, format de données ?

Claude : Excellent ! Votre librairie `ketu` est très bien conçue. Pour mettre en place un framework d'analyse de corrélations entre vos aspects planétaires et les prix crypto, voici une architecture optimale :

## Structure de données recommandée

### 1. Format de données unifié

```python
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Structure pour les aspects planétaires

class AstronomicalData:
    """
    DataFrame avec index temporel (datetime) et colonnes :
    - timestamp: datetime UTC
    - julian_day: float
    - planet1_id: int
    - planet2_id: int
    - aspect_type: int (0-6 pour les 7 aspects)
    - orb: float (degrés)
    - aspect_strength: float (1 - abs(orb)/max_orb)
    """

    @staticmethod
    def generate_aspects_timeseries(start_date, end_date, freq='1H'):
        """Génère une série temporelle d'aspects avec ketu"""
        dates = pd.date_range(start_date, end_date, freq=freq)
        
        aspects_list = []
        for dt in dates:
            from zoneinfo import ZoneInfo
            import ketu
            
            dt_utc = dt.tz_localize('UTC')
            jday = ketu.utc_to_julian(dt_utc)
            aspects = ketu.calculate_aspects(jday)
            
            for body1, body2, aspect_idx, orb in aspects:
                # Calculer la force de l'aspect (inversement proportionnel à l'orbe)
                max_orb = ketu.calculate_orb(body1, body2)
                strength = 1 - (abs(orb) / max_orb)
                
                aspects_list.append({
                    'timestamp': dt_utc,
                    'julian_day': jday,
                    'planet1': body1,
                    'planet2': body2,
                    'aspect': aspect_idx,
                    'orb': orb,
                    'strength': strength,
                    'planet1_name': ketu.body_name(body1).decode(),
                    'planet2_name': ketu.body_name(body2).decode(),
                    'aspect_name': ketu.aspects['name'][aspect_idx].decode()
                })
        
        return pd.DataFrame(aspects_list)

# Structure pour les prix crypto

class CryptoData:
    """
    DataFrame avec index temporel et colonnes :
    - timestamp: datetime UTC
    - open, high, low, close: float
    - volume: float
    - returns: float (log returns)
    """

    @staticmethod
    def fetch_solana_data(start_date, end_date, interval='1h'):
        """Récupère les données Solana via ccxt"""
        import ccxt
        
        exchange = ccxt.binance()
        since = exchange.parse8601(start_date.isoformat())
        
        ohlcv = exchange.fetch_ohlcv('SOL/USDT', interval, since)
        
        df = pd.DataFrame(
            ohlcv, 
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df['returns'] = np.log(df['close'] / df['close'].shift(1))
        
        return df.set_index('timestamp')
```

### 2. Pipeline d'alignement des données

```python
class DataAligner:
    """Aligne les séries temporelles astro et crypto"""

    @staticmethod
    def align_datasets(astro_df, crypto_df, method='nearest'):
        """
        Aligne les deux DataFrames sur un index temporel commun
        
        Args:
            astro_df: DataFrame des aspects
            crypto_df: DataFrame des prix
            method: 'nearest', 'forward', 'backward'
        """
        # Réindexer sur l'intersection des périodes
        common_start = max(astro_df['timestamp'].min(), crypto_df.index.min())
        common_end = min(astro_df['timestamp'].max(), crypto_df.index.max())
        
        # Créer un index unifié
        unified_index = pd.date_range(
            common_start, 
            common_end, 
            freq='1H'
        )
        
        # Aligner crypto_df
        crypto_aligned = crypto_df.reindex(unified_index, method=method)
        
        return unified_index, crypto_aligned, astro_df
    
    @staticmethod
    def create_feature_matrix(astro_df, unified_index):
        """
        Transforme les aspects en matrice de features
        Chaque colonne = un type d'aspect entre deux planètes
        """
        # Créer une matrice sparse pour chaque combinaison planète-aspect
        features = pd.DataFrame(index=unified_index)
        
        # Grouper par type d'aspect et paire de planètes
        for (p1, p2, asp), group in astro_df.groupby(['planet1', 'planet2', 'aspect']):
            col_name = f"{ketu.body_name(p1).decode()}_{ketu.body_name(p2).decode()}_{ketu.aspects['name'][asp].decode()}"
            
            # Pour chaque timestamp, prendre la force de l'aspect
            aspect_series = group.set_index('timestamp')['strength']
            features[col_name] = aspect_series.reindex(unified_index, fill_value=0)
        
        return features
```

### 3. Framework d'analyse de corrélation

```python
class CorrelationAnalyzer:
    """Analyse les corrélations aspects-prix"""

    def __init__(self, astro_features, crypto_data):
        self.astro = astro_features
        self.crypto = crypto_data
        
    def compute_correlations(self, target='returns', lags=range(-24, 25)):
        """
        Calcule les corrélations croisées pour différents lags
        
        Args:
            target: colonne crypto à analyser ('returns', 'close', etc.)
            lags: liste de décalages temporels (en heures)
        """
        results = []
        
        for col in self.astro.columns:
            for lag in lags:
                if lag < 0:
                    corr = self.astro[col].shift(-lag).corr(self.crypto[target])
                else:
                    corr = self.astro[col].corr(self.crypto[target].shift(-lag))
                
                results.append({
                    'aspect': col,
                    'lag_hours': lag,
                    'correlation': corr
                })
        
        return pd.DataFrame(results)
    
    def statistical_significance(self, correlations_df, alpha=0.05):
        """Teste la significativité statistique des corrélations"""
        from scipy import stats
        
        n = len(self.astro)
        
        # Test t pour la corrélation
        correlations_df['t_stat'] = correlations_df['correlation'] * np.sqrt((n-2) / (1 - correlations_df['correlation']**2))
        correlations_df['p_value'] = 2 * (1 - stats.t.cdf(np.abs(correlations_df['t_stat']), n-2))
        correlations_df['significant'] = correlations_df['p_value'] < alpha
        
        return correlations_df
    
    def spectral_analysis(self):
        """Analyse spectrale pour détecter les périodicités communes"""
        from scipy import signal
        
        results = {}
        
        # FFT sur les returns crypto
        freqs_crypto, psd_crypto = signal.periodogram(
            self.crypto['returns'].dropna(),
            fs=1  # 1 échantillon par heure
        )
        
        # FFT sur chaque aspect
        for col in self.astro.columns:
            freqs_astro, psd_astro = signal.periodogram(
                self.astro[col].fillna(0),
                fs=1
            )
            
            # Corrélation entre les spectres
            spec_corr = np.corrcoef(psd_crypto[:len(psd_astro)], psd_astro)[0, 1]
            
            results[col] = {
                'spectral_correlation': spec_corr,
                'dominant_freq': freqs_astro[np.argmax(psd_astro)],
                'period_hours': 1 / freqs_astro[np.argmax(psd_astro)] if freqs_astro[np.argmax(psd_astro)] > 0 else np.inf
            }
        
        return pd.DataFrame(results).T
```

### 4. Exemple d'utilisation complète

```python
# Générer les données

start = datetime(2024, 1, 1, tzinfo=ZoneInfo('UTC'))
end = datetime(2024, 6, 1, tzinfo=ZoneInfo('UTC'))

# 1. Aspects astrologiques

astro_df = AstronomicalData.generate_aspects_timeseries(start, end, freq='1H')

# 2. Prix Solana

crypto_df = CryptoData.fetch_solana_data(start, end, interval='1h')

# 3. Alignement

unified_idx, crypto_aligned, astro_aligned = DataAligner.align_datasets(astro_df, crypto_df)

# 4. Création de la matrice de features

astro_features = DataAligner.create_feature_matrix(astro_aligned, unified_idx)

# 5. Analyse de corrélation

analyzer = CorrelationAnalyzer(astro_features, crypto_aligned)
correlations = analyzer.compute_correlations(target='returns', lags=range(-48, 49))
correlations_sig = analyzer.statistical_significance(correlations)

# 6. Résultats significatifs

significant = correlations_sig[correlations_sig['significant']].sort_values('correlation', key=abs, ascending=False)
print(significant.head(20))

# 7. Analyse spectrale

spectral = analyzer.spectral_analysis()
print(spectral.sort_values('spectral_correlation', ascending=False))
```

### 5. Format de persistance

```python
# Sauvegarder en format efficace

astro_features.to_parquet('astro_features.parquet')
crypto_aligned.to_parquet('crypto_data.parquet')
correlations_sig.to_parquet('correlations.parquet')

# Format HDF5 pour de gros volumes

with pd.HDFStore('analysis.h5', mode='w') as store:
    store['astro'] = astro_features
    store['crypto'] = crypto_aligned
    store['correlations'] = correlations_sig
```

Voulez-vous que je développe un aspect particulier, comme l'intégration avec des modèles ML ou la visualisation des résultats ?

Loc : Tu dis :

```python
class AstronomicalData:
    """
    DataFrame avec index temporel (datetime) et colonnes :
    - timestamp: datetime UTC
    - julian_day: float
    - planet1_id: int
    - planet2_id: int
    - aspect_type: int (0-6 pour les 7 aspects)
    - orb: float (degrés)
    - aspect_strength: float (1 - abs(orb)/max_orb)
```

ok mais je ne sais pas trop où je suis dans le cycle d'aspect même si j'ai `aspect_type` et la force de l'aspect avec `aspect_strength`, par exemple si j'ai un square, est-ce celui entre la conjonction et l'opposition ou celui entre l'opposition et la conjonction, est-ce que l'aspect est appliquant ou séparant. Comment capturer le cycle, le mouvement ?

Claude : Excellente question ! Vous avez raison, pour capturer la dynamique du cycle, il faut enrichir les données avec des informations sur la **direction** et la **phase** du cycle. Voici une structure améliorée :

## Structure de données enrichie pour capturer le mouvement cyclique

```python
import numpy as np
import pandas as pd
from enum import Enum

class AspectPhase(Enum):
    """Phase du cycle aspect"""
    APPLYING = "applying"      # Planètes se rapprochent de l'aspect exact
    EXACT = "exact"            # Aspect exact (orbe minimal)
    SEPARATING = "separating"  # Planètes s'éloignent de l'aspect exact

class CycleQuadrant(Enum):
    """Quadrant du cycle planétaire (0° -> 360°)"""
    WAXING_SQUARE = 1      # 0° -> 90° (conjonction vers carré croissant)
    WAXING_TRINE = 2       # 90° -> 180° (carré croissant vers opposition)
    WANING_TRINE = 3       # 180° -> 270° (opposition vers carré décroissant)
    WANING_SQUARE = 4      # 270° -> 360° (carré décroissant vers conjonction)

class AstronomicalData:
    """
    DataFrame enrichi avec informations cycliques :
    - timestamp: datetime UTC
    - julian_day: float
    - planet1_id, planet2_id: int
    - aspect_type: int (0-6)
    - orb: float (degrés)
    - aspect_strength: float

    ### NOUVEAU : Informations cycliques ###
    - angular_separation: float (0-360°) distance angulaire entre les planètes
    - phase: str ('applying', 'exact', 'separating')
    - cycle_quadrant: int (1-4)
    - cycle_progress: float (0-1) progression dans le cycle complet
    - relative_velocity: float (vitesse relative en °/jour)
    - days_to_exact: float (jours avant/après aspect exact, négatif=passé)
    - cycle_direction: str ('waxing', 'waning')
    """
    
    @staticmethod
    def calculate_angular_separation(long1, long2):
        """
        Calcule la séparation angulaire entre deux longitudes
        Retourne toujours un angle entre 0° et 360°
        """
        diff = (long2 - long1) % 360
        return diff
    
    @staticmethod
    def get_cycle_info(angular_sep):
        """
        Détermine le quadrant et la direction du cycle
        
        Returns:
            quadrant: int (1-4)
            direction: str ('waxing' ou 'waning')
            progress: float (0-1)
        """
        if 0 <= angular_sep < 90:
            return 1, 'waxing', angular_sep / 360
        elif 90 <= angular_sep < 180:
            return 2, 'waxing', angular_sep / 360
        elif 180 <= angular_sep < 270:
            return 3, 'waning', angular_sep / 360
        else:  # 270-360
            return 4, 'waning', angular_sep / 360
    
    @staticmethod
    def determine_phase(orb, orb_prev, orb_threshold=0.1):
        """
        Détermine si l'aspect est appliquant, exact ou séparant
        
        Args:
            orb: orbe actuel
            orb_prev: orbe précédent
            orb_threshold: seuil pour considérer l'aspect comme exact
        """
        if abs(orb) <= orb_threshold:
            return AspectPhase.EXACT.value
        elif abs(orb) < abs(orb_prev):
            return AspectPhase.APPLYING.value
        else:
            return AspectPhase.SEPARATING.value
    
    @staticmethod
    def estimate_days_to_exact(orb, relative_velocity):
        """
        Estime le nombre de jours avant l'aspect exact
        Négatif = aspect passé, Positif = aspect à venir
        """
        if abs(relative_velocity) < 0.001:
            return np.nan
        
        days = -orb / relative_velocity
        return days
    
    @staticmethod
    def generate_aspects_timeseries(start_date, end_date, freq='1H'):
        """Génère une série temporelle d'aspects enrichie"""
        from zoneinfo import ZoneInfo
        import ketu
        
        dates = pd.date_range(start_date, end_date, freq=freq)
        aspects_list = []
        
        # Cache pour les positions précédentes
        prev_positions = {}
        prev_aspects = {}
        
        for i, dt in enumerate(dates):
            dt_utc = dt.tz_localize('UTC') if dt.tz is None else dt
            jday = ketu.utc_to_julian(dt_utc)
            
            # Calculer les positions de toutes les planètes
            positions = {}
            velocities = {}
            for body_id in range(10):  # 0-9 pour les 10 corps principaux
                positions[body_id] = ketu.long(jday, body_id)
                
                # Calculer la vitesse (position actuelle - position précédente)
                if body_id in prev_positions:
                    dt_hours = (dt_utc - dates[i-1]).total_seconds() / 3600
                    velocities[body_id] = (positions[body_id] - prev_positions[body_id]) / (dt_hours / 24)
                else:
                    velocities[body_id] = 0
            
            # Détecter les aspects
            aspects = ketu.calculate_aspects(jday)
            
            for body1, body2, aspect_idx, orb in aspects:
                # Calculer la séparation angulaire
                long1 = positions[body1]
                long2 = positions[body2]
                angular_sep = AstronomicalData.calculate_angular_separation(long1, long2)
                
                # Infos sur le cycle
                quadrant, direction, progress = AstronomicalData.get_cycle_info(angular_sep)
                
                # Vitesse relative
                rel_velocity = velocities.get(body2, 0) - velocities.get(body1, 0)
                
                # Phase de l'aspect (appliquant/séparant)
                aspect_key = (body1, body2, aspect_idx)
                if aspect_key in prev_aspects:
                    orb_prev = prev_aspects[aspect_key]
                    phase = AstronomicalData.determine_phase(orb, orb_prev)
                else:
                    phase = AspectPhase.APPLYING.value  # Défaut pour le premier point
                
                prev_aspects[aspect_key] = orb
                
                # Jours avant aspect exact
                days_to_exact = AstronomicalData.estimate_days_to_exact(orb, rel_velocity)
                
                # Force de l'aspect
                max_orb = ketu.calculate_orb(body1, body2)
                strength = 1 - (abs(orb) / max_orb)
                
                aspects_list.append({
                    'timestamp': dt_utc,
                    'julian_day': jday,
                    'planet1': body1,
                    'planet2': body2,
                    'aspect': aspect_idx,
                    'orb': orb,
                    'strength': strength,
                    
                    # Informations cycliques
                    'angular_separation': angular_sep,
                    'phase': phase,
                    'cycle_quadrant': quadrant,
                    'cycle_direction': direction,
                    'cycle_progress': progress,
                    'relative_velocity': rel_velocity,
                    'days_to_exact': days_to_exact,
                    
                    # Noms lisibles
                    'planet1_name': ketu.body_name(body1).decode(),
                    'planet2_name': ketu.body_name(body2).decode(),
                    'aspect_name': ketu.aspects['name'][aspect_idx].decode()
                })
            
            # Sauvegarder les positions pour le prochain tour
            prev_positions = positions.copy()
        
        return pd.DataFrame(aspects_list)
```

## Création de features enrichies pour le ML

```python
class EnrichedFeatureExtractor:
    """Extrait des features capturant le mouvement cyclique"""

    @staticmethod
    def create_cyclic_features(astro_df, unified_index):
        """
        Crée des features qui capturent la dynamique cyclique
        """
        features = pd.DataFrame(index=unified_index)
        
        for (p1, p2, asp), group in astro_df.groupby(['planet1', 'planet2', 'aspect']):
            base_name = f"{group.iloc[0]['planet1_name']}_{group.iloc[0]['planet2_name']}_{group.iloc[0]['aspect_name']}"
            
            group_indexed = group.set_index('timestamp')
            
            # 1. Force brute de l'aspect
            features[f"{base_name}_strength"] = group_indexed['strength'].reindex(unified_index, fill_value=0)
            
            # 2. Phase (appliquant = 1, exact = 0, séparant = -1)
            phase_map = {'applying': 1, 'exact': 0, 'separating': -1}
            features[f"{base_name}_phase"] = group_indexed['phase'].map(phase_map).reindex(unified_index, fill_value=0)
            
            # 3. Direction du cycle (croissant = 1, décroissant = -1)
            direction_map = {'waxing': 1, 'waning': -1}
            features[f"{base_name}_direction"] = group_indexed['cycle_direction'].map(direction_map).reindex(unified_index, fill_value=0)
            
            # 4. Progression dans le cycle (0-1)
            features[f"{base_name}_cycle_progress"] = group_indexed['cycle_progress'].reindex(unified_index, fill_value=0)
            
            # 5. Vitesse relative (capture l'accélération/décélération)
            features[f"{base_name}_velocity"] = group_indexed['relative_velocity'].reindex(unified_index, fill_value=0)
            
            # 6. Proximité de l'aspect exact (sigmoïde inversée)
            features[f"{base_name}_exactness"] = np.exp(-abs(group_indexed['days_to_exact'])).reindex(unified_index, fill_value=0)
            
            # 7. Quadrant du cycle (encodage cyclique)
            # Utiliser sin/cos pour préserver la continuité cyclique
            quadrant_angle = (group_indexed['cycle_quadrant'] - 1) * np.pi / 2
            features[f"{base_name}_quadrant_sin"] = np.sin(quadrant_angle).reindex(unified_index, fill_value=0)
            features[f"{base_name}_quadrant_cos"] = np.cos(quadrant_angle).reindex(unified_index, fill_value=0)
        
        return features
    
    @staticmethod
    def create_interaction_features(features_df):
        """
        Crée des features d'interaction capturant les combinaisons d'aspects
        Par exemple : Jupiter-Saturne carré appliquant + Mars-Pluton opposition séparant
        """
        interaction_features = pd.DataFrame(index=features_df.index)
        
        # Identifier toutes les colonnes de force d'aspect
        strength_cols = [col for col in features_df.columns if col.endswith('_strength')]
        phase_cols = [col for col in features_df.columns if col.endswith('_phase')]
        
        # Interaction force × phase (aspect fort ET appliquant)
        for strength_col in strength_cols:
            base_name = strength_col.replace('_strength', '')
            phase_col = f"{base_name}_phase"
            
            if phase_col in features_df.columns:
                # Fort et appliquant = positif, fort et séparant = négatif
                interaction_features[f"{base_name}_force×phase"] = (
                    features_df[strength_col] * features_df[phase_col]
                )
        
        return pd.concat([features_df, interaction_features], axis=1)
```

## Exemple d'analyse avec les nouvelles features

```python
# Générer les données enrichies

start = datetime(2024, 1, 1, tzinfo=ZoneInfo('UTC'))
end = datetime(2024, 6, 1, tzinfo=ZoneInfo('UTC'))

astro_df = AstronomicalData.generate_aspects_timeseries(start, end, freq='1H')

# Explorer les phases

print("\nDistribution des phases:")
print(astro_df['phase'].value_counts())

# Aspects les plus proches de l'exactitude

exact_aspects = astro_df[astro_df['phase'] == 'exact'].sort_values('strength', ascending=False)
print("\nTop aspects exacts:")
print(exact_aspects[['timestamp', 'planet1_name', 'planet2_name', 'aspect_name', 'orb']].head(10))

# Analyser la vitesse relative pendant les aspects

print("\nVitesse relative moyenne par type d'aspect:")
print(astro_df.groupby['aspect_name']('relative_velocity').mean())

# Créer les features enrichies

crypto_df = CryptoData.fetch_solana_data(start, end, interval='1h')
unified_idx, crypto_aligned, astro_aligned = DataAligner.align_datasets(astro_df, crypto_df)

enriched_features = EnrichedFeatureExtractor.create_cyclic_features(astro_aligned, unified_idx)
enriched_features = EnrichedFeatureExtractor.create_interaction_features(enriched_features)

print(f"\nNombre total de features: {len(enriched_features.columns)}")
print(f"Features par aspect: {len(enriched_features.columns) / len(astro_aligned.groupby(['planet1', 'planet2', 'aspect'])):.1f}")
```

## Visualisation du cycle

```python
import matplotlib.pyplot as plt

def plot_aspect_cycle(astro_df, planet1_name, planet2_name, aspect_name):
    """Visualise l'évolution d'un aspect spécifique dans le temps"""

    mask = (
        (astro_df['planet1_name'] == planet1_name) &
        (astro_df['planet2_name'] == planet2_name) &
        (astro_df['aspect_name'] == aspect_name)
    )
    
    data = astro_df[mask].sort_values('timestamp')
    
    fig, axes = plt.subplots(4, 1, figsize=(15, 12), sharex=True)
    
    # 1. Force de l'aspect et phase
    ax1 = axes[0]
    ax1.plot(data['timestamp'], data['strength'], label='Strength', color='blue')
    ax1.scatter(
        data[data['phase'] == 'applying']['timestamp'],
        data[data['phase'] == 'applying']['strength'],
        color='green', label='Applying', alpha=0.5, s=10
    )
    ax1.scatter(
        data[data['phase'] == 'separating']['timestamp'],
        data[data['phase'] == 'separating']['strength'],
        color='red', label='Separating', alpha=0.5, s=10
    )
    ax1.set_ylabel('Strength')
    ax1.legend()
    ax1.set_title(f'{planet1_name}-{planet2_name} {aspect_name}')
    
    # 2. Orbe dans le temps
    ax2 = axes[1]
    ax2.plot(data['timestamp'], data['orb'], color='purple')
    ax2.axhline(0, color='red', linestyle='--', alpha=0.5)
    ax2.set_ylabel('Orb (degrees)')
    
    # 3. Séparation angulaire et cycle
    ax3 = axes[2]
    ax3.plot(data['timestamp'], data['angular_separation'], color='orange')
    ax3.set_ylabel('Angular Separation (degrees)')
    
    # 4. Vitesse relative
    ax4 = axes[3]
    ax4.plot(data['timestamp'], data['relative_velocity'], color='brown')
    ax4.axhline(0, color='black', linestyle='--', alpha=0.3)
    ax4.set_ylabel('Relative Velocity (°/day)')
    ax4.set_xlabel('Time')
    
    plt.tight_layout()
    return fig

# Exemple d'utilisation

fig = plot_aspect_cycle(astro_df, 'Jupiter', 'Saturn', 'Square')
plt.show()
```

Cette structure capture maintenant **complètement le mouvement cyclique** : vous savez si l'aspect est appliquant ou séparant, dans quel quadrant du cycle vous êtes, et à quelle vitesse les planètes se déplacent l'une par rapport à l'autre. Cela devrait donner des features beaucoup plus riches pour le machine learning !

Loc : Influences des rétrogations, intégré dans l'analyse du cycle, feature en plus ? Et si j'analyse sur les données journalières, les aspects entre planètes lentes ne changent pas beaucoup, les aspects à la lune si, et si j'analyse en haute fréquence, à la minute par exemple, les aspects ne bougent pas, et ceux avec la lune très peu..  Comment optimiser les calculs et correspondances ? Il y aura pour chaque date ou chaque moment, beaucoup d'aspects et la plupart sont du bruit. Le ML ou les algos font le tri entre le bruit et ceux qui correspondent à la courbe de prix ?

Claude : Excellentes observations ! Vous touchez à des points cruciaux pour l'efficacité et la pertinence de l'analyse. Abordons ces questions une par une.

## 1. Intégration des rétrogradations

Les rétrogradations modifient profondément la dynamique des aspects. Voici comment les intégrer :

```python
class AstronomicalData:

    @staticmethod
    def get_retrogradation_info(jday, body_id):
        """
        Détecte si une planète est rétrograde et calcule des métriques

        Returns:
            is_retro: bool
            retro_intensity: float (proche de 0 = station, 1 = vitesse normale)
        """
        import ketu
        
        is_retro = ketu.is_retrograde(jday, body_id)
        
        # Calculer la vitesse instantanée
        dt = 0.1  # 0.1 jour
        pos1 = ketu.long(jday - dt, body_id)
        pos2 = ketu.long(jday + dt, body_id)
        
        velocity = (pos2 - pos1) / (2 * dt)
        
        # Vitesse moyenne de la planète (en valeur absolue)
        avg_speeds = {
            0: 0.986,   # Sun
            1: 13.176,  # Moon
            2: 1.383,   # Mercury
            3: 1.200,   # Venus
            4: 0.524,   # Mars
            5: 0.083,   # Jupiter
            6: 0.034,   # Saturn
            7: 0.012,   # Uranus
            8: 0.007,   # Neptune
            9: 0.004,   # Pluto
        }
        
        avg_speed = avg_speeds.get(body_id, 0.5)
        
        # Intensité de la rétrogradation (0 = station, 1 = vitesse normale)
        retro_intensity = abs(velocity) / avg_speed if avg_speed > 0 else 0
        
        return is_retro, retro_intensity, velocity

    @staticmethod
    def generate_aspects_timeseries(start_date, end_date, freq='1H',
                                     adaptive_sampling=True):
        """
        Génère une série temporelle avec informations de rétrogradation

        Args:
            adaptive_sampling: Si True, adapte la fréquence selon les vitesses planétaires
        """
        from zoneinfo import ZoneInfo
        import ketu
        
        dates = pd.date_range(start_date, end_date, freq=freq)
        aspects_list = []
        
        prev_positions = {}
        prev_aspects = {}
        
        for i, dt in enumerate(dates):
            dt_utc = dt.tz_localize('UTC') if dt.tz is None else dt
            jday = ketu.utc_to_julian(dt_utc)
            
            # Calculer positions et rétrogradations
            positions = {}
            velocities = {}
            retrogradations = {}
            
            for body_id in range(10):
                positions[body_id] = ketu.long(jday, body_id)
                
                # Info rétrogradation
                is_retro, retro_intensity, velocity = AstronomicalData.get_retrogradation_info(jday, body_id)
                retrogradations[body_id] = {
                    'is_retro': is_retro,
                    'intensity': retro_intensity,
                    'velocity': velocity
                }
                
                velocities[body_id] = velocity
            
            aspects = ketu.calculate_aspects(jday)
            
            for body1, body2, aspect_idx, orb in aspects:
                long1 = positions[body1]
                long2 = positions[body2]
                angular_sep = AstronomicalData.calculate_angular_separation(long1, long2)
                
                quadrant, direction, progress = AstronomicalData.get_cycle_info(angular_sep)
                
                rel_velocity = velocities[body2] - velocities[body1]
                
                # Phase de l'aspect
                aspect_key = (body1, body2, aspect_idx)
                if aspect_key in prev_aspects:
                    orb_prev = prev_aspects[aspect_key]
                    phase = AstronomicalData.determine_phase(orb, orb_prev)
                else:
                    phase = AspectPhase.APPLYING.value
                
                prev_aspects[aspect_key] = orb
                
                days_to_exact = AstronomicalData.estimate_days_to_exact(orb, rel_velocity)
                
                max_orb = ketu.calculate_orb(body1, body2)
                strength = 1 - (abs(orb) / max_orb)
                
                # NOUVELLES FEATURES DE RÉTROGRADATION
                retro1 = retrogradations[body1]
                retro2 = retrogradations[body2]
                
                # Configuration rétrograde
                both_retro = retro1['is_retro'] and retro2['is_retro']
                one_retro = retro1['is_retro'] or retro2['is_retro']
                none_retro = not (retro1['is_retro'] or retro2['is_retro'])
                
                # Score de "staticité" : proche de 0 = une planète en station
                staticity = min(retro1['intensity'], retro2['intensity'])
                
                aspects_list.append({
                    'timestamp': dt_utc,
                    'julian_day': jday,
                    'planet1': body1,
                    'planet2': body2,
                    'aspect': aspect_idx,
                    'orb': orb,
                    'strength': strength,
                    'angular_separation': angular_sep,
                    'phase': phase,
                    'cycle_quadrant': quadrant,
                    'cycle_direction': direction,
                    'cycle_progress': progress,
                    'relative_velocity': rel_velocity,
                    'days_to_exact': days_to_exact,
                    
                    # Features de rétrogradation
                    'planet1_retro': retro1['is_retro'],
                    'planet2_retro': retro2['is_retro'],
                    'planet1_retro_intensity': retro1['intensity'],
                    'planet2_retro_intensity': retro2['intensity'],
                    'both_retrograde': both_retro,
                    'one_retrograde': one_retro,
                    'staticity_score': staticity,  # Plus proche de 0 = plus statique
                    
                    'planet1_name': ketu.body_name(body1).decode(),
                    'planet2_name': ketu.body_name(body2).decode(),
                    'aspect_name': ketu.aspects['name'][aspect_idx].decode()
                })
            
            prev_positions = positions.copy()
        
        return pd.DataFrame(aspects_list)
```

## 2. Échantillonnage adaptatif selon les vitesses planétaires

Pour optimiser les calculs, on adapte la fréquence d'échantillonnage selon la vitesse des corps :

```python
class AdaptiveSampler:
    """Optimise l'échantillonnage selon les vitesses planétaires"""

   # Vitesses moyennes en degrés/jour

    PLANET_SPEEDS = {
        'Sun': 0.986,
        'Moon': 13.176,
        'Mercury': 1.383,
        'Venus': 1.200,
        'Mars': 0.524,
        'Jupiter': 0.083,
        'Saturn': 0.034,
        'Uranus': 0.012,
        'Neptune': 0.007,
        'Pluto': 0.004,
    }

    @staticmethod
    def get_optimal_sampling_rate(body1_name, body2_name, target_resolution_deg=0.5):
        """
        Calcule la fréquence d'échantillonnage optimale pour un couple de planètes

        Args:
            target_resolution_deg: résolution souhaitée en degrés
        
        Returns:
            sampling_hours: nombre d'heures entre chaque échantillon
        """
        speed1 = AdaptiveSampler.PLANET_SPEEDS.get(body1_name, 0.5)
        speed2 = AdaptiveSampler.PLANET_SPEEDS.get(body2_name, 0.5)
        
        # Vitesse relative maximale
        max_relative_speed = speed1 + speed2
        
        # Temps nécessaire pour parcourir target_resolution_deg
        days_per_sample = target_resolution_deg / max_relative_speed if max_relative_speed > 0 else 1
        hours_per_sample = days_per_sample * 24
        
        # Limiter entre 1 heure et 30 jours
        hours_per_sample = max(1, min(hours_per_sample, 30 * 24))
        
        return hours_per_sample

    @staticmethod
    def create_sampling_groups():
        """
        Groupe les paires de planètes par fréquence d'échantillonnage similaire

        Returns:
            dict: {sampling_rate: [(planet1, planet2), ...]}
        """
        import ketu
        
        sampling_groups = {}
        
        # Générer toutes les paires
        for body1 in range(10):
            for body2 in range(body1 + 1, 10):
                name1 = ketu.body_name(body1).decode()
                name2 = ketu.body_name(body2).decode()
                
                sampling_rate = AdaptiveSampler.get_optimal_sampling_rate(name1, name2)
                
                # Arrondir à des valeurs standard (1h, 6h, 12h, 24h, 7j, 30j)
                if sampling_rate <= 1:
                    rate_key = '1H'
                elif sampling_rate <= 6:
                    rate_key = '6H'
                elif sampling_rate <= 12:
                    rate_key = '12H'
                elif sampling_rate <= 24:
                    rate_key = '1D'
                elif sampling_rate <= 7 * 24:
                    rate_key = '7D'
                else:
                    rate_key = '30D'
                
                if rate_key not in sampling_groups:
                    sampling_groups[rate_key] = []
                
                sampling_groups[rate_key].append((body1, body2, name1, name2))
        
        return sampling_groups

    @staticmethod
    def generate_optimized_aspects(start_date, end_date):
        """
        Génère les aspects avec échantillonnage adaptatif par groupe de planètes
        """
        from zoneinfo import ZoneInfo
        import ketu

        sampling_groups = AdaptiveSampler.create_sampling_groups()
        
        all_aspects = []
        
        for freq, planet_pairs in sampling_groups.items():
            print(f"Sampling {len(planet_pairs)} planet pairs at {freq}")
            
            dates = pd.date_range(start_date, end_date, freq=freq)
            
            for dt in dates:
                dt_utc = dt.tz_localize('UTC') if dt.tz is None else dt
                jday = ketu.utc_to_julian(dt_utc)
                
                # Calculer uniquement les aspects pour ce groupe de planètes
                for body1, body2, name1, name2 in planet_pairs:
                    # Calculer l'aspect entre ces deux planètes
                    long1 = ketu.long(jday, body1)
                    long2 = ketu.long(jday, body2)
                    
                    angular_sep = (long2 - long1) % 360
                    
                    # Vérifier si un aspect est formé
                    aspect_angles = [0, 30, 60, 90, 120, 150, 180]
                    max_orb = ketu.calculate_orb(body1, body2)
                    
                    for aspect_idx, target_angle in enumerate(aspect_angles):
                        orb = min(
                            abs(angular_sep - target_angle),
                            abs(angular_sep - (target_angle + 360)),
                            abs(angular_sep - (target_angle - 360))
                        )
                        
                        if orb <= max_orb:
                            strength = 1 - (orb / max_orb)
                            
                            all_aspects.append({
                                'timestamp': dt_utc,
                                'planet1': body1,
                                'planet2': body2,
                                'planet1_name': name1,
                                'planet2_name': name2,
                                'aspect': aspect_idx,
                                'aspect_name': ketu.aspects['name'][aspect_idx].decode(),
                                'orb': orb,
                                'strength': strength,
                                'sampling_freq': freq
                            })
        
        return pd.DataFrame(all_aspects).sort_values('timestamp')

# Exemple d'utilisation

sampling_groups = AdaptiveSampler.create_sampling_groups()
for freq, pairs in sampling_groups.items():
    print(f"\n{freq}:")
    for _,_, name1, name2 in pairs[:5]:  # Afficher 5 premiers
        print(f"  {name1}-{name2}")
```

## 3. Filtrage du bruit et sélection des aspects pertinents

Le ML peut faire le tri, mais on peut aussi pré-filtrer intelligemment :

```python
class AspectFilter:
    """Filtre les aspects pour réduire le bruit"""

    @staticmethod
    def filter_by_strength(astro_df, min_strength=0.5):
        """Ne garde que les aspects forts"""
        return astro_df[astro_df['strength'] >= min_strength]
    
    @staticmethod
    def filter_by_exactness(astro_df, max_days_to_exact=3):
        """Ne garde que les aspects proches de l'exactitude"""
        return astro_df[abs(astro_df['days_to_exact']) <= max_days_to_exact]
    
    @staticmethod
    def filter_by_phase(astro_df, phases=['applying', 'exact']):
        """Ne garde que certaines phases (ex: seulement appliquant)"""
        return astro_df[astro_df['phase'].isin(phases)]
    
    @staticmethod
    def filter_slow_planets_only(astro_df, slow_bodies=[4, 5, 6, 7, 8, 9]):
        """
        Ne garde que les aspects impliquant au moins une planète lente
        Mars (4), Jupiter (5), Saturne (6), Uranus (7), Neptune (8), Pluton (9)
        """
        mask = (astro_df['planet1'].isin(slow_bodies)) | (astro_df['planet2'].isin(slow_bodies))
        return astro_df[mask]
    
    @staticmethod
    def filter_major_aspects_only(astro_df, major_aspects=[0, 3, 4, 6]):
        """
        Ne garde que les aspects majeurs
        Conjonction (0), Carré (3), Trigone (4), Opposition (6)
        """
        return astro_df[astro_df['aspect'].isin(major_aspects)]
    
    @staticmethod
    def deduplicate_aspects(astro_df, time_window='1D'):
        """
        Élimine les aspects redondants dans une fenêtre temporelle
        Garde l'aspect le plus fort par fenêtre
        """
        astro_df = astro_df.copy()
        astro_df['time_group'] = astro_df['timestamp'].dt.floor(time_window)
        
        # Grouper par fenêtre temporelle et paire planète-aspect
        grouped = astro_df.groupby([
            'time_group', 'planet1', 'planet2', 'aspect'
        ])
        
        # Garder l'aspect le plus fort de chaque groupe
        idx = grouped['strength'].idxmax()
        
        return astro_df.loc[idx].drop('time_group', axis=1)
    
    @staticmethod
    def apply_smart_filter(astro_df, strategy='balanced'):
        """
        Applique une stratégie de filtrage prédéfinie
        
        Strategies:
            - 'aggressive': Très sélectif, uniquement aspects forts et exacts
            - 'balanced': Équilibre entre signal et bruit
            - 'conservative': Garde plus d'aspects mais filtre la redondance
        """
        if strategy == 'aggressive':
            filtered = AspectFilter.filter_slow_planets_only(astro_df)
            filtered = AspectFilter.filter_major_aspects_only(filtered)
            filtered = AspectFilter.filter_by_strength(filtered, min_strength=0.7)
            filtered = AspectFilter.filter_by_phase(filtered, phases=['exact'])
            
        elif strategy == 'balanced':
            filtered = AspectFilter.filter_slow_planets_only(astro_df)
            filtered = AspectFilter.filter_by_strength(filtered, min_strength=0.5)
            filtered = AspectFilter.deduplicate_aspects(filtered, time_window='6H')
            
        elif strategy == 'conservative':
            filtered = AspectFilter.filter_by_strength(astro_df, min_strength=0.3)
            filtered = AspectFilter.deduplicate_aspects(filtered, time_window='1H')
            
        else:
            filtered = astro_df
        
        return filtered

# Exemple d'utilisation

astro_df = AstronomicalData.generate_aspects_timeseries(start, end, freq='1H')

print(f"Aspects bruts: {len(astro_df)}")

filtered_aggressive = AspectFilter.apply_smart_filter(astro_df, strategy='aggressive')
print(f"Après filtrage agressif: {len(filtered_aggressive)} (-{100*(1-len(filtered_aggressive)/len(astro_df)):.1f}%)")

filtered_balanced = AspectFilter.apply_smart_filter(astro_df, strategy='balanced')
print(f"Après filtrage équilibré: {len(filtered_balanced)} (-{100*(1-len(filtered_balanced)/len(astro_df)):.1f}%)")
```

## 4. Feature Selection avec ML

Le ML peut identifier les aspects les plus prédictifs :

```python
from sklearn.feature_selection import mutual_info_regression, SelectKBest
from sklearn.ensemble import RandomForestRegressor

class MLFeatureSelector:
    """Sélectionne les features les plus pertinentes avec le ML"""

    @staticmethod
    def mutual_information_selection(X, y, k=50):
        """
        Sélectionne les k features avec la plus haute information mutuelle
        """
        selector = SelectKBest(mutual_info_regression, k=k)
        X_selected = selector.fit_transform(X, y)
        
        # Récupérer les noms des features sélectionnées
        selected_features = X.columns[selector.get_support()].tolist()
        
        # Scores d'importance
        scores = pd.DataFrame({
            'feature': X.columns,
            'score': selector.scores_
        }).sort_values('score', ascending=False)
        
        return X_selected, selected_features, scores
    
    @staticmethod
    def random_forest_importance(X, y, n_estimators=100):
        """
        Utilise Random Forest pour identifier les features importantes
        """
        rf = RandomForestRegressor(n_estimators=n_estimators, random_state=42, n_jobs=-1)
        rf.fit(X.fillna(0), y)
        
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    @staticmethod
    def progressive_feature_filtering(enriched_features, crypto_data, 
                                       target='returns', threshold=0.01):
        """
        Filtre progressif : garde uniquement les features qui améliorent le modèle
        """
        from sklearn.model_selection import cross_val_score
        from sklearn.linear_model import Ridge
        
        X = enriched_features.fillna(0)
        y = crypto_data[target].fillna(0)
        
        # Aligner X et y
        common_idx = X.index.intersection(y.index)
        X = X.loc[common_idx]
        y = y.loc[common_idx]
        
        selected_features = []
        base_score = 0
        
        # Tester chaque feature individuellement
        for col in X.columns:
            if len(selected_features) == 0:
                X_test = X[[col]]
            else:
                X_test = X[selected_features + [col]]
            
            score = cross_val_score(
                Ridge(alpha=1.0), 
                X_test, 
                y, 
                cv=5, 
                scoring='r2'
            ).mean()
            
            if score > base_score + threshold:
                selected_features.append(col)
                base_score = score
                print(f"Added {col}: R² = {score:.4f}")
        
        return selected_features

# Exemple d'utilisation complète

enriched_features = EnrichedFeatureExtractor.create_cyclic_features(
    filtered_balanced,
    unified_idx
)

# Sélection par information mutuelle

_, selected_mi, scores_mi = MLFeatureSelector.mutual_information_selection(
    enriched_features,
    crypto_aligned['returns'].fillna(0),
    k=30
)

print("\nTop 10 features par information mutuelle:")
print(scores_mi.head(10))

# Importance Random Forest

importance_rf = MLFeatureSelector.random_forest_importance(
    enriched_features,
    crypto_aligned['returns'].fillna(0)
)

print("\nTop 10 features par Random Forest:")
print(importance_rf.head(10))
```

## Résumé des optimisations

1. **Rétrogradations** : Features additionnelles pour capturer la staticité et les configurations rétrogrades
2. **Échantillonnage adaptatif** : Fréquences différentes selon la vitesse des planètes (Lune: 1H, planètes lentes: 7-30D)
3. **Filtrage intelligent** : Stratégies pré-définies pour réduire le bruit (aggressive/balanced/conservative)
4. **Feature selection ML** : Le modèle identifie quels aspects sont réellement prédictifs

Le ML fait effectivement le tri final, mais un pré-filtrage intelligent réduit drastiquement la dimensionnalité et améliore les performances !
