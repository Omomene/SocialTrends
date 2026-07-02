db = db.getSiblingDB("social_db");

db.createUser({
    user: "app",
    pwd: "app12345",
    roles: [
        {
            role: "readWrite",
            db: "social_db"
        }
    ]
});

db.createCollection("posts");

/*
 * Un post est unique
 */
db.posts.createIndex(
    { post_id: 1 },
    { unique: true }
);

/*
 * Recherche par match
 */
db.posts.createIndex(
    { match_id: 1 }
);

/*
 * Recherche temporelle
 */
db.posts.createIndex(
    { created_at: 1 }
);

/*
 * Recherche par sentiment
 */
db.posts.createIndex(
    { "sentiment.label": 1 }
);

/*
 * Recherche par topic
 */
db.posts.createIndex(
    { "topic.label": 1 }
);

/*
 * Très utile pour les agrégations
 * groupby(match_id, created_at)
 */
db.posts.createIndex(
    {
        match_id: 1,
        created_at: 1
    }
);

/*
 * Recherche par langue
 */
db.posts.createIndex(
    { language: 1 }
);

/*
 * Recherche par source
 */
db.posts.createIndex(
    { source: 1 }
);

/*
 * Recherche par date de traitement NLP
 */
db.posts.createIndex(
    { processed_at: 1 }
);

print("MongoDB initialized successfully.");