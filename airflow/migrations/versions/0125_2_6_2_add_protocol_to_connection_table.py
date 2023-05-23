#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""add protocol column to connection table

Revision ID: 937cbd173ca1
Revises: 98ae134e6fff
Create Date: 2023-05-23 12:16:35.948209

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "937cbd173ca1"
down_revision = "98ae134e6fff"
branch_labels = None
depends_on = None
airflow_version = "2.6.2"


def upgrade():
    """Apply add protocol column to connection table"""
    with op.batch_alter_table("connection", schema=None) as batch_op:
        batch_op.add_column(sa.Column("protocol", sa.String(length=500), nullable=True))


def downgrade():
    """Unapply add protocol column to connection table"""
    with op.batch_alter_table("connection", schema=None) as batch_op:
        batch_op.drop_column("protocol")
