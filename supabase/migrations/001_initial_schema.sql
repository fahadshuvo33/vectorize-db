/* 
====================================================================
   MASTER SCHEMA: USER, SUBSCRIPTION, SUPPORT, NOTIFICATION, COUPONS
====================================================================
*/

-- 1. CLEANUP (Optional: Only run this if you want to wipe the db and start fresh)
-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;

-- ==========================================
-- SECTION A: ENUMS (Must be created first)
-- ==========================================

-- User & Auth
CREATE TYPE notification_type AS ENUM ('email', 'in_app', 'push');
CREATE TYPE notification_category AS ENUM ('account', 'billing', 'system', 'promotion');
CREATE TYPE email_status AS ENUM ('pending', 'sent', 'failed');

-- Support
CREATE TYPE ticket_category AS ENUM ('general', 'bug', 'feature_request', 'billing', 'account_deletion');
CREATE TYPE ticket_status AS ENUM ('open', 'in_progress', 'waiting_on_user', 'resolved', 'closed');
CREATE TYPE ticket_priority AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE sender_type AS ENUM ('user', 'support_agent', 'system');

-- Subscription & Plans
CREATE TYPE plan_status AS ENUM ('draft', 'pending_approval', 'approved', 'rejected');
CREATE TYPE subscription_type AS ENUM ('standard', 'custom');
CREATE TYPE billing_cycle AS ENUM ('monthly', 'annual');
CREATE TYPE sub_status AS ENUM ('active', 'paused', 'canceled');
CREATE TYPE upgrade_type AS ENUM ('standard_to_standard', 'standard_to_custom', 'custom_to_custom');
CREATE TYPE urgency AS ENUM ('immediate', 'next_cycle', 'flexible');
CREATE TYPE request_status AS ENUM ('pending', 'offer_sent', 'accepted', 'rejected', 'expired', 'completed');
CREATE TYPE offer_type AS ENUM ('prorated', 'custom_price', 'discount', 'free_days');
CREATE TYPE offer_status AS ENUM ('pending', 'sent', 'accepted', 'rejected', 'expired');

-- Finance
CREATE TYPE transaction_type AS ENUM ('subscription', 'upgrade', 'credit', 'refund');
CREATE TYPE transaction_status AS ENUM ('succeeded', 'pending', 'failed');
CREATE TYPE discount_type AS ENUM ('percentage', 'flat_amount');
CREATE TYPE coupon_duration AS ENUM ('once', 'repeating', 'forever');


-- ==========================================
-- SECTION B: USERS & PROFILES
-- ==========================================

-- 1. PROFILES (Linked to Supabase Auth)
CREATE TABLE profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    
    is_email_verified BOOLEAN DEFAULT FALSE,
    has_password BOOLEAN DEFAULT FALSE,
    
    referral_code VARCHAR(20),
    referred_by VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_profiles_referral ON profiles(referral_code);

-- 2. SOCIAL ACCOUNTS
CREATE TABLE social_accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    
    provider VARCHAR(50) NOT NULL,
    provider_id VARCHAR(255) NOT NULL,
    email TEXT NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    
    access_token JSONB NOT NULL,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    raw_data JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_social_user ON social_accounts(user_id);

-- 3. USAGE STATS (Daily Tracking)
CREATE TABLE usage_stats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    date DATE NOT NULL,
    
    conversions_used INTEGER DEFAULT 0,
    chats_used INTEGER DEFAULT 0,
    api_requests INTEGER DEFAULT 0,
    app_bot_messages INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_usage_user_date ON usage_stats(user_id, date);


-- ==========================================
-- SECTION C: NOTIFICATIONS
-- ==========================================

-- 4. TEMPLATES
CREATE TABLE notification_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    slug VARCHAR(50) NOT NULL,
    type notification_type NOT NULL,
    category notification_category DEFAULT 'system',
    
    subject_template VARCHAR(255),
    body_template TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_template_slug ON notification_templates(slug, type);

