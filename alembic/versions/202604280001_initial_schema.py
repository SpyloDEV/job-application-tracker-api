"""Initial schema.

Revision ID: 202604280001
Revises:
Create Date: 2026-04-28 23:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202604280001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


application_status = sa.Enum(
    "saved",
    "applied",
    "interview",
    "technical_test",
    "offer",
    "rejected",
    "archived",
    name="applicationstatus",
    native_enum=False,
)
application_source = sa.Enum(
    "Wellfound",
    "LinkedIn",
    "Indeed",
    "WeWorkRemotely",
    "RemoteOK",
    "HackerRank",
    "Turing",
    "Upwork",
    "Other",
    name="applicationsource",
    native_enum=False,
)
remote_type = sa.Enum(
    "remote",
    "hybrid",
    "onsite",
    "flexible",
    name="remotetype",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "job_applications",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("company_name", sa.String(length=180), nullable=False),
        sa.Column("job_title", sa.String(length=220), nullable=False),
        sa.Column("job_url", sa.String(length=1000), nullable=True),
        sa.Column("location", sa.String(length=180), nullable=True),
        sa.Column("remote_type", remote_type, nullable=False),
        sa.Column("salary_min", sa.Float(), nullable=True),
        sa.Column("salary_max", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("status", application_status, nullable=False),
        sa.Column("source", application_source, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("applied_at", sa.Date(), nullable=True),
        sa.Column("follow_up_date", sa.Date(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_job_applications_applied_at"),
        "job_applications",
        ["applied_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_applications_company_name"),
        "job_applications",
        ["company_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_applications_follow_up_date"),
        "job_applications",
        ["follow_up_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_applications_job_title"),
        "job_applications",
        ["job_title"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_applications_remote_type"),
        "job_applications",
        ["remote_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_applications_source"),
        "job_applications",
        ["source"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_applications_status"),
        "job_applications",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_applications_user_id"),
        "job_applications",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "application_notes",
        sa.Column("application_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["job_applications.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_application_notes_application_id"),
        "application_notes",
        ["application_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_application_notes_user_id"),
        "application_notes",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "reminders",
        sa.Column("application_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["job_applications.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reminders_application_id"),
        "reminders",
        ["application_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reminders_due_date"),
        "reminders",
        ["due_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reminders_is_completed"),
        "reminders",
        ["is_completed"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reminders_user_id"),
        "reminders",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reminders_user_id"), table_name="reminders")
    op.drop_index(op.f("ix_reminders_is_completed"), table_name="reminders")
    op.drop_index(op.f("ix_reminders_due_date"), table_name="reminders")
    op.drop_index(op.f("ix_reminders_application_id"), table_name="reminders")
    op.drop_table("reminders")

    op.drop_index(op.f("ix_application_notes_user_id"), table_name="application_notes")
    op.drop_index(
        op.f("ix_application_notes_application_id"),
        table_name="application_notes",
    )
    op.drop_table("application_notes")

    op.drop_index(op.f("ix_job_applications_user_id"), table_name="job_applications")
    op.drop_index(op.f("ix_job_applications_status"), table_name="job_applications")
    op.drop_index(op.f("ix_job_applications_source"), table_name="job_applications")
    op.drop_index(
        op.f("ix_job_applications_remote_type"), table_name="job_applications"
    )
    op.drop_index(op.f("ix_job_applications_job_title"), table_name="job_applications")
    op.drop_index(
        op.f("ix_job_applications_follow_up_date"),
        table_name="job_applications",
    )
    op.drop_index(
        op.f("ix_job_applications_company_name"), table_name="job_applications"
    )
    op.drop_index(op.f("ix_job_applications_applied_at"), table_name="job_applications")
    op.drop_table("job_applications")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
