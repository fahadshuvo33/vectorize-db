CORE TABLES
1. profiles

Purpose: Store user profile information extending Supabase Auth
Relationships: Links to auth.users (1:1)
Field	Type	Description	Why Added
id	UUID	Primary key, references auth.users.id	Links to Supabase authentication system
full_name	TEXT	User's display name	For personalization in UI and emails
avatar_url	TEXT	Profile picture URL	Visual identification, social proof
current_plan	TEXT	Active plan slug ('basic', 'standard', 'premium', 'business', 'custom')	Determines user's access level and limits
plan_ends_at	TIMESTAMPTZ	When current paid plan expires	Handle subscription renewals and grace periods
referral_code	TEXT (UNIQUE)	Unique 8-character code for referrals	Viral growth - users can share their code
referred_by	UUID (FK)	ID of user who referred this user	Track referral chain for rewards
created_at	TIMESTAMPTZ	Account creation timestamp	User lifetime analytics
updated_at	TIMESTAMPTZ	Last profile update	Track profile modifications

Indexes:

    profiles(id) - Primary key
    profiles(referral_code) - Fast referral lookup
    profiles(referred_by) - Referral analytics



2. social_logins

Purpose: Store OAuth provider data for social authentication
Relationships: Links to auth.users (Many:1) - user can have multiple providers
Field	Type	Description	Why Added
id	UUID	Primary key	Unique identifier for each social login
user_id	UUID (FK)	References auth.users.id	Link social account to user
provider	TEXT	OAuth provider name ('google', 'github')	Identify which service user logged in with
provider_id	TEXT	Provider's unique user ID	Match user across sessions
email	TEXT	Email from OAuth provider	Auto-verified email, no confirmation needed
name	TEXT	Full name from OAuth	Pre-fill profile data
avatar_url	TEXT	Profile picture from OAuth	Instant avatar without upload
raw_data	JSONB	Complete OAuth response	Store extra data (locale, verified status, etc.)
access_token	TEXT	OAuth access token (encrypted)	API calls to provider if needed
refresh_token	TEXT	OAuth refresh token (encrypted)	Renew access without re-login
token_expires_at	TIMESTAMPTZ	When access token expires	Know when to refresh
created_at	TIMESTAMPTZ	First login with this provider	Track when user added provider

Indexes:

    social_logins(user_id) - Get all providers for user
    social_logins(provider, provider_id) - Fast OAuth lookup

Unique Constraints:

    (provider, provider_id) - One account per provider

3. files_original

