"""initial_schema_pg

Revision ID: 0001_initial_schema_pg
Revises: 
Create Date: 2026-09-08 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema_pg'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable required PostgreSQL extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "citext"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # 2. Organizations
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('org_type', sa.String(length=50), nullable=False),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)

    # 3. Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('email', postgresql.CITEXT(), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('avatar_url', sa.String(length=512), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_org_id'), 'users', ['org_id'], unique=False)

    # 4. Creator Profiles
    op.create_table(
        'creator_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('handle', sa.String(length=100), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('primary_language', sa.String(length=50), nullable=False),
        sa.Column('niches', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('public_id_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_creator_profiles_handle'), 'creator_profiles', ['handle'], unique=True)
    op.create_index(op.f('ix_creator_profiles_id'), 'creator_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_creator_profiles_user_id'), 'creator_profiles', ['user_id'], unique=True)

    # 5. Platform Connections
    op.create_table(
        'platform_connections',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('platform_user_id', sa.String(length=255), nullable=False),
        sa.Column('platform_handle', sa.String(length=255), nullable=False),
        sa.Column('access_token_enc', sa.Text(), nullable=False),
        sa.Column('refresh_token_enc', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scopes', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['creator_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_platform_connections_creator_id'), 'platform_connections', ['creator_id'], unique=False)
    op.create_index(op.f('ix_platform_connections_id'), 'platform_connections', ['id'], unique=False)

    # 6. Campaigns
    op.create_table(
        'campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('starts_on', sa.Date(), nullable=True),
        sa.Column('ends_on', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_campaigns_org_id'), 'campaigns', ['org_id'], unique=False)

    # 7. Contracts
    op.create_table(
        'contracts',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('parent_contract_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('raw_document_key', sa.String(length=512), nullable=True),
        sa.Column('raw_document_filename', sa.String(length=255), nullable=True),
        sa.Column('source_content_hash', sa.String(length=64), nullable=True),
        sa.Column('parsed_at', sa.String(length=50), nullable=True),
        sa.Column('fee_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('fee_currency', sa.String(length=3), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creator_id'], ['creator_profiles.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_contract_id'], ['contracts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contracts_campaign_id'), 'contracts', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_contracts_creator_id'), 'contracts', ['creator_id'], unique=False)
    op.create_index(op.f('ix_contracts_id'), 'contracts', ['id'], unique=False)
    op.create_index(op.f('ix_contracts_source_content_hash'), 'contracts', ['source_content_hash'], unique=False)

    # 8. Clauses
    op.create_table(
        'clauses',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('contract_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('ordinal', sa.Integer(), nullable=False),
        sa.Column('clause_ref', sa.String(length=50), nullable=False),
        sa.Column('source_text', sa.Text(), nullable=False),
        sa.Column('requirement', sa.Text(), nullable=False),
        sa.Column('clause_type', sa.String(length=50), nullable=False),
        sa.Column('params', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('modality', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('is_auto_checkable', sa.Boolean(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('review_status', sa.String(length=50), nullable=False),
        sa.Column('source_page', sa.Integer(), nullable=True),
        sa.Column('source_bbox', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('edited_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['edited_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clauses_contract_id'), 'clauses', ['contract_id'], unique=False)
    op.create_index(op.f('ix_clauses_id'), 'clauses', ['id'], unique=False)

    # 9. Submissions
    op.create_table(
        'submissions',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('contract_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('contract_version', sa.Integer(), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('kind', sa.String(length=50), nullable=False),
        sa.Column('video_file_key', sa.String(length=512), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('caption_text', sa.Text(), nullable=True),
        sa.Column('platform_url', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creator_id'], ['creator_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submissions_contract_id'), 'submissions', ['contract_id'], unique=False)
    op.create_index(op.f('ix_submissions_creator_id'), 'submissions', ['creator_id'], unique=False)
    op.create_index(op.f('ix_submissions_id'), 'submissions', ['id'], unique=False)

    # 10. Analysis Artifacts
    op.create_table(
        'analysis_artifacts',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('artifact_type', sa.String(length=50), nullable=False),
        sa.Column('storage_key', sa.String(length=512), nullable=True),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_artifacts_id'), 'analysis_artifacts', ['id'], unique=False)
    op.create_index(op.f('ix_analysis_artifacts_submission_id'), 'analysis_artifacts', ['submission_id'], unique=False)

    # 11. Compliance Reports
    op.create_table(
        'compliance_reports',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('overall_score', sa.Integer(), nullable=False),
        sa.Column('verdict', sa.String(length=50), nullable=False),
        sa.Column('clauses_total', sa.Integer(), nullable=False),
        sa.Column('clauses_passed', sa.Integer(), nullable=False),
        sa.Column('clauses_failed', sa.Integer(), nullable=False),
        sa.Column('clauses_flagged', sa.Integer(), nullable=False),
        sa.Column('model_version', sa.String(length=100), nullable=False),
        sa.Column('prompt_version', sa.String(length=50), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processing_ms', sa.Integer(), nullable=False),
        sa.Column('cost_estimate_usd', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_compliance_reports_id'), 'compliance_reports', ['id'], unique=False)
    op.create_index(op.f('ix_compliance_reports_submission_id'), 'compliance_reports', ['submission_id'], unique=True)

    # 12. Clause Verdicts
    op.create_table(
        'clause_verdicts',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('report_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('clause_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('clause_ref', sa.String(length=50), nullable=False),
        sa.Column('verdict', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('measured_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('required_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_overridden', sa.Boolean(), nullable=False),
        sa.Column('override_verdict', sa.String(length=50), nullable=True),
        sa.Column('override_reason', sa.Text(), nullable=True),
        sa.Column('overridden_by', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('overridden_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['clause_id'], ['clauses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['overridden_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['report_id'], ['compliance_reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clause_verdicts_clause_id'), 'clause_verdicts', ['clause_id'], unique=False)
    op.create_index(op.f('ix_clause_verdicts_id'), 'clause_verdicts', ['id'], unique=False)
    op.create_index(op.f('ix_clause_verdicts_report_id'), 'clause_verdicts', ['report_id'], unique=False)

    # 13. Evidence Items
    op.create_table(
        'evidence_items',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('verdict_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('evidence_type', sa.String(length=50), nullable=False),
        sa.Column('start_ms', sa.Integer(), nullable=False),
        sa.Column('end_ms', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('thumbnail_key', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['verdict_id'], ['clause_verdicts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evidence_items_id'), 'evidence_items', ['id'], unique=False)
    op.create_index(op.f('ix_evidence_items_verdict_id'), 'evidence_items', ['verdict_id'], unique=False)

    # 14. Reviews
    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)
    op.create_index(op.f('ix_reviews_reviewer_id'), 'reviews', ['reviewer_id'], unique=False)
    op.create_index(op.f('ix_reviews_submission_id'), 'reviews', ['submission_id'], unique=False)

    # 15. Audit Events
    op.create_table(
        'audit_events',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('actor_type', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('before', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('after', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('request_id', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_events_actor_id'), 'audit_events', ['actor_id'], unique=False)
    op.create_index(op.f('ix_audit_events_id'), 'audit_events', ['id'], unique=False)

    # 16. Notifications
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.String(length=1024), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)

    # 17. Jobs
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('task_name', sa.String(length=100), nullable=False),
        sa.Column('celery_task_id', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('attempt', sa.Integer(), nullable=False),
        sa.Column('max_attempts', sa.Integer(), nullable=False),
        sa.Column('error_class', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('celery_task_id')
    )
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=False)
    op.create_index(op.f('ix_jobs_submission_id'), 'jobs', ['submission_id'], unique=False)


def downgrade() -> None:
    op.drop_table('jobs')
    op.drop_table('notifications')
    op.drop_table('audit_events')
    op.drop_table('reviews')
    op.drop_table('evidence_items')
    op.drop_table('clause_verdicts')
    op.drop_table('compliance_reports')
    op.drop_table('analysis_artifacts')
    op.drop_table('submissions')
    op.drop_table('clauses')
    op.drop_table('contracts')
    op.drop_table('campaigns')
    op.drop_table('platform_connections')
    op.drop_table('creator_profiles')
    op.drop_table('users')
    op.drop_table('organizations')
