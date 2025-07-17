import logging
import os
import signal
import sys
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

_logger = logging.getLogger('utils')

class DirectoryWatcher(FileSystemEventHandler):
    _instances = {}
    _shutdown_hooked = False
    _instances_lock = threading.Lock()

    def __new__(cls, directory: str, recursive: bool = False):
        abs_directory = os.path.abspath(directory)
        _logger.debug(f'Request for Directory Watcher on: {directory}')

        with cls._instances_lock:
            if abs_directory not in cls._instances:
                _logger.debug(f'No instance found for: {abs_directory}, making a new instance')
                instance = super().__new__(cls)
                
                instance.watch_dir = abs_directory
                instance._watchers = {}
                instance._lock = threading.Lock()
                instance.observer = Observer()
                instance.observer.daemon = True
                instance.observer.schedule(instance, path=abs_directory, recursive=recursive)
                instance.observer.start()

                if not cls._shutdown_hooked:
                    _logger.debug(f'signal hooks not yet in place, setting SIGTERM & SIGINT signal hooks for safe thread handling on stop')
                    signal.signal(signal.SIGTERM, cls._handle_shutdown)
                    signal.signal(signal.SIGINT, cls._handle_shutdown)
                    cls._shutdown_hooked = True
                
                cls._instances[abs_directory] = instance
        for thread in threading.enumerate():
            _logger.debug(f'Thread: {thread.name} isDaemon: {thread.isDaemon()}')
        return cls._instances[abs_directory]

    def on_modified(self, event):
        if event.is_directory:
            return
        _logger.debug(f'modification event, source: {event.src_path}')
        abs_path = os.path.abspath(event.src_path)

        with self._lock:
            file_watcher = self._watchers.get(abs_path)
        if file_watcher:
            file_watcher.reload()

    @classmethod
    def register_watcher(cls, file_watcher):
        directory = os.path.dirname(file_watcher.file_path)
        abs_file_path = os.path.abspath(file_watcher.file_path)

        watcher_instance = cls(directory)
        with watcher_instance._lock:
            watcher_instance._watchers[abs_file_path] = file_watcher

    @classmethod
    def _handle_shutdown(cls, signal, frame):
        _logger.debug(f'Shutdown triggered by signal: {signal}')
        cls.stop()
        sys.exit(0)

    @classmethod
    def stop(cls):
        _logger.info(f'Grafefully stopping observer threads...')
        for instance in cls._instances.values():
            _logger.debug(f'Stopping instance for: {instance.watch_dir}')
            instance.observer.stop()
            instance.observer.join()