from tools.logger import logger
import hvac, os

VAULT_HOST = os.getenv('VAULT_ADDR', 'default')

def read_vault_token():
    try:
        with open('/mnt/vault-token/token', 'r') as file:
            token = file.read().strip()
        return token
    except Exception as e:
        logger.info(f"Error reading file at: /mnt/vault-token/token: {e}")
        return None

def get_vault_secret(secret_name: str):
    logger.info(f"Vault Host: {VAULT_HOST}" )
    client = hvac.Client(url=VAULT_HOST)
    client.token = read_vault_token()

    secret = client.secrets.kv.v2.read_secret(path=secret_name)    
    return secret
