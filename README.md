<p align="center">
  <img src="assets/ai-slop-thresher-banner.png" alt="흰 고양이가 탈곡기로 긴 원고를 다듬는 픽셀 아트. AI Slop Thresher: 이 글은 흥미롭지 않습니다." width="100%">
</p>

<h1 align="center">AI Slop 탈곡기:<br>이 글은 흥미롭지 않습니다.</h1>

<p align="center">
  한국어 초안의 상투어, 과잉 설명과 반복 수사를 줄이는 에이전트 스킬입니다.<br>
  원문의 사실과 말투를 유지하며 문장을 다듬습니다.
</p>

<p align="center">
  <a href="https://github.com/Burntgogi/ai-slop-thresher/releases/tag/v1.2.1"><img src="https://img.shields.io/badge/status-released-f3a6ca" alt="상태: 공개 릴리즈"></a>
  <a href="https://github.com/Burntgogi/ai-slop-thresher/releases/tag/v1.2.1"><img src="https://img.shields.io/badge/release-v1.2.1-315BFF" alt="릴리즈: v1.2.1"></a>
  <a href="#편집-기준"><img src="https://img.shields.io/badge/language-Korean-2f80ed" alt="윤문 대상 언어: 한국어"></a>
  <a href="#확인한-범위"><img src="https://img.shields.io/badge/checks-fixtures_passed-8a78d6" alt="검사: 저장된 가상 예문 검사 통과"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-3aa675" alt="라이선스: Apache-2.0"></a>
</p>

<p align="center">
  <strong>한국어</strong> · <a href="README.en.md">English</a> ·
  <a href="#적용-전후">적용 전후</a> · <a href="#설치">설치</a> ·
  <a href="#사용법">사용법</a> · <a href="#라이선스">라이선스</a>
</p>

**v1.2.1**은 기존 윤문·의미 보존과 하네스별 배포 구조에 가독성 개선을 통합한 릴리즈입니다. 정보 없는 흥미·칭찬을 덜고, 조건과 적용 단위를 유지하며 표현을 압축합니다. 문맥상 필요한 경우에만 정보 묶음과 위치를 조정합니다.

[릴리즈 변경 내용](docs/releases/v1.2.1.md)과 [최종 검토](reports/release-finalization-20261002.md)에 확인 범위와 사용자 피드백을 기록했습니다. 추가 비교 실험은 종료했으며 모든 글에서 이전 버전보다 좋다고 주장하지 않습니다. 이전 버전 사용자는 [버전 선택 안내](docs/version-choice.md)를 참고하세요.

Codex에서는 설치 후 다듬을 글과 함께 입력하세요. 다른 하네스에서는 해당 스킬 호출 문법을 사용하세요.

```text
$thresh 아래 글의 뜻과 말투를 유지하면서 자연스럽게 다듬어 주세요.
```

## 적용 전후

아래는 제작 과정에서 사용한 가상 제품 안내문입니다.

### 적용 전

> 흥미로운 점은 새 대시보드가 빠르고, 신속하며, 민첩한 업무 처리를 지원한다는 점입니다. 내부 테스트에서 주간 보고서 작성 시간은 30분에서 10분으로 줄었습니다. 하지만, 보고서는 'CSV'로도 내려받을 수 있습니다. 재미있는 점은 이처럼 보고서 작성 시간을 줄였다는 것입니다. **업무의 새로운 기준**을 제시하는 변화입니다.

### 적용 후

> 새 대시보드의 내부 테스트에서 주간 보고서 작성 시간이 30분에서 10분으로 줄었습니다. 보고서는 CSV로도 내려받을 수 있습니다.

반복 칭찬과 문맥에 맞지 않는 역접을 덜었습니다. 내부 테스트라는 범위, 두 수치와 CSV 기능은 남겼습니다. [20개 예문 전문](reports/comparisons.md)에서 조건, 인용문과 코드가 있는 사례도 볼 수 있습니다.

