import os
import time

from .repository import JsonRepository
from config import Paths
from util import (
    FileWatcher,
    modify_json_file
)

class TruthOrDareRepo(JsonRepository):
    _watched_truth_dares_json = None

    def __init__(self):
        os.makedirs(Paths.data_dir, exist_ok=True)

        if self.__class__._watched_truth_dares_json is None:
            self.__class__._watched_truth_dares_json = FileWatcher(Paths.truth_dare)
    
    def _get(self, *keys: str) -> any:
        return super()._get(self.__class__._watched_truth_dares_json, *keys)
    
    def _set(self, *keys: str, value: any) -> None:
        modify_json_file(
            Paths.truth_dare,
            lambda data: super(TruthOrDareRepo, self)._set(data, *keys, value=value)
        )
    
    def _remove(self, *keys: str) -> None:
        modify_json_file(
            Paths.truth_dare,
            lambda data: super(TruthOrDareRepo, self)._remove(data, *keys)
        )
    
    # Guilds

    def get_guilds(self) -> list[str] | None:
        return list(self.__class__._watched_truth_dares_json.keys())
    
    # Dares

    def get_dares(self, guild_id: int) -> list[str] | None:
        return self._get(str(guild_id), 'dares')

    def get_dares_count(self, guild_id: int) -> int:
        if str(guild_id) in self.__class__._watched_truth_dares_json:
            if 'dares' in self.__class__._watched_truth_dares_json[str(guild_id)]:
                return len(self.__class__._watched_truth_dares_json[str(guild_id)]['dares'])
        
        return 0

    def get_dare(self, guild_id: int, index: int) -> dict[str, int | str]:
        return self._get(str(guild_id), 'dares')[index]

    def set_dare(self, guild_id: int, user_id: int, dare_str: str):
        dares = self.get_dares(guild_id) or []
        dares.append({
            'unix_time': int(time.time()),
            'user_id': user_id,
            'dare_str': dare_str
        })
        self._set(str(guild_id), 'dares', value=dares)
    
    def remove_dare(self, guild_id: str, index: int) -> str | None:
        dares = self.get_dares(guild_id) or []
        if len(dares) <= index:
            return None
        removed_dare = dares.pop(index)
        self._set(str(guild_id), 'dares', value=dares)
        return removed_dare
