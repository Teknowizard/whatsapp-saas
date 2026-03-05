"""Add admin and subscription fields

Revision ID: 002
Revises: 001
Create Date: 2024-01-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type first
    subscription_status_enum = postgresql.ENUM('trial', 'active', 'expired', 'suspended', name='subscriptionstatus', create_type=True)
    subscription_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Add new columns to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('is_suspended', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('is_payment_exempt', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('subscription_status', 
        sa.Enum('trial', 'active', 'expired', 'suspended', name='subscriptionstatus'), 
        nullable=False, server_default='trial'))
    op.add_column('users', sa.Column('subscription_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('plan', sa.String(50), nullable=False, server_default='free'))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()))


def downgrade():
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'plan')
    op.drop_column('users', 'subscription_expires_at')
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'is_payment_exempt')
    op.drop_column('users', 'is_suspended')
    op.drop_column('users', 'is_admin')
    
    # Drop the enum type
    sa.Enum(name='subscriptionstatus').drop(op.get_bind(), checkfirst=True)
