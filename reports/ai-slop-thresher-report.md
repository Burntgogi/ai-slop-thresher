# AI Slop 탈곡기: 이 글은 흥미롭지 않습니다.

제작·비교·개선 보고서. 작성일: 2026년 9월 12일. 현재 버전: ai-slop-thresher 1.1.0.

English: AI Slop Thresher: This Text Is Not Interesting.

정식 호출: `$ai-slop-thresher`. 짧은 호출: `$thresh`. 1.1.0은 이름과 호출명 변경이다. 아래 예문과 5회 개선 기록은 편집 지침이 같은 1.0.0 당시 결과다. [변경 기록](../research/rename-notes.md)

한국어 초안의 반복 수사와 과잉 설명을 줄이는 스킬을 제작했다. 최근 12개월 이내 생성되고 별 수가 1,000개 이상인 관련 GitHub 저장소 7개를 비교했다. 초기본 이후 다섯 차례 규칙을 개선했으며, 기본 예문 12개와 추가 전이 예문 8개를 검토했다.

스킬은 원문을 짧게 만드는 것만을 목표로 삼지 않는다. 불필요한 예고와 장식을 줄이면서 조건·예외·수치·인용·말투를 유지하도록 설계했다. 이미 자연스러운 문장은 그대로 반환한다.

[스킬 원문](../skills/ai-slop-thresher/SKILL.md) · [전체 적용 전후 20개 사례](comparisons.md) · [평가 방법](../evaluation/protocol.md) · [재현 검사 결과](../evaluation/checks/summary.json)

## 1. 적용 요소와 편집 기준

| 요청 요소 | 적용 방법 | 보존할 예외 |
| --- | --- | --- |
| AI slop | 내용 없는 예고, 과장, 반대편을 꾸며내는 대구, 반복 결말을 줄인다. | 저자의 실제 의견과 감정은 유지한다. |
| TMI | 중복 설명과 요청에 필요 없는 일반론을 덜고 후속 제안을 자동으로 붙이지 않는다. | 조건·근거·절차·요청된 예시는 보존한다. |
| 독특한 점 반복 언급 | 흥미로운 점 등의 예고를 빼고 사실을 바로 쓴다. 같은 특징을 재차 칭찬하지 않는다. | 인용문과 해당 표현 자체를 분석하는 진단은 유지한다. |
| 문맥에 맞지 않는 접속사 | 실제 역접·인과·시간 순서인지 확인해 삭제하거나 재구성한다. | 실제 관계를 알려주는 접속사는 남긴다. |
| 같은 성격의 단어 나열 | 동의어 수식은 하나로 줄인다. | 서로 다른 기능·원인·조건은 전부 남긴다. |
| 쉼표·작은따옴표 과잉 | 호흡용 쉼표와 단어를 감싸는 강조를 덜어낸다. | 인용·실제 표시 문구·숫자 구분과 필요한 구문 구분은 보존한다. |
| Markdown·대시·하이픈 강조 | 일반 산문의 장식용 굵게·기울임·대시·하이픈 불릿을 쓰지 않는다. | 날짜·음수·범위·URL·코드·명령어와 요청한 문서 구조는 보존한다. |

em dash와 en dash, hyphen은 문자이며 Markdown 전용 문법은 아니다. 이번 요구는 산문에서 강조 장치로 사용하는 것을 피하라는 뜻으로 적용했다. 직접 인용과 기능 표기의 문자는 손상시키지 않는다.

## 2. GitHub 저장소 선정과 비교

기간은 2025년 9월 12일부터 2026년 9월 12일까지다. 생성 여부는 GitHub REST API의 created_at으로 확인했고 별 수 역시 API 조회 값을 기록했다. 최근 커밋 날짜나 과거 검색 캐시를 생성일·현재 별 수로 사용하지 않았다. 아래 생성일은 UTC 날짜다.

