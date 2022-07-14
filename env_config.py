import os

from dataclasses import dataclass


class EnvironmentConfigurationError(Exception):
    pass


def _get_or_fail(variable_name: str) -> str:
    val = os.environ.get(variable_name)
    if val is None:
        raise EnvironmentConfigurationError(f"environment variable {variable_name} MUST be set to run application!")

    return val


@dataclass(frozen=True)
class EnvironmentConfig:
    """
    global environment configuration can be imported like so:

        from env_config import CONFIG

    design choices:
     * all env files should be committed to git, therefore secrets are not allowed, but pointers to secrets are
     * all env variables must be set, otherwise fail loudly
    """
    env_name: str = _get_or_fail("ENV_NAME")
    gcp_project_id: str = _get_or_fail("GCP_PROJECT_ID")
    bucket_name: str = _get_or_fail("BUCKET_NAME")
    temp_dir: str = _get_or_fail("TEMP_DIR")
    magic_word_secrets_key: str = _get_or_fail("MAGIC_WORD_SECRETS_KEY")
    google_application_credentials: str = _get_or_fail("GOOGLE_APPLICATION_CREDENTIALS")
    test_secret_secrets_key: str = _get_or_fail("TEST_SECRET_SECRETS_KEY")
    api_tests_target_host: str = _get_or_fail("HTTP_TEST_TARGET_HOST")


CONFIG = EnvironmentConfig()