## 설치

공통 지침은 `skills/`, Codex 전용 표시 정보는 `integrations/codex/`, 생성된 Codex 플러그인은 `plugins/codex/ai-slop-thresher/`에 있습니다. 공통 스킬에는 Codex manifest와 `agents/openai.yaml`이 들어 있지 않습니다.

```text
skills/                            # 하네스 중립 원본 두 스킬
integrations/codex/agents/          # Codex 전용 메타데이터
plugins/codex/ai-slop-thresher/     # 원본에서 생성하는 플러그인
.agents/plugins/marketplace.json   # Codex 로컬 마켓플레이스
```

수동 설치에는 Python이 필요하지 않습니다. portable ZIP의 두 스킬 폴더를 같은 스킬 디렉터리에 놓으세요. Codex 플러그인 설치와 Claude Code·OpenCode·Cursor의 경로, 안전한 설치 스크립트 사용법은 [하네스별 설치 안내](docs/installation.md)에 있습니다. 스크립트에는 Python 3.10 이상이 필요하며 기본 실행은 쓰기 없는 미리보기입니다.

```powershell
python scripts/distribute.py install --target codex
python scripts/distribute.py install --target claude-code
python scripts/distribute.py install --target opencode
python scripts/distribute.py install --target cursor
```

경로를 확인한 뒤 선택한 명령에 `--apply`를 붙이면 설치합니다. 이미 같은 이름의 스킬이 있으면 덮어쓰지 않습니다. Codex에서는 플러그인과 스킬 직접 설치 중 한 방식을 선택하세요.

## 사용법

`$thresh`와 `$ai-slop-thresher`는 같은 편집 지침을 적용합니다. 짧은 호출용 `thresh`가 본 스킬을 읽으므로 두 폴더를 함께 설치해야 합니다.

| 원하는 작업 | 요청 예시 |
| --- | --- |
| 본문만 윤문 | `$thresh 아래 글을 정중한 말투로 다듬어 주세요.` |
| 적용 전후 비교 | `$thresh 원문과 수정문을 함께 보여주고 바뀐 이유를 짧게 적어 주세요.` |
| 문제 구간 진단 | `$thresh 글을 고치지 말고 어색한 구간과 이유만 알려 주세요.` |
| Markdown 파일 편집 | `$thresh README.md의 문장을 다듬어 주세요. 제목, 표, 링크와 명령어는 유지해 주세요.` |

기본 응답은 다듬은 본문입니다. 작업 설명이나 후속 제안, 제품 부제를 자동으로 붙이지 않습니다.

## 편집 기준

| 덜어내는 것 | 지키는 것 |
| --- | --- |
| 흥미로운 점 같은 상투적인 도입과 반복 칭찬 | 고유한 주장과 저자의 감정 |
| 문맥에 맞지 않는 접속사와 같은 뜻의 수식어 나열 | 실제 원인, 대조와 시간 순서 |
| 불필요한 쉼표, 강조용 작은따옴표와 장식 서식 | 직접 인용, 코드, URL, 날짜와 수치 표기 |
| 이미 한 말을 되풀이하는 설명과 마무리 | 독자에게 필요한 조건, 근거, 절차와 예시 |
| 앞 문장을 부정하고 같은 내용을 다시 정의하는 반복 수사 | 오류 정정, 책임, 피해, 원인 구별, 위험과 불확실성 |

가능성을 사실로 단정하거나 원문에 없는 경험을 보태지 않습니다. 이미 자연스러운 문장은 유지합니다. 자세한 규칙은 [SKILL.md](skills/ai-slop-thresher/SKILL.md)에 있습니다.

## 확인한 범위

v1.0.0 제작 당시 지침을 5회 개선했고, 기본 예문 12개와 추가 예문 8개의 적용 전후를 기록했습니다. 저장된 결과의 문자 검사와 자체 의미 검토를 수행했습니다. 상단의 `checks` 배지는 이 기존 예문의 문자 검사 결과를 나타냅니다.

