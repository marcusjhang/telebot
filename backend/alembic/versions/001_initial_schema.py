"""Initial schema with users, goals, logs, events, notifications

Revision ID: 001
Revises: 
Create Date: 2025-12-10 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='Asia/Singapore'),
        sa.Column('broadcast_opt_out', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recap_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('week_start_day', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_active', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_telegram_id', 'users', ['telegram_user_id'], unique=True)
    op.create_index('idx_users_active', 'users', ['is_active', 'last_active'])
    
    # Create goals table
    op.create_table(
        'goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('daily_water_bottles', sa.Numeric(precision=4, scale=1), nullable=False, server_default='3.0'),
        sa.Column('daily_carb_max_portions', sa.Numeric(precision=4, scale=1), nullable=False, server_default='4.0'),
        sa.Column('weekly_exercise_sessions', sa.Integer(), nullable=False, server_default='6'),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('daily_water_bottles > 0', name='check_water_positive'),
        sa.CheckConstraint('daily_carb_max_portions > 0', name='check_carb_positive'),
        sa.CheckConstraint('weekly_exercise_sessions > 0', name='check_exercise_positive'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'effective_from', name='uq_user_effective_from')
    )
    op.create_index('idx_goals_user_effective', 'goals', ['user_id', sa.text('effective_from DESC')])
    
    # Create daily_logs table
    op.create_table(
        'daily_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('log_date', sa.Date(), nullable=False),
        sa.Column('water_bottles', sa.Numeric(precision=5, scale=1), nullable=False, server_default='0'),
        sa.Column('carb_portions', sa.Numeric(precision=5, scale=1), nullable=False, server_default='0'),
        sa.Column('exercise_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('water_bottles >= 0', name='check_water_non_negative'),
        sa.CheckConstraint('carb_portions >= 0', name='check_carb_non_negative'),
        sa.CheckConstraint('exercise_sessions >= 0', name='check_exercise_non_negative'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'log_date', name='uq_user_log_date')
    )
    op.create_index('idx_daily_logs_user_date', 'daily_logs', ['user_id', sa.text('log_date DESC')])
    
    # Create weekly_logs table
    op.create_table(
        'weekly_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('week_start_date', sa.Date(), nullable=False),
        sa.Column('exercise_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('exercise_sessions >= 0', name='check_weekly_exercise_non_negative'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'week_start_date', name='uq_user_week_start')
    )
    op.create_index('idx_weekly_logs_user_week', 'weekly_logs', ['user_id', sa.text('week_start_date DESC')])
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=20), nullable=False),
        sa.Column('delta', sa.Numeric(precision=5, scale=1), nullable=False),
        sa.Column('subtype', sa.String(length=20), nullable=True),
        sa.Column('portions', sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('message_id', sa.BigInteger(), nullable=True),
        sa.Column('callback_query_id', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=20), nullable=False, server_default='bot'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_events_user_time', 'events', ['user_id', sa.text('occurred_at DESC')])
    op.create_index('idx_events_callback', 'events', ['callback_query_id'], unique=False, 
                    postgresql_where=sa.text('callback_query_id IS NOT NULL'))
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('target_user_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notifications_status', 'notifications', ['status', 'scheduled_for'])
    op.create_index('idx_notifications_user', 'notifications', ['target_user_id', sa.text('created_at DESC')])


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('events')
    op.drop_table('weekly_logs')
    op.drop_table('daily_logs')
    op.drop_table('goals')
    op.drop_table('users')

