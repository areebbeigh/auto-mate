"""integration nullable credentials by type

Revision ID: d3e4f5a6b7c8
Revises: c2f8a1b3d4e5
Create Date: 2026-03-27

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "d3e4f5a6b7c8"
down_revision = "c2f8a1b3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("integrations") as batch:
        batch.alter_column(
            "access_key",
            existing_type=sa.String(length=255),
            nullable=True,
        )
        batch.alter_column(
            "access_key_secret",
            existing_type=sa.String(length=255),
            nullable=True,
        )
        batch.alter_column(
            "username",
            existing_type=sa.String(length=255),
            nullable=True,
        )
        batch.alter_column(
            "password",
            existing_type=sa.String(length=255),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("integrations") as batch:
        batch.alter_column(
            "password",
            existing_type=sa.String(length=255),
            nullable=False,
        )
        batch.alter_column(
            "username",
            existing_type=sa.String(length=255),
            nullable=False,
        )
        batch.alter_column(
            "access_key_secret",
            existing_type=sa.String(length=255),
            nullable=False,
        )
        batch.alter_column(
            "access_key",
            existing_type=sa.String(length=255),
            nullable=False,
        )
