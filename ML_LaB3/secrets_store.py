import os
import time
from functools import lru_cache

import hvac


class VaultSecretError(RuntimeError):
    """Ошибка получения секретов из Vault."""



def _required_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise VaultSecretError(f"Не задана переменная окружения {name}")
    return value


@lru_cache(maxsize=1)
def get_db_credentials() -> dict[str, str]:
    """Загружает креды БД из Hashicorp Vault (KV v2)."""
    vault_addr = _required_env("VAULT_ADDR", "http://vault:8200")
    vault_token = _required_env("VAULT_TOKEN", "root-token")
    secret_path = _required_env("VAULT_SECRET_PATH", "ml-lab3/db")
    kv_mount = _required_env("VAULT_KV_MOUNT", "secret")

    client = hvac.Client(url=vault_addr, token=vault_token)

    last_error: Exception | None = None
    for _ in range(20):
        try:
            response = client.secrets.kv.v2.read_secret_version(
                mount_point=kv_mount,
                path=secret_path,
            )
            data = response["data"]["data"]

            return {
                "DB_USER": data["DB_USER"],
                "DB_PASSWORD": data["DB_PASSWORD"],
                "DB_NAME": data["DB_NAME"],
            }
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1)

    raise VaultSecretError(
        "Не удалось получить секреты БД из Vault"
    ) from last_error
