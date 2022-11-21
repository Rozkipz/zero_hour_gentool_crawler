import datetime
from typing import Optional


class Player:
    def __init__(self, player_id, name, first_seen=None, last_seen=None):
        self.player_id: hex = player_id

        if isinstance(name, str):
            self.names: list[list[str]] = [[name, str(datetime.datetime.utcnow()), str(datetime.datetime.utcnow())]]

        else:
            self.names: list[list[str]] = name

        self.first_seen: Optional[datetime.datetime] = first_seen
        self.last_seen: Optional[datetime.datetime] = last_seen

    def as_dict(self):
        return self.__dict__
