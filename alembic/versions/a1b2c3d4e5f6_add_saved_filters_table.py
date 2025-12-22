"""add saved_filters table

Revision ID: a1b2c3d4e5f6
Revises: 8c57b2c84100
Create Date: 2025-12-20 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8c57b2c84100'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('saved_filters',
    sa.Column('filter_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('price_min', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('price_max', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('price_sqm_min', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('price_sqm_max', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('rooms', sa.Text(), nullable=True),
    sa.Column('city', sa.String(length=255), nullable=True),
    sa.Column('city_district', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('filter_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('saved_filters')

