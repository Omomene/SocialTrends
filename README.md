
---

#  SocialTrends

### Plateforme d’analyse de données sociales en temps réel (Big Data + NLP + BI)

**SocialTrends** est une plateforme complète de **Big Data Analytics** simulant un système d’analyse de réseaux sociaux basé sur les tweets de la Coupe du Monde FIFA 2022.

Le projet démontre comment des données sociales peuvent être :

* ingérées (Kafka)
* stockées (MinIO / Bronze–Silver–Gold)
* enrichies avec du NLP (sentiment + topic detection)
* combinées avec des événements sportifs (match_events.csv)
* exploitées via des dashboards BI (Apache Superset)

---

#  Équipe du projet

Projet réalisé dans le cadre d’un Master en **Data Engineering & AI**

* Groupe : *[ajouter les membres ici]*

---

#  Objectif du projet

L’objectif principal est de construire une architecture complète de **data engineering pipeline** capable de :

* Simuler un flux de données social media (tweets)
* Ingest les données avec Kafka
* Structurer un Data Lake (Bronze / Silver / Gold)
* Appliquer du NLP (sentiment + language + topic detection)
* Enrichir les tweets avec des événements de match
* Stocker les données analytiques dans PostgreSQL
* Créer des dashboards interactifs avec Superset

---

#  Architecture globale

```text
Dataset CSV (Tweets + Match Events)
        │
        ▼
Airflow Collection DAG
        │
        ├────────► Kafka (RAW topic)
        │
        └────────► MinIO Bronze Layer
                        │
                        ▼
Airflow Cleaning DAG
        │
        ├────────► Kafka (clean_posts)
        │
        └────────► MinIO Silver Layer
                        │
                        ▼
Airflow NLP DAG
        │
        ├── Language Detection (langdetect)
        ├── Sentiment Analysis (VADER)
        ├── Topic Detection (rule-based matching)
        │
        ▼
MongoDB (NLP enriched documents)
        │
        ▼
Airflow Gold DAG (Event Matching + Aggregation)
        │
        ▼
PostgreSQL (Gold Analytical Table)
        │
        ▼
Apache Superset Dashboards
```

---

#  Technologies utilisées

| Technologie             | Rôle                        |
| ----------------------- | --------------------------- |
| Python                  | Data processing             |
| Apache Airflow          | Orchestration des workflows |
| Apache Kafka            | Streaming des données       |
| MinIO                   | Data Lake (S3 compatible)   |
| MongoDB                 | Stockage des documents NLP  |
| PostgreSQL              | Data Warehouse (Gold layer) |
| Apache Superset         | Data Visualization          |
| VADER                   | Sentiment analysis          |
| LangDetect              | Language detection          |
| Pandas                  | Manipulation des données    |
| Docker / Docker Compose | Conteneurisation            |

---

#  Structure du projet

```text
SocialTrends/
├── dags/
│   ├── social_posts_collect_hourly.py
│   ├── social_cleaning_hourly.py
│   ├── social_nlp_hourly.py
│   ├── social_gold_build_hourly.py
│
├── data/
│   ├── fifa_world_cup_2022_tweets.csv
│   ├── match_events.csv
│
├── sql/
│   ├── schema.sql
│   ├── gold_tables.sql
│   ├── analytics_tables.sql
│
├── storage/
│   ├── minio_client.py
│   ├── mongo_client.py
│   ├── postgres_client.py
│
├── superset/
├── docker-compose.yml
└── README.md
```

---

#  Sources de données

## 1. Dataset tweets (social media)

Des tweets liés à la Coupe du Monde FIFA 2022 : sur Kaggle https://www.kaggle.com/competitions/football-sentiment/data

* texte du tweet
* likes
* source
* timestamp

---

## 2. Match Events (`match_events.csv`)

Dataset structuré contenant les événements de match : Simuler à partir du https://github.com/statsbomb/open-data/tree/master/data

```text
event_time, match, event_type, team, player
```

Exemple :

```text
00:10, Argentina vs Saudi Arabia, Goal, Argentina, Lionel Messi
```

Ce dataset est utilisé pour **enrichir les tweets avec le contexte réel des matchs**.

---

#  Pipeline de données

---

## 1. Data Collection (Bronze Layer)

