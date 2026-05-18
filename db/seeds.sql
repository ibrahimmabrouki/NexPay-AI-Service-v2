-- Seed data for NexPay AI Backend
-- WARNING: This file will insert sample rows; adjust IDs as needed.

-- Clear existing rows (safe for development only)
TRUNCATE TABLE stripe_topups, currency_conversions, transfers, ledger_transactions, users RESTART IDENTITY CASCADE;

-- Users
INSERT INTO users (id, full_name, phone_number) VALUES
('user-1', 'Alice Example', '+96170000001'),
('user-2', 'Bob Example', '+96170000002');

-- Ledger transactions
INSERT INTO ledger_transactions (id, user_id, type, amount, currency, reference_id, reference_type, created_at, embedded) VALUES
('lt-1', 'user-1', 'credit', 1000, 'USD', 'topup-1', 'topup', NOW(), false),
('lt-2', 'user-1', 'debit', 200, 'USD', 'transfer-1', 'transfer', NOW(), false),
('lt-3', 'user-2', 'credit', 500, 'USD', 'stripe-1', 'stripe_topup', NOW(), false);

-- Transfers
INSERT INTO transfers (id, sender_id, receiver_id, amount, currency, created_at) VALUES
('tr-1', 'user-1', 'user-2', 200, 'USD', NOW());

-- Currency conversions
INSERT INTO currency_conversions (id, user_id, from_currency, to_currency, amount_from, amount_to, created_at) VALUES
('cc-1', 'user-1', 'USD', 'LBP', 100, 150000, NOW());

-- Stripe topups
INSERT INTO stripe_topups (id, user_id, amount, currency, created_at) VALUES
('st-1', 'user-2', 500, 'USD', NOW());
