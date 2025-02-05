import logging
import os
import sys

from util.logger import ANSI

_logger = logging.getLogger('utils')

class BotConfig:
    def __init__(self, botname: str):
        self.botname = botname
        self._arg_test_bot = '--test-bot'
        self._arg_no_notif = '--no-notif'
        self._default_prefix = '>'

        self._is_test_bot_set = self._arg_test_bot in sys.argv
        self._is_no_notif_set = self._arg_no_notif in sys.argv

        self._guardians = BotConfig.retrieve_guardians()
        self._token = self._retrieve_token()
        self._prefix = self._retrieve_prefix()
        self._start_notif = not self._is_no_notif_set

        self._log_config()

    @classmethod
    def retrieve_guardians(cls) -> list:
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
    
    def _log_config(self):
        border = "=" * 40
        sub_border = "-" * 40

        _logger.info(ANSI.set_on_text(border, ANSI.CODES['foreground']['black']))
        _logger.info(ANSI.set_on_text('Bot Configuration Details', ANSI.CODES['transform']['bold']))
        _logger.info(ANSI.set_on_text(border, ANSI.CODES['foreground']['black']))

        _logger.debug(f'  {'Token':<12}: {self._token}')
        _logger.info(f'  {'Guardians':<12}: {self._guardians}')
        _logger.info(f'  {'Prefix':<12}: {self._prefix}')
        _logger.info(f'  {'Mode':<12}: {ANSI.set_on_text(
            ('Test' if self._is_test_bot_set else 'Normal'),
            (ANSI.CODES['foreground']['yellow'] if self._is_test_bot_set else ANSI.CODES['foreground']['green'])
            )}')
        _logger.info(f'  {'Start Notif':<12}: {ANSI.set_on_text(
            str(self._start_notif),
            (ANSI.CODES['foreground']['green'] if self._start_notif else ANSI.CODES['foreground']['red'])
            )}')

        _logger.info(ANSI.set_on_text(sub_border, ANSI.CODES['foreground']['black']))

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
