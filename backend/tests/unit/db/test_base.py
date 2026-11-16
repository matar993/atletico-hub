from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, UniqueConstraint
from sqlalchemy.schema import CreateTable

from atletico_hub.db.base import NAMING_CONVENTION, Base


class TestBase:
    def test_metadata_uses_the_naming_convention(self) -> None:
        assert NAMING_CONVENTION.items() <= Base.metadata.naming_convention.items()

    def test_naming_convention_names_every_constraint(self) -> None:
        metadata = MetaData(naming_convention=NAMING_CONVENTION)
        Table("team", metadata, Column("id", Integer, primary_key=True))
        player = Table(
            "player",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("email", String),
            Column("team_id", Integer, ForeignKey("team.id")),
            UniqueConstraint("email"),
        )

        ddl = str(CreateTable(player))

        assert "CONSTRAINT pk_player PRIMARY KEY" in ddl
        assert "CONSTRAINT uq_player_email UNIQUE" in ddl
        assert "CONSTRAINT fk_player_team_id_team FOREIGN KEY" in ddl
