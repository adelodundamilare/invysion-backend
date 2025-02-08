"""add_cascade_delete_to_user_relationships

Revision ID: 5c73ef7d15b8
Revises: 1937e10644cb
Create Date: 2025-02-08 02:01:43.333091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c73ef7d15b8'
down_revision: Union[str, None] = '1937e10644cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop existing foreign key constraints
    op.drop_constraint('folders_user_id_fkey', 'folders', type_='foreignkey')
    op.drop_constraint('files_user_id_fkey', 'files', type_='foreignkey')
    op.drop_constraint('settings_user_id_fkey', 'settings', type_='foreignkey')

    # Add new foreign key constraints with ON DELETE CASCADE
    op.create_foreign_key(
        'folders_user_id_fkey', 'folders', 'users', ['user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'files_user_id_fkey', 'files', 'users', ['user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'settings_user_id_fkey', 'settings', 'users', ['user_id'], ['id'], ondelete='CASCADE'
    )

def downgrade():
    # Drop the new foreign key constraints
    op.drop_constraint('folders_user_id_fkey', 'folders', type_='foreignkey')
    op.drop_constraint('files_user_id_fkey', 'files', type_='foreignkey')
    op.drop_constraint('settings_user_id_fkey', 'settings', type_='foreignkey')

    # Recreate the original foreign key constraints without ON DELETE CASCADE
    op.create_foreign_key(
        'folders_user_id_fkey', 'folders', 'users', ['user_id'], ['id']
    )
    op.create_foreign_key(
        'files_user_id_fkey', 'files', 'users', ['user_id'], ['id']
    )
    op.create_foreign_key(
        'settings_user_id_fkey', 'settings', 'users', ['user_id'], ['id']
    )
