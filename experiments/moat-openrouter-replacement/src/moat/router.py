import time
import requests
from typing import Dict, List, Any, Optional

class LLMProvider:
    def __init__(self, name: str, api_base: str, api_key: str = "", model_map: Optional[Dict[str, str]] = None):
        self.name = name
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.model_map = model_map or {}
        self.is_healthy = True
        self.latency_ms = 0.0

    def chat_completion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.api_base}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Remap model if necessary
        req_payload = payload.copy()
        requested_model = req_payload.get("model", "")
        if requested_model in self.model_map:
            req_payload["model"] = self.model_map[requested_model]

        start_time = time.time()
        try:
            resp = requests.post(url, json=req_payload, headers=headers, timeout=10)
            self.latency_ms = (time.time() - start_time) * 1000
            if resp.status_code == 200:
                self.is_healthy = True
                return resp.json()
            else:
                self.is_healthy = False
                raise RuntimeError(f"Provider {self.name} error status {resp.status_code}: {resp.text}")
        except Exception as e:
            self.latency_ms = (time.time() - start_time) * 1000
            self.is_healthy = False
            raise RuntimeError(f"Provider {self.name} connection failed: {str(e)}")


class MoatRouter:
    def __init__(self, strategy: str = "fallback"):
        self.providers: List[LLMProvider] = []
        self.strategy = strategy
        self._rr_index = 0

    def add_provider(self, provider: LLMProvider):
        self.providers.append(provider)

    def route_chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.providers:
            raise ValueError("No LLM providers configured in Moat router.")

        if self.strategy == "fallback":
            errors = []
            for provider in self.providers:
                try:
                    return provider.chat_completion(payload)
                except Exception as e:
                    errors.append(str(e))
                    continue
            raise RuntimeError(f"All providers failed in fallback mode: {errors}")

        elif self.strategy == "round-robin":
            num_providers = len(self.providers)
            for _ in range(num_providers):
                provider = self.providers[self._rr_index]
                self._rr_index = (self._rr_index + 1) % num_providers
                try:
                    return provider.chat_completion(payload)
                except Exception:
                    continue
            raise RuntimeError("All providers failed in round-robin mode.")

        else:
            raise ValueError(f"Unknown routing strategy: {self.strategy}")
