# main.py


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users
from app.core.supabase import supabase_client
from app.core.config import settings
from app.utils import utc_now

app = FastAPI(
    title="VectorizeDB API",
    description="Turn databases into AI-ready formats",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "VectorizeDB API",
        "version": "1.0.0",
        "message": "Welcome to VectorizeDB API",
        "docs": "/docs",
        "endpoints": {
            "health": "/",
            "api_docs": "/docs",
            "auth": "/api/v1/auth",
            "upload": "/api/v1/upload",
            "chat": "/api/v1/chat",
        },
    }


@app.get("/health")
async def health():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "VectorizeDB API",
        "version": "1.0.0",
        "timestamp": utc_now().isoformat(),
    }


@app.get("/health/supabase")
async def supabase_health():
    """
    Simple Supabase connectivity check.
    Uses the admin (service-role) client to bypass RLS where possible.
    """
    try:
        # Get the admin client
        client = supabase_client.admin
        
        # First, try to list all tables to verify connection
        try:
            # This uses the SQL endpoint which should be accessible with service role
            tables = client.rpc('list_tables').execute()
            print(f"Successfully connected to Supabase. Found {len(tables.data) if tables.data else 0} tables.")
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "Supabase",
                "error": f"Failed to list tables: {str(e)}",
                "connection_works": False
            }
        
        # Then try to query the profiles table
        try:
            resp = client.table("profiles").select("id").limit(1).execute()
            return {
                "status": "healthy",
                "service": "Supabase",
                "error": None,
                "row_count": len(resp.data) if isinstance(resp.data, list) else 0,
                "connection_works": True,
                "profiles_accessible": True
            }
        except Exception as e:
            return {
                "status": "partially_healthy",
                "service": "Supabase",
                "error": f"Connection works but profiles table access failed: {str(e)}",
                "connection_works": True,
                "profiles_accessible": False
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Supabase",
            "error": f"Failed to initialize Supabase client: {str(e)}",
            "connection_works": False,
            "profiles_accessible": False
        }


@app.get("/health/supabase/deep")
async def supabase_deep_health():
    """
    Deeper Supabase health check that tries a lightweight query
    against a set of important tables.
    """
    # Tables from your initial migration
    tables_to_check = [
        "profiles",
        "social_accounts",
        "usage_stats",
        "notification_templates",
        "in_app_notifications",
        "email_logs",
        "support_tickets",
        "ticket_messages",
        "app_reviews",
        "plans",
        "custom_plans",
        "subscriptions",
        "subscription_usage",
        "upgrade_requests",
        "upgrade_offers",
        "billing_history",
        "coupons",
        "coupon_redemptions",
    ]

    try:
        client = supabase_client.admin
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Supabase",
            "error": f"Admin client not configured or invalid: {e}",
            "results": [],
        }

    results = []
    overall_ok = True

    for table in tables_to_check:
        try:
            resp = (
                client.table(table)
                .select("id")
                .limit(1)
                .execute()
            )
            row_count = len(resp.data) if isinstance(resp.data, list) else 0
            results.append(
                {
                    "table": table,
                    "status": "ok",
                    "row_count": row_count,
                    "error": None,
                }
            )
        except Exception as e:
            overall_ok = False
            results.append(
                {
                    "table": table,
                    "status": "error",
                    "row_count": None,
                    "error": str(e),
                }
            )

    return {
        "status": "healthy" if overall_ok else "degraded",
        "service": "Supabase",
        "error": None,
        "results": results,
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
