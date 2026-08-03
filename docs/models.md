# Ollama Cloud 모델 소개

Ollama Cloud에서 제공하는 18개 모델의 상세 자료입니다.

- **스펙**(파라미터·컨텍스트·기능·배포일)은 `/api/tags`, `/api/show` 로 직접 조회한 값입니다.
- **소개 문구**는 ollama.com 공식 설명을 옮긴 것으로, 제조사 주장입니다.
- **무료/유료** 구분은 각 모델에 실제 요청을 보내 확인했습니다.

조회일: 2026-08-03 · 상위 문서: [README](../README.md)

---

## 한눈에 보기

| 모델 | 티어 | 파라미터 | 컨텍스트 | vision | 배포일 |
|---|:--:|---:|---:|:--:|---|
| [`kimi-k3`](#kimi-k3) | 💳 | 2.81T | 1.05M | ✅ | 2026-07-27 |
| [`deepseek-v4-pro`](#deepseek-v4-pro) | 💳 | 1.6T | 524K | — | 2026-04-24 |
| [`kimi-k2.6`](#kimi-k26) | 💳 | 1.04T | 262K | ✅ | 2026-03-31 |
| [`kimi-k2.7-code`](#kimi-k27-code) | 💳 | 1.04T | 262K | ✅ | 2026-06-12 |
| [`glm-5.2`](#glm-52) | 💳 | 756B | 1.0M | — | 2026-06-16 |
| [`glm-5.1`](#glm-51) | 💳 | 756B | 203K | — | 2026-04-07 |
| [`mistral-large-3:675b`](#mistral-large-3675b) | 💳 | 675B | 262K | ✅ | 2025-12-02 |
| [`nemotron-3-ultra`](#nemotron-3-ultra) | ✅ | 550B | 262K | — | 2026-06-04 |
| [`qwen3.5:397b`](#qwen35397b) | 💳 | 397B | 262K | ✅ | 2026-02-16 |
| [`deepseek-v4-flash:0731`](#deepseek-v4-flash0731) | 💳 | 304B | 1.05M | — | 2026-07-31 |
| [`minimax-m2.7`](#minimax-m27) | 💳 | 229B | 197K | — | 2026-03-18 |
| [`deepseek-v4-flash`](#deepseek-v4-flash) | 💳 | 158B | 1.05M | — | 2026-04-24 |
| [`nemotron-3-super`](#nemotron-3-super) | ✅ | 120B | 262K | — | 2026-03-11 |
| [`gpt-oss:120b`](#gpt-oss120b) | ✅ | 117B | 131K | — | 2025-08-05 |
| [`gemma4:31b`](#gemma431b) | ✅ | 32.7B | 262K | ✅ | 2026-04-02 |
| [`nemotron-3-nano:30b`](#nemotron-3-nano30b) | ✅ | 32B | 262K | — | 2025-12-15 |
| [`gpt-oss:20b`](#gpt-oss20b) | ✅ | 20.9B | 131K | — | 2025-08-05 |
| [`minimax-m3`](#minimax-m3) | ✅ | 비공개 | 524K | ✅ | 2026-06-01 |

✅ 무료 · 💳 구독 필요 · `thinking`과 `tools`는 **전 모델 지원**

---

# ✅ 무료 모델 (7개)

## nemotron-3-ultra

> NVIDIA Nemotron 3 Ultra is built for high-throughput reasoning and long-running agent workflows.

| | |
|---|---|
| 제조사 | NVIDIA |
| 파라미터 | 550B |
| 컨텍스트 | 262,144 |
| 기능 | completion, thinking, tools |
| 배포일 | 2026-06-04 |

**무료 티어에서 쓸 수 있는 가장 큰 모델입니다.** 고처리량 추론과 장시간 실행되는
에이전트 워크플로를 겨냥해 만들어졌습니다. 무료로 최대 성능이 필요하면 첫 후보입니다.
다만 vision은 지원하지 않습니다.

```bash
./occ -m nemotron-3-ultra "복잡한 추론이 필요한 질문"
```

---

## nemotron-3-super

> NVIDIA Nemotron 3 Super is a 120B open MoE model activating just 12B parameters
> to deliver maximum compute efficiency and accuracy for complex multi-agent applications.

| | |
|---|---|
| 제조사 | NVIDIA |
| 파라미터 | 120B (MoE, 활성 12B) |
| 컨텍스트 | 262,144 |
| 기능 | completion, thinking, tools |
| 배포일 | 2026-03-11 |

120B 규모지만 MoE 구조로 **실제 활성 파라미터는 12B**라 응답이 빠릅니다.
멀티 에이전트 애플리케이션을 목표로 설계됐습니다. Ultra가 과하고 Nano가 부족할 때
중간 선택지로 적합합니다.

---

## gpt-oss:120b

> OpenAI's open-weight models designed for powerful reasoning, agentic tasks,
> and versatile developer use cases.

| | |
|---|---|
| 제조사 | OpenAI |
| 파라미터 | 117B |
| 컨텍스트 | 131,072 |
| 기능 | completion, thinking, tools |
| 배포일 | 2025-08-05 |

OpenAI의 공개 가중치 모델입니다. 목록에서 **가장 오래된 모델**(2025-08)이지만
범용성이 검증돼 있어 무난한 기본값으로 쓰입니다. 컨텍스트 131K는 무료 모델 중
가장 작은 편이므로 긴 문서 작업에는 맞지 않습니다.

---

## gpt-oss:20b

> OpenAI's open-weight models designed for powerful reasoning, agentic tasks,
> and versatile developer use cases.

| | |
|---|---|
| 제조사 | OpenAI |
| 파라미터 | 20.9B |
| 컨텍스트 | 131,072 |
| 기능 | completion, thinking, tools |
| 배포일 | 2025-08-05 |

120b의 경량판입니다. **전체 목록에서 가장 작은 모델**이라 응답이 가장 빠릅니다.
간단한 분류·추출·요약처럼 반복 호출이 많은 작업에 비용 대비 효율이 좋습니다.

---

## minimax-m3

> MiniMax M3: Coding & Agentic Frontier. 1M context window. Native Multimodality.

| | |
|---|---|
| 제조사 | MiniMax |
| 파라미터 | 비공개 (API가 0 반환) |
| 컨텍스트 | 524,288 |
| 기능 | completion, thinking, tools, **vision** |
| 배포일 | 2026-06-01 |

**무료 모델 중 컨텍스트가 가장 큽니다(524K).** 코딩과 에이전트 작업을 표방하며
네이티브 멀티모달을 지원합니다. 무료로 이미지를 다뤄야 한다면 이 모델과
`gemma4:31b` 둘 중 하나입니다.

> ⚠️ 공식 설명은 "1M context window"라고 하지만, `/api/show` 실측값은 **524,288**입니다.
> 클라우드 배포본에서 축소됐을 가능성이 있습니다.

---

## gemma4:31b

> Gemma 4 models are designed to deliver frontier-level performance at each size.
> They are well-suited for reasoning, agentic workflows, coding, and multimodal understanding.

| | |
|---|---|
| 제조사 | Google |
| 파라미터 | 32.7B |
| 컨텍스트 | 262,144 |
| 양자화 | BF16 |
| 기능 | completion, thinking, tools, **vision** |
| 배포일 | 2026-04-02 |

이 저장소의 **기본 모델**입니다. 32.7B로 크지 않으면서 262K 컨텍스트와 vision을
모두 갖춰 균형이 좋습니다. 한국어 응답 품질도 무난합니다.

```bash
./occ "한국의 수도는?"        # 기본값이 gemma4:31b
```

---

## nemotron-3-nano:30b

> Nemotron-3-Nano is a new Standard for Efficient, Open, and Intelligent Agentic Models,
> now updated with a 4B parameter count model.

| | |
|---|---|
| 제조사 | NVIDIA |
| 파라미터 | 32B |
| 컨텍스트 | 262,144 |
| 기능 | completion, thinking, tools |
| 배포일 | 2025-12-15 |

효율 중심의 소형 에이전트 모델입니다. 32B로 가벼우면서 262K 컨텍스트를 유지해,
긴 입력을 빠르게 처리해야 할 때 유용합니다.

> 공식 설명이 언급하는 4B 모델은 클라우드에 없고, 제공되는 태그는 `:30b` 하나입니다.

---

# 💳 구독 필요 모델 (11개)

호출 시 `HTTP 403 — this model requires a subscription` 이 반환됩니다.
구독은 https://ollama.com/upgrade 참고.

## kimi-k3

> Kimi K3 is an open-weight, native multimodal agentic model and our most capable model to date.

| | |
|---|---|
| 제조사 | Moonshot AI |
| 파라미터 | **2.81T** |
| 컨텍스트 | **1,048,576** |
| 기능 | completion, thinking, tools, vision |
| 배포일 | 2026-07-27 |

**목록 전체에서 파라미터가 가장 크고(2.81T), 컨텍스트도 최대(1.05M)입니다.**
가장 최근 배포된 모델이기도 합니다. Moonshot AI가 자사 최고 성능 모델로 소개합니다.

---

## deepseek-v4-pro

> DeepSeek-V4-Pro is a frontier Mixture-of-Experts model with a large context window
> and three reasoning modes.

| | |
|---|---|
| 제조사 | DeepSeek |
| 파라미터 | 1.6T |
| 컨텍스트 | 524,288 |
| 기능 | completion, thinking, tools |
| 배포일 | 2026-04-24 |

MoE 구조의 프런티어 모델로, **세 가지 추론 모드**를 제공한다고 소개됩니다.

---

## kimi-k2.6

> Kimi K2.6 is an open-source, native multimodal agentic model that advances practical
> capabilities in long-horizon coding, coding-driven design, proactive autonomous execution,
> and swarm-based task orchestration.

| | |
|---|---|
| 제조사 | Moonshot AI |
| 파라미터 | 1.04T |
| 컨텍스트 | 262,144 |
| 기능 | completion, thinking, tools, vision |
| 배포일 | 2026-03-31 |

장기 코딩 작업, 자율 실행, 스웜 기반 태스크 오케스트레이션을 강조합니다.

---

## kimi-k2.7-code

> Kimi K2.7 Code is Moonshot AI's coding-focused agentic model built upon Kimi K2.6,
> with substantial improvements on real-world long-horizon coding tasks and roughly
> 30% lower thinking-token usage.

| | |
|---|---|
| 제조사 | Moonshot AI |
| 파라미터 | 1.04T |
| 컨텍스트 | 262,144 |
| 기능 | completion, thinking, tools, vision |
| 배포일 | 2026-06-12 |

K2.6 기반의 **코딩 특화** 파생 모델입니다. thinking 토큰 사용량을 약 30% 줄였다고
소개돼, 추론 비용이 부담될 때 유리합니다.

---

## glm-5.2

> GLM-5.2 is Z.ai's flagship model for the era of long-horizon tasks.

| | |
|---|---|
| 제조사 | Z.ai |
| 파라미터 | 756B |
| 컨텍스트 | **1,000,000** |
| 기능 | completion, thinking, tools |
| 배포일 | 2026-06-16 |

Z.ai의 플래그십으로, 장기 실행 작업을 겨냥합니다. 100만 토큰 컨텍스트를 제공합니다.

---

## glm-5.1

> GLM-5.1 is our next-generation flagship model for agentic engineering, with significantly
> stronger coding capabilities than its predecessor. It achieves state-of-the-art performance
> on SWE-Bench Pro and leads GLM-5 by a wide margin.

| | |
|---|---|
| 제조사 | Z.ai |
| 파라미터 | 756B |
| 컨텍스트 | 202,752 |
| 기능 | completion, thinking, tools |
| 배포일 | 2026-04-07 |

**SWE-Bench Pro에서 SOTA를 주장**하는 코딩 특화 모델입니다. 파라미터는 5.2와 같지만
컨텍스트가 203K로 작습니다.

---

## mistral-large-3:675b

> A general-purpose multimodal mixture-of-experts model for production-grade tasks
> and enterprise workloads.

| | |
|---|---|
| 제조사 | Mistral AI |
| 파라미터 | 675B |
| 컨텍스트 | 262,144 |
| 기능 | completion, tools, vision |
| 배포일 | 2025-12-02 |

엔터프라이즈 워크로드를 겨냥한 범용 멀티모달 MoE 모델입니다.

> 목록에서 **유일하게 `thinking`을 지원하지 않는 모델**입니다.

---

## qwen3.5:397b

> Qwen 3.5 is a family of open-source multimodal models that delivers exceptional
> utility and performance.

| | |
|---|---|
| 제조사 | Alibaba |
| 파라미터 | 397B |
| 컨텍스트 | 262,144 |
| 기능 | completion, thinking, tools, vision |
| 배포일 | 2026-02-16 |

오픈소스 멀티모달 계열로, 범용성과 성능의 균형을 내세웁니다.

---

## deepseek-v4-flash:0731

> DeepSeek-V4-Flash is a preview of the DeepSeek-V4 series, a Mixture-of-Experts model
> with 284B total parameters and 13B activated, built for efficient reasoning across
> a 1M-token context window.

| | |
|---|---|
| 제조사 | DeepSeek |
| 파라미터 | 304B |
| 컨텍스트 | **1,048,576** |
| 기능 | completion, thinking, tools |
| 배포일 | 2026-07-31 |

`deepseek-v4-flash`의 **7월 31일 스냅샷**입니다. 목록에서 두 번째로 최근 배포됐습니다.
날짜 태그로 고정하면 모델 갱신에 따른 동작 변화를 피할 수 있습니다.

---

## minimax-m2.7

> MiniMax's M2-series model for coding, agentic workflows, and professional productivity.

| | |
|---|---|
| 제조사 | MiniMax |
| 파라미터 | 229B |
| 컨텍스트 | 196,608 |
| 기능 | completion, thinking, tools |
| 배포일 | 2026-03-18 |

M3의 이전 세대입니다. 무료인 M3가 더 크고 최신이므로, 특별히 M2.7 동작이
필요한 경우가 아니면 M3를 쓰는 편이 낫습니다.

---

## deepseek-v4-flash

> DeepSeek-V4-Flash is a preview of the DeepSeek-V4 series, a Mixture-of-Experts model
> with 284B total parameters and 13B activated, built for efficient reasoning across
> a 1M-token context window.

| | |
|---|---|
| 제조사 | DeepSeek |
| 파라미터 | 158B |
| 컨텍스트 | **1,048,576** |
| 기능 | completion, thinking, tools |
| 배포일 | 2026-04-24 |

V4 시리즈의 프리뷰 경량판입니다. **100만 토큰 컨텍스트를 가진 모델 중 가장 작습니다.**

> ⚠️ 공식 설명은 "284B total / 13B activated"라고 하지만 `/api/show` 실측값은
> **158B**입니다. 날짜 태그(`:0731`)는 304B로 또 다릅니다. 태그마다 실제 배포본이
> 다르므로 스펙에 의존하는 코드라면 직접 조회해 확인하세요.

---

# 선택 가이드

## 무료로 쓴다면

| 상황 | 추천 |
|---|---|
| 최대 성능 | `nemotron-3-ultra` (550B) |
| 균형 (기본값) | `gemma4:31b` |
| 긴 문서 처리 | `minimax-m3` (524K) |
| 이미지 입력 | `minimax-m3`, `gemma4:31b` |
| 빠른 응답 · 대량 호출 | `gpt-oss:20b` (20.9B) |
| 멀티 에이전트 | `nemotron-3-super` (활성 12B) |

## 구독한다면

| 상황 | 추천 |
|---|---|
| 최고 성능 | `kimi-k3` (2.81T / 1.05M) |
| 코딩 | `kimi-k2.7-code`, `glm-5.1` |
| 초장문 + 효율 | `deepseek-v4-flash` 계열 (1.05M) |
| 엔터프라이즈 범용 | `mistral-large-3:675b` |

---

# 알아둘 점

- **`thinking`과 `tools`는 18개 전 모델이 지원합니다.** 이 두 기능으로는 모델을 가릴 필요가 없습니다.
- **`vision` 지원은 7개** — `kimi-k3`, `kimi-k2.6`, `kimi-k2.7-code`, `mistral-large-3`,
  `qwen3.5`, `minimax-m3`, `gemma4:31b`. 이 중 무료는 뒤의 두 개뿐입니다.
- **100만 토큰급 컨텍스트는 무료에 없습니다.** `kimi-k3`, `glm-5.2`, `deepseek-v4-flash`
  계열 모두 구독이 필요합니다.
- **공식 설명과 실측 스펙이 어긋나는 경우가 있습니다** (`minimax-m3`의 컨텍스트,
  `deepseek-v4-flash`의 파라미터). 정확한 값이 필요하면 `/api/show`로 직접 조회하세요.

```bash
./occ show minimax-m3
```

```python
from ollama_cloud import OllamaCloud
OllamaCloud().show("minimax-m3")
```

---

# 목록 갱신하기

모델 구성은 수시로 바뀝니다. 최신 상태는 직접 조회하세요.

```bash
./occ ls                    # 전체 목록
./occ show <모델명>          # 개별 스펙
```

무료/유료 구분은 실제 호출로만 알 수 있습니다.

```bash
for m in $(./occ ls); do
  printf "%-24s " "$m"
  curl -s https://ollama.com/api/chat -H "Authorization: Bearer $OLLAMA_API_KEY" \
    -d "{\"model\":\"$m\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"stream\":false,\"options\":{\"num_predict\":1}}" \
    | grep -q '"error"' && echo "💳 구독" || echo "✅ 무료"
done
```
