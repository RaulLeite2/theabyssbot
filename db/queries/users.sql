INSERT INTO users (discord_id, level, base_hp)
VALUES ($1, 1, 100)
ON CONFLICT (discord_id) DO NOTHING;
