"""Safe Docker Client wrapper for controlled container failure injection.

Ensures strict allowlisting so only designated project containers can be targeted.
Falls back safely to HTTP-based chaos simulation if Docker socket is not present.
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("chaoslab.docker")

# Strict Allowlist of safe containers that ChaosLab can touch
ALLOWED_CONTAINER_NAMES = {
    "product-service": ["product-service", "chaoslab-product-service", "chaoslab-product-service-1"],
    "order-service": ["order-service", "chaoslab-order-service", "chaoslab-order-service-1"]
}


class SafeDockerController:
    def __init__(self, socket_path: str = "/var/run/docker.sock"):
        self.socket_path = socket_path
        self._docker_available = None

    def is_docker_available(self) -> bool:
        """Check if Docker daemon is accessible."""
        if self._docker_available is not None:
            return self._docker_available

        # Check socket existence or try connecting
        if os.path.exists(self.socket_path):
            try:
                import docker
                client = docker.DockerClient(base_url=f"unix://{self.socket_path}")
                client.ping()
                self._docker_available = True
                return True
            except Exception as e:
                logger.debug(f"Docker socket exists but ping failed: {e}")

        # Check Windows / environment named pipe or env
        try:
            import docker
            client = docker.from_env()
            client.ping()
            self._docker_available = True
            return True
        except Exception:
            self._docker_available = False
            return False

    def _get_client(self):
        import docker
        if os.path.exists(self.socket_path):
            return docker.DockerClient(base_url=f"unix://{self.socket_path}")
        return docker.from_env()

    def _resolve_container(self, target_service: str):
        """Find container matching target service within allowlist."""
        allowed_names = ALLOWED_CONTAINER_NAMES.get(target_service)
        if not allowed_names:
            raise ValueError(f"Target service '{target_service}' is not in Docker allowlist")

        client = self._get_client()
        containers = client.containers.list(all=True)
        for c in containers:
            c_name = c.name.lstrip("/")
            for pattern in allowed_names:
                if pattern in c_name:
                    return c
        raise LookupError(f"No running or stopped container found matching '{target_service}'")

    def stop_container(self, target_service: str, timeout: int = 2) -> Dict[str, Any]:
        """Stop target test container."""
        if not self.is_docker_available():
            return {"mode": "fallback", "message": "Docker not available, using HTTP hook fallback"}

        container = self._resolve_container(target_service)
        logger.info(f"Stopping test container {container.name} (id: {container.short_id})")
        container.stop(timeout=timeout)
        return {
            "mode": "docker",
            "action": "stop",
            "container_id": container.short_id,
            "container_name": container.name,
            "status": "stopped"
        }

    def start_container(self, target_service: str) -> Dict[str, Any]:
        """Start previously stopped test container."""
        if not self.is_docker_available():
            return {"mode": "fallback", "message": "Docker not available, using HTTP hook fallback"}

        container = self._resolve_container(target_service)
        logger.info(f"Starting test container {container.name} (id: {container.short_id})")
        container.start()
        return {
            "mode": "docker",
            "action": "start",
            "container_id": container.short_id,
            "container_name": container.name,
            "status": "started"
        }

    def restart_container(self, target_service: str, timeout: int = 2) -> Dict[str, Any]:
        """Restart test container."""
        if not self.is_docker_available():
            return {"mode": "fallback", "message": "Docker not available, using HTTP hook fallback"}

        container = self._resolve_container(target_service)
        logger.info(f"Restarting test container {container.name} (id: {container.short_id})")
        container.restart(timeout=timeout)
        return {
            "mode": "docker",
            "action": "restart",
            "container_id": container.short_id,
            "container_name": container.name,
            "status": "restarted"
        }


docker_controller = SafeDockerController()
