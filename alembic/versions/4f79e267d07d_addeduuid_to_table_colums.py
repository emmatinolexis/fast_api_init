"""addeduuid to table colums

Revision ID: 4f79e267d07d
Revises: 6aabe0cfff7c
Create Date: 2023-10-27 10:40:39.910086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid



# revision identifiers, used by Alembic.
revision: str = '4f79e267d07d'
down_revision: Union[str, None] = '6aabe0cfff7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('profiles', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('asset_types', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('assets', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('token', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('email_verifications', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('package_items', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('packages', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('package_item_assignments', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('features', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('equipments', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('equipment_types', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('onboardings', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('onboarding_feature_assignments', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))
    op.add_column('contact_sales', sa.Column('uuid', sa.String(length=50), nullable=False, default=uuid.uuid4, index=True))

def downgrade() -> None:
    op.drop_column('users', 'uuid')
    op.drop_column('profiles', 'uuid')
    op.drop_column('asset_types', 'uuid')
    op.drop_column('assets', 'uuid')
    op.drop_column('token', 'uuid')
    op.drop_column('email_verifications', 'uuid')
    op.drop_column('package_items', 'uuid')
    op.drop_column('packages', 'uuid')
    op.drop_column('package_item_assignments', 'uuid')
    op.drop_column('features', 'uuid')
    op.drop_column('equipments', 'uuid')
    op.drop_column('equipment_types', 'uuid')
    op.drop_column('onboardings', 'uuid')
    op.drop_column('onboarding_feature_assignments', 'uuid')
    op.drop_column('contact_sales', 'uuid')
    
