from google.cloud.secretmanager_v1 import AccessSecretVersionResponse

from env_config import CONFIG, EnvironmentConfig
from google.cloud.secretmanager import SecretManagerServiceClient


class SecretsUtils:
    def __init__(self,
                 env_config: EnvironmentConfig = CONFIG
                 ):
        self._env_config = env_config
        self._client = SecretManagerServiceClient()

    @property
    def secrets_client(self) -> SecretManagerServiceClient:
        return self._client

    def fetch_secret(self, key: str) -> str:
        response: AccessSecretVersionResponse =  self._client.access_secret_version(name=key)
        return response.payload.data.decode('UTF-8')

SECRETS = SecretsUtils()
