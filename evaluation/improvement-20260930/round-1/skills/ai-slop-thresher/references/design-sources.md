# 설계 근거

조사 기준일은 2026년 9월 12일이다. GitHub 저장소 생성일이 2025년 9월 12일 이후이고 별 수가 1,000개 이상인 관련 저장소에서 규칙 설계를 비교했다. 최신 수정일을 생성일 대신 사용하지 않았다. 별 수는 선정 조건이며 품질 점수가 아니다.

아래는 당시 읽은 소스의 고정 리비전과 채택 여부다. 규칙과 한국어 예문은 이 작업의 요구에 맞춰 새로 작성했으며 상류의 코드나 규칙 문구를 복제하지 않았다. 저장소들의 실제 윤문 성능을 동일 모델로 비교한 실험은 아니다.

| 저장소와 확인 소스 | 반영한 판단 | 채택하지 않은 부분 |
| --- | --- | --- |
| [blader/humanizer](https://github.com/blader/humanizer/blob/9862685f575c65a8247f90369951df1b3416e3d6/SKILL.md) | 문장 단어뿐 아니라 반복되는 도입·결말과 문단 구조를 검토한다. 사실을 보존하고 재검토한다. | 초안·잔여 패턴·최종본을 매번 모두 출력하는 방식과 원문에 없는 반응 추가는 채택하지 않는다. |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh/blob/91f3d394db8419c20d67ebe22a96cf8fee0a404b/SKILL.md) | 영어권 패턴을 대상 언어의 예문으로 다시 설계한다. 번역투와 과도한 서식을 함께 본다. | 인격을 주입하는 방향, 자기평가 점수의 합계로 자연스러움을 증명하는 방식은 채택하지 않는다. |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop/blob/8da1f030185bdfe8471220585162991eaeb970e9/SKILL.md) | 본론 전 예고, 불필요한 대구, 내용이 없는 결론과 장식 대시를 줄인다. | 모든 부사·피동문 제거, 세 항목을 두 항목보다 나쁘게 보는 규칙은 채택하지 않는다. |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing/blob/e7faf81f2c9353bd5e5c6ad6ce82f513bb89ee3e/SKILL.md) | 원문에 없는 1인칭·사실을 넣지 않는다. 진단과 윤문을 구별하며 수정 후 다시 읽는다. | 기본 응답의 여러 진단 섹션, 영어 어휘 목록의 직역, 무거운 탐지기 의존은 채택하지 않는다. |
| [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai/blob/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7/codex/skills/humanize-korean/SKILL.md) | 한국어 조사·연결어미, 명사형·피동, 서법, 격식, 직접 인용을 중심으로 국소 편집한다. | 고정 변경률에 따른 중단, 매번 파일·숨은 요약 주석 생성, 종결어미와 길이의 획일적 할당은 채택하지 않는다. |
| [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer/blob/94b88b23703bed7df507acae7d6d5876209a0cdf/SKILL.md) | 조건·표본 범위·유보와 수치·결과·인용을 보존한다. 학술 문장을 임의로 구어체로 바꾸지 않는다. | 연구비 제안서 구조나 문단 수 고정은 일반 한국어 윤문의 필수 규칙으로 옮기지 않는다. |
| [Nanako0129/sepia](https://github.com/Nanako0129/sepia/blob/abddddb545ad791fc39d65331080bd0e1422c1d1/skills/sepia/SKILL.md) | 장르와 독자에 맞게 편집하고 원문의 목소리를 보존한다. 최소 수정과 전체 흐름 검토를 함께 한다. | 소설 서사 구조 수리, 작성 모델 추정·분류, 특정 작가 목소리 주입은 이번 범위에 넣지 않는다. |

한국어 세부 검토에는 다음 소스도 읽었다.

1. [im-not-ai quick-rules.md](https://github.com/epoko77-ai/im-not-ai/blob/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7/skills/humanize-korean/references/quick-rules.md)
2. [im-not-ai rewriting-playbook.md](https://github.com/epoko77-ai/im-not-ai/blob/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7/skills/humanize-korean/references/rewriting-playbook.md)

원문보다 구체적인 내용을 만들어 내지 않고, 의미를 가진 반복과 문장 구조를 보존한다는 기준을 우선했다. 상류 문서의 통계나 탐지 성능 주장은 이 스킬의 성능 근거로 사용하지 않는다.

