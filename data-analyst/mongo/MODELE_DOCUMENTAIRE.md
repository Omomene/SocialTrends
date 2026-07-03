# Modèle documentaire MongoDB

## Objectif

MongoDB constitue la couche de stockage documentaire du projet.

Son rôle est de stocker les messages enrichis par les traitements NLP avant leur agrégation dans PostgreSQL.

Architecture :

```text
Collecte
    ↓
Silver Layer
    ↓
NLP
    ↓
MongoDB
    ↓
Agrégations
    ↓
PostgreSQL
    ↓
Superset
```

---

## Collection utilisée

Collection :

```text
posts
```

Chaque document représente un message social enrichi.

---

## Structure d'un document

```json
{
  "post_id": "cc19e6787acfc51c2072c7d70d82c02d9876b0b9",
  "match_id": "fifa_world_cup_2022",
  "match_name": "FIFA World Cup 2022",
  "source": "Twitter for iPhone",
  "created_at": "2022-11-20T15:30:00",

  "text_raw": "Come on England!",
  "text_clean": "come on england",

  "language": "en",

  "sentiment": {
    "label": "positif",
    "score": 0.95,
    "method": "hugging_face_xlm_roberta"
  },

  "topic": {
    "id": 5,
    "label": "england / home / coming / xi",
    "method": "bertopic_sample"
  },

  "processed_at": "2026-07-03T02:00:00"
}
```

---

## Description des attributs

| Champ | Type | Description |
|---------|---------|---------|
| post_id | String | Identifiant unique du message |
| match_id | String | Identifiant du match |
| match_name | String | Nom du match ou de la compétition |
| source | String | Source de publication |
| created_at | Datetime | Date de publication |
| text_raw | String | Texte original |
| text_clean | String | Texte nettoyé utilisé pour le NLP |
| language | String | Langue détectée |
| sentiment | Objet | Résultat de l'analyse de sentiment |
| topic | Objet | Résultat du topic modeling |
| processed_at | Datetime | Date d'enrichissement NLP |

---

## Objet sentiment

```json
{
  "label": "positif",
  "score": 0.95,
  "method": "hugging_face_xlm_roberta"
}
```

### Description

- label : sentiment détecté
- score : niveau de confiance du modèle
- method : modèle utilisé

Valeurs possibles :

```text
positif
neutre
négatif
```

---

## Objet topic

```json
{
  "id": 5,
  "label": "england / home / coming / xi",
  "method": "bertopic_sample"
}
```

### Description

- id : identifiant du sujet
- label : sujet détecté
- method : méthode utilisée

---

## Index MongoDB

### Index d'unicité

```javascript
{ post_id: 1 }
```

Objectif :

Éviter les doublons.

---

### Index de recherche

```javascript
{ match_id: 1 }
```

Permet de filtrer les messages d'un match.

---

```javascript
{ created_at: 1 }
```

Permet les agrégations temporelles.

---

```javascript
{ "sentiment.label": 1 }
```

Permet l'analyse des sentiments.

---

```javascript
{ "topic.label": 1 }
```

Permet l'analyse des sujets.

---

```javascript
{
  match_id: 1,
  created_at: 1
}
```

Permet d'optimiser les agrégations vers PostgreSQL.

---

## Justification du choix MongoDB

MongoDB a été choisi pour plusieurs raisons :

- les résultats NLP sont semi-structurés ;
- les enrichissements peuvent évoluer dans le temps ;
- les objets sentiment et topic sont naturellement représentés sous forme d'objets imbriqués ;
- le modèle documentaire est particulièrement adapté aux données textuelles enrichies ;
- l'ajout de nouveaux attributs ne nécessite pas de modification de schéma complexe.

MongoDB sert ainsi de couche intermédiaire entre les traitements NLP et la couche analytique PostgreSQL.

---

## Résultats obtenus

Dataset analysé :

```text
FIFA World Cup 2022
```

Nombre de documents stockés :

```text
3000 posts enrichis
```

Ces documents sont ensuite agrégés afin d'alimenter les tables analytiques PostgreSQL utilisées par Superset.

---

## Conclusion

MongoDB constitue la couche de stockage documentaire du projet.

Il permet de conserver les résultats enrichis du NLP dans un format flexible avant leur transformation en indicateurs analytiques destinés à PostgreSQL et aux tableaux de bord Superset.