"""users table

Revision ID: 59db735876eb
Revises: 
Create Date: 2019-03-25 19:08:29.540382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59db735876eb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('firstname', sa.String(length=120), nullable=True),
    sa.Column('lastname', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_firstname'), 'user', ['firstname'], unique=True)
    op.create_index(op.f('ix_user_lastname'), 'user', ['lastname'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_lastname'), table_name='user')
    op.drop_index(op.f('ix_user_firstname'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###