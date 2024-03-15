"""empty message

Revision ID: 5825e25f1b3a
Revises: 30f902853d29
Create Date: 2024-03-15 16:38:18.774275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5825e25f1b3a'
down_revision = '30f902853d29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('_title', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])
        batch_op.drop_column('title')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')
        batch_op.drop_column('_title')

    # ### end Alembic commands ###
