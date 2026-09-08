"""pdf_extractions_and_clause_bboxes

Revision ID: 0002_pdf_extractions
Revises: 0001_initial_schema_pg
Create Date: 2026-09-08 18:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0002_pdf_extractions'
down_revision: Union[str, None] = '0001_initial_schema_pg'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create pdf_extractions table
    op.create_table(
        'pdf_extractions',
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False),
        sa.Column('full_text', sa.Text(), nullable=False),
        sa.Column('pages', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_scanned', sa.Boolean(), nullable=False),
        sa.Column('extraction_method', sa.String(length=50), nullable=False),
        sa.Column('char_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('content_hash')
    )
    op.create_index(op.f('ix_pdf_extractions_content_hash'), 'pdf_extractions', ['content_hash'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_pdf_extractions_content_hash'), table_name='pdf_extractions')
    op.drop_table('pdf_extractions')
