import logging
import time

from discord.ext.commands import Bot, HelpCommand
from discord.ext.commands.bot import _default
from discord.utils import MISSING
from discord.app_commands import CommandTree, AppCommandContext, AppInstallationType
from discord import Intents

from config import BotConfig, Paths
from datetime import timedelta
from repositories import Repository, RepositoriesDict
from typing import Optional, Type, TypeVar
from util import setup_logger, to_snake_case

T = TypeVar('T', bound=Repository)

class EchoBot(Bot):
    def __init__(
        self,
        *,
        name: str,
        version_num: str = None,
        console_logging: bool = True,
        console_log_level: int = logging.INFO,
        ignore_discord_logs: bool = False,
        file_logging: bool = False,
        custom_log_file_path: str = None,
        file_log_level: int = logging.INFO,
        max_file_size: int = 2048,
        file_log_rotation_count: int = 10,
        help_command: Optional[HelpCommand] = _default,
        tree_cls: Type[CommandTree[any]] = CommandTree,
        description: Optional[str] = None,
        allowed_contexts: AppCommandContext = MISSING,
        allowed_installs: AppInstallationType = MISSING,
        intents: Intents,
        **options: any
    ):
        self.name = name
        self.version_num = version_num
        self.start_time = time.time()
        self._repositories: RepositoriesDict = {}

        if file_logging:
            log_file_path = custom_log_file_path or f'{Paths.logs_dir}/{name}_{logging.getLevelName(console_log_level)}.log'

        self.logger = setup_logger(
            console_logging=console_logging,
            console_log_level=console_log_level,
            ignore_discord_logs=ignore_discord_logs,
            log_file=log_file_path if file_logging else None,
            file_log_level=file_log_level,
            max_file_size=max_file_size,
            file_log_rotation_count=file_log_rotation_count
        )

        self.config = BotConfig(bot_name=name)
        
        super().__init__(
            command_prefix=self.config.prefix,
            help_command=help_command,
            tree_cls=tree_cls,
            description=description,
            allowed_contexts=allowed_contexts,
            allowed_installs=allowed_installs,
            intents=intents,
            **options
        )


    def add_repository(self, repository: Repository):
        """
        Adds a repository using its snake_case class name as the key.
        To access methods of the repository you can do so using .properties['repo_classname_in_snake_case'].some_method()

        Last docstring edit: -FoxyHunter V4.3.0
        Last method edit: -FoxyHunter V4.3.0
        :param repository: A repository class instance
        :return: None
        """
        if not isinstance(repository, Repository):
            raise TypeError(f'Unexptected: {repository.__class__.__name__} when a Repository was expected')
        repo_key = to_snake_case(repository.__class__.__name__)
        if repo_key in RepositoriesDict.__annotations__:
            self._repositories[repo_key] = repository
        else:
            raise ValueError(f"Repository '{repo_key}' is not defined in RepositoriesDict")


    @property
    def uptime(self) -> timedelta:
        return timedelta(seconds=time.time() - self.start_time)
    
    @property
    def repositories(self) -> RepositoriesDict:
        return self._repositories
