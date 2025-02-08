"""adding relationships

Revision ID: 882c36ea22b4
Revises: 5c73ef7d15b8
Create Date: 2025-02-08 05:45:42.719933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '882c36ea22b4'
down_revision: Union[str, None] = '5c73ef7d15b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
