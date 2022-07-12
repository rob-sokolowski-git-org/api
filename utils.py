import logging

from env_config import CONFIG


def read_magic_word() -> str:
    with open(CONFIG.dev_magic_word) as f:
        return f.read().strip()


def check_magic_word(s: str) -> bool:
    """lazy secrets manager alternative. it should be easy to drop-in the real thing when needed
       while avoid committing secret text blobs to git"""
    try:
        magic_word = read_magic_word()
    except Exception as ex:
        logging.exception("Expecting magic word file, didn't find it")
        return False
    return s == magic_word
