# Ollama Cloud 사용 가이드

이 머신(CPU-only, GPU 없음)은 **클라우드 전용**으로 구성돼 있습니다.
아래 내용은 모두 실제 API를 호출해 검증한 결과입니다 (검증일: 2026-08-02).

---

## 1. 현재 구성

| 항목 | 값 |
|---|---|
| 로컬 systemd 데몬 | `inactive` + `disabled` — `localhost:11434` 응답 없음 |
| `OLLAMA_HOST` | `https://ollama.com` (`~/.zshrc`) |
| `OLLAMA_API_KEY` | `~/.secrets/OLLAMA_API_KEY` (권한 600, zshrc 루프가 자동 export) |
| ollama 버전 | 0.32.5 (linux-arm64) |

로컬 추론으로 되돌리려면:

```bash
sudo systemctl enable --now ollama
# 그리고 ~/.zshrc 의 OLLAMA_HOST 줄을 주석 처리
```

### `ollama` CLI를 쓰려면

CLI는 API 키가 아니라 `~/.ollama/id_ed25519` 키페어로 요청에 서명합니다.
따라서 브라우저 인증이 **한 번** 필요합니다:

```bash
ollama signin
```

CLI 없이 HTTP API만 쓸 거라면 불필요합니다.

---

## 2. 무료 티어에서 쓸 수 있는 모델

전체 18개 중 **7개**만 접근 가능합니다. 나머지는
`this model requires a subscription` 오류가 납니다.

| 모델 | 무료 |
|---|:--:|
| `gemma4:31b` | ✅ |
| `gpt-oss:120b` | ✅ |
| `gpt-oss:20b` | ✅ |
| `minimax-m3` | ✅ |
| `nemotron-3-nano:30b` | ✅ |
| `nemotron-3-super` | ✅ |
| `nemotron-3-ultra` | ✅ |
| `deepseek-v4-pro` / `-flash` / `-flash:0731` | ❌ 구독 |
| `glm-5.1` / `glm-5.2` | ❌ 구독 |
| `kimi-k3` / `k2.7-code` / `k2.6` | ❌ 구독 |
| `minimax-m2.7` | ❌ 구독 |
| `mistral-large-3:675b` | ❌ 구독 |
| `qwen3.5:397b` | ❌ 구독 |

### `gemma4:31b` 스펙 (`/api/show`)

```
capabilities   : completion, thinking, tools, vision
context_length : 262,144
parameter_size : 32.7B
quantization   : BF16
```

---

## 3. 엔드포인트 지원 현황

| 엔드포인트 | 상태 |
|---|---|
| `POST /api/chat` | ✅ 네이티브, 권장 |
| `POST /api/generate` | ✅ 단발 완성 |
| `POST /api/tags` `/api/show` | ✅ |
| `POST /v1/chat/completions` | ✅ OpenAI 호환 |
| `POST /v1/completions` | ✅ |
| `POST /v1/responses` | ✅ OpenAI Responses 호환 (제약 있음, §5) |
| `GET /v1/models` | ✅ (POST는 405) |
| `POST /v1/embeddings` | ❌ 404 미지원 |
| `GET /v1/responses/{id}` | ❌ 404 미지원 |

---

## 4. ⚠️ 서버 전반의 제약 — 엔드포인트 바꿔도 동일

교차 검증 결과, 아래 두 기능은 **어느 엔드포인트에서도 동작하지 않습니다.**
요청은 200으로 받아주지만 조용히 무시됩니다.

| 기능 | `/v1/responses` | `/v1/chat/completions` | `/api/chat` |
|---|:--:|:--:|:--:|
| 구조화 출력 (JSON Schema) | ❌ | ❌ | ❌ |
| `tool_choice` 특정 함수 강제 | ❌ | ❌ | — |

### 대응 방법

