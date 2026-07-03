# Dashboard Superset – Social Buzz & Fan Sentiment Analysis

## Objectif

Le dashboard permet de visualiser l'évolution du sentiment des supporters et les sujets dominants lors d'un événement sportif à partir des résultats NLP enrichis.

Les données sont issues de :

Silver Layer
→ NLP (Sentiment + Topic Modeling)
→ MongoDB
→ Agrégations Gold PostgreSQL
→ Superset

---

## Source de données

Base PostgreSQL :

sports_analytics

Tables utilisées :

- sentiment_timeline
- sentiment_hourly
- topic_hourly
- event_correlations
- trend_summary

---

## KPI

### Messages analysés

Dataset :
sentiment_timeline

Metric :
SUM(total_posts)

Objectif :
Afficher le volume total de messages traités.

---

### Sentiment moyen

Dataset :
sentiment_timeline

Metric :
AVG(sentiment_index)

Objectif :
Mesurer la tendance globale du sentiment.

Valeurs :

-1 = très négatif
0 = neutre
+1 = très positif

---

### Evénements analysés

Dataset :
event_correlations

Metric :
COUNT(event_id)

Objectif :
Afficher le nombre total d'événements sportifs corrélés.

---

## Visualisations

### Evolution du sentiment

Dataset :
sentiment_timeline

Type :
Time Series Line Chart

Mesure :
AVG(sentiment_index)

Dimension temporelle :
hour_ts

Objectif :
Visualiser les variations du sentiment heure par heure.

---

### Nombre de messages par heure

Dataset :
sentiment_timeline

Type :
Bar Chart

Mesure :
SUM(total_posts)

Objectif :
Identifier les pics d'activité sociale.

---

### Répartition des sentiments

Dataset :
sentiment_hourly

Type :
Stacked Bar Chart

Mesures :

- SUM(positive_count)
- SUM(neutral_count)
- SUM(negative_count)

Objectif :
Comparer les sentiments positifs, neutres et négatifs.

---

### Top sujets

Dataset :
topic_hourly

Type :
Horizontal Bar Chart

Mesure :
SUM(occurrences)

Dimension :
topic

Objectif :
Identifier les sujets les plus discutés.

---

### Force des corrélations

Dataset :
event_correlations

Type :
Pie Chart

Mesure :
COUNT(event_id)

Dimension :
correlation_strength

Objectif :
Mesurer la répartition des corrélations faibles, moyennes et fortes.

---

### Impact des événements sportifs

Dataset :
event_correlations

Type :
Table

Colonnes :

- event_type
- volume_delta
- sentiment_delta
- correlation_strength

Objectif :
Mesurer l'impact des événements sportifs sur les réactions des supporters.

---

## Résultats obtenus

Sur le dataset FIFA World Cup 2022 :

- 3000 messages analysés
- 24 agrégations horaires
- 770 agrégations de topics
- 300 corrélations d'événements
- 1 résumé automatique généré par NLP

---

## Conclusion

Le dashboard permet de suivre :

- l'évolution du sentiment des supporters,
- le volume des discussions,
- les sujets dominants,
- l'impact des événements sportifs,
- les corrélations entre le terrain et les réactions sociales.

Il constitue la couche de restitution finale de l'architecture Data.