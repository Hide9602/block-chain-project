"""
CRUD operations for User model
"""
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.models.user import User
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


class UserCRUD:
    """
    CRUD operations for User model
    ユーザーモデルのCRUD操作
    """
    
    async def get_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User UUID
        
        Returns:
            User object or None if not found
        """
        try:
            result = await db.execute(
                select(User).where(User.id == uuid.UUID(user_id))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}", exc_info=True)
            return None
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            db: Database session
            email: User email address
        
        Returns:
            User object or None if not found
        """
        try:
            result = await db.execute(
                select(User).where(User.email == email.lower())
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}", exc_info=True)
            return None
    
    async def create(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        organization: Optional[str] = None,
        job_title: Optional[str] = None,
        role: str = "analyst"
    ) -> User:
        """
        Create a new user
        
        Args:
            db: Database session
            email: User email address
            password: Plain text password (will be hashed)
            full_name: User full name
            organization: Organization name
            job_title: Job title
            role: User role (default: "analyst")
        
        Returns:
            Created User object
        
        Raises:
            ValueError: If email already exists
        """
        try:
            # Check if user already exists
            existing_user = await self.get_by_email(db, email)
            if existing_user:
                raise ValueError(f"User with email {email} already exists")
            
            # Create new user
            user = User(
                id=uuid.uuid4(),
                email=email.lower(),
                hashed_password=get_password_hash(password),
                full_name=full_name,
                organization=organization,
                job_title=job_title,
                role=role,
                is_active=True,
                is_superuser=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Created new user: {email} (ID: {user.id})")
            return user
            
        except ValueError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating user {email}: {str(e)}", exc_info=True)
            raise
    
    async def update(
        self,
        db: AsyncSession,
        user_id: str,
        data: Dict[str, Any]
    ) -> Optional[User]:
        """
        Update user information
        
        Args:
            db: Database session
            user_id: User UUID
            data: Dictionary of fields to update
        
        Returns:
            Updated User object or None if not found
        """
        try:
            user = await self.get_by_id(db, user_id)
            if not user:
                return None
            
            # Update fields
            for field, value in data.items():
                if hasattr(user, field) and field not in ["id", "created_at", "hashed_password"]:
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Updated user: {user.email} (ID: {user.id})")
            return user
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}", exc_info=True)
            return None
    
    async def update_password(
        self,
        db: AsyncSession,
        user_id: str,
        new_password: str
    ) -> bool:
        """
        Update user password
        
        Args:
            db: Database session
            user_id: User UUID
            new_password: New plain text password (will be hashed)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            user = await self.get_by_id(db, user_id)
            if not user:
                return False
            
            user.hashed_password = get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"Updated password for user: {user.email} (ID: {user.id})")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating password for user {user_id}: {str(e)}", exc_info=True)
            return False
    
    async def update_last_login(
        self,
        db: AsyncSession,
        user_id: str
    ) -> bool:
        """
        Update user's last login timestamp
        
        Args:
            db: Database session
            user_id: User UUID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            user = await self.get_by_id(db, user_id)
            if not user:
                return False
            
            user.last_login_at = datetime.utcnow()
            
            await db.commit()
            
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating last login for user {user_id}: {str(e)}", exc_info=True)
            return False
    
    async def deactivate(
        self,
        db: AsyncSession,
        user_id: str
    ) -> bool:
        """
        Deactivate user account
        
        Args:
            db: Database session
            user_id: User UUID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            user = await self.get_by_id(db, user_id)
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"Deactivated user: {user.email} (ID: {user.id})")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deactivating user {user_id}: {str(e)}", exc_info=True)
            return False
    
    async def delete(
        self,
        db: AsyncSession,
        user_id: str
    ) -> bool:
        """
        Delete user (hard delete)
        
        Args:
            db: Database session
            user_id: User UUID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            user = await self.get_by_id(db, user_id)
            if not user:
                return False
            
            await db.delete(user)
            await db.commit()
            
            logger.info(f"Deleted user: {user.email} (ID: {user_id})")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}", exc_info=True)
            return False


# Global instance
user_crud = UserCRUD()
