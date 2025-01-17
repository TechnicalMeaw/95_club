"""primary id changed from mobile to email

Revision ID: b460250efb4f
Revises: ab3456dc82c9
Create Date: 2024-08-27 21:14:16.415284

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b460250efb4f'
down_revision: Union[str, None] = 'ab3456dc82c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('temp_users', sa.Column('username', sa.String(), nullable=False))
    op.drop_index('ix_temp_users_phone_number', table_name='temp_users')
    op.create_index(op.f('ix_temp_users_username'), 'temp_users', ['username'], unique=True)
    op.drop_column('temp_users', 'phone_number')
    op.alter_column('users', 'phone_no',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_constraint('users_phone_no_key', 'users', type_='unique')
    op.create_unique_constraint(None, 'users', ['email'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.create_unique_constraint('users_phone_no_key', 'users', ['phone_no'])
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'phone_no',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.add_column('temp_users', sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_temp_users_username'), table_name='temp_users')
    op.create_index('ix_temp_users_phone_number', 'temp_users', ['phone_number'], unique=True)
    op.drop_column('temp_users', 'username')
    # ### end Alembic commands ###
