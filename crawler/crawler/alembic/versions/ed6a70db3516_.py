"""empty message

Revision ID: ed6a70db3516
Revises: 
Create Date: 2022-11-19 19:03:34.397385

"""
import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import VARCHAR, ARRAY, INTEGER, FLOAT, TIMESTAMP

# revision identifiers, used by Alembic.
revision = 'ed6a70db3516'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "armies",
        sa.Column("id", INTEGER, autoincrement=True, primary_key=True, nullable=False, index=True),  # Why on earth would you use strings for IDs???
        sa.Column("name", VARCHAR(64), nullable=False),  # names defined as {{"name1", "first_seen_UTC", "last_seen_UTC"},}
    )

    op.create_table(
        "player",
        sa.Column("id", VARCHAR(12), primary_key=True, nullable=False, index=True),  # Who uses str for IDs?????
        sa.Column("names", ARRAY(VARCHAR(64), dimensions=2), nullable=False),  # names defined as {{"name1", "first_seen_UTC", "last_seen_UTC"},}
        sa.Column("first_seen", TIMESTAMP(timezone=True), default=datetime.datetime.utcnow()),  # Allow these to be nullable for now, as we have to get each battle to fill them in.
        sa.Column("last_seen", TIMESTAMP(timezone=True), default=datetime.datetime.utcnow()),
    )

    op.create_table(
        "battles",
        sa.Column("id", INTEGER, autoincrement=True, primary_key=True, nullable=False, index=True),
        sa.Column("uploader_player_id", VARCHAR(12), sa.ForeignKey("player.id", name="player_uploader_id_fk_1"), nullable=False, index=True),
        # sa.Column("map_id", INTEGER, nullable=False),  # Make a map table in the future?
        sa.Column("length_seconds", INTEGER, nullable=False),
        sa.Column("start_cash", INTEGER, nullable=False),
        sa.Column("match_mode", VARCHAR(20), nullable=False),
        sa.Column("match_start", TIMESTAMP(timezone=True), nullable=False),
        sa.Column("gt_version", FLOAT, nullable=False),  # Bank on GT keeping versions as simply `x.x`
        sa.Column("game_version", VARCHAR(20), nullable=False),  # Varchar here as I'm not sure what values might be defined in a replay.

        # Each player's ID
        sa.Column("first", VARCHAR(12), sa.ForeignKey("player.id", name=f"player_first_id_fk_1"), nullable=False, index=True),
        sa.Column("second", VARCHAR(12), sa.ForeignKey("player.id", name=f"player_second_id_fk_1"), nullable=False, index=True),
        sa.Column("third", VARCHAR(12), sa.ForeignKey("player.id", name=f"player_third_id_fk_1"), index=True),
        sa.Column("fourth", VARCHAR(12), sa.ForeignKey("player.id", name=f"player_fourth_id_fk_1"), index=True),
        sa.Column("fifth", VARCHAR(12), sa.ForeignKey("player.id", name=f"player_fifth_id_fk_1"), index=True),
        sa.Column("sixth", VARCHAR(12), sa.ForeignKey("player.id", name=f"player_sixth_id_fk_1"), index=True),
        sa.Column("seventh", VARCHAR(12), sa.ForeignKey("player.id", name=f"player_seventh_id_fk_1"), index=True),
        sa.Column("eighth", VARCHAR(12), sa.ForeignKey("player.id", name=f"player_eighth_id_fk_1"), index=True),

        # Each player's army
        sa.Column(f"first_army_id", INTEGER, sa.ForeignKey("armies.id", name=f"army_first_id_fk_1"), nullable=False),
        sa.Column(f"second_army_id", INTEGER, sa.ForeignKey("armies.id", name=f"army_second_id_fk_1"), nullable=False),
        sa.Column(f"third_army_id", INTEGER, sa.ForeignKey("armies.id", name=f"army_third_id_fk_1")),
        sa.Column(f"fourth_army_id", INTEGER, sa.ForeignKey("armies.id", name=f"army_fourth_id_fk_1")),
        sa.Column(f"fifth_army_id", INTEGER, sa.ForeignKey("armies.id", name=f"army_fifth_id_fk_1")),
        sa.Column(f"sixth_army_id", INTEGER, sa.ForeignKey("armies.id", name=f"army_sixth_id_fk_1")),
        sa.Column(f"seventh_army_id", INTEGER, sa.ForeignKey("armies.id", name=f"army_seventh_id_fk_1")),
        sa.Column(f"eighth_army_id", INTEGER, sa.ForeignKey("armies.id", name=f"army_eighth_id_fk_1")),

        # player_ids of each team makeup
        sa.Column("team1", ARRAY(VARCHAR(12), dimensions=1), default=None),
        sa.Column("team2", ARRAY(VARCHAR(12), dimensions=1), default=None),
        sa.Column("team3", ARRAY(VARCHAR(12), dimensions=1), default=None),
        sa.Column("team4", ARRAY(VARCHAR(12), dimensions=1), default=None),

        # Just a list of files that could be retrieved from gentool.net
        sa.Column("gt_associated_files", ARRAY(VARCHAR(1000), dimensions=1)),  # Potentially could have huge replay filenames

    )

    def downgrade():
        op.drop_table("armies")
        op.drop_table("player")
        op.drop_table("battles")
