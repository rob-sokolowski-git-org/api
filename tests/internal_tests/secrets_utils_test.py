from api.secrets_utils import SECRETS
from env_config import CONFIG


def test_fetch_secret():
    secret = SECRETS.fetch_secret(key=CONFIG.test_secret_secrets_key)

    # NB: assumes there is a configured secret in the pointed-to secrets key from env config
    assert secret == "TEST_VALUE"
