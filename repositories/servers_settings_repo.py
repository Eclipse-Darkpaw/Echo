import os

from .repository import JsonRepository
from config import Paths
from util import (
    FileWatcher,
    modify_json_file
)

class ServersSettingsRepo(JsonRepository):
    _watched_servers_json = None

    def __init__(self):
        os.makedirs(Paths.data_dir, exist_ok=True)

        if self.__class__._watched_servers_json is None:
            self.__class__._watched_servers_json = FileWatcher(Paths.servers_settings)

    def _get(self, *keys: str) -> any:
        return super()._get(self.__class__._watched_servers_json, *keys)

    def _set(self, *keys: str, value: any) -> None:
        modify_json_file(
            Paths.servers_settings,
            lambda data: super(ServersSettingsRepo, self)._set(data, *keys, value=value)
        )

    def _remove(self, *keys: str) -> None:
        modify_json_file(
            Paths.servers_settings,
            lambda data: super(ServersSettingsRepo, self)._remove(data, *keys)
        )
        
    # guild_name

    def get_guild_name(self, guild_id: str) -> str | None:
        return self._get(guild_id, 'name')
    
    def set_guild_name(self, guild_id: str, guild_name: str):
        self._set(guild_id, 'name', value=guild_name)

    # guild code word

    def get_guild_code_word(self, guild_id: str) -> str | None:
        return self._get(guild_id, 'codeword')

    def set_guild_code_word(self, guild_id: str, code_word: str):
        self._set(guild_id, 'codeword', value=code_word)

    # guild channels
    
    def get_guild_channels(self, guild_id: str) -> dict | None:
        return self._get(guild_id, 'channels')

    def get_guild_channel(self, guild_id: str, channel_name: str) -> int | None:
        return self._get(guild_id, 'channels', channel_name)

    def set_guild_channels(self, guild_id: str, channels: dict):
        self._set(guild_id, 'channels', value=channels)

    def set_guild_channel(self, guild_id: str, channel_name: str, channel_id: int | str):
        self._set(guild_id, 'channels', channel_name, value=int(channel_id))

    def remove_guild_channel(self, guild_id: str, channel_name: str):
        self._remove(guild_id, 'channels', channel_name)
    
    def remove_guild_channels(self, guild_id: str, channel_names: list):
        for channel_name in channel_names:
            self.remove_guild_channel(guild_id, channel_name)

    # Guild Roles
    
    def get_guild_roles(self, guild_id: str) -> dict | None:
        return self._get(guild_id, 'roles')

    def get_guild_role(self, guild_id: str, role_name: str) -> int | None:
        return self._get(guild_id, 'roles', role_name)
    
    def set_guild_roles(self, guild_id: str, roles: dict):
        self._set(guild_id, 'roles', value=roles)

    def set_guild_role(self, guild_id: str, role_name: str, role_id):
        self._set(guild_id, 'roles', role_name, value=role_id)

    def remove_guild_role(self, guild_id: str, role_name: str):
        self._remove(guild_id, 'roles', role_name)
    
    def remove_guild_roles(self, guild_id: str, role_names: list):
        for role_name in role_names:
            self.remove_guild_role(guild_id, role_name)

    # Guild Questions

    def get_guild_questions(self, guild_id: str) -> list[str] | None:
        return self._get(guild_id, 'questions')
    
    def set_guild_questions(self, guild_id: str, questions: list[str]):
        self._set(guild_id, 'questions', value=questions)

    def remove_guild_questions(self, guild_id):
        self._remove(guild_id, 'questions')

    # Guild Question Displays

    def get_guild_question_displays(self, guild_id: str) -> list[str] | None:
        return self._get(guild_id, 'questions_display')
    
    def set_guild_question_displays(self, guild_id: str, question_displays: list[str]):
        self._set(guild_id, 'questions_display', value=question_displays)
    
    def remove_guild_question_displays(self, guild_id: str):
        self._remove(guild_id, 'questions_display')
