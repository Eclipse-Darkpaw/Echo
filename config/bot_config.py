import logging
import os
import sys

_logger = logging.getLogger('utils')

class BotConfig:
    def __init__(self, botname: str):
        self.botname = botname
        self._arg_test_bot = '--test-bot'
        self._arg_no_notif = '--no-notif'
        self._default_prefix = '>'

        self._is_test_bot_set = self._arg_test_bot in sys.argv
        self._is_no_notif_set = self._arg_no_notif in sys.argv

        self._guardians = self._retrieve_guardians()
        self._token = self._retrieve_token()
        self._prefix = self._retrieve_prefix()
        self._start_notif = not self._is_no_notif_set

        self._log_config()

    def _log_config(self):
        _logger.info(f'Guardians: {self._guardians}')
        if self._is_no_notif_set:
            _logger.info(f"{self._arg_no_notif} is set: guardians won't be DM'd about startup")
        _logger.debug(f"{self._arg_test_bot} is set")

    def _retrieve_guardians(self) -> list:
        env = os.getenv('GUARDIANS', '')
        return env.split(',') if env else []

    def _retrieve_token(self) -> str:
        test_prefix = 'TEST_' if self._is_test_bot_set else ''
        env_var = f"{self.botname.upper()}_{test_prefix}TOKEN"
        return os.getenv(env_var, '')

    def _retrieve_prefix(self) -> str:
        test_prefix = 'TEST_' if self._is_test_bot_set else ''
        env_var = f"{self.botname.upper()}_{test_prefix}PREFIX"
        return os.getenv(env_var, self._default_prefix)

    @property
    def token(self) -> str:
        return self._token

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def start_notif(self) -> bool:
        return self._start_notif

    @property
    def guardians(self) -> list:
        return self._guardians
