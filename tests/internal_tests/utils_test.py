import utils


def test_magic_word_verification():
    assert utils.check_magic_word(s="this is not the magic word") is False

    # read secret from file, verify it's the correct one
    # this avoids commit the secret to git, while not having to deal with secrets manager for now
    assert utils.check_magic_word(s=utils.read_magic_word()) is True
