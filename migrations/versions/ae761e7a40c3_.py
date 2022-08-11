"""empty message

Revision ID: ae761e7a40c3
Revises: c4c31f1ca649
Create Date: 2022-08-09 15:07:50.881332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae761e7a40c3'
down_revision = 'c4c31f1ca649'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_Show_artist_id'), 'Show', ['artist_id'], unique=False)
    op.create_index(op.f('ix_Show_venue_id'), 'Show', ['venue_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_Show_venue_id'), table_name='Show')
    op.drop_index(op.f('ix_Show_artist_id'), table_name='Show')
    # ### end Alembic commands ###
