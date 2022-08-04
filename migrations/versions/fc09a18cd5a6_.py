"""empty message

Revision ID: fc09a18cd5a6
Revises: 91bc0deedc34
Create Date: 2022-08-02 21:23:50.079014

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fc09a18cd5a6'
down_revision = '91bc0deedc34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('AvailabilityArtist')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('AvailabilityArtist',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"AvailabilityArtist_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('end_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], name='AvailabilityArtist_artist_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='AvailabilityArtist_pkey')
    )
    # ### end Alembic commands ###
