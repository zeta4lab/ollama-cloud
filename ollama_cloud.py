# Copyright 2026 제타포랩(zeta4lab)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
import random
import socket
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Iterator

BASE_URL = "https://ollama.com"
DEFAULT_MODEL = "gemma4:31b"

# 재시도해도 의미가 있는 상태 코드. 403(구독 필요)은 영구 실패이므로 제외한다.
RETRYABLE_STATUS = frozenset({408, 429, 500, 502, 503, 504})


class OllamaCloudError(RuntimeError):
    """일반 오류."""


class SubscriptionRequiredError(OllamaCloudError):
    """유료 구독이 필요한 모델을 호출했을 때. 재시도해도 해결되지 않는다."""


class RateLimitError(OllamaCloudError):
    """재시도를 모두 소진하고도 한도에 걸린 경우."""


class OllamaCloud:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        base_url: str = BASE_URL,
        timeout: float = 120.0,
        max_retries: int = 5,
        backoff_base: float = 1.0,
        backoff_cap: float = 60.0,
        verbose: bool = False,
    ) -> None:
        self.api_key = api_key or os.environ.get("OLLAMA_API_KEY", "")
        if not self.api_key:
            raise OllamaCloudError(
                "OLLAMA_API_KEY가 없습니다. ~/.secrets/OLLAMA_API_KEY 를 확인하세요."
            )
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_cap = backoff_cap
        self.verbose = verbose

    # -------------------------------------------------------------- 재시도

    def _sleep_for(self, attempt: int, retry_after: str | None) -> float:
        """Retry-After 헤더를 우선 존중하고, 없으면 지수 백오프 + 지터."""
        if retry_after:
            try:
                return min(float(retry_after), self.backoff_cap)
            except ValueError:
                pass  # HTTP-date 형식은 무시하고 백오프로 넘어간다
        delay = min(self.backoff_base * (2**attempt), self.backoff_cap)
        return delay * (0.5 + random.random() / 2)  # 지터로 동시 재시도 분산

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"[ollama_cloud] {msg}", file=sys.stderr)

    # ------------------------------------------------------------------ 내부

    def _request(self, path: str, payload: dict[str, Any] | None, method: str = "POST"):
        """요청을 보내고 응답 객체를 돌려준다. 429/5xx/네트워크 오류는 재시도한다.

        403(구독 필요)은 재시도해도 영구히 실패하므로 즉시 예외를 던진다.
        """
        body = json.dumps(payload).encode() if payload is not None else None
        url = f"{self.base_url}{path}"
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            req = urllib.request.Request(
                url,
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
                detail = e.read().decode(errors="replace")[:300]

                if e.code == 403 and "subscription" in detail:
                    raise SubscriptionRequiredError(
                        f"'{(payload or {}).get('model', '?')}' 는 유료 구독이 필요합니다. "
                        f"무료 모델 목록은 README 참고. (HTTP 403)"
                    ) from e

                if e.code not in RETRYABLE_STATUS or attempt == self.max_retries:
                    err = RateLimitError if e.code == 429 else OllamaCloudError
                    raise err(f"HTTP {e.code}: {detail}") from e

                wait = self._sleep_for(attempt, e.headers.get("Retry-After"))
                self._log(
                    f"HTTP {e.code} — {wait:.1f}초 후 재시도 "
                    f"({attempt + 1}/{self.max_retries})"
                )
                last_error = e
                time.sleep(wait)

            except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
                if attempt == self.max_retries:
                    raise OllamaCloudError(f"네트워크 오류: {e}") from e
                wait = self._sleep_for(attempt, None)
                self._log(
                    f"네트워크 오류 ({e}) — {wait:.1f}초 후 재시도 "
                    f"({attempt + 1}/{self.max_retries})"
                )
                last_error = e
                time.sleep(wait)

        raise OllamaCloudError(f"재시도 소진: {last_error}")  # 도달하지 않음

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
