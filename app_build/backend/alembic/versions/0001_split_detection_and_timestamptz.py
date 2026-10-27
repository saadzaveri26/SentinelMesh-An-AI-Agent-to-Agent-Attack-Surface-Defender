from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "agents",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "trust_edges",
        "last_interaction",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        postgresql_using="last_interaction AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "messages",
        "timestamp",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        postgresql_using="timestamp AT TIME ZONE 'UTC'",
    )
    op.add_column("messages", sa.Column("bert_score", sa.Float(), nullable=False, server_default="0.0"))
    op.add_column("messages", sa.Column("rule_hits", sa.JSON(), nullable=True))
    op.add_column("messages", sa.Column("anomaly_flags", sa.JSON(), nullable=True))
    op.execute("UPDATE messages SET bert_score = threat_score")
    op.drop_column("messages", "threat_score")


def downgrade():
    op.add_column("messages", sa.Column("threat_score", sa.Float(), nullable=False, server_default="0.0"))
    op.execute("UPDATE messages SET threat_score = bert_score")
    op.drop_column("messages", "anomaly_flags")
    op.drop_column("messages", "rule_hits")
    op.drop_column("messages", "bert_score")
    op.alter_column(
        "messages",
        "timestamp",
        type_=sa.DateTime(timezone=False),
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "trust_edges",
        "last_interaction",
        type_=sa.DateTime(timezone=False),
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "agents",
        "created_at",
        type_=sa.DateTime(timezone=False),
        existing_type=sa.DateTime(timezone=True),
    )
