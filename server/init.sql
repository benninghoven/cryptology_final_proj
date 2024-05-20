CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    public_key VARCHAR(1024) NOT NULL,
    private_key VARCHAR(1024) NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_histories (
    id SERIAL PRIMARY KEY,
    user1 VARCHAR(255) NOT NULL,
    user2 VARCHAR(255) NOT NULL,
    sym_key VARCHAR(1024) NOT NULL,
    chat TEXT NOT NULL,
    CHECK (user1 < user2),  -- Ensures user1 is always lexicographically smaller than user2
    UNIQUE (user1, user2),  -- Ensures unique pairs of users
    INDEX (user1),
    INDEX (user2)
);

