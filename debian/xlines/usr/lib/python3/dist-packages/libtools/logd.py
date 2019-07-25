"""
Summary:
    Project-level logging module

"""
import os
import sys
import inspect
import logging
import logging.handlers
from pathlib import Path
from libtools.statics import local_config

syslog = logging.getLogger()
syslog.setLevel(logging.DEBUG)

valid_modes = ('STEAM', 'FILE', 'SYSLOG')


def mode_assignment(mode):
    """
    Translates arg to enforce proper assignment
    """
    mode = mode.upper()
    return {
        'STREAM': 'STREAM',
        'CONSOLE': 'STREAM',
        'STDOUT': 'STREAM',
        'FILE': 'FILE',
        'FILEOBJECT': 'FILE',
        'FILESYSTEM': 'FILE',
        'SYSLOG': 'SYSLOG',
        'MESSAGES': 'SYSLOG',
        'SYSTEM': 'SYSLOG'
    }.get(mode, 'STREAM')


def logprep(mode):
    """
    Summary:
        prerequisites for logging to file mode

    Args:
        :mode (str): valid value is 'FILE'; parameter
            used for logging type validation only
    Return:
        Success | Failure, TYPE: bool

    """
    try:
        if not mode.startswith('FILE'):
            return False

        log_path = local_config['LOGGING']['LOG_PATH']
        path, log_dirname = os.path.split(log_path)

        if not os.path.exists(path):
            os.makedirs(path)

        if not os.path.exists(log_path):
            Path(log_path).touch(mode=0o644, exist_ok=True)

    except OSError as e:
        syslog.exception(f'{inspect.stack()[0][3]}: Failure while seeding log file path: {e}')
        syslog.warning(f'{inspect.stack()[0][3]}: Log preparation fail - exit')
        sys.exit(1)
    return True


def _format_map(format):
    return {
        'FILE': '%(asctime)s - %(pathname)s - %(name)s - [%(levelname)s]: %(message)s',
        'STREAM': '%(pathname)s - %(name)s - [%(levelname)s]: %(message)s',
        'SYSLOG': '- %(pathname)s - %(name)s - [%(levelname)s]: %(message)s'
    }.get(mode_assignment(format), 'STREAM')


def getLogger(*args, **kwargs):
    """
    Summary:
        custom format logger

    Args:
        mode (str):  The Logger module supprts the following log modes:

            - log to console / stdout. Log_mode = 'stream'
            - log to file
            - log to system logger (syslog)

    Returns:
        logging object | TYPE: logging singleton
    """
    def _logconfig_file(logger_object):

        if logprep(mode_assignment(log_mode)):
            # file handler
            f_handler = logging.FileHandler(local_config['LOGGING']['LOG_PATH'])
            f_formatter = logging.Formatter(_format_map('file'), asctime_format)
            f_handler.setFormatter(f_formatter)
            logger.addHandler(f_handler)
            logger.setLevel(logging.DEBUG)
            return logger

    def _logconfig_stdout(logger_object):
        # stream handlers
        s_handler = logging.StreamHandler()
        s_formatter = logging.Formatter(_format_map('stdout'))
        s_handler.setFormatter(s_formatter)
        logger.addHandler(s_handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def _logconfig_syslog(logger_object):
        syslog_facility = 'local7' if local_config['LOGGING']['SYSLOG_FILE'] else 'user'
        sys_handler = logging.handlers.SysLogHandler(address='/dev/log', facility=syslog_facility)
        sys_formatter = logging.Formatter(_format_map('syslog'))
        sys_handler.setFormatter(sys_formatter)
        logger.addHandler(sys_handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def _logmode_map(mode, _lobject):
        return {
                "FILE": _logconfig_file,
                "STREAM": _logconfig_stdout,
                "SYSLOG": _logconfig_syslog,
            }.get(mode, lambda x: _logconfig_stdout)(_lobject)

    # query local configuration for logging methodology
    log_mode = local_config['LOGGING']['LOG_MODE']

    # timestamp; all modes
    asctime_format = "%Y-%m-%d %H:%M:%S"

    try:

        logger = logging.getLogger(*args, **kwargs)
        logger.propagate = False

        if mode_assignment(log_mode) not in valid_modes:
            ex = Exception(
                    '%s: Unsupported mode indicated by log_mode value: %s' %
                    (inspect.stack()[0][3], str(log_mode))
                )
            raise ex

        if not logger.handlers:
            # branch on output format, default to stream
            return _logmode_map(mode_assignment(log_mode), logger)

    except OSError as e:
        syslog.warning(
            '%s: [WARN]: Unknown error configuring logging objects for log mode (%s)' %
            (inspect.stack()[0][3], str(log_mode))
        )
        raise e
