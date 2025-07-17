"""Создание таблиц quests и quest_tasks

Revision ID: c75618ad87d3
Revises: 1172c6b5505c
Create Date: 2025-05-15 16:04:50.247194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c75618ad87d3'
down_revision: Union[str, None] = '1172c6b5505c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'quests',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('description', sa.String),
        sa.Column('status', sa.String, nullable=False, default="pending")
    )

    op.create_table(
        'quest_tasks',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('quest_id', sa.Integer, sa.ForeignKey('quests.id', ondelete="CASCADE")),
        sa.Column('description', sa.String, nullable=False),
        sa.Column('status', sa.String, nullable=False, default="pending"),
        sa.Column('comment', sa.String)
    )


def downgrade():
    op.drop_table('quest_tasks')
    op.drop_table('quests')