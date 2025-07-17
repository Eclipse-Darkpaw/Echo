from typing import TypedDict
from .artfight_repo import ArtfightRepo
from .repository import Repository, JsonRepository, LogRepository
from .servers_settings_repo import ServersSettingsRepo
from .scam_log_repo import ScamLogRepo

__all__ = ['ServersSettingsRepo', 'ArtfightRepo', 'Repository']

class RepositoriesDict(TypedDict, total=True):
    servers_settings_repo: ServersSettingsRepo
    artfight_repo: ArtfightRepo
    scam_log_repo: ScamLogRepo