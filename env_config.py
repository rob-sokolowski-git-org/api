import os

from dataclasses import dataclass


class EnvironmentConfigurationError(Exception):
    pass


def _get_or_fail(variable_name: str) -> str:
    val = os.environ.get(variable_name)
    if val is None:
        # I'm debating an exit(-1) here, but that might be too harsh
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
    bucket_name: str = _get_or_fail("BUCKET_NAME")
    google_application_credentials: str = _get_or_fail("GOOGLE_APPLICATION_CREDENTIALS")


CONFIG = EnvironmentConfig()