Purpose: Store metadata for uploaded files
Relationships: Links to auth.users (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique file identifier
user_id	UUID (FK)	File owner	Row-level security, usage tracking
filename	TEXT	Stored filename (UUID-based)	Avoid collisions, security
original_name	TEXT	User's original filename	Display in UI ("products.csv")
size_bytes	BIGINT	File size in bytes	Enforce upload limits, storage analytics
mime_type	TEXT	File MIME type	Validate file types, security
storage_path	TEXT	R2/S3 path to file	Retrieve file for processing
uploaded_at	TIMESTAMPTZ	Upload timestamp	Audit trail, cleanup old files

Indexes:

    files_original(user_id) - User's files dashboard
    files_original(uploaded_at DESC) - Recent files first

4. files_converted

Purpose: Store processed/converted output files
Relationships: Links to files_original (Many:1) and auth.users (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique converted file ID
user_id	UUID (FK)	File owner	Security, quota tracking
original_file_id	UUID (FK)	Source file reference	Link output to input
filename	TEXT	Output filename	Download label
output_type	TEXT	Format ('vector', 'jsonl', 'parquet', 'rag_code')	What user can download
embedding_model	TEXT	Model used ('minilm', 'openai')	Show user which model was used
row_count	INT	Number of rows processed	Display stats, validate success
storage_path	TEXT	R2/S3 path	Download endpoint
config_snapshot	JSONB	Conversion settings	Reproducibility, show user what was done
created_at	TIMESTAMPTZ	Conversion timestamp	Sort outputs, cleanup old files

Indexes:

    files_converted(user_id) - User's conversions
    files_converted(original_file_id) - All outputs for one input

Unique Constraints:

    (original_file_id, output_type) - One output per type per file (replace on re-convert)

5. conversion_steps

Purpose: Audit trail of data processing steps
Relationships: Links to files_converted (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique step ID
converted_file_id	UUID (FK)	Which conversion this belongs to	Group steps together
step_order	INT	Sequence number (1, 2, 3...)	Replay processing in order
action	TEXT	Step type ('select_columns', 'remove_duplicates', 'fill_missing', 'embed')	What operation was performed
details	JSONB	Step parameters	Exact settings for reproducibility
created_at	TIMESTAMPTZ	When step executed	Debug timing issues

Example JSONB:
{
  "columns_selected": ["name", "price", "description"],
  "fill_strategy": "mean",
  "embedding_config": {
    "model": "all-MiniLM-L6-v2",
    "batch_size": 32
  }
}

Indexes:

    conversion_steps(converted_file_id, step_order) - Ordered step retrieval

Unique Constraints:

    (converted_file_id, step_order) - No duplicate step numbers

6. chat_sessions

Purpose: Chat conversation containers (both user data chats and app help bot)
Relationships: Links to auth.users (Many:1) and files_converted (Many:1, optional)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique session ID
user_id	UUID (FK)	Session owner (NULL for anonymous app_bot)	Ownership, limits enforcement
converted_file_id	UUID (FK)	Data file being chatted with (NULL for app_bot)	Link chat to specific dataset
session_type	TEXT	'user' or 'app_bot'	Different limits for data chat vs help bot
title	TEXT	Session name ("Chat with products.csv")	Sidebar display, history
is_visible	BOOLEAN	Show in sidebar	Hide old sessions for Basic/Standard users
message_count	INT	Total messages in session	Quick count without scanning messages
expires_at	TIMESTAMPTZ	When session auto-deletes	Plan-based retention (1h Basic, 24h Standard, 30d Premium)
created_at	TIMESTAMPTZ	Session start time	Sort by recency
last_active	TIMESTAMPTZ	Last message timestamp	Auto-expire inactive sessions

Indexes:

    chat_sessions(user_id, is_visible, created_at DESC) - Sidebar recent chats
    chat_sessions(expires_at) - Cleanup job

7. chat_messages

Purpose: Individual messages within chat sessions
Relationships: Links to chat_sessions (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique message ID
session_id	UUID (FK)	Parent chat session	Group messages together
role	TEXT	'user' or 'assistant'	Who sent the message
content	TEXT	Message text	The actual chat content
created_at	TIMESTAMPTZ	Message timestamp	Display in chronological order

Indexes:

    chat_messages(session_id, created_at) - Fetch conversation in order

Why no JSON file storage:

    PostgreSQL enables search, pagination, analytics
    RLS for security
    Message-level permissions
    Future: message reactions, edits, sharing

8. usage_stats

Purpose: Daily usage tracking per user for quota enforcement
Relationships: Links to auth.users (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique stat record
user_id	UUID (FK)	User being tracked	Link stats to user
date	DATE	Stats date	Daily granularity
conversions_used	INT	Files converted today/month	Enforce plan limits
chats_used	INT	Data chats started today	Daily chat limits
api_requests	INT	API calls made today	Rate limiting
app_bot_messages	INT	Help bot messages sent today	Separate limit from data chats
updated_at	TIMESTAMPTZ	Last stat update	Real-time tracking

Indexes:

    usage_stats(user_id, date DESC) - Recent usage lookup

Unique Constraints:

    (user_id, date) - One record per user per day

Cleanup:

    Delete records older than 90 days (keep recent for analytics)

PLAN & FEATURE SYSTEM
9. plans

Purpose: Available subscription plans (catalog)
Relationships: Standalone reference table
Field	Type	Description	Why Added
id	UUID	Primary key	Unique plan identifier
slug	TEXT (UNIQUE)	URL-safe identifier ('basic', 'standard', 'premium', 'business', 'custom')	Code references, URL routing
name	TEXT	Display name ("Standard Plan")	Marketing copy
description	TEXT	Plan description	Pricing page
price_monthly	BIGINT	Monthly price in cents (1500 = $15)	Billing integration
price_yearly	BIGINT	Yearly price in cents	Annual discount option
is_custom	BOOLEAN	True for business/custom plans	Hide from public pricing page
is_visible	BOOLEAN	Show on pricing page	A/B testing, phased rollouts
sort_order	INT	Display order (1, 2, 3...)	Pricing page layout
created_at	TIMESTAMPTZ	Plan creation date	Audit trail

Indexes:

    plans(slug) - Fast plan lookup


10. features

Purpose: Catalog of all available features (independent of plans)
Relationships: Standalone reference table
Field	Type	Description	Why Added
id	UUID	Primary key	Unique feature ID
key	TEXT (UNIQUE)	Code identifier ('max_conversions_month', 'api_access')	API feature checks
name	TEXT	Display name ("Monthly Conversions")	UI labels
description	TEXT	Feature explanation	Help text, tooltips
category	TEXT	Group ('limits', 'access', 'api', 'analysis')	Organize in UI
value_type	TEXT	Data type ('number', 'boolean', 'string', 'json')	Validate values
default_value	TEXT	Fallback value ('0', 'false')	Used if no plan/override exists
is_active | BOOLEAN | Feature enabled globally | Kill switch for features |
| sort_order | INT | Display order in UI | Feature list organization |
| created_at | TIMESTAMPTZ | Feature creation date | Version tracking |

Indexes:

    features(key) - Fast feature lookup
    features(category, sort_order) - Grouped feature display

Limits:
- max_conversions_month (number)
- max_chats_day (number)
- max_rows (number)
- chat_expiry_hours (number)

Access:
- show_chat_history (boolean)
- api_access (boolean)
- webhook_access (boolean)
- priority_support (boolean)

API:
- api_rate_limit_rpm (number)
- supported_db_types (string: "mysql,postgres,mongodb")
- export_formats (string: "csv,json,parquet,sql")

Bot & Trial:
- website_bot_messages_day (number)
- trial_chats_per_db (number)

Advanced:
- openai_embeddings (boolean)
- data_analysis (boolean)

11. plan_features

Purpose: Junction table - which features each plan includes
Relationships: Links plans (Many:1) to features (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique association ID
plan_id	UUID (FK)	References plans.id	Which plan
feature_id	UUID (FK)	References features.id	Which feature
feature_value	TEXT	Feature value for this plan ('50', 'true', '-1')	Plan-specific limits
is_included	BOOLEAN	Feature enabled for this plan	Quick on/off toggle
created_at	TIMESTAMPTZ	When feature added to plan	Audit changes


Basic Plan:
- max_conversions_month = 5
- api_access = false
- website_bot_messages_day = 5

Standard Plan:
- max_conversions_month = 50
- api_access = true
- api_rate_limit_rpm = 60

Premium Plan:
- max_conversions_month = -1 (unlimited)
- api_access = true
- api_rate_limit_rpm = 300

Indexes:

    plan_features(plan_id) - Get all features for a plan
    plan_features(feature_id) - See which plans have a feature

Unique Constraints:

    (plan_id, feature_id) - One value per feature per plan


Why This Design:

    Adding new feature = insert into features table only
    Changing plan limits = update plan_features row
    No schema changes for new features
    Custom plans = create new plan + copy features + modify values

12. user_features

Purpose: User-specific feature overrides (custom plans, promotions)
Relationships: Links auth.users (Many:1) to features (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique override ID
user_id	UUID (FK)	References auth.users.id	Which user
feature_id	UUID (FK)	References features.id	Which feature to override
feature_value	TEXT	Custom value	Override plan default
is_override	BOOLEAN	True = ignore plan value	Toggle override on/off
granted_by	UUID (FK)	Admin who granted override	Accountability
granted_reason	TEXT	Why override was given	"Beta tester", "Complaint resolution"
expires_at	TIMESTAMPTZ	Override expiration (NULL = permanent)	Temporary promotions
created_at	TIMESTAMPTZ	When override created	Audit trail

Use Cases:

    Custom Business Plan: User wants 200 conversions/month instead of 50
    Beta Tester: Give premium features for free temporarily
    Complaint Resolution: Grant extra quota after service issue
    Influencer Deal: Unlimited access for 6 months

Indexes:

    user_features(user_id) - Get all overrides for user
    user_features(expires_at) - Cleanup expired overrides

Unique Constraints:

    (user_id, feature_id) - One override per feature per user

Priority Logic:
1. Check user_features (highest priority)
2. If not found, check plan_features
3. If not found, use features.default_value

13. subscription_changes

Purpose: Complete audit trail of all plan changes (upgrades only, no downgrades)
Relationships: Links to auth.users (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique change ID
user_id	UUID (FK)	User who changed plan	Link to user
from_plan	TEXT	Previous plan slug (NULL if new subscription)	Track upgrade path
to_plan	TEXT	New plan slug	Where user upgraded to
change_type	TEXT	'new', 'upgrade', 'cancel'	Type of change
proration_option	TEXT	'immediate_charge' or 'next_cycle'	User's choice for billing
old_price	BIGINT	Previous plan price (cents)	Calculate savings
new_price	BIGINT	New plan price (cents)	New billing amount
days_remaining	INT	Days left in current cycle	Proration calculation
proration_credit	BIGINT	Unused amount from old plan (cents)	What user gets back
proration_charge	BIGINT	Additional charge for new plan (cents)	Prorated cost
total_charge	BIGINT	Actual amount charged (cents)	What user paid
effective_date	TIMESTAMPTZ	When change takes effect	Schedule change
stripe_invoice_id	TEXT	Stripe invoice reference	Link to payment
stripe_subscription_id	TEXT	Stripe subscription ID	Update subscription
created_at	TIMESTAMPTZ	When change was made	Audit timestamp

Why Track This:

    Revenue analytics: Track upgrade patterns
    User journey: Understand conversion funnel
    Support: "When did I upgrade?" questions
    Refund calculations: Know what user paid
    Compliance: Financial audit trail

Example Scenarios:

Scenario 1: Immediate Upgrade
Day 15 of Standard ($15/mo) → Premium ($39/mo)
- from_plan: 'standard'
- to_plan: 'premium'
- change_type: 'upgrade'
- proration_option: 'immediate_charge'
- days_remaining: 15
- proration_credit: 750 ($7.50)
- proration_charge: 1950 ($19.50)
- total_charge: 1200 ($12.00)
- effective_date: NOW()

Scenario 2: Next Cycle Upgrade
- proration_option: 'next_cycle'
- total_charge: 0 (nothing charged now)
- effective_date: (end of current cycle + 1 day)

Indexes:

    subscription_changes(user_id, created_at DESC) - User's change history
    subscription_changes(change_type) - Analytics by type

14. cancellation_requests

Purpose: Track subscription cancellations and refund eligibility
Relationships: Links to auth.users (Many:1) and payments (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique cancellation ID
user_id	UUID (FK)	User cancelling	Link to user
subscription_id	UUID (FK)	References payments.id	Which subscription to cancel
requested_at	TIMESTAMPTZ	When user clicked cancel	Timestamp for refund calculation
cancellation_type	TEXT	'immediate' or 'end_of_cycle'	User's choice
refund_eligibility	TEXT	'full', 'partial_50', 'none'	Calculated refund tier
refund_amount	BIGINT	Refund in cents	What user gets back
refund_reason	TEXT	User's cancellation reason (optional)	Feedback for improvement
days_used	INT	Days into billing cycle	Calculate fair refund
cancels_at	TIMESTAMPTZ	When access ends	Schedule termination
stripe_refund_id	TEXT	Stripe refund reference	Track refund in Stripe
status	TEXT	'pending', 'processed', 'refunded'	Cancellation state
created_at	TIMESTAMPTZ	Request timestamp	Audit trail

Refund Policy Logic:
Days 0-7:   100% refund ("Not what I expected")
Days 8-14:  50% refund ("Partial use")
Days 15+:   No refund, access until cycle end ("Fair use")
Why These Fields:

    refund_eligibility: Calculated by API based on days_used
    cancellation_type: User choice affects access immediately or later
    refund_reason: Collect feedback to improve product
    cancels_at: Schedule future termination (user keeps access)

Indexes:

    cancellation_requests(user_id) - User's cancellation history
    cancellation_requests(status) - Process pending cancellations

PAYMENTS & DISCOUNTS
15. payments

Purpose: Stripe subscription and payment records
Relationships: Links to auth.users (Many:1) and discount_codes (Many:1, optional)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique payment ID
user_id	UUID (FK)	Payment owner	Link to user
stripe_subscription_id	TEXT (UNIQUE)	Stripe subscription ID	Sync with Stripe
plan_slug	TEXT	Which plan purchased	Quick plan lookup
amount	BIGINT	Charged amount in cents	Revenue tracking
discount_code_id	UUID (FK)	References discount_codes.id (NULL if none)	Link to discount used
discount_applied	BIGINT	Discount amount in cents	Calculate net revenue
status	TEXT	'active', 'canceled', 'past_due', 'trialing'	Subscription state
current_period_end	TIMESTAMPTZ	When subscription renews	Renewal notifications
created_at	TIMESTAMPTZ	First payment date	Customer lifetime

Status Values:

    active: Subscription is paid and active
    trialing: In free trial period
    past_due: Payment failed, awaiting retry
    canceled: User cancelled, access may continue until period end

Why Track discount_code_id:

    Attribution: Which codes drive conversions
    ROI: Calculate discount effectiveness
    Prevent abuse: One code per user (check in user_discount_usage)

Indexes:

    payments(user_id) - User's payment history
    payments(stripe_subscription_id) - Webhook lookups
    payments(status) - Active subscriptions query

16. discount_codes

Purpose: Promotional discount codes for marketing campaigns
Relationships: Links to auth.users (Many:1, optional for creator tracking)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique discount ID
code	TEXT (UNIQUE)	Discount code ('LAUNCH50', 'YEARLY20')	User enters this
type	TEXT	'percent' or 'fixed'	Discount calculation method
value	BIGINT	50 = 50% OR 1500 = $15	Discount amount
plan_slug	TEXT	Restrict to plan (NULL = any plan)	Plan-specific promos
max_uses	INT	Total redemption limit (-1 = unlimited)	Prevent abuse
used_count	INT	Current redemptions	Track usage
created_by	UUID (FK)	Admin/affiliate who created code	Attribution for affiliates
valid_from	TIMESTAMPTZ	Code activation date	Schedule campaigns
valid_until	TIMESTAMPTZ	Code expiration date	Time-limited offers
is_active	BOOLEAN	Enable/disable code	Quick toggle
created_at	TIMESTAMPTZ	Creation timestamp	Audit trail

Example Codes:
LAUNCH50:
- type: 'percent'
- value: 50
- plan_slug: NULL (any plan)
- max_uses: 100
- valid_until: 2024-03-01

YEARLY20:
- type: 'percent'
- value: 20
- plan_slug: NULL
- max_uses: -1 (unlimited)
- valid_until: NULL (no expiration)

REFERRAL10:
- type: 'fixed'
- value: 1000 ($10)
- max_uses: -1

Why These Fields:

    created_by: Track affiliate/influencer codes
    used_count: Auto-increment when redeemed
    max_uses: Prevent going viral unintentionally
    plan_slug: "Premium only" exclusive offers

Indexes:

    discount_codes(code) - Fast lookup at checkout
    discount_codes(is_active, valid_until) - Valid codes query

17. user_discount_usage

Purpose: Prevent discount code abuse (track who used what)
Relationships: Links auth.users (Many:1) to discount_codes (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique usage record
user_id	UUID (FK)	User who used code	Link to user
discount_code_id	UUID (FK)	Code that was used	Link to discount
applied_at	TIMESTAMPTZ	When code was redeemed	Audit timestamp

Why This Table:

    Prevent abuse: User can't use LAUNCH50 twice by cancelling and re-subscribing
    One code per user: Enforce unique constraint
    Analytics: "Who used which codes" reporting

    Fraud detection: Flag suspicious patterns (same IP, same card, different accounts)

Unique Constraints:

    (user_id, discount_code_id) - One redemption per user per code

Validation Flow:
1. User enters "LAUNCH50" at checkout
2. Check discount_codes: is_active=true, not expired, max_uses not exceeded
3. Check user_discount_usage: user hasn't used this code before
4. Apply discount to Stripe checkout
5. Insert record into user_discount_usage
6. Increment discount_codes.used_count

Indexes:

    user_discount_usage(user_id) - User's discount history
    user_discount_usage(discount_code_id) - Code usage analytics

GROWTH & ENGAGEMENT
18. referral_rewards

Purpose: Track referral program rewards ("Give 10,Get10,Get10")
Relationships: Links to profiles (Many:1 for both referrer and referred)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique reward ID
referrer_id	UUID (FK)	References profiles.id (person who referred)	Who gets the reward
referred_id	UUID (FK)	References profiles.id (person who signed up)	Who triggered the reward
reward_type	TEXT	'discount', 'free_month', 'credits', 'cash'	Type of reward
reward_value	BIGINT	Amount in cents or credits	Reward quantity
status	TEXT	'pending', 'applied', 'expired', 'cancelled'	Reward state
applied_at	TIMESTAMPTZ	When reward was redeemed (NULL if pending)	Track redemption
expires_at	TIMESTAMPTZ	Reward expiration (e.g., 90 days)	Encourage fast redemption
created_at	TIMESTAMPTZ	When referral completed	Track referral velocity

Status Flow:
1. pending: Referred user signed up, reward created
2. applied: Referred user paid → referrer gets reward
3. expired: Referred user never paid within 90 days
4. cancelled: Referred user refunded within 30 days

Reward Types:

    discount: 50% off next month (value = 50)
    free_month: One month free (value = plan price)
    credits: Platform credits (value = credit amount)
    cash: PayPal/bank payout for affiliates (value = cash amount)

Example Scenarios:

Scenario 1: Standard Referral
- User A shares referral code "ALICE123"
- User B signs up using "ALICE123"
- Insert reward: status='pending', reward_type='discount', reward_value=1000 ($10)
- User B pays for Standard plan ($15)
- Update reward: status='applied'
- User A gets $10 credit or discount code
Scenario 2: Expired Referral
- User A refers User B
- Reward created: status='pending', expires_at=NOW()+90 days
- User B never upgrades to paid plan
- Cron job after 90 days: status='expired'

Why Track This:

    Viral coefficient: How many users does each user bring?
    Attribution: Which users are best advocates?
    Payout tracking: Who to pay for affiliate program
    Fraud detection: Prevent self-referrals

Indexes:

    referral_rewards(referrer_id, status) - User's pending rewards
    referral_rewards(referred_id) - Check if signup came from referral
    referral_rewards(expires_at) - Cleanup expired rewards

19. blog_posts

Purpose: SEO-optimized blog content for organic traffic
Relationships: Links to auth.users (Many:1) for author
Field	Type	Description	Why Added
id	UUID	Primary key	Unique post ID
slug	TEXT (UNIQUE)	URL-safe identifier ('how-to-convert-csv-to-ai')	SEO-friendly URLs
title	TEXT	Post headline	Browser title, social shares
content_html	TEXT	Full HTML content	Rich text with images, code blocks
excerpt	TEXT	Short summary (150-200 chars)	Meta description, post previews
author_id	UUID (FK)	Post author	Attribution, multi-author support
published	BOOLEAN	Visibility flag	Draft vs published state
published_at	TIMESTAMPTZ	Publication date (NULL if draft)	Sort by recency, schedule posts
created_at	TIMESTAMPTZ	Creation timestamp	Author dashboard
updated_at	TIMESTAMPTZ	Last edit timestamp	Show "Updated on..."

SEO Features:

    slug: Clean URLs like /blog/csv-to-ai-chatbot
    excerpt: Auto-fills meta description
    published_at: Schedule future posts
    content_html: Supports rich media, code syntax highlighting

Content Strategy:
Target Keywords:
- "convert CSV to AI"
- "database to chatbot"
- "RAG from Excel"
- "vector database tutorial"

Each post = potential customer acquisition channel
Why Store HTML:

    Flexibility: Supports images, videos, embeds
    Security: Sanitize before saving
    Performance: No Markdown parsing on each request
    Editor: Use rich text editor (TipTap, Quill)

Image Storage:

    Upload to Supabase Storage
    Store URLs in HTML: <img src="https://storage.../image.png">

Indexes:

    blog_posts(slug) - Fast post lookup
    blog_posts(published, published_at DESC) - Published posts, newest first
    blog_posts(author_id) - Author's posts dashboard

20. notifications

Purpose: In-app notification system (bell icon alerts)
Relationships: Links to auth.users (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique notification ID
user_id	UUID (FK)	Notification recipient	Who sees this
type	TEXT	'info', 'success', 'warning', 'upgrade_offer', 'feature_announcement'	Visual styling
title	TEXT	Notification headline	Bold text in notification
message	TEXT	Notification body	Detailed text
read	BOOLEAN	Read status (default false)	Mark as read functionality
action_url	TEXT	Optional link (NULL if none)	CTA: "View File", "Upgrade Now"
action_label	TEXT	Button text ("View", "Upgrade")	CTA label
created_at	TIMESTAMPTZ	Notification timestamp	Sort by recency

Notification Types:

1. System Notifications:
type: 'success'
title: "Your file is ready!"
message: "products.csv has been converted to vector embeddings"
action_url: "/files/abc123"
action_label: "Download"

2. Upgrade Prompts:
type: 'upgrade_offer'
title: "🚀 You've used 5/5 free conversions"
message: "Upgrade to Standard and get 50 conversions/month + API access"
action_url: "/pricing"
action_label: "Upgrade Now"

3. Feature Announcements:
type: 'info'
title: "New: MongoDB support!"
message: "You can now convert MongoDB exports to AI-ready format"
action_url: "/blog/mongodb-support"
action_label: "Learn More"

4. Usage Warnings:
type: 'warning'
title: "Chat session expiring soon"
message: "Your trial chat expires in 10 minutes. Upgrade to save your conversation."
action_url: "/pricing"
action_label: "Upgrade"

Why This Table:

    User engagement: Keep users informed
    Conversion prompts: Timely upgrade nudges
    Product updates: Announce new features
    Support: System status, maintenance alerts

API Endpoints:
GET /api/notifications - Get unread count + recent notifications
PATCH /api/notifications/:id/read - Mark as read
DELETE /api/notifications/:id - Dismiss notification

Indexes:

    notifications(user_id, read, created_at DESC) - Unread notifications first
    notifications(created_at) - Cleanup old read notifications (>30 days)

Cleanup Strategy:

    Keep unread notifications forever (until read)
    Delete read notifications after 30 days
    Keep upgrade_offer notifications until user upgrades

API & INTEGRATIONS
21. api_keys

Purpose: User-generated API keys for programmatic access
Relationships: Links to auth.users (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique key ID
user_id	UUID (FK)	Key owner	Link to user account
name	TEXT	Key label ("Production API", "Dev Testing")	User-friendly identifier
key_hash	TEXT	Hashed API key (bcrypt)	Security: never store plaintext
key_prefix	TEXT	First 8 chars ("dbm_abc...")	Display in UI without exposing full key
is_active	BOOLEAN	Enable/disable key	User can revoke without deleting
last_rate_limit_reset	TIMESTAMPTZ	Rate limit window start	Track current rate limit window
requests_this_minute	INT	Current window request count	Enforce rate limits
created_at	TIMESTAMPTZ	Key creation date	Audit trail
last_used	TIMESTAMPTZ	Last API call timestamp	Show "Last used 2 hours ago"

API Key Format:
dbm_1a2b3c4d5e6f7g8h9i0j  (32 chars after prefix)

Prefix: dbm_  (identifies VectorizeDB)
Secret: random 32-char alphanumeric

Why These Fields:

key_hash:

    Store bcrypt hash, never plaintext
    Show full key only once at creation
    API validates by hashing request key and comparing

key_prefix:

    Show "dbm_1a2b3c..." in UI
    User can identify which key without security risk

Rate Limiting (Simplified):
1. Request arrives with API key
2. Lookup api_keys by key_hash
3. Check: NOW() - last_rate_limit_reset > 1 minute?
   - YES: Reset requests_this_minute = 0, last_rate_limit_reset = NOW()
   - NO: Continue
4. Check: requests_this_minute >= user's limit (60 or 300 RPM)?
   - YES: Return 429 Too Many Requests
   - NO: Increment requests_this_minute, allow request
Security Features:

    Hash key before storing
    Rotate keys without deleting (create new, deactivate old)
    Track last_used for security monitoring
    is_active allows instant revocation

Indexes:

    api_keys(user_id, is_active) - User's active keys
    api_keys(key_hash) - Fast validation lookup

22. webhooks

Purpose: User-configured webhooks for event notifications
Relationships: Links to auth.users (Many:1)
Field	Type	Description	Why Added
id	UUID	Primary key	Unique webhook ID
user_id	UUID (FK)	Webhook owner	Link to user
url	TEXT	Webhook endpoint (https://user-app.com/webhook)	Where to send events
event_types	TEXT[]	Array of events to listen for	Selective event subscription
secret	TEXT	Webhook signing secret	Verify request authenticity
is_active	BOOLEAN	Enable/disable webhook	Toggle without deleting
retry_count	INT	Failed delivery attempts (default 0)	Track reliability issues
last_triggered	TIMESTAMPTZ	Most recent delivery (NULL if never)	Monitor webhook activity
last_success	TIMESTAMPTZ	Last successful delivery	Health monitoring
last_error	TEXT	Most recent error message	Debug failed deliveries
created_at	TIMESTAMPTZ	Webhook creation date	Audit trail

Available Event Types:
conversion.started      - File upload began processing
conversion.completed    - File ready for download
conversion.failed       - Processing error occurred
chat.session_created    - New chat started
chat.message_sent       - User sent message
chat.session_expired    - Chat auto-deleted
payment.succeeded       - Subscription paid
payment.failed          - Payment declined
plan.upgraded           - User upgraded plan
plan.cancelled          - User cancelled subscription

Webhook Payload Example:
POST https://user-app.com/webhook
Headers:
  X-VectorizeDB-Signature: sha256=abc123...
  X-VectorizeDB-Event: conversion.completed

Body:
{
  "id": "evt_1a2b3c4d",
  "type": "conversion.completed",
  "created_at": "2024-01-15T10:30:00Z",
  "data": {
    "user_id": "usr_abc123",
    "file_id": "file_xyz789",
    "filename": "products.csv",
    "row_count": 1500,
    "output_types": ["vector", "jsonl", "rag_code"],
    "download_url": "https://api.vectorizedb.com/v1/files/xyz789/download"
  }
}
Security - Signature Verification:
// User's backend verifies signature
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const hash = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');
  
  return `sha256=${hash}` === signature;
}
Retry Logic:
1. Send webhook POST request
2. If response is 2xx: Update last_success, reset retry_count
3. If response is 4xx/5xx or timeout:
   - Increment retry_count
   - Store error in last_error
   - Retry after: 1min, 5min, 30min (max 3 retries)
4. After 3 failures: Set is_active=false, notify user

Why These Fields:

event_types (array):

    User subscribes only to relevant events
    Reduces noise, improves performance
    Example: ['conversion.completed', 'payment.succeeded']

secret:

    Generated when webhook created
    User uses it to verify requests came from VectorizeDB
    Prevents spoofing attacks

retry_count:

    Track webhook reliability
    Auto-disable after repeated failures
    Alert user to fix their endpoint

last_error:

    Help user debug issues
    Show in UI: "Last error: Connection timeout"

Indexes:

    webhooks(user_id, is_active) - User's active webhooks
    webhooks(last_triggered) - Monitor webhook health

Plan Restrictions:

    Basic: No webhooks
    Standard: 5 webhooks max
    Premium: Unlimited webhooks

23. api_db_support

Purpose: Track which database types are supported by API version
Relationships: Standalone configuration table
Field	Type	Description	Why Added
id	UUID	Primary key	Unique support record
db_type	TEXT	Database type ('mysql', 'postgres', 'mongodb', 'sqlite', 'csv', 'excel', 'json')	What database
api_version	TEXT	API version ('v1', 'v2')	Version-specific support
is_supported	BOOLEAN	Feature flag	Enable/disable support
read_support	BOOLEAN	Can read from this DB	Read capabilities
write_support	BOOLEAN	Can write to this DB	Write capabilities
min_plan_required	TEXT	Minimum plan needed (NULL = all plans)	Premium-only DBs
features	JSONB	DB-specific features	Detailed capabilities
connection_info	JSONB	Connection requirements	Help docs data
created_at	TIMESTAMPTZ	Support added date	Version tracking

Example Data:

MySQL Support:
{
  "db_type": "mysql",
  "api_version": "v1",
  "is_supported": true,
  "read_support": true,
  "write_support": true,
  "min_plan_required": "standard",
  "features": {
    "direct_connection": true,
    "dump_file_import": true,
    "incremental_sync": false,
    "supported_versions": ["5.7", "8.0"],
    "max_connection_timeout": 30
  },
  "connection_info": {
    "required_fields": ["host", "port", "database", "username", "password"],
    "default_port": 3306,
    "ssl_supported": true
  }
}
MongoDB Support:
{
  "db_type": "mongodb",
  "api_version": "v1",
  "is_supported": true,
  "read_support": true,
  "write_support": false,
  "min_plan_required": "premium",
  "features": {
    "direct_connection": true,
    "dump_file_import": true,
    "incremental_sync": false,
    "supported_versions": ["4.4", "5.0", "6.0"],
    "authentication_methods": ["SCRAM", "X.509"]
  },
  "connection_info": {
    "required_fields": ["connection_string"],
    "example": "mongodb://user:pass@host:27017/db",
    "atlas_supported": true
  }
}
CSV/Excel (Always Free):
{
  "db_type": "csv",
  "api_version": "v1",
  "is_supported": true,
  "read_support": true,
  "write_support": true,
  "min_plan_required": null,
  "features": {
    "encoding_detection": true,
    "delimiter_auto_detect": true,
    "max_file_size_mb": 50,
    "streaming_upload": true
  }
}

Why This Table:

Dynamic Feature Rollout:

    Add MongoDB support without code deploy
    UPDATE api_db_support SET is_supported=true WHERE db_type='mongodb'

Plan-Based Access:

    Basic users: CSV, Excel, JSON only
    Standard users: + MySQL, PostgreSQL, SQLite
    Premium users: + MongoDB, advanced features

API Documentation:

    Auto-generate docs from this table
    Show supported DBs by plan
    Display connection requirements

Version Management:

    API v1 vs v2 may support different DBs
    Graceful deprecation path

Feature Flags:

    is_supported: Kill switch for problematic DBs
    read_support/write_support: Gradual rollout

Indexes:

    api_db_support(db_type, api_version) - Fast support lookup
    api_db_support(is_supported, min_plan_required) - Available DBs query

API Usage:
// Check if user can use MongoDB
GET /api/v1/supported-databases

Response:
{
  "databases": [
    {
      "type": "mysql",
      "available": true,
      "plan_required": "standard",
      "capabilities": ["read", "write"]
    },
    {
      "type": "mongodb",
      "available": false,  // User is on Standard plan
      "plan_required": "premium",
      "capabilities": ["read"]
    }
  ]
}

INDEXES SUMMARY

Critical Indexes (Must Have):
-- User lookups
profiles(id)
profiles(referral_code)

-- File operations
files_original(user_id, uploaded_at DESC)
files_converted(user_id)
files_converted(original_file_id, output_type)

-- Chat
chat_sessions(user_id, is_visible, created_at DESC)
chat_messages(session_id, created_at)

-- Usage tracking
usage_stats(user_id, date DESC)

-- Plans & features
plans(slug)
features(key)
plan_features(plan_id, feature_id)
user_features(user_id)

-- Payments
payments(user_id)
payments(stripe_subscription_id)
discount_codes(code)
user_discount_usage(user_id, discount_code_id)

-- API
api_keys(key_hash)
api_keys(user_id, is_active)

-- Blog
blog_posts(slug)
blog_posts(published, published_at DESC)

UNIQUE CONSTRAINTS SUMMARY
-- One profile per user
profiles(id)

-- One referral code per user
profiles(referral_code)

-- One plan per slug
plans(slug)

-- One feature per key
features(key)

-- One value per feature per plan
plan_features(plan_id, feature_id)

-- One override per feature per user
user_features(user_id, feature_id)

-- One active conversion per output type
files_converted(original_file_id, output_type)

-- One usage record per user per day
usage_stats(user_id, date)

-- One Stripe subscription per payment
payments(stripe_subscription_id)

-- One discount code name
discount_codes(code)

-- One redemption per user per code
user_discount_usage(user_id, discount_code_id)

-- One blog post per URL
blog_posts(slug)

-- One social login per provider per user
social_logins(provider, provider_id)

FOREIGN KEY RELATIONSHIPS

auth.users (Supabase)
  ↓ (1:1)
  profiles
    ↓ (1:Many)
    ├─ files_original
    │    ↓ (1:Many)
    │    └─ files_converted
    │         ↓ (1:Many)
    │         └─ conversion_steps
    ├─ chat_sessions
    │    ↓ (1:Many)
    │    └─ chat_messages
    ├─ usage_stats
    ├─ payments
    ├─ api_keys
    ├─ webhooks
    ├─ notifications
    ├─ user_features
    └─ social_logins

plans
  ↓ (1:Many)
  └─ plan_features
       ↑
       └─ features

profiles (referrer)
  ↓ (1:Many)
  └─ referral_rewards
       ↓
       └─ profiles (referred)

discount_codes
  ↓ (1:Many)
  ├─ user_discount_usage
  └─ payments

Thought Process
expand

The user wants me to continue from the Webhook Payload Example section. Let me continue with the webhook documentation and complete the remaining tables.

json

POST https://user-app.com/webhook
Headers:
  X-VectorizeDB-Signature: sha256=abc123...
  X-VectorizeDB-Event: conversion.completed

Body:
{
  "id": "evt_1a2b3c4d",
  "type": "conversion.completed",
  "created_at": "2024-01-15T10:30:00Z",
  "data": {
    "user_id": "usr_abc123",
    "file_id": "file_xyz789",
    "filename": "products.csv",
    "row_count": 1500,
    "output_types": ["vector", "jsonl", "rag_code"],
    "download_url": "https://api.vectorizedb.com/v1/files/xyz789/download"
  }
}

Security - Signature Verification:

javascript

// User's backend verifies signature
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const hash = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');
  
  return `sha256=${hash}` === signature;
}

Retry Logic:

text

1. Send webhook POST request
2. If response is 2xx: Update last_success, reset retry_count
3. If response is 4xx/5xx or timeout:
   - Increment retry_count
   - Store error in last_error
   - Retry after: 1min, 5min, 30min (max 3 retries)
4. After 3 failures: Set is_active=false, notify user

Why These Fields:

event_types (array):

    User subscribes only to relevant events
    Reduces noise, improves performance
    Example: ['conversion.completed', 'payment.succeeded']

secret:

    Generated when webhook created
    User uses it to verify requests came from VectorizeDB
    Prevents spoofing attacks

retry_count:

    Track webhook reliability
    Auto-disable after repeated failures
    Alert user to fix their endpoint

last_error:

    Help user debug issues
    Show in UI: "Last error: Connection timeout"

Indexes:

    webhooks(user_id, is_active) - User's active webhooks
    webhooks(last_triggered) - Monitor webhook health

Plan Restrictions:

    Basic: No webhooks
    Standard: 5 webhooks max
    Premium: Unlimited webhooks

23. api_db_support

Purpose: Track which database types are supported by API version
Relationships: Standalone configuration table
Field	Type	Description	Why Added
id	UUID	Primary key	Unique support record
db_type	TEXT	Database type ('mysql', 'postgres', 'mongodb', 'sqlite', 'csv', 'excel', 'json')	What database
api_version	TEXT	API version ('v1', 'v2')	Version-specific support
is_supported	BOOLEAN	Feature flag	Enable/disable support
read_support	BOOLEAN	Can read from this DB	Read capabilities
write_support	BOOLEAN	Can write to this DB	Write capabilities
min_plan_required	TEXT	Minimum plan needed (NULL = all plans)	Premium-only DBs
features	JSONB	DB-specific features	Detailed capabilities
connection_info	JSONB	Connection requirements	Help docs data
created_at	TIMESTAMPTZ	Support added date	Version tracking

Example Data:

MySQL Support:

json

{
  "db_type": "mysql",
  "api_version": "v1",
  "is_supported": true,
  "read_support": true,
  "write_support": true,
  "min_plan_required": "standard",
  "features": {
    "direct_connection": true,
    "dump_file_import": true,
    "incremental_sync": false,
    "supported_versions": ["5.7", "8.0"],
    "max_connection_timeout": 30
  },
  "connection_info": {
    "required_fields": ["host", "port", "database", "username", "password"],
    "default_port": 3306,
    "ssl_supported": true
  }
}

MongoDB Support:

json

{
  "db_type": "mongodb",
  "api_version": "v1",
  "is_supported": true,
  "read_support": true,
  "write_support": false,
  "min_plan_required": "premium",
  "features": {
    "direct_connection": true,
    "dump_file_import": true,
    "incremental_sync": false,
    "supported_versions": ["4.4", "5.0", "6.0"],
    "authentication_methods": ["SCRAM", "X.509"]
  },
  "connection_info": {
    "required_fields": ["connection_string"],
    "example": "mongodb://user:pass@host:27017/db",
    "atlas_supported": true
  }
}

CSV/Excel (Always Free):

json

{
  "db_type": "csv",
  "api_version": "v1",
  "is_supported": true,
  "read_support": true,
  "write_support": true,
  "min_plan_required": null,
  "features": {
    "encoding_detection": true,
    "delimiter_auto_detect": true,
    "max_file_size_mb": 50,
    "streaming_upload": true
  }
}

Why This Table:

Dynamic Feature Rollout:

    Add MongoDB support without code deploy
    UPDATE api_db_support SET is_supported=true WHERE db_type='mongodb'

Plan-Based Access:

    Basic users: CSV, Excel, JSON only
    Standard users: + MySQL, PostgreSQL, SQLite
    Premium users: + MongoDB, advanced features

API Documentation:

    Auto-generate docs from this table
    Show supported DBs by plan
    Display connection requirements

Version Management:

    API v1 vs v2 may support different DBs
    Graceful deprecation path

Feature Flags:

    is_supported: Kill switch for problematic DBs
    read_support/write_support: Gradual rollout

Indexes:

    api_db_support(db_type, api_version) - Fast support lookup
    api_db_support(is_supported, min_plan_required) - Available DBs query

API Usage:

javascript

// Check if user can use MongoDB
GET /api/v1/supported-databases

Response:
{
  "databases": [
    {
      "type": "mysql",
      "available": true,
      "plan_required": "standard",
      "capabilities": ["read", "write"]
    },
    {
      "type": "mongodb",
      "available": false,  // User is on Standard plan
      "plan_required": "premium",
      "capabilities": ["read"]
    }
  ]
}

INDEXES SUMMARY

Critical Indexes (Must Have):

sql

-- User lookups
profiles(id)
profiles(referral_code)

-- File operations
files_original(user_id, uploaded_at DESC)
files_converted(user_id)
files_converted(original_file_id, output_type)

-- Chat
chat_sessions(user_id, is_visible, created_at DESC)
chat_messages(session_id, created_at)

-- Usage tracking
usage_stats(user_id, date DESC)

-- Plans & features
plans(slug)
features(key)
plan_features(plan_id, feature_id)
user_features(user_id)

-- Payments
payments(user_id)
payments(stripe_subscription_id)
discount_codes(code)
user_discount_usage(user_id, discount_code_id)

-- API
api_keys(key_hash)
api_keys(user_id, is_active)

-- Blog
blog_posts(slug)
blog_posts(published, published_at DESC)

UNIQUE CONSTRAINTS SUMMARY

sql

-- One profile per user
profiles(id)

-- One referral code per user
profiles(referral_code)

-- One plan per slug
plans(slug)

-- One feature per key
features(key)

-- One value per feature per plan
plan_features(plan_id, feature_id)

-- One override per feature per user
user_features(user_id, feature_id)

-- One active conversion per output type
files_converted(original_file_id, output_type)

-- One usage record per user per day
usage_stats(user_id, date)

-- One Stripe subscription per payment
payments(stripe_subscription_id)

-- One discount code name
discount_codes(code)

-- One redemption per user per code
user_discount_usage(user_id, discount_code_id)

-- One blog post per URL
blog_posts(slug)

-- One social login per provider per user
social_logins(provider, provider_id)

FOREIGN KEY RELATIONSHIPS

text

auth.users (Supabase)
  ↓ (1:1)
  profiles
    ↓ (1:Many)
    ├─ files_original
    │    ↓ (1:Many)
    │    └─ files_converted
    │         ↓ (1:Many)
    │         └─ conversion_steps
    ├─ chat_sessions
    │    ↓ (1:Many)
    │    └─ chat_messages
    ├─ usage_stats
    ├─ payments
    ├─ api_keys
    ├─ webhooks
    ├─ notifications
    ├─ user_features
    └─ social_logins

plans
  ↓ (1:Many)
  └─ plan_features
       ↑
       └─ features

profiles (referrer)
  ↓ (1:Many)
  └─ referral_rewards
       ↓
       └─ profiles (referred)

discount_codes
  ↓ (1:Many)
  ├─ user_discount_usage
  └─ payments

DATA RETENTION POLICIES
Table	Retention	Reason
profiles	Forever	Core user data
files_original	Plan-based (1d/7d/30d)	Storage costs
files_converted	Plan-based	Storage costs
chat_sessions	Plan-based (1h/24h/30d)	Privacy + storage
chat_messages	Same as session	Cascade delete
usage_stats	90 days	Analytics window
payments	Forever	Financial compliance
subscription_changes	Forever	Audit trail
cancellation_requests	Forever	Financial audit
discount_codes	Forever	Marketing analytics
blog_posts	Forever	SEO value
notifications	30 days (if read)	Cleanup
api_keys	Forever (unless revoked)	Security audit
webhooks	Forever	User config
CLEANUP JOBS (Scheduled Tasks)

-- Daily: Delete expired chat sessions
DELETE FROM chat_sessions 
WHERE expires_at < NOW();

-- Daily: Delete old read notifications
DELETE FROM notifications 
WHERE read = true AND created_at < NOW() - INTERVAL '30 days';

-- Daily: Expire old referral rewards
UPDATE referral_rewards 
SET status = 'expired' 
WHERE status = 'pending' AND expires_at < NOW();

-- Weekly: Delete old usage stats
DELETE FROM usage_stats 
WHERE date < CURRENT_DATE - INTERVAL '90 days';

-- Monthly: Delete expired files (based on plan)
DELETE FROM files_original 
WHERE user_id IN (
  SELECT id FROM profiles WHERE current_plan = 'basic'
) AND uploaded_at < NOW() - INTERVAL '1 day';

-- Monthly: Process failed webhooks
UPDATE webhooks 
SET is_active = false 
WHERE retry_count >= 3 AND is_active = true;

SECURITY NOTES
Row Level Security (RLS) Must Be Enabled:

    All tables except plans, features, blog_posts (public read)
    Users can only see/modify their own data
    Admin access via service role key

Sensitive Data Encryption:

    social_logins.access_token - Encrypt at rest
    social_logins.refresh_token - Encrypt at rest
    api_keys.key_hash - Bcrypt hash (never plaintext)
    webhooks.secret - Generate random, never show again after creation

API Security:

    Rate limiting via api_keys.requests_this_minute
    API key validation on every request
    Webhook signature verification required
    CORS restrictions on frontend


FUTURE CONSIDERATIONS
Tables You Might Add Later:

1. team_memberships (Team Plans)

sql

- team_id UUID
- user_id UUID
- role TEXT ('owner', 'admin', 'member')
- invited_by UUID
- joined_at TIMESTAMPTZ

2. audit_logs (Compliance)

sql

- user_id UUID
- action TEXT
- resource_type TEXT
- resource_id UUID
- ip_address TEXT
- user_agent TEXT
- created_at TIMESTAMPTZ

3. support_tickets (Customer Support)

sql

- user_id UUID
- subject TEXT
- status TEXT
- priority TEXT
- assigned_to UUID
- messages JSONB

4. feature_requests (Product Feedback)

sql

- user_id UUID
- title TEXT
- description TEXT
- votes INT
- status TEXT ('pending', 'planned', 'completed')

✅ FINAL CHECKLIST

Before generating SQL:

    ✅ 23 tables documented
    ✅ All fields explained with "Why Added"
    ✅ Relationships mapped
    ✅ Indexes identified
    ✅ Unique constraints defined
    ✅ Security considerations noted
    ✅ Cleanup jobs documented
    ✅ Future extensibility considered

This schema is production-ready and handles:
✅ User authentication & profiles
✅ File uploads & conversions
✅ Chat sessions (data + help bot)
✅ Flexible plan system with custom features
✅ Dynamic upgrades with proration
✅ Refund-eligible cancellations
✅ Discount codes & referrals
✅ API keys & rate limiting
✅ Webhooks for integrations
✅ Blog for SEO
✅ In-app notifications

Ready for SQL generation? Type "Generate SQL" and I'll create the complete Supabase schema!


