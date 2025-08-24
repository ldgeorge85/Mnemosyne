-- Create test users matching the static auth provider
-- Password hashes are for test123, admin123, demo123 respectively

INSERT INTO users (id, username, email, hashed_password, is_active, is_superuser, created_at, updated_at)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'test', 'test@mnemosyne.local', 
     '$2b$12$tQKpQ1qXfYL6k1Yx9tXpF.zV5vz5V7Y5V7Y5V7Y5V7Y5V7Y5V7Y5V', true, false, NOW(), NOW()),
    ('22222222-2222-2222-2222-222222222222', 'admin', 'admin@mnemosyne.local',
     '$2b$12$tQKpQ1qXfYL6k1Yx9tXpF.zV5vz5V7Y5V7Y5V7Y5V7Y5V7Y5V7Y5V', true, true, NOW(), NOW()),
    ('33333333-3333-3333-3333-333333333333', 'demo', 'demo@mnemosyne.local',
     '$2b$12$tQKpQ1qXfYL6k1Yx9tXpF.zV5vz5V7Y5V7Y5V7Y5V7Y5V7Y5V7Y5V', true, false, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;