**구조화 출력이 필요하면** 스키마에 의존하지 말고 프롬프트로 지시한 뒤
파싱 실패에 대비하세요. 모델이 코드펜스(```json)를 씌우는 경우가 많으므로
벗겨내야 합니다 — `occ -j` 가 이 처리를 해줍니다.

**도구 호출은 자동 선택(`auto`)만 신뢰하세요.** 자동 판단은 정확히 동작합니다.

---

## 5. Responses API 제약

응답 본문에 **`"store": false`** 가 고정돼 있고 서버가 응답을 보관하지 않습니다.
따라서 Responses API의 대표 기능인 `previous_response_id` 체이닝이 무력합니다:

```
1차: "내 이름은 홍길동이야. 기억해."   → id: resp_296697
2차: previous_response_id=resp_296697 로 "내 이름이 뭐라고 했지?"
→ "죄송하지만, 아직 성함을 말씀해주신 적이 없어서..."
```

**멀티턴 대화는 클라이언트가 직접 이력을 관리해야 합니다.**
`/api/chat` 의 `messages` 배열이나 Responses 의 `input` 배열에 전체 맥락을 매번 실으세요.

### 동작하는 것

`input`, `instructions`, `stream`(SSE), `temperature`, `top_p`,
`max_output_tokens`, `tools`(자동 선택 + 결과 왕복)

---

## 6. 요청 파라미터

### `/api/chat` body

```json
{
  "model": "gemma4:31b",
  "messages": [
    {"role": "system", "content": "너는 간결한 조수야."},
    {"role": "user", "content": "안녕"}
  ],
  "stream": false,
  "think": false,
  "tools": [],
  "options": {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "num_predict": 512,
    "num_ctx": 8192,
    "seed": 42,
    "stop": ["\n\n"],
    "repeat_penalty": 1.1
  }
}
```

모델 추론 설정은 최상위가 아니라 **`options` 안**에 넣습니다.
`num_predict` 는 실측으로 동작 확인했습니다 (`eval_count` 일치, `done_reason: "length"`).

### 응답

```json
{
  "message": {"role": "assistant", "content": "...", "thinking": "..."},
  "done": true,
  "done_reason": "stop",
  "prompt_eval_count": 73,
  "eval_count": 73,
  "total_duration": 961635614
}
```

`done_reason` — `stop`(정상) / `length`(`num_predict` 도달)

> **참고:** 클라우드에는 `keep_alive` / `ollama ps` 같은 모델 로드 개념이 없습니다.
> 서버가 상시 서빙하므로 `num_gpu` 등 하드웨어 옵션도 무의미합니다.

---

## 7. 도구 호출 (검증됨)

### Responses 형식 — `tools` 가 **flat** 구조

```json
"tools": [{
  "type": "function",
  "name": "get_weather",
  "description": "특정 도시의 현재 날씨를 조회한다",
  "parameters": {
    "type": "object",
    "properties": {"city": {"type": "string"}},
    "required": ["city"]
  }
}]
```

1차 응답:

```json
"output": [{
  "type": "function_call",
  "call_id": "call_w4w7crhv",
  "name": "get_weather",
  "arguments": "{\"city\":\"서울\"}"
}]
```

2차 — 결과를 `call_id` 로 짝지어 되돌립니다:

```json
"input": [
  {"type": "message", "role": "user", "content": "서울 날씨 알려줘"},
  {"type": "function_call", "call_id": "call_w4w7crhv",
   "name": "get_weather", "arguments": "{\"city\":\"서울\"}"},
  {"type": "function_call_output", "call_id": "call_w4w7crhv",
   "output": "{\"temp_c\":31,\"condition\":\"맑음\"}"}
]
```

→ `"현재 서울의 날씨는 맑으며, 기온은 31°C, 습도는 45%입니다."`

`/api/chat` 과 `/v1/chat/completions` 는 `function` 으로 한 번 더 중첩된
기존 형식을 씁니다.

---

## 8. 이 디렉터리의 도구

### `occ` — 셸 래퍼

```bash
./occ "한국의 수도는?"              # 스트리밍 프롬프트
./occ -m gpt-oss:120b "안녕"        # 모델 지정
./occ -j "홍길동은 30살 디자이너야"   # JSON 출력 (코드펜스 자동 제거)
./occ ls                            # 모델 목록
./occ show gemma4:31b               # 모델 스펙
```

`OCC_MODEL` 환경변수로 기본 모델을 바꿀 수 있습니다.

### `ollama_cloud.py` — 파이썬 클라이언트

외부 의존성 없이 표준 라이브러리만 씁니다 (`ollama` / `openai` 패키지 불필요).

```python
from ollama_cloud import OllamaCloud

oc = OllamaCloud()

oc.chat("한국의 수도는?")                       # → "서울"
oc.generate("1+1은?", temperature=0)             # 단발 완성
oc.respond("일본의 수도는?", instructions="한 단어로")  # Responses API

for piece in oc.chat("긴 설명 부탁", stream=True):
    print(piece, end="", flush=True)

tools = [{"type": "function", "name": "get_weather", "description": "날씨 조회",
          "parameters": {"type": "object",
                         "properties": {"city": {"type": "string"}},
                         "required": ["city"]}}]
r = oc.respond("서울 날씨 알려줘", tools=tools, raw=True)
oc.tool_calls(r)   # [{'call_id': ..., 'name': 'get_weather', 'arguments': {'city': '서울'}}]

oc.models()        # 18개 (구독 전용 포함)
oc.show()          # 모델 스펙
```

단독 실행도 됩니다:

```bash
python3 ollama_cloud.py "안녕"     # 스트리밍 응답
python3 ollama_cloud.py            # 모델 목록
```

---

## 9. 기존 도구에 연결

OpenAI 호환 엔드포인트가 살아 있어, base URL을 받는 도구는 대부분 그대로 붙습니다.

```
Base URL : https://ollama.com/v1
API Key  : $OLLAMA_API_KEY
Model    : gemma4:31b / gpt-oss:120b / minimax-m3 ...
```

단, §4의 제약(구조화 출력·`tool_choice` 강제 미지원)에 의존하는 도구는 오작동할 수 있습니다.

---

## 10. 참고 링크

- 문서: https://docs.ollama.com/cloud
- API 키 관리: https://ollama.com/settings/keys
- 모델 목록: https://ollama.com/search?c=cloud
- 구독: https://ollama.com/upgrade
