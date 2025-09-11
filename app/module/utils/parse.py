import json
from datetime import datetime
from pathlib import Path

import requests
from steam.steamid import SteamID

BASE_DIR = Path(__file__).resolve().parent.parent


class SteamID32:
    @classmethod
    def get_steamid32(cls, link: str) -> int:
        steamid32 = SteamID.from_url(link).as_32
        return steamid32


class Parse:
    def __init__(self, userid):
        self.steam32id = userid
        self.userinfo = self._get_profile_info()
        self.heroes = self._get_heroes()

    def _get_profile_info(self) -> dict:
        url = f'https://api.opendota.com/api/players/{self.steam32id}'
        return requests.get(url).json()

    def _get_heroes(self) -> dict:
        with open(f'{BASE_DIR}/utils/heroes_id.json', 'r') as f:
            return json.load(f)

    def get_username(self) -> str:
        return self.userinfo['profile']['personaname']

    def get_avatar_url(self) -> str:
        return self.userinfo['profile']['avatarfull']

    def get_loccountrycode(self) -> str:
        return self.userinfo['profile']['loccountrycode']

    def get_profile_url(self) -> str:
        return self.userinfo['profile']['profileurl']

    def get_steamid(self) -> str:
        return self.userinfo['profile']['steamid']

    def get_rank_tier(self) -> int | None:
        return self.userinfo['rank_tier']

    def get_leaderboard_rank(self) -> int | None:
        return self.userinfo['leaderboard_rank']

    def get_mmr_estimate(self) -> str | None:
        return str(self.userinfo['mmr_estimate']['estimate'])

    def _get_wl(self, game_mode: int = None) -> dict:
        if game_mode is None:
            url = f'https://api.opendota.com/api/players/{self.steam32id}/wl'
        else:
            url = f'https://api.opendota.com/api/players/{self.steam32id}/wl?game_mode={str(game_mode)}'
        return requests.get(url).json()

    def get_won(self, game_mode: int = None) -> str:
        return str(self._get_wl(game_mode)['win'])

    def get_losses(self, game_mode: int = None) -> str:
        return str(self._get_wl(game_mode)['lose'])

    def is_dota_plus(self) -> bool:
        return self.userinfo['profile']['plus']

    def get_five_player_heroes(self) -> list:
        return self._get_player_heroes()[0:5]

    def _get_player_heroes(self) -> list:
        url = f'https://api.opendota.com/api/players/{self.steam32id}/heroes'
        return requests.get(url).json()

    def get_five_player_heroes_names(self) -> list:
        return [self.search_hero_name(hero['hero_id']) for hero in self.get_five_player_heroes()]

    def search_hero_name(self, id) -> str:
        return self.heroes[str(id)]

    def get_last_match_time(self) -> str:
        start_time = self._get_player_recent_matches()[0]['start_time']
        data = datetime.fromtimestamp(start_time)
        return data.strftime("%d %B %Y %H:%M")

    def _get_player_recent_matches(self) -> list:
        url = f'https://api.opendota.com/api/players/{self.steam32id}/recentMatches'
        return requests.get(url).json()

    def get_winrate(self) -> str:
        wins = int(self.get_won())
        losses = int(self.get_losses())
        total_matches = wins + losses
        winrate: float | int = (wins / total_matches) * 100 if total_matches else 0
        return f"{winrate:.2f}"

    @classmethod
    def get_user_info(cls, userid) -> dict:
        user = Parse(userid)
        user_info = {
            'account_id': user.steam32id,
            'steamid': user.get_steamid(),
            'personaname': user.get_username(),
            'avatar': user.get_avatar_url(),
            'profile_url': user.get_profile_url(),
            'win_count': user.get_won(),
            'lose_count': user.get_losses(),
            'rank_tier': user.get_rank_tier(),
            'heroes': user.get_five_player_heroes_names(),
            'last_match': user.get_last_match_time(),
            'plus': user.is_dota_plus(),
            'winrate': user.get_winrate(),
            'get_leaderboard_rank': str(user.get_leaderboard_rank())
        }
        return user_info


class Rank:
    def __init__(self, steam32id: int):
        player = Parse(steam32id)
        rank = player.get_rank_tier()
        self.leaderboard_rank = player.get_leaderboard_rank()

        if rank == 'null':
            self.rank = None
            return

        if type(rank) is int or type(rank) is float:
            rank = str(rank)

        if not all([rank.isdigit(), len(rank) == 2]):
            print("Something went wrong!\nRank input: %s\n" % rank)
            self.rank = None
            return

        self.rank = rank

    def __str__(self):
        return str(self.name)

    @property
    def name(self) -> str | None:
        if self.rank is None:
            return None

        if self.rank[0] == "8":
            return f"Immortal {self.leaderboard_rank}"

        ranks = {"1": "Herald",
                 "2": "Guardian",
                 "3": "Crusader",
                 "4": "Archon",
                 "5": "Legend",
                 "6": "Ancient",
                 "7": "Divine"}

        return f"{ranks[self.rank[0]]} {self.rank[1]}"
