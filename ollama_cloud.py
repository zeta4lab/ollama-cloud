"""Ollama Cloud 클라이언트 — 표준 라이브러리만 사용.

인증은 OLLAMA_API_KEY 환경변수(= ~/.secrets/OLLAMA_API_KEY)를 씁니다.
로컬 데몬은 비활성화된 상태이므로 모든 요청이 https://ollama.com 으로 나갑니다.

사용 예:
    from ollama_cloud import OllamaCloud

    oc = OllamaCloud()
    print(oc.chat("한국의 수도는?"))

    for piece in oc.chat("긴 설명 부탁", stream=True):
        print(piece, end="", flush=True)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Iterator

BASE_URL = "https://ollama.com"
DEFAULT_MODEL = "gemma4:31b"


class OllamaCloudError(RuntimeError):
    pass


class OllamaCloud:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        base_url: str = BASE_URL,
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("OLLAMA_API_KEY", "")
        if not self.api_key:
            raise OllamaCloudError(
                "OLLAMA_API_KEY가 없습니다. ~/.secrets/OLLAMA_API_KEY 를 확인하세요."
            )
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------ 내부

    def _request(self, path: str, payload: dict[str, Any] | None, method: str = "POST"):
        body = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            return urllib.request.urlopen(req, timeout=self.timeout)
        except urllib.error.HTTPError as e:
            raise OllamaCloudError(f"HTTP {e.code}: {e.read().decode()[:300]}") from e

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._request(path, payload) as resp:
            data = json.loads(resp.read())
        if isinstance(data, dict) and data.get("error"):
            raise OllamaCloudError(str(data["error"]))
        return data

    def _post_stream(self, path: str, payload: dict[str, Any]) -> Iterator[dict]:
        """/api/* 의 줄 단위 JSON 스트림을 파싱한다."""
        with self._request(path, payload) as resp:
            for raw in resp:
                line = raw.decode().strip()
                if line:
                    yield json.loads(line)

    # ------------------------------------------------------------------ 공개 API

    def chat(
        self,
        prompt: str | None = None,
        *,
        messages: list[dict] | None = None,
        system: str | None = None,
        model: str | None = None,
        stream: bool = False,
        tools: list[dict] | None = None,
        raw: bool = False,
        **options: Any,
    ):
        """/api/chat 호출. options 는 temperature, num_predict, seed 등."""
        if messages is None:
            if prompt is None:
                raise OllamaCloudError("prompt 또는 messages 중 하나는 필요합니다.")
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools
        if options:
            payload["options"] = options

        if stream:
            return self._stream_chat(payload)

        data = self._post_json("/api/chat", payload)
        return data if raw else data["message"]["content"]

    def _stream_chat(self, payload: dict[str, Any]) -> Iterator[str]:
        for chunk in self._post_stream("/api/chat", payload):
            piece = chunk.get("message", {}).get("content", "")
            if piece:
                yield piece
            if chunk.get("done"):
                break

    def generate(self, prompt: str, *, model: str | None = None, **options: Any) -> str:
        """/api/generate — 대화 맥락 없는 단발 완성."""
        payload: dict[str, Any] = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": False,
        }
        if options:
            payload["options"] = options
        return self._post_json("/api/generate", payload)["response"]

    def respond(
        self,
        text: str | list[dict],
        *,
        instructions: str | None = None,
        model: str | None = None,
        tools: list[dict] | None = None,
        raw: bool = False,
        **kwargs: Any,
    ):
        """/v1/responses — OpenAI Responses API 호환.

        주의: 서버가 store:false 로 고정하므로 previous_response_id 체이닝은
        동작하지 않습니다. 대화 이력은 input 배열로 직접 넘기세요.
        """
        payload: dict[str, Any] = {"model": model or self.model, "input": text}
        if instructions:
            payload["instructions"] = instructions
        if tools:
            payload["tools"] = tools
        payload.update(kwargs)

        data = self._post_json("/v1/responses", payload)
        if raw:
            return data
        return self.output_text(data)

    @staticmethod
    def output_text(response: dict[str, Any]) -> str:
        """Responses 응답에서 텍스트만 뽑는다 (function_call 항목은 건너뜀)."""
        parts = []
        for item in response.get("output", []):
            for block in item.get("content", []) or []:
                if block.get("type") == "output_text":
                    parts.append(block.get("text", ""))
        return "".join(parts)

    @staticmethod
    def tool_calls(response: dict[str, Any]) -> list[dict]:
        """Responses 응답에서 function_call 항목만 뽑아 arguments 를 파싱한다."""
        calls = []
        for item in response.get("output", []):
            if item.get("type") == "function_call":
                calls.append(
                    {
                        "call_id": item["call_id"],
                        "name": item["name"],
                        "arguments": json.loads(item.get("arguments") or "{}"),
                    }
                )
        return calls

    def models(self) -> list[str]:
        with self._request("/api/tags", None, method="GET") as resp:
            data = json.loads(resp.read())
        return sorted(m["name"] for m in data.get("models", []))

    def show(self, model: str | None = None) -> dict[str, Any]:
        return self._post_json("/api/show", {"model": model or self.model})


if __name__ == "__main__":
    import sys

    oc = OllamaCloud()
    if len(sys.argv) > 1:
        for piece in oc.chat(" ".join(sys.argv[1:]), stream=True):
            print(piece, end="", flush=True)
        print()
    else:
        print("사용 가능한 모델:")
        for name in oc.models():
            print(" ", name)