-- 5. IN-APP NOTIFICATIONS
CREATE TABLE in_app_notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    
    category notification_category NOT NULL,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    action_link VARCHAR(255),
    
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    data JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_notif_user_read ON in_app_notifications(user_id, is_read);

-- 6. EMAIL LOGS
CREATE TABLE email_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    template_id UUID REFERENCES notification_templates(id),
    
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    status email_status DEFAULT 'pending',
    
    context_data JSONB,
    provider_response JSONB,
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ==========================================
-- SECTION D: SUPPORT & CHAT
-- ==========================================

-- 7. SUPPORT TICKETS
CREATE TABLE support_tickets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    
    subject VARCHAR(255) NOT NULL,
    category ticket_category DEFAULT 'general',
    status ticket_status DEFAULT 'open',
    priority ticket_priority DEFAULT 'medium',
    
    assigned_to VARCHAR(50),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_ticket_user ON support_tickets(user_id);
CREATE INDEX idx_ticket_status ON support_tickets(status);

-- 8. TICKET MESSAGES
CREATE TABLE ticket_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ticket_id UUID REFERENCES support_tickets(id) ON DELETE CASCADE NOT NULL,
    
    sender_id VARCHAR(50) NOT NULL,
    sender_type sender_type NOT NULL,
    
    message TEXT NOT NULL,
    attachments JSONB,
    is_internal BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. APP REVIEWS
CREATE TABLE app_reviews (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment VARCHAR(1000),
    is_public BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ==========================================
-- SECTION E: SUBSCRIPTIONS & PLANS
-- ==========================================

-- 10. PLANS
CREATE TABLE plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    
    monthly_price DOUBLE PRECISION NOT NULL,
    annual_price DOUBLE PRECISION,
    
    file_limit INTEGER NOT NULL,
    row_limit INTEGER NOT NULL,
    daily_convert INTEGER NOT NULL,
    api_access BOOLEAN DEFAULT FALSE,
    priority_support BOOLEAN DEFAULT FALSE,
    
    display_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    icon_color VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 11. CUSTOM PLANS
CREATE TABLE custom_plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    
    plan_name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    
    file_limit INTEGER NOT NULL,
    row_limit INTEGER NOT NULL,
    daily_convert INTEGER NOT NULL,
    api_access BOOLEAN DEFAULT FALSE,
    priority_support BOOLEAN DEFAULT FALSE,
    
    requested_price DOUBLE PRECISION NOT NULL,
    approved_price DOUBLE PRECISION,
    annual_price DOUBLE PRECISION,
    
    status plan_status DEFAULT 'draft',
    admin_notes VARCHAR(500),
    reviewed_by VARCHAR(50),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    
    is_active BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 12. SUBSCRIPTIONS
CREATE TABLE subscriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    
    plan_id UUID REFERENCES plans(id),
    custom_plan_id UUID REFERENCES custom_plans(id),
    
    subscription_type subscription_type NOT NULL,
    
    monthly_price DOUBLE PRECISION NOT NULL,
    annual_price DOUBLE PRECISION,
    
    billing_start_date DATE NOT NULL,
    billing_end_date DATE NOT NULL,
    billing_cycle billing_cycle DEFAULT 'monthly',
    auto_renew BOOLEAN DEFAULT TRUE,
    
    status sub_status DEFAULT 'active',
    
    last_upgrade_request_id VARCHAR(50),
    last_upgrade_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_user_active_subscription UNIQUE (user_id, status)
);
CREATE INDEX idx_sub_user_status ON subscriptions(user_id, status);

-- 13. SUBSCRIPTION USAGE
CREATE TABLE subscription_usage (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    
    files_used INTEGER DEFAULT 0,
    rows_used INTEGER DEFAULT 0,
    daily_converts_used INTEGER DEFAULT 0,
    api_calls_used INTEGER DEFAULT 0,
    
    files_remaining INTEGER,
    rows_remaining INTEGER,
    daily_convert_remaining INTEGER,
    
    usage_date DATE NOT NULL,
    last_daily_reset TIMESTAMP WITH TIME ZONE,
    last_monthly_reset TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_sub_date UNIQUE (subscription_id, usage_date)
);

