"""fix_room_open_data_structure

Revision ID: 2ffce2cb4e05
Revises: 7234b2f78d8f
Create Date: 2024-04-26 05:00:47.727948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2ffce2cb4e05'
down_revision: Union[str, None] = '7234b2f78d8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('discord_room_announce_messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('guild_id', sa.BigInteger(), nullable=False),
    sa.Column('channel_id', sa.BigInteger(), nullable=False),
    sa.Column('message_id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discord_room_announce_messages_guild_id'), 'discord_room_announce_messages', ['guild_id'], unique=False)
    op.drop_index('ix_discord_announce_messages_guild_id', table_name='discord_announce_messages')
    op.drop_table('discord_announce_messages')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('discord_announce_messages',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('guild_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('channel_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('message_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='discord_announce_messages_pkey')
    )
    op.create_index('ix_discord_announce_messages_guild_id', 'discord_announce_messages', ['guild_id'], unique=False)
    op.drop_index(op.f('ix_discord_room_announce_messages_guild_id'), table_name='discord_room_announce_messages')
    op.drop_table('discord_room_announce_messages')
    # ### end Alembic commands ###