### DAG: `social_posts_collect_hourly`

* Lecture du dataset CSV
* Envoi vers Kafka (`raw_posts`)
* Stockage dans MinIO Bronze

---

## 2. Data Cleaning (Silver Layer)

### DAG: `social_cleaning_hourly`

* Consommation Kafka raw
* Nettoyage du texte (hashtags, caractères spéciaux)
* Normalisation des données
* Stockage MinIO Silver

---

## 3. NLP Layer (MongoDB)

### DAG: `social_nlp_hourly`

---

##  Language Detection

* Librairie: `langdetect`
* Langues supportées : en, fr, es, pt, other

---

## Sentiment Analysis (VADER)

Modèle léger basé sur lexique :

* positive
* neutral
* negative
* sentiment_score (-1 à 1)

---

## Topic Detection (rule-based)

Classification basée sur mots-clés :

* Player
* Team
* Match
* Goal
* Referee
* Stadium
* Fans
* Media
* Other

---

## Stockage MongoDB

Exemple document :

```json
{
  "post_id": 123,
  "text_clean": "MESSI SCORED AGAIN!",
  "language": "en",
  "sentiment": "positive",
  "sentiment_score": 0.87,
  "topic": "Player"
}
```

---

## 4. Gold Layer (Business Layer)

### DAG: `social_gold_build_hourly`

---

##  Enrichissement avec Match Events

Les tweets sont reliés aux événements du match via matching texte :

Exemple :

```text
Tweet: "MESSI IS THE GOAT"
```

Devient :

```json
{
  "text": "MESSI IS THE GOAT",
  "player": "Lionel Messi",
  "match": "Argentina vs France",
  "event_type": "Goal",
  "sentiment": "positive"
}
```

---

##  Table Gold PostgreSQL

Table finale utilisée pour Superset :

| Column          | Description      |
| --------------- | ---------------- |
| post_id         | ID du tweet      |
| text            | contenu          |
| likes           | engagement       |
| language        | langue           |
| sentiment       | sentiment VADER  |
| sentiment_score | score numérique  |
| topic           | sujet détecté    |
| match           | match associé    |
| team            | équipe           |
| player          | joueur           |
| event_type      | type d’événement |
| processed_at    | timestamp        |

---

#  Superset Dashboards

##  Visualisations disponibles

### 1. Sentiment Distribution

* Positive / Neutral / Negative

### 2. Players popularity

* joueurs les plus mentionnés

### 3. Matches engagement

* matchs les plus discutés

### 4. Event impact analysis

* impact des goals / penalties sur sentiment

### 5. Topic distribution

* distribution des sujets

### 6. Language distribution

* analyse des langues

---

#  Infrastructure Docker

| Service    | Rôle           |
| ---------- | -------------- |
| Airflow    | Orchestration  |
| Kafka      | Streaming      |
| MinIO      | Data Lake      |
| MongoDB    | NLP storage    |
| PostgreSQL | Gold warehouse |
| Superset   | BI dashboards  |

---

#  Lancer le projet

```bash
git clone https://github.com/your-repo/SocialTrends.git
cd SocialTrends
docker compose up -d
```

---

##  Accès aux services

| Service    | URL                                            |
| ---------- | ---------------------------------------------- |
| Airflow    | [http://localhost:8080](http://localhost:8080) |
| Superset   | [http://localhost:8088](http://localhost:8088) |
| MinIO      | [http://localhost:9001](http://localhost:9001) |
| Kafka      | localhost:9092                                 |
| PostgreSQL | localhost:5432                                 |
| MongoDB    | localhost:27017                                |

---

# Ce que démontre ce projet

Ce projet illustre :

* Architecture Big Data complète
* Data Lake (Bronze / Silver / Gold)
* Pipeline Kafka + Airflow
* NLP simple et efficace (VADER + rule-based)
* Data enrichment avec events sportifs
* Data warehouse pour analytics
* BI dashboards avec Superset
* Déploiement full Docker

---

#  Améliorations futures

* Remplacer rule-based topic detection par ML model
* Ajouter Spark pour processing distribué
* Streaming temps réel Superset
* Déploiement Kubernetes
* API ingestion Twitter/X live
* NLP avancé (BERT / transformer models)
* Monitoring avec Prometheus & Grafana

---