-- 14. UPGRADE REQUESTS
CREATE TABLE upgrade_requests (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE NOT NULL,
    
    from_plan_id UUID REFERENCES plans(id),
    from_custom_plan_id UUID REFERENCES custom_plans(id),
    
    to_plan_id UUID REFERENCES plans(id),
    to_custom_plan_id UUID REFERENCES custom_plans(id),
    
    upgrade_type upgrade_type NOT NULL,
    
    reason VARCHAR(255),
    urgency urgency DEFAULT 'flexible',
    status request_status DEFAULT 'pending',
    
    admin_reviewed_at TIMESTAMP WITH TIME ZONE,
    offer_sent_at TIMESTAMP WITH TIME ZONE,
    user_responded_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 15. UPGRADE OFFERS
CREATE TABLE upgrade_offers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- ... Continuing from upgrade_offers table

    upgrade_request_id UUID REFERENCES upgrade_requests(id) ON DELETE CASCADE NOT NULL,
    
    offer_type offer_type NOT NULL,
    
    current_plan_price DOUBLE PRECISION,
    new_plan_price DOUBLE PRECISION,
    days_remaining INTEGER,
    days_in_cycle INTEGER,
    
    credit_balance DOUBLE PRECISION,
    credit_applied DOUBLE PRECISION,
    charge_amount DOUBLE PRECISION,
    
    discount_percentage INTEGER DEFAULT 0,
    discount_reason VARCHAR(255),
    bonus_free_days INTEGER DEFAULT 0,
    
    admin_notes VARCHAR(500),
    calculated_by VARCHAR(50),
    
    valid_until TIMESTAMP WITH TIME ZONE,
    status offer_status DEFAULT 'pending',
    
    user_decision VARCHAR(50),
    user_response_at TIMESTAMP WITH TIME ZONE,
    user_notes VARCHAR(500),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- 16. BILLING HISTORY
CREATE TABLE billing_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) NOT NULL,
    subscription_id UUID REFERENCES subscriptions(id),
    
    upgrade_request_id UUID REFERENCES upgrade_requests(id),
    upgrade_offer_id UUID REFERENCES upgrade_offers(id),
    
    amount DOUBLE PRECISION NOT NULL,
    
    transaction_type transaction_type NOT NULL,
    
    payment_processor VARCHAR(50),
    processor_transaction_id VARCHAR(255),
    invoice_number VARCHAR(50),
    
    status transaction_status DEFAULT 'pending',
    
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Indexes for Billing
CREATE INDEX idx_bill_user_date ON billing_history(user_id, created_at);
CREATE INDEX idx_bill_status ON billing_history(status);
CREATE INDEX idx_bill_subscription_id ON billing_history(subscription_id);


-- ==========================================
-- SECTION F: COUPONS
-- ==========================================

-- 17. COUPONS
CREATE TABLE coupons (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    
    discount_type discount_type NOT NULL,
    discount_value DOUBLE PRECISION NOT NULL,
    
    duration coupon_duration DEFAULT 'once',
    duration_in_months INTEGER,
    
    max_redemptions INTEGER, -- NULL = Unlimited
    times_redeemed INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB, -- For influencer tracking etc
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_coupon_code ON coupons(code);

-- 18. COUPON REDEMPTIONS
CREATE TABLE coupon_redemptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    coupon_id UUID REFERENCES coupons(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    
    -- Links this redemption to a specific payment
    billing_history_id UUID REFERENCES billing_history(id) ON DELETE CASCADE NOT NULL,
    
    discount_amount_applied DOUBLE PRECISION NOT NULL,
    redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ==========================================
-- SECTION G: AUTOMATION (TRIGGERS)
-- ==========================================

/* 
   CRITICAL: 
   This function automatically creates a Public Profile 
   whenever a user signs up via Supabase Auth.
*/

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url, created_at, updated_at)
  VALUES (
    new.id, 
    new.email, 
    new.raw_user_meta_data->>'full_name', 
    new.raw_user_meta_data->>'avatar_url',
    now(),
    now()
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger the function on new user creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();