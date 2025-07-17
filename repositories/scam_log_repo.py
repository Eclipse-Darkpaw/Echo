from .repository import LogRepository
from config import Paths

class ScamLogRepo(LogRepository):
    def log(self, content: str):
        super()._log(log_file_path=Paths.scam_log, content=f'{content}\n')