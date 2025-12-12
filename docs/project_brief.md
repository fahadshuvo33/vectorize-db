VectorizeDB – Initial Launch Plan (MVP with Live Chatbot Preview)

Launch Goal: Ship a simple, addictive tool that turns any database into AI-ready format + lets users chat with their data in real time.

Core Promise: “Drop your DB file → See your AI chatbot live in 30 seconds → Download code.”

---

## 1. App Overview (What It Is)
VectorizeDB is a web app where users:
1. Upload a file (Excel, CSV, SQL dump, JSON, Mongo export)
2. See a smart preview + auto-cleaning
3. Click “Melt” → get:
   - Vector embeddings
   - JSONL for LLMs
   - RAG-ready LangChain code
   - A LIVE chatbot (preview) they can talk to instantly
4. Download everything or upgrade for more

No code. No setup. Works in 60 seconds.

---

## 2. Supported Input Formats (Launch)
- Excel (.xlsx, .xls)
- CSV (.csv)
- SQL Dump (.sql) – MySQL, PostgreSQL, SQLite
- JSON / JSONL
- MongoDB Export (mongoexport JSON)

---

## 3. Supported Output Formats (Launch)
- Vector Embeddings (JSON + embedding column)
- JSONL (for fine-tuning)
- RAG Starter Code (LangChain + Chroma)
- Downloadable ZIP (all above)

---

## 4. Live Chatbot Preview (The “Wow” Feature)
After clicking “Melt”:
- A chat window appears on the right
- User can type questions → bot answers using their data
- Feels like magic

### Free Tier Limits (Strict but Fair)
- Max 10 messages per session
- Session expires after 15 minutes
- Max 5,000 rows
- Only free embedding model (all-MiniLM-L6-v2)

### Pro Tier (Melt Plan)
- Unlimited messages
- 1-hour session
- Up to 250,000 rows
- OpenAI embeddings (optional)

---

## 5. User Flow (Step-by-Step)
1. Sign up / log in (email or GitHub)
2. Go to Dashboard
3. Drag & drop file
4. See live table preview
   - AI highlights text columns
   - One-click: remove duplicates, fill blanks
5. Click “Melt to Chatbot”
6. Wait 5–15 seconds
7. Right side: Chat window appears
   - Bot says: “Hi! Ask me anything about your data.”
   - User types → bot replies
8. Bottom: “Download RAG Code” + “Export Files”
9. Free user hits limit → “Upgrade to keep chatting → $15/mo”

---

## 6. Pricing (Launch – Individuals Only)
| Tier   | Price       | Row Limit | Melts/mo | Live Chat Preview       | Outputs                          |
|--------|-------------|-----------|----------|--------------------------|----------------------------------|
| Free   | $0          | ≤ 5K      | 5        | 10 messages, 15 min      | Vectors (MiniLM), JSONL, RAG code |
| Melt   | $15/mo      | ≤ 250K    | Unlimited| Unlimited, 1 hour        | All + OpenAI, Parquet, SQL export |
| Melt+  | $29/mo      | ≤ 1M      | Unlimited| Save chatbot 30 days     | All + Multimodal, Templates       |

---

## 7. Tech Stack (Simple & Cheap)
- Frontend: React + TypeScript + Tailwind
- Backend: FastAPI (Python)
- Database: Supabase (auth + storage + logs)
- Storage: Cloudflare R2
- Embeddings: Hugging Face (free) + OpenAI (Pro)
- Vector DB (Preview): FAISS in-memory (free)
- Hosting: Fly.io or Railway ($0–$20/mo)

---

## 8. MVP Features to Build (Launch in 4 Weeks)
| Week | Build This |
|------|------------|
| 1    | Supabase auth + file upload + preview table |
| 2    | Pandas cleaning + MiniLM embedding + JSONL export |
| 3    | LangChain RAG code generator + download ZIP |
| 4    | Live Chatbot Preview (FAISS + 10-message/15-min timer) + Free limits |

---

## 9. Free Tier Restrictions (Hard Limits)
- 5 melts per month
- 5,000 rows max
- Live preview: 10 messages OR 15 minutes (whichever first)
- Auto-delete session after timer
- No OpenAI embeddings
- Watermark: “Powered by VectorizeDB”

---

## 10. Pro Upgrade Triggers
- “You’ve used 5/5 free melts” → Upgrade
- “Live preview expired (10 messages)” → Upgrade
- “File too big (5K rows)” → Upgrade
- “Want better answers? Use OpenAI embeddings” → Upgrade

---

## 11. Security & Privacy
- Files encrypted at rest
- Auto-delete after 24 hours (Free) / 7 days (Pro)
- No data sharing
- GDPR-ready

---

## 12. Launch Messaging
> “Turn any Excel, CSV, or SQL file into a live AI chatbot — in 60 seconds.  
> No code. Just drop, melt, and chat.”

---

## 13. What NOT to Build Yet
- Hosted chatbot widget (wait for $2K+ MRR)
- Team plans
- Webhook sync
- CLI tool
- Custom models

---

VectorizeDB Launch MVP = Simple, Fast, Addictive.  
Free users get a taste → Pro users get the full power.  
Build the live preview. Ship in 4 weeks. Watch upgrades pour in.