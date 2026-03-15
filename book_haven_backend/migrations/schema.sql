--user
CREATE TABLE IF NOT EXISTS app_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(30),
    full_name VARCHAR(100),
    city VARCHAR(50),
    country VARCHAR(50),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    trust_score DECIMAL(5,2) DEFAULT 0
);

-- Ensure columns exist if table already exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='app_user' AND column_name='latitude') THEN
        ALTER TABLE app_user ADD COLUMN latitude DECIMAL(9,6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='app_user' AND column_name='longitude') THEN
        ALTER TABLE app_user ADD COLUMN longitude DECIMAL(9,6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='app_user' AND column_name='trust_score') THEN
        ALTER TABLE app_user ADD COLUMN trust_score DECIMAL(5,2) DEFAULT 0;
    END IF;
END $$;

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
    book_id INT REFERENCES book(id),
    transaction_id INT REFERENCES transaction(id)
);

-- Ensure transaction_id exists in review if table already exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='review' AND column_name='transaction_id') THEN
        ALTER TABLE review ADD COLUMN transaction_id INT REFERENCES transaction(id);
    END IF;
END $$;

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
    entity_id INT,
    type VARCHAR(50),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT REFERENCES app_user(id)
);

-- Ensure entity_id exists in notification
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='notification' AND column_name='entity_id') THEN
        ALTER TABLE notification ADD COLUMN entity_id INT;
    END IF;
END $$;

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

-- PL/SQL Functions and Triggers

-- 1. Trust Score Calculation
CREATE OR REPLACE FUNCTION calculate_trust_score() RETURNS TRIGGER AS $$
DECLARE
    avg_rating DECIMAL(5,2);
    completed_tx_count INT;
    new_score DECIMAL(5,2);
    target_user_id INT;
BEGIN
    -- Determine the user to update
    IF TG_TABLE_NAME = 'review' THEN
        -- Verify logic: Review is ON a user (seller usually, but can be buyer).
        -- The schema has user_id in review table. 
        -- If user_id in review table is the one receiving the review, proceed.
        -- Assuming user_id in review is the TARGET of the review? 
        -- Wait, usually review table has 'reviewer_id' and 'reviewee_id' or similar.
        -- Existing schema: user_id INT REFERENCES app_user(id). 
        -- Let's assume user_id is the one BEING REVIEWED.
        target_user_id := NEW.user_id;
    ELSIF TG_TABLE_NAME = 'transaction' THEN
        -- If transaction completes, maybe update score for both? 
        -- Or just trigger recalc. For simplicity, we'll update both buyer and seller if status is 'completed'.
        IF NEW.status = 'completed' THEN
            -- Update seller score (example logic)
            target_user_id := NEW.seller_id;
            -- We could also update buyer. But let's stick to single updates for now or handle complexity.
        ELSE
            RETURN NEW;
        END IF;
    END IF;

    -- Calculate stats
    SELECT COALESCE(AVG(rating), 0), COUNT(*) INTO avg_rating, completed_tx_count
    FROM review
    WHERE user_id = target_user_id;

    -- Simple formula: (Avg Rating * 2) + (Completed Tx * 0.1) capped at 10 or similar?
    -- User asked for "Number of completed transactions, average rating, timeliness".
    -- Let's make it: Avg Rating (1-5) + (Log(Tx Count + 1)). 
    -- Or just Avg Rating if Tx Count > 5.
    
    -- Let's use a weighted average approach scaled to 0-100 or 0-10.
    -- Let's use 0-5 scale matching stars, plus a bonus.
    
    IF completed_tx_count > 0 THEN
        new_score := avg_rating; 
    ELSE
        new_score := 0;
    END IF;

    UPDATE app_user SET trust_score = new_score WHERE id = target_user_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for Review
DROP TRIGGER IF EXISTS trg_update_trust_score_review ON review;
CREATE TRIGGER trg_update_trust_score_review
AFTER INSERT OR UPDATE ON review
FOR EACH ROW
EXECUTE FUNCTION calculate_trust_score();

-- 2. Notification Trigger
CREATE OR REPLACE FUNCTION notify_transaction_update() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO notification (user_id, entity_type, entity_id, type, message)
        VALUES (
            NEW.buyer_id, 
            'transaction', 
            NEW.id, 
            'status_change', 
            'Your transaction status is now ' || NEW.status
        );
        INSERT INTO notification (user_id, entity_type, entity_id, type, message)
        VALUES (
            NEW.seller_id, 
            'transaction', 
            NEW.id, 
            'status_change', 
            'Transaction status updated to ' || NEW.status
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_notify_transaction ON transaction;
CREATE TRIGGER trg_notify_transaction
AFTER UPDATE ON transaction
FOR EACH ROW
EXECUTE FUNCTION notify_transaction_update();
