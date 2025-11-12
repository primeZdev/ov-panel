"""Add health check and sync fields to nodes table

This migration adds new fields to support health monitoring and synchronization:
- is_healthy: boolean flag for node health
- last_health_check: timestamp of last health check
- response_time: response time in seconds
- consecutive_failures: count of consecutive failures
- last_sync_time: timestamp of last sync
- sync_status: current sync status (synced, pending, failed, never_synced)
- tunnel_address: tunnel address for node connection

Revision ID: health_sync_fields
Revises: 494ff940dc52
Create Date: 2025-11-12
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'health_sync_fields'
down_revision = '494ff940dc52'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tunnel_address field (should have been added earlier but missing)
    op.add_column('nodes', sa.Column('tunnel_address', sa.String(), nullable=True))
    
    # Add health check fields
    op.add_column('nodes', sa.Column('is_healthy', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('nodes', sa.Column('last_health_check', sa.DateTime(), nullable=True))
    op.add_column('nodes', sa.Column('response_time', sa.Float(), nullable=True))
    op.add_column('nodes', sa.Column('consecutive_failures', sa.Integer(), nullable=False, server_default='0'))
    
    # Add sync fields
    op.add_column('nodes', sa.Column('last_sync_time', sa.DateTime(), nullable=True))
    op.add_column('nodes', sa.Column('sync_status', sa.String(), nullable=False, server_default='synced'))


def downgrade() -> None:
    # Remove added columns in reverse order
    op.drop_column('nodes', 'sync_status')
    op.drop_column('nodes', 'last_sync_time')
    op.drop_column('nodes', 'consecutive_failures')
    op.drop_column('nodes', 'response_time')
    op.drop_column('nodes', 'last_health_check')
    op.drop_column('nodes', 'is_healthy')
    op.drop_column('nodes', 'tunnel_address')