원문과 윤문은 같은 에이전트가 작성한 가상 자료입니다. 독립 평가나 AI 탐지기 통과율을 측정한 결과는 아닙니다. 실제 문서에서는 수치, 조건과 인용을 원문과 대조해 주세요.

1.2.0 제작 당시 후보의 실제 에이전트 출력, 별도 개선 5회와 Codex·Dot·Muse 감수 범위는 [이번 개선 보고서](reports/improvement-20260930.md)에 기록합니다. 별도 Codex 에이전트도 같은 모델 계열을 사용하므로 독립 인간 평가나 모델 간 일반화 근거로 보지 않습니다.

[v1.1.0 / v1.2.0 릴리즈 A/B 비교](reports/ab-comparison-20260930.md)를 별도로 공개했습니다. 의미 보존 판정은 같았고 문체는 이전 버전 우세 10쌍·새 버전 우세 5쌍·동률 40쌍이었습니다. 합성 사례 28건을 두 번씩 실행한 탐색적 비교이며 새 버전의 전반적인 품질 우세는 확인하지 못했습니다.

## 참고한 프로젝트

다음 프로젝트의 편집 기준과 문서 구성을 참고했습니다. 이 스킬의 지침과 한국어 예문은 새로 작성했습니다.

| 프로젝트 | 참고한 내용 |
| --- | --- |
| [blader/humanizer](https://github.com/blader/humanizer) | 반복되는 도입·결말과 문단 구조 검토 |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) | 대상 언어에 맞춘 번역투와 서식 검토 |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | 본론 전 예고, 빈 결론과 장식 대시 줄이기 |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | 없는 사실 추가 금지, 진단과 윤문 구분 |
| [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai) | 한국어 조사·연결어미, 격식과 인용 보존 |
| [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer) | 학술 문장의 조건·표본 범위와 유보 보존 |
| [Nanako0129/sepia](https://github.com/Nanako0129/sepia) | 장르·독자에 맞춘 최소 수정과 원문 목소리 보존 |
| [Burntgogi/Gpt_Codex_HWP](https://github.com/Burntgogi/Gpt_Codex_HWP) | 배너, 제목, 바로가기와 결과 예시 배치 |
| [Burntgogi/codex_oracle](https://github.com/Burntgogi/codex_oracle) | 가운데 정렬 소개, 배지 색상·배치, 언어 전환과 릴리즈 문서 구성 |

읽은 리비전, 라이선스 원문과 구체적인 반영 범위는 [ATTRIBUTIONS.md](ATTRIBUTIONS.md)에 정리했습니다. 각 프로젝트의 유지관리자와 기여자께 감사드립니다.

상단 배지는 [Shields.io](https://shields.io/badges/static-badge)로 표시합니다. 배지의 참고 경로와 각 항목의 뜻은 [화면 구성 문서](docs/github-frontpage.md)에 적었습니다.

## 라이선스

Apache-2.0으로 배포합니다. [LICENSE](LICENSE)에 전체 조건을, [NOTICE](NOTICE)와 [ATTRIBUTIONS.md](ATTRIBUTIONS.md)에 저작권 고지와 참고 자료를 담았습니다. 참고 프로젝트의 저작권과 라이선스는 각 원저작자에게 남습니다.

## 문서

[릴리즈 노트](RELEASE_NOTES.md) · [변경 이력](CHANGELOG.md) · [제작 보고서](reports/ai-slop-thresher-report.md) · [20개 적용 전후 사례](reports/comparisons.md) · [재검증 방법](docs/verification.md)

[화면 구성과 참고 자료](docs/github-frontpage.md) · [README·릴리즈 노트 윤문 기록](reports/document-editing.md) · [전체 제작 자료 ZIP](https://github.com/Burntgogi/ai-slop-thresher/releases/download/v1.2.1/ai-slop-thresher-workbench.zip)
