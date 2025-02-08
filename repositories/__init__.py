from typing import TypedDict
from .artfight_repo import ArtfightRepo
from .repository import Repository
from .servers_settings_repo import ServersSettingsRepo

__all__ = ['ServersSettingsRepo', 'ArtfightRepo', 'Repository']

class RepositoriesDict(TypedDict, total=True):
    servers_settings_repo: ServersSettingsRepo
    artfight_repo: ArtfightRepo