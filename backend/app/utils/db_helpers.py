"""
Database helper functions - Common queries.
"""

from typing import Optional, List

from sqlmodel import Session, select

from app.models.user import Profile, SocialAccount


# ==================================================
#  Profile Queries
# ==================================================

def get_profile_by_id(db: Session, user_id: str) -> Optional[Profile]:
    """Get profile by ID."""
    return db.exec(select(Profile).where(Profile.id == user_id)).first()


def get_profile_by_email(db: Session, email: str) -> Optional[Profile]:
    """Get profile by email."""
    return db.exec(select(Profile).where(Profile.email == email)).first()


def get_profile_by_referral_code(db: Session, code: str) -> Optional[Profile]:
    """Get profile by referral code."""
    return db.exec(select(Profile).where(Profile.referral_code == code)).first()


def create_profile(
    db: Session,
    user_id: str,
    email: str,
    full_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    is_email_verified: bool = False,
    has_password: bool = True,
    referral_code: Optional[str] = None,
    referred_by: Optional[str] = None,
    commit: bool = True,
) -> Profile:
    """Create new profile."""
    from app.utils.generators import generate_referral_code
    
    profile = Profile(
        id=user_id,
        email=email,
        full_name=full_name,
        avatar_url=avatar_url,
        is_email_verified=is_email_verified,
        has_password=has_password,
        referral_code=referral_code or generate_referral_code(),
        referred_by=referred_by,
    )
    
    db.add(profile)
    
    if commit:
        db.commit()
        db.refresh(profile)
    
    return profile


def update_profile(
    db: Session,
    profile: Profile,
    commit: bool = True,
    **kwargs,
) -> Profile:
    """Update profile with given fields."""
    for key, value in kwargs.items():
        if hasattr(profile, key) and value is not None:
            setattr(profile, key, value)
    
    db.add(profile)
    
    if commit:
        db.commit()
        db.refresh(profile)
    
    return profile


# ==================================================
#  Social Account Queries
# ==================================================

def get_social_account(
    db: Session,
    provider: str,
    provider_id: str,
) -> Optional[SocialAccount]:
    """Get social account by provider and provider_id."""
    return db.exec(
        select(SocialAccount).where(
            SocialAccount.provider == provider,
            SocialAccount.provider_id == provider_id,
        )
    ).first()


def get_user_social_accounts(db: Session, user_id: str) -> List[SocialAccount]:
    """Get all social accounts for a user."""
    return list(db.exec(
        select(SocialAccount).where(SocialAccount.user_id == user_id)
    ).all())


def create_social_account(
    db: Session,
    user_id: str,
    provider: str,
    provider_id: str,
    email: str,
    name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    access_token: Optional[dict] = None,
    refresh_token: Optional[str] = None,
    commit: bool = True,
) -> SocialAccount:
    """Create new social account link."""
    social_account = SocialAccount(
        user_id=user_id,
        provider=provider,
        provider_id=provider_id,
        email=email,
        name=name,
        avatar_url=avatar_url,
        access_token=access_token or {},
        refresh_token=refresh_token,
    )
    
    db.add(social_account)
    
    if commit:
        db.commit()
        db.refresh(social_account)
    
    return social_account


def update_social_account_tokens(
    db: Session,
    social_account: SocialAccount,
    access_token: dict,
    refresh_token: Optional[str] = None,
    commit: bool = True,
) -> SocialAccount:
    """Update social account tokens."""
    social_account.access_token = access_token
    if refresh_token:
        social_account.refresh_token = refresh_token
    
    db.add(social_account)
    
    if commit:
        db.commit()
        db.refresh(social_account)
    
    return social_account