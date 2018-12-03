"""Functions to set-up logging."""
import logging
import os


class MyFormatter(logging.Formatter):
    """
    Big thanks to JS. <https://stackoverflow.com/users/310399/js> for his
    outstanding example on StackOverflow.
    """
    dbg_fmt = ('{asctime} {name}[{process}] {levelname}'
               '[{filename}:l.{lineno}]: {message}')

    def __init__(self):
        normal_fmt = '{asctime} {name}[{process:d}] {levelname}: {message}'
        logging.Formatter.__init__(self, fmt=normal_fmt,
                                   datefmt='%Y-%m-%d %H:%M:%S', style='{')

    def format(self, record):
        """Custom format method, look at logging.Formatter.format for details

        We overwrite this in order to display a custom debug format.
        """
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        # pylint: disable=protected-access
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = MyFormatter.dbg_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        if record.levelno == logging.DEBUG:
            self._style._fmt = format_orig

        return result


def setup_logging(logfile=None, lvl_bash=logging.INFO,
                  lvl_logfile=logging.WARNING, symlink=None):
    """Initiate logging to terminal and to a logfile.

    Arguments:
        logfile (str): full path to the log file
        level_bash (int): logging level for terminal output;
                          None for not displaying at bash.
                          Default: logging.INFO
        level_logfile (int): logging level for terminal output
                             Default: logging.WARNING
        symlink (str): directory where to create symlinks to the current logs
                       default: None

    Returns:
        root (logging.RootLogger): logging object
    """
    root = logging.getLogger()

    map(root.removeHandler, root.handlers[:])
    map(root.removeFilter, root.filters[:])
    root.handlers = []
    root.filters = []
    root.setLevel(0)

    # Initialise shell output, potentially with colors.
    if lvl_bash is not None:
        _ch = logging.StreamHandler()
        _ch.setLevel(lvl_bash)
        _ch.setFormatter(MyFormatter())
        root.addHandler(_ch)

    # Add handlers for file output.
    # Always saving a visible log file (custom level) and a hidden one
    # (DEBUG level).
    if logfile is not None and lvl_logfile is not None:

        # Create log directory if it does not exist
        _logdir = os.path.dirname(logfile)
        if not os.path.exists(_logdir):
            logging.warning('Creating new directory %s', _logdir)
            os.makedirs(_logdir)

        # Log file handler
        file_handler = logging.FileHandler(logfile)
        file_handler.setLevel(lvl_logfile)
        file_handler.setFormatter(MyFormatter())
        root.addHandler(file_handler)

        # Adding also a hidden log file with all debug informations
        _path, _file = os.path.split(logfile)
        _name, _ext = os.path.splitext(_file)
        debug_file = os.path.join(_path, '.' + _name + '_DEBUG' + _ext)
        file_handler = logging.FileHandler(debug_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(MyFormatter())
        root.addHandler(file_handler)

        if symlink is not None:
            sym1 = os.path.join(symlink, '.recent_DEBUG.log')
            if os.path.exists(sym1):
                os.remove(sym1)
            os.symlink(os.path.abspath(debug_file), sym1)
            sym2 = os.path.join(symlink, 'recent.log')
            if os.path.exists(sym2):
                os.remove(sym2)
            os.symlink(os.path.abspath(logfile), sym2)
            logging.debug("updated symlinks at '%s' and '%s'", sym1, sym2)

        if lvl_bash is not None:
            logging.info('Log enabled. Log file is located at %s',
                         os.path.abspath(logfile))

    return root
