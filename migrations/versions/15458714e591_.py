"""empty message

Revision ID: 15458714e591
Revises: d552425f004b
Create Date: 2022-05-15 20:50:05.678715

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15458714e591'
down_revision = 'd552425f004b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recordings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=True),
    sa.Column('recording', sa.String(length=255), nullable=True),
    sa.Column('accent', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recordings')
    # ### end Alembic commands ###