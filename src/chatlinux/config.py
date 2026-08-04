"Typed environment configuration for ChatLinux."

from chatenv import BaseEnvConfig, EnvField


class ChatlinuxConfig(BaseEnvConfig):
    "ChatLinux ChatEnv configuration."

    _title = "ChatLinux Configuration"
    _aliases = ["chatlinux"]
    _storage_dir = "Chatlinux"

    @classmethod
    def test(cls) -> None:
        """Validate schema registration without external side effects."""

        print(f"Testing {cls._title}...")
        print("Schema loaded; no network test is required.")

    CHATLINUX_API_KEY = EnvField(
        "CHATLINUX_API_KEY",
        desc="API key",
        is_sensitive=True,
    )


__all__ = ["ChatlinuxConfig"]
