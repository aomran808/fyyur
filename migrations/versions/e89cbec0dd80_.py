"""empty message

Revision ID: e89cbec0dd80
Revises: 
Create Date: 2021-02-01 01:00:01.007045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e89cbec0dd80'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('city', sa.String(length=120), nullable=False),
    sa.Column('state', sa.String(length=120), nullable=False),
    sa.Column('phone', sa.String(length=120), nullable=False),
    sa.Column('website', sa.String(length=120), nullable=True),
    sa.Column('genres', sa.String(length=120), nullable=False),
    sa.Column('image_link', sa.String(length=500), nullable=False),
    sa.Column('facebook_link', sa.String(length=120), nullable=True),
    sa.Column('seeking_venue', sa.Boolean(), nullable=False),
    sa.Column('seeking_description', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('venue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('genres', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('city', sa.String(length=120), nullable=False),
    sa.Column('state', sa.String(length=120), nullable=False),
    sa.Column('address', sa.String(length=120), nullable=False),
    sa.Column('phone', sa.String(length=120), nullable=False),
    sa.Column('website', sa.String(length=120), nullable=False),
    sa.Column('image_link', sa.String(length=500), nullable=False),
    sa.Column('facebook_link', sa.String(length=120), nullable=False),
    sa.Column('seeking_talent', sa.Boolean(), nullable=False),
    sa.Column('seeking_description', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('show',
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('Artist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['Artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.PrimaryKeyConstraint('venue_id', 'Artist_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('show')
    op.drop_table('venue')
    op.drop_table('artist')
    # ### end Alembic commands ###
