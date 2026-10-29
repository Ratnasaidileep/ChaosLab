"""ChaosLab Backend Configuration."""
import os


class Settings:
    CHAOSLAB_PORT: int = int(os.getenv("CHAOSLAB_PORT", "8000"))
    CHAOSLAB_HOST: str = os.getenv("CHAOSLAB_HOST", "0.0.0.0")
    CHAOSLAB_ENV: str = os.getenv("CHAOSLAB_ENV", "development")
    DB_PATH: str = os.getenv("CHAOSLAB_DB_PATH", "chaoslab.db")

    PRODUCT_SERVICE_URL: str = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001").rstrip("/")
    ORDER_SERVICE_URL: str = os.getenv("ORDER_SERVICE_URL", "http://localhost:8002").rstrip("/")

    HEALTH_CHECK_INTERVAL_SECONDS: float = float(os.getenv("HEALTH_CHECK_INTERVAL_SECONDS", "1.5"))
    RECOVERY_TIMEOUT_SECONDS: float = float(os.getenv("RECOVERY_TIMEOUT_SECONDS", "30.0"))
    DETECTION_TIMEOUT_SECONDS: float = float(os.getenv("DETECTION_TIMEOUT_SECONDS", "25.0"))

    MAX_EXPERIMENT_DURATION_SECONDS: int = int(os.getenv("MAX_EXPERIMENT_DURATION_SECONDS", "60"))
    MAX_CPU_LOAD_PERCENT: int = int(os.getenv("MAX_CPU_LOAD_PERCENT", "80"))
    MAX_MEMORY_MB: int = int(os.getenv("MAX_MEMORY_MB", "350"))
    ALLOWED_TARGET_SERVICES: list = ["product-service", "order-service"]

    DOCKER_HOST_SOCKET: str = os.getenv("DOCKER_HOST_SOCKET", "/var/run/docker.sock")
    ENABLE_DOCKER_CHAOS: bool = os.getenv("ENABLE_DOCKER_CHAOS", "true").lower() in ("true", "1", "yes")


settings = Settings()
