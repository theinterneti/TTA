#!/usr/bin/env python3
"""
Script to create clinical user for the TTA system.

This script creates the dr_smith/clinician123 user with clinical role
for accessing the clinical dashboard at localhost:3001.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.player_experience.database.user_repository import UserRepository
from src.player_experience.models.auth import (
    MFAConfig,
    SecuritySettings,
    UserRegistration,
    UserRole,
)
from src.player_experience.services.auth_service import EnhancedAuthService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def create_clinical_user():
    """Create the clinical user for dashboard access."""
    try:
        logger.info("🏥 Creating clinical user for TTA system")

        # Initialize user repository
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

        user_repository = None
        try:
            user_repository = UserRepository(neo4j_uri, neo4j_username, neo4j_password)
            user_repository.connect()
            logger.info("✅ Connected to Neo4j database")
        except Exception as e:
            logger.warning(f"⚠️ Could not connect to Neo4j: {e}")
            logger.info("📝 Will use in-memory storage for development")

        # Initialize auth service
        jwt_secret = os.getenv(
            "JWT_SECRET_KEY", "TTA_JWT_Secret_Key_Change_In_Production_2024!"
        )
        auth_service = EnhancedAuthService(
            secret_key=jwt_secret,
            user_repository=user_repository,
            security_settings=SecuritySettings(),
            mfa_config=MFAConfig(enabled=False),  # Disable MFA for development
        )

        # Create clinical user registration
        clinical_registration = UserRegistration(
            username="dr_smith",
            email="dr.smith@tta-clinical.com",
            password="clinician123",
            role=UserRole.THERAPIST,  # Use THERAPIST role for clinical access
            therapeutic_preferences={
                "clinical_focus": ["anxiety", "depression", "trauma"],
                "intervention_style": "evidence_based",
                "monitoring_level": "comprehensive",
            },
            privacy_settings={
                "audit_logging": True,
                "data_retention": "clinical_standard",
                "hipaa_compliance": True,
            },
        )

        # Check if user already exists
        existing_user = None
        if user_repository:
            try:
                existing_user = user_repository.get_user_by_username("dr_smith")
            except Exception as e:
                logger.warning(f"Could not check existing user: {e}")
        else:
            # Check in-memory store
            existing_user = auth_service.in_memory_users.get("dr_smith")

        if existing_user:
            logger.info("👨‍⚕️ Clinical user 'dr_smith' already exists")
            logger.info(f"   User ID: {existing_user.user_id}")
            logger.info(f"   Role: {existing_user.role.value}")
            logger.info(f"   Email: {existing_user.email}")
            return True

        # Register the clinical user
        logger.info("👨‍⚕️ Creating clinical user 'dr_smith'...")

        # For development, create user directly in in-memory store if database is not available
        if not user_repository:
            logger.info("📝 Using in-memory storage for development")
            from uuid import uuid4

            from src.player_experience.models.user import User

            # Create user directly
            hashed_password = auth_service.security_service.hash_password(
                "clinician123"
            )
            clinical_user = User(
                user_id=str(uuid4()),
                username="dr_smith",
                email="dr.smith@tta-clinical.com",
                password_hash=hashed_password,
                role=UserRole.THERAPIST,
                email_verified=True,
                created_at=datetime.utcnow(),
                account_status="active",
                failed_login_attempts=0,
            )

            # Store in in-memory store
            auth_service.in_memory_users["dr_smith"] = clinical_user
            success = True
            errors = []
        else:
            success, errors = auth_service.register_user(clinical_registration)

        if success:
            logger.info("✅ Clinical user created successfully!")
            logger.info("📋 Clinical User Details:")
            logger.info("   Username: dr_smith")
            logger.info("   Password: clinician123")
            logger.info(f"   Role: {UserRole.THERAPIST.value}")
            logger.info("   Email: dr.smith@tta-clinical.com")
            logger.info("   Dashboard URL: http://localhost:3001")
            logger.info("")
            logger.info("🔐 Authentication Details:")
            logger.info("   - JWT-based authentication enabled")
            logger.info("   - Clinical role permissions granted")
            logger.info("   - HIPAA compliance settings configured")
            logger.info("   - Audit logging enabled")

            return True
        else:
            logger.error("❌ Failed to create clinical user")
            for error in errors:
                logger.error(f"   Error: {error}")
            return False

    except Exception as e:
        logger.error(f"❌ Error creating clinical user: {e}")
        return False
    finally:
        if user_repository:
            try:
                if hasattr(user_repository, "close"):
                    user_repository.close()
                    logger.info("🔌 Closed database connection")
            except Exception as e:
                logger.warning(f"Warning closing database: {e}")


async def verify_clinical_authentication():
    """Verify that clinical authentication works."""
    try:
        logger.info("🔍 Verifying clinical authentication...")

        # Initialize auth service (same as above)
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

        user_repository = None
        try:
            user_repository = UserRepository(neo4j_uri, neo4j_username, neo4j_password)
            user_repository.connect()
        except Exception:
            pass  # Use in-memory storage

        jwt_secret = os.getenv(
            "JWT_SECRET_KEY", "TTA_JWT_Secret_Key_Change_In_Production_2024!"
        )
        auth_service = EnhancedAuthService(
            secret_key=jwt_secret,
            user_repository=user_repository,
            security_settings=SecuritySettings(),
            mfa_config=MFAConfig(enabled=False),
        )

        # Test authentication
        from src.player_experience.models.auth import UserCredentials

        credentials = UserCredentials(username="dr_smith", password="clinician123")
        user = auth_service.authenticate_user(credentials)

        if user:
            logger.info("✅ Clinical authentication verified!")
            logger.info(f"   User ID: {user.user_id}")
            logger.info(f"   Role: {user.role.value}")
            logger.info(f"   Permissions: {[p.value for p in user.permissions]}")

            # Test token creation
            session_id = auth_service.create_session(user, "127.0.0.1", "test-client")
            access_token = auth_service.create_access_token(user, session_id)

            logger.info("🎫 JWT Token created successfully")
            logger.info(f"   Token length: {len(access_token)} characters")
            logger.info(f"   Session ID: {session_id}")

            return True
        else:
            logger.error("❌ Clinical authentication failed")
            return False

    except Exception as e:
        logger.error(f"❌ Error verifying authentication: {e}")
        return False
    finally:
        if user_repository:
            try:
                if hasattr(user_repository, "close"):
                    user_repository.close()
            except Exception:
                pass


async def main():
    """Main function."""
    logger.info("🚀 TTA Clinical User Setup")
    logger.info("=" * 50)

    # Create clinical user
    create_success = await create_clinical_user()

    if create_success:
        logger.info("")
        logger.info("=" * 50)

        # Verify authentication
        verify_success = await verify_clinical_authentication()

        if verify_success:
            logger.info("")
            logger.info("🎉 Clinical user setup completed successfully!")
            logger.info("📱 You can now access the clinical dashboard at:")
            logger.info("   URL: http://localhost:3001")
            logger.info("   Username: dr_smith")
            logger.info("   Password: clinician123")
        else:
            logger.error(
                "❌ Clinical user created but authentication verification failed"
            )
            return False
    else:
        logger.error("❌ Clinical user setup failed")
        return False

    return True


if __name__ == "__main__":
    asyncio.run(main())
