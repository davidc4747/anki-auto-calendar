import os


def get_credential_file_path() -> str:
    return os.path.join(os.path.dirname(__file__), "credentials.json")


def get_token_file_path() -> str:
    return os.path.join(os.path.dirname(__file__), "token.json")
