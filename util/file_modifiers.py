import json
import logging
from filelock import FileLock, Timeout
from typing import Callable

_logger = logging.getLogger('utils')

def modify_json_file(file_path: str, modifier: Callable[[dict], None]):
    """
    Modifies the provided json file, calling the modifier_fn callback to perform the preferred changes.
    This function utelises file locking to prevent race conditions, this is BLOCKING (up to 5s)!
    If it fails to acquire a lock after 5s, it will timeout.

    CAUTION:
    https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-callback
    According to the discord dev documentation, a bot has 3s to respond to an interaction,
    after that the interaction token is valid for up to 15 minutes.
    Hence why it is advised to respond to the interaction before calling this definition!!

    Last docstring edit: ~FoxyHunter v4.3.0
    Last method edit: ~FoxyHunter v4.3.0

    :param file_path: Path of the file to be modified
    :param modifier: Callback function expected to modify the data, this funtcion gets the data dict
    :throws RuntimeError:
    :throws TimeoutError:
    """
    lock = FileLock(f'{file_path}.lock')

    try:   
        with lock.acquire(timeout=5):
            _logger.debug(f'Lock acquired for: {file_path}')

            try:
                with open(file_path, 'r+', encoding="utf-8") as file:
                    _logger.debug(f'{file_path} opened for reading & writing')

                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = {}
                        _logger.error(f'Failed to decode JSON for: {file_path}, loading as empty dict instead')

                    file.seek(0)
                    file.truncate()

                    modifier(data)

                    json.dump(data, file, indent=4)
                    file.flush()
            except:
                _logger.exception(f'Unexpected error while modifying: {file_path}')
                raise RuntimeError(f'Unexpected error while modifying: {file_path}')
            finally:
                _logger.debug(f'Lock released, for: {file_path}')

    except Timeout:
        _logger.error(f'Failed to acquire lock on {file_path}: file is currently locked by another process.')
        raise TimeoutError(f'Failed to acquire lock on {file_path}: file is currently locked by another process')