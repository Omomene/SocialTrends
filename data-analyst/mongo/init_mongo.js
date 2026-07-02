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

db.posts.createIndex(
    { post_id: 1 },
    { unique: true }
);

db.posts.createIndex(
    { event_id: 1 }
);

db.posts.createIndex(
    { created_at: 1 }
);

db.posts.createIndex(
    { "sentiment.label": 1 }
);

print("MongoDB initialized.");