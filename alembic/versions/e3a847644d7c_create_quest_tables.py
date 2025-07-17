"""create_quest_tables

Revision ID: e3a847644d7c
Revises: 790a6c677044
Create Date: 2025-05-21 13:02:57.145315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3a847644d7c'
down_revision: Union[str, None] = '790a6c677044'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Таблица шаблонов квестов
    op.create_table(
        'quest_templates',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('description', sa.Text, nullable=True)
    )

    # Таблица шагов квеста (привязана к шаблону)
    op.create_table(
        'quest_steps',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('quest_template_id', sa.Integer, sa.ForeignKey('quest_templates.id', ondelete='CASCADE')),
        sa.Column('step_number', sa.Integer, nullable=False),
        sa.Column('description', sa.Text, nullable=False)
    )

    # Таблица назначенных квестов
    op.create_table(
        'quest_assignments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('quest_template_id', sa.Integer, sa.ForeignKey('quest_templates.id', ondelete='CASCADE')),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('due_date', sa.Date, nullable=False),
        sa.Column('is_completed', sa.Boolean, default=False)
    )

    # Таблица выполнения шагов
    op.create_table(
        'quest_progress',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('assignment_id', sa.Integer, sa.ForeignKey('quest_assignments.id', ondelete='CASCADE')),
        sa.Column('quest_step_id', sa.Integer, sa.ForeignKey('quest_steps.id', ondelete='CASCADE')),
        sa.Column('is_done', sa.Boolean, default=False),
        sa.Column('comment', sa.Text, nullable=True)
    )


def downgrade():
    op.drop_table('quest_progress')
    op.drop_table('quest_assignments')
    op.drop_table('quest_steps')
    op.drop_table('quest_templates')