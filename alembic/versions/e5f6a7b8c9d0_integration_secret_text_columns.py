"""integration secret columns as TEXT for Fernet payloads

Revision ID: e5f6a7b8c9d0
Revises: d3e4f5a6b7c8
Create Date: 2026-03-27

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "e5f6a7b8c9d0"
down_revision = "d3e4f5a6b7c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("integrations") as batch:
        batch.alter_column(
            "access_key",
            existing_type=sa.String(length=255),
            type_=sa.Text(),
            nullable=True,
        )
        batch.alter_column(
            "access_key_secret",
            existing_type=sa.String(length=255),
            type_=sa.Text(),
            nullable=True,
        )
        batch.alter_column(
            "password",
            existing_type=sa.String(length=255),
            type_=sa.Text(),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("integrations") as batch:
        batch.alter_column(
            "password",
            existing_type=sa.Text(),
            type_=sa.String(length=255),
            nullable=True,
        )
        batch.alter_column(
            "access_key_secret",
            existing_type=sa.Text(),
            type_=sa.String(length=255),
            nullable=True,
        )
        batch.alter_column(
            "access_key",
            existing_type=sa.Text(),
            type_=sa.String(length=255),
            nullable=True,
        )
