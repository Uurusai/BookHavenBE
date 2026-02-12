--user
CREATE TABLE IF NOT EXISTS app_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(30),
    full_name VARCHAR(100),
    city VARCHAR(50),
    country VARCHAR(50)
);

--community + membership
CREATE TABLE IF NOT EXISTS community (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    member_count INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS membership (
    user_id INT REFERENCES app_user(id) ON DELETE CASCADE,
    community_id INT REFERENCES community(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(30) DEFAULT 'member',
    PRIMARY KEY (user_id, community_id)
);

--discussion
CREATE TABLE IF NOT EXISTS discussion (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT REFERENCES app_user(id),
    community_id INT REFERENCES community(id)
);

--meet event
CREATE TABLE IF NOT EXISTS meet_event (
    id SERIAL PRIMARY KEY,
    title TEXT,
    meet_time TIMESTAMP,
    latitude DECIMAL(9,6) DEFAULT NULL,
    longitude DECIMAL(9,6) DEFAULT NULL,
    live_url TEXT DEFAULT NULL,
    event_type VARCHAR(30),
    community_id INT REFERENCES community(id)
);

--book
CREATE TABLE IF NOT EXISTS book (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(20),
    title TEXT NOT NULL,
    author TEXT,
    publisher TEXT,
    category TEXT
);

--book offer
CREATE TABLE IF NOT EXISTS book_offer (
    id SERIAL PRIMARY KEY,
    offer_type VARCHAR(10) CHECK (offer_type IN ('SELL', 'BUY')),
    price NUMERIC(10,2),
    condition VARCHAR(30),
    quantity INT,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    is_active BOOLEAN DEFAULT TRUE,
    user_id INT REFERENCES app_user(id),
    book_id INT REFERENCES book(id)
);

--chat
CREATE TABLE IF NOT EXISTS chat_thread (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS chat_message (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sender_id INT REFERENCES app_user(id),
    thread_id INT REFERENCES chat_thread(id)
);

--transaction
CREATE TABLE IF NOT EXISTS transaction (
    id SERIAL PRIMARY KEY,
    status VARCHAR(30),
    final_price NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    buyer_id INT REFERENCES app_user(id),
    seller_id INT REFERENCES app_user(id),
    book_offer_id INT REFERENCES book_offer(id)
);

--review
CREATE TABLE IF NOT EXISTS review (
    id SERIAL PRIMARY KEY,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT REFERENCES app_user(id),
    book_id INT REFERENCES book(id)
);

--report 
CREATE TABLE IF NOT EXISTS report (
    id SERIAL PRIMARY KEY,
    reason TEXT,
    status VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reporter_id INT REFERENCES app_user(id),
    reported_user_id INT REFERENCES app_user(id)
);

--notification
CREATE TABLE IF NOT EXISTS notification (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50),
    type VARCHAR(50),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT REFERENCES app_user(id)
);
--wishlist
CREATE TABLE IF NOT EXISTS wishlist (
    user_id INT REFERENCES app_user(id),
    book_id INT REFERENCES book(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, book_id)
);

--reading history
CREATE TABLE IF NOT EXISTS reading_history (
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT REFERENCES app_user(id),
    book_id INT REFERENCES book(id),
    PRIMARY KEY (user_id, book_id)
);
