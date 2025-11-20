"""
Migration script template for Alembic.
"""

% if imports:
% for imp in imports:
from ${imp} import *
% endfor

% if env_opts.py3k:
# coding: utf-8
% endif

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass


def downgrade():
    pass