| 저장소 | 생성일 | 조회 별 수 | 비교할 원문 |
| --- | --- | ---: | --- |
| [blader/humanizer](https://github.com/blader/humanizer) | 2026-01-18 | 46,981 | [고정 리비전](https://github.com/blader/humanizer/blob/9862685f575c65a8247f90369951df1b3416e3d6/SKILL.md) · [API 메타데이터](https://api.github.com/repos/blader/humanizer) |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) | 2026-01-19 | 17,077 | [고정 리비전](https://github.com/op7418/Humanizer-zh/blob/91f3d394db8419c20d67ebe22a96cf8fee0a404b/SKILL.md) · [API 메타데이터](https://api.github.com/repos/op7418/Humanizer-zh) |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | 2026-01-11 | 17,039 | [고정 리비전](https://github.com/hardikpandya/stop-slop/blob/8da1f030185bdfe8471220585162991eaeb970e9/SKILL.md) · [API 메타데이터](https://api.github.com/repos/hardikpandya/stop-slop) |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | 2026-03-06 | 4,315 | [고정 리비전](https://github.com/conorbronsdon/avoid-ai-writing/blob/e7faf81f2c9353bd5e5c6ad6ce82f513bb89ee3e/SKILL.md) · [API 메타데이터](https://api.github.com/repos/conorbronsdon/avoid-ai-writing) |
| [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai) | 2026-04-24 | 5,459 | [고정 리비전](https://github.com/epoko77-ai/im-not-ai/blob/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7/codex/skills/humanize-korean/SKILL.md) · [API 메타데이터](https://api.github.com/repos/epoko77-ai/im-not-ai) |
| [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer) | 2026-06-20 | 1,501 | [고정 리비전](https://github.com/AIScientists-Dev/academic-humanizer/blob/94b88b23703bed7df507acae7d6d5876209a0cdf/SKILL.md) · [API 메타데이터](https://api.github.com/repos/AIScientists-Dev/academic-humanizer) |
| [Nanako0129/sepia](https://github.com/Nanako0129/sepia) | 2026-08-28 | 2,556 | [고정 리비전](https://github.com/Nanako0129/sepia/blob/abddddb545ad791fc39d65331080bd0e1422c1d1/skills/sepia/SKILL.md) · [API 메타데이터](https://api.github.com/repos/Nanako0129/sepia) |

관련 후보 8개 중 7개를 선정했다. RevoltDevScript/Revolt-Script는 학습 플랫폼 자동화가 중심이어서 비교 범위에서 제외했다. Humanizer-zh는 다른 두 저장소의 영향을 명시하므로 7개를 독립적인 방법 7가지로 보지 않는다. 별 수는 선정 조건이며 품질 순위가 아니다. 검색 범위와 제외 근거는 [선정 기록](../research/selection-notes.md), 조회값은 [메타데이터](../research/repositories.json)에 있다.

| 저장소 | 채택한 내용 | 제외·조정한 내용 |
| --- | --- | --- |
| [blader/humanizer](https://github.com/blader/humanizer/blob/9862685f575c65a8247f90369951df1b3416e3d6/SKILL.md) | 문장 단어뿐 아니라 반복되는 도입·결말과 문단 구조를 검토한다. 사실을 보존하고 재검토한다. | 초안·잔여 패턴·최종본을 매번 모두 출력하는 방식과 원문에 없는 반응 추가는 채택하지 않는다. |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh/blob/91f3d394db8419c20d67ebe22a96cf8fee0a404b/SKILL.md) | 영어권 패턴을 대상 언어의 예문으로 다시 설계한다. 번역투와 과도한 서식을 함께 본다. | 인격을 주입하는 방향, 자기평가 점수의 합계로 자연스러움을 증명하는 방식은 채택하지 않는다. |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop/blob/8da1f030185bdfe8471220585162991eaeb970e9/SKILL.md) | 본론 전 예고, 불필요한 대구, 내용이 없는 결론과 장식 대시를 줄인다. | 모든 부사·피동문 제거, 세 항목을 두 항목보다 나쁘게 보는 규칙은 채택하지 않는다. |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing/blob/e7faf81f2c9353bd5e5c6ad6ce82f513bb89ee3e/SKILL.md) | 원문에 없는 1인칭·사실을 넣지 않는다. 진단과 윤문을 구별하며 수정 후 다시 읽는다. | 기본 응답의 여러 진단 섹션, 영어 어휘 목록의 직역, 무거운 탐지기 의존은 채택하지 않는다. |
| [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai/blob/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7/codex/skills/humanize-korean/SKILL.md) | 한국어 조사·연결어미, 명사형·피동, 서법, 격식, 직접 인용을 중심으로 국소 편집한다. | 고정 변경률에 따른 중단, 매번 파일·숨은 요약 주석 생성, 종결어미와 길이의 획일적 할당은 채택하지 않는다. |
| [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer/blob/94b88b23703bed7df507acae7d6d5876209a0cdf/SKILL.md) | 조건·표본 범위·유보와 수치·결과·인용을 보존한다. 학술 문장을 임의로 구어체로 바꾸지 않는다. | 연구비 제안서 구조나 문단 수 고정은 일반 한국어 윤문의 필수 규칙으로 옮기지 않는다. |
| [Nanako0129/sepia](https://github.com/Nanako0129/sepia/blob/abddddb545ad791fc39d65331080bd0e1422c1d1/skills/sepia/SKILL.md) | 장르와 독자에 맞게 편집하고 원문의 목소리를 보존한다. 최소 수정과 전체 흐름 검토를 함께 한다. | 소설 서사 구조 수리, 작성 모델 추정·분류, 특정 작가 목소리 주입은 이번 범위에 넣지 않는다. |

규칙과 예문은 새로 작성했다. 상류 스킬을 모두 실행해 성능을 순위화한 비교는 아니며, 상류의 탐지율·통계 주장을 이 스킬의 성능 근거로 옮기지 않았다. 참조한 파일은 커밋 리비전과 함께 [출처 기록](../research/source-revisions.json)에 고정했다.

## 3. 미적용과 적용 결과

대조군은 별도 모델의 무스킬 응답이 아니라 같은 초안 원문이다. 아래 예문도 실제 제품이나 연구의 사실 자료가 아닌 가상 설정이다.

### C01 · 제품 안내

미적용

```text
흥미로운 점은 새 대시보드가 빠르고, 신속하며, 민첩한 업무 처리를 지원한다는 점입니다. 내부 테스트에서 주간 보고서 작성 시간은 30분에서 10분으로 줄었습니다. 하지만, 보고서는 'CSV'로도 내려받을 수 있습니다. 재미있는 점은 이처럼 보고서 작성 시간을 줄였다는 것입니다. **업무의 새로운 기준**을 제시하는 변화입니다.
```

적용

```text
새 대시보드의 내부 테스트에서 주간 보고서 작성 시간이 30분에서 10분으로 줄었습니다. 보고서는 CSV로도 내려받을 수 있습니다.
```

반복 칭찬과 빈 역접을 덜었다. 내부 테스트라는 범위, 시간 두 수치와 CSV 기능을 유지했다.

### C05 · 가상 반품 안내

미적용

```text
중요하고 핵심적인 부분은 제품을 개봉하지 않은 경우에만 수령 후 7일 이내 반품을 신청할 수 있다는 점입니다. 다만 주문 제작 상품은 제외됩니다. 반품 배송비 3,000원은 구매자가 부담해야 합니다. 이 점을 반드시, 꼭, 필수적으로 기억해 주시기 바랍니다.
```

적용

```text
제품을 개봉하지 않은 경우에만 수령 후 7일 이내 반품을 신청할 수 있습니다. 다만 주문 제작 상품은 제외됩니다. 반품 배송비 3,000원은 구매자가 부담해야 합니다.
```

미개봉 조건, 기한, 제외 상품, 배송비와 부담 주체를 모두 남겼다.

### C11 · 개인 경험

미적용

```text
나는 발표 직전에 꼭 물을 마셔요. 긴장하면 입이 마르거든요. 어제도 그랬어요. 첫 문장을 읽고 나니 좀 나아졌고요.
```

적용

```text
나는 발표 직전에 꼭 물을 마셔요. 긴장하면 입이 마르거든요. 어제도 그랬어요. 첫 문장을 읽고 나니 좀 나아졌고요.
```

이미 자연스러워 변경하지 않았다. 꼭과 좀을 부사라는 이유로 제거하지 않았다.

[전체 사례 전문](comparisons.md)에는 기술 문서, 직접 인용, 요금 조건, 초보자 설명, 번호 목록, 모호한 출처와 진단 전용 요청도 포함했다.

## 4. 다섯 차례 재귀개선

각 회차는 기존 버전 적용, 결과 또는 경계 사례 검토, 규칙 수정, 재적용·검사 순서로 진행했다. 관찰한 출력 결함과 지침의 모호함을 구분했다. 2~4차에서는 기존 후보가 이미 보존한 내용을 일부러 망가뜨리지 않고 지침을 명확히 했다. 이전 통과 결과는 바꿀 이유가 없으면 유지했다.

| 회차 | 버전 | 발견 근거 | 반영한 수정 | 누적 문자 검사 |
| --- | --- | --- | --- | --- |
| 1 | 0.1.0 → 0.2.0 | C03에 명사형·피동과 비슷한 예정 표현이 남음 | 한국어 동사문과 원래 격식 보존 | 3/3 |
| 2 | 0.2.0 → 0.3.0 | C04·C05에서 가능성·의무·표본 범위를 판단할 명시적 기준이 부족 | 부정·조건·범위·인과·출처를 보존 목록에 추가 | 5/5 |
| 3 | 0.3.0 → 0.4.0 | C06~C08에서 장식과 인용·기능 문자를 구별할 기준이 부족 | 인용, 날짜, 코드, URL, 표시 문구의 보존 예외 추가 | 8/8 |
| 4 | 0.4.0 → 0.5.0 | C09~C11에서 실제 열거·필요한 비유·원래 부사를 지울 위험 | TMI 제거와 요약을 구별하고 보존 기준을 강화 | 11/11 |
| 5 | 0.5.0 → 1.0.0 | C04의 조사 연결이 어색함. C12와 진단 요청의 출력 계약을 정리할 필요 | 문단 전체 재독, 출력 방식과 입력 경계 명확화 | 12/12 |

검사 수가 늘어난 것은 누적 사례 수가 늘었기 때문이다. 3/3에서 12/12로 바뀐 것을 성능 향상률로 해석하지 않는다. 각 회차의 실제 결과와 관찰 근거는 [rounds 폴더](../evaluation/rounds), 지침 스냅샷은 [versions 폴더](../evaluation/versions)에 있다.

추가 검수에서 T02의 불과하며를 불과해로 바꾼 표현이 인과를 강하게 만들 수 있음을 발견했다. 문자 검사는 이를 통과시켰지만 자체 의미 검토로 불과하고로 복원했다. 이는 1.0.0의 기존 규칙을 적용한 출력 수정이며 여섯 번째 규칙 개선으로 집계하지 않았다. [수정 기록](../evaluation/final-qa.json)

## 5. 측정 결과와 한계

기본 12개 사례의 편집 가능 부분에서 집계했다. 보호 대상으로 지정한 직접 인용·코드·실제 표시 문구는 표면 표현 집계에서 제외했다. 단, 문자 보존 여부는 따로 검사했다.

| 측정 항목 | 미적용 | 적용 | 해석 |
| --- | ---: | ---: | --- |
| 전체 글자 수 | 1,595 | 1,053 | 공백·줄바꿈·기호 포함. 짧을수록 좋다는 점수가 아님 |
| 지정 예고 표현 | 6 | 0 | 검사기에 명시한 유한한 표현 목록만 셈 |
| 쉼표 문자 | 23 | 3 | 실제 열거와 금액 구분용 쉼표가 남음 |
| 작은따옴표 문자 | 6 | 0 | 보호 인용·표시 문구 제외 |
| 장식 대시·하이픈 패턴 | 1 | 0 | en dash·하이픈 추가 사례는 T07에서 별도 확인 |
| 굵게 표시 구간 | 5 | 0 | 보존할 문서 구조와 구별 |

기본 사례의 숫자 토큰·보존 문자열·기호 검사는 12/12, 추가 전이 사례 검사는 8/8 통과했다. 금액 변경, 명령어 변조, 인용 변경, 기능 누락을 의도적으로 넣은 네 가지 검사 대조군은 모두 오류로 잡혔다. 이는 검사기가 단순히 모든 문자열을 통과시키지 않는다는 확인이다.

의미와 요청 충족 여부는 [자체 검토 기록](../evaluation/semantic-review.json)에 사례별로 남겼다. 숫자 토큰 검사는 숫자 집합의 누락·추가만 확인하므로 숫자와 대상의 관계가 뒤바뀌는 오류까지 보장하지 않는다. 쉼표나 표현 개수도 문맥을 이해하지 못한다. T02처럼 문자 검사에 잡히지 않는 오류를 따로 읽어야 한다.

원문 작성·윤문·의미 평가는 같은 에이전트가 수행했다. 기본 및 전이 예문 모두 자체 작성이므로 독립적인 사람 평가, 통제된 모델 비교, 홀드아웃 성능 검증으로 볼 수 없다. 이번 작업은 실행 가능한 스킬, 요구별 예시, 실제 수정 이력과 재현 가능한 문자 검사까지 제공한다. 인간 작성 판별이나 AI 탐지 회피율은 평가하지 않았다.

## 6. 사용과 재현

기본 호출

```text
$thresh 아래 글의 뜻과 말투를 유지하면서 자연스럽게 다듬어 주세요.

여기에 원문을 붙여 넣습니다.
```

비교가 필요하면 적용 전후와 변경 이유를 함께 요청한다. 진단만 필요하면 고쳐 쓰지 말고 문제 구간만 짚어 달라고 요청한다. 평소에는 윤문 본문만 반환한다. 런타임은 지침 파일만 읽으며 외부 API나 추가 Python 패키지가 필요하지 않다.

평가 문자 검사 재실행은 Python 3 표준 라이브러리만 사용한다. 저장된 결과를 다시 검사하며 새 윤문을 생성하지 않는다.

```powershell
python evaluation/run_checks.py
python evaluation/build_report.py
```

공식 skill-creator의 quick_validate.py로 최종 SKILL.md 형식을 검증했고 UI 메타데이터의 YAML, 설명 길이와 호출명을 확인했다. 이 형식 검증은 자연스러움 검증과 별개다. 배포 파일은 [ai-slop-thresher.zip](../dist/ai-slop-thresher.zip)이며, 배포 ZIP에는 ai-slop-thresher 본 스킬 네 파일과 thresh 단축 스킬 두 파일이 함께 들어 있다.
