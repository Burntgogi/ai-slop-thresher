# 참고 자료와 반영 범위

2026년 9월 12일 확인. 이 문서는 AI Slop 탈곡기의 설계와 화면 구성에 참고한 프로젝트를 기록합니다.

편집 지침과 한국어 예문은 이 프로젝트의 요구에 맞춰 새로 작성했습니다. 아래 표에는 판단 기준이나 구성을 참고한 범위를 적었습니다. 원본 저장소의 소스 파일, 실행 코드와 배너 원본 파일은 배포 ZIP에 포함하지 않았습니다.

## 윤문 기준

| 참고 저장소와 읽은 소스 | 이 프로젝트에 반영한 내용 | 해당 리비전의 LICENSE |
| --- | --- | --- |
| [blader/humanizer](https://github.com/blader/humanizer/blob/9862685f575c65a8247f90369951df1b3416e3d6/SKILL.md) | 반복되는 도입·결말과 문단 구조를 검토하고, 수정 후 사실을 다시 대조합니다. | [MIT](https://github.com/blader/humanizer/blob/9862685f575c65a8247f90369951df1b3416e3d6/LICENSE) |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh/blob/91f3d394db8419c20d67ebe22a96cf8fee0a404b/SKILL.md) | 영어권 패턴을 그대로 옮기지 않고 대상 언어의 번역투와 서식 문제로 다시 살핍니다. | [MIT](https://github.com/op7418/Humanizer-zh/blob/91f3d394db8419c20d67ebe22a96cf8fee0a404b/LICENSE) |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop/blob/8da1f030185bdfe8471220585162991eaeb970e9/SKILL.md) | 본론 전 예고, 불필요한 대구, 내용 없는 결론과 장식 대시를 줄입니다. | [MIT](https://github.com/hardikpandya/stop-slop/blob/8da1f030185bdfe8471220585162991eaeb970e9/LICENSE) |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing/blob/e7faf81f2c9353bd5e5c6ad6ce82f513bb89ee3e/SKILL.md) | 없는 경험과 사실을 보태지 않고, 진단과 윤문을 구별한 뒤 결과를 다시 읽습니다. | [MIT](https://github.com/conorbronsdon/avoid-ai-writing/blob/e7faf81f2c9353bd5e5c6ad6ce82f513bb89ee3e/LICENSE) |
| [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai/blob/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7/codex/skills/humanize-korean/SKILL.md) | 한국어 조사·연결어미, 명사형·피동, 격식과 직접 인용을 기준으로 국소 편집합니다. | [MIT](https://github.com/epoko77-ai/im-not-ai/blob/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7/LICENSE) |
| [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer/blob/94b88b23703bed7df507acae7d6d5876209a0cdf/SKILL.md) | 수치·인용, 조건·표본 범위와 유보 표현을 보존하고 학술 문체를 유지합니다. | [MIT 표기, 비표준 본문](https://github.com/AIScientists-Dev/academic-humanizer/blob/94b88b23703bed7df507acae7d6d5876209a0cdf/LICENSE) |
| [Nanako0129/sepia](https://github.com/Nanako0129/sepia/blob/abddddb545ad791fc39d65331080bd0e1422c1d1/skills/sepia/SKILL.md) | 장르와 독자에 맞춰 원문의 목소리를 보존하고, 최소 수정과 전체 흐름 검토를 함께 합니다. | [MIT](https://github.com/Nanako0129/sepia/blob/abddddb545ad791fc39d65331080bd0e1422c1d1/LICENSE) |

## 화면과 문서 구성

| 참고 저장소와 읽은 소스 | 이 프로젝트에 반영한 내용 | 해당 리비전의 LICENSE |
| --- | --- | --- |
| [Burntgogi/Gpt_Codex_HWP](https://github.com/Burntgogi/Gpt_Codex_HWP/blob/ec55c59bfbe1cab9d98a800ac8c95de890747aea/README.md) | 전체 폭 배너, 가운데 정렬 제목, 바로가기와 결과 예시·설치 안내의 배치를 참고했습니다. | [Apache-2.0](https://github.com/Burntgogi/Gpt_Codex_HWP/blob/ec55c59bfbe1cab9d98a800ac8c95de890747aea/LICENSE) |
| [Burntgogi/codex_oracle](https://github.com/Burntgogi/codex_oracle/blob/aedbbb13f434c7722555bd485f0398d2a9f91a05/README.md) | 가운데 정렬 소개, Shields.io 배지의 색상·배치, 한국어·영어 전환, 첫 호출 예시와 릴리즈 문서 구성을 참고했습니다. | [MIT](https://github.com/Burntgogi/codex_oracle/blob/aedbbb13f434c7722555bd485f0398d2a9f91a05/LICENSE) |

배지 이미지는 [Shields.io의 정적 배지](https://shields.io/badges/static-badge)를 사용합니다. `codex_oracle`의 README에 적힌 이미지 주소와 같은 `flat` 형식과 색상을 적용하고, 표시 값과 링크는 이 프로젝트의 공개 상태에 맞췄습니다. 외부 서비스에서 제공하는 배지 이미지를 연결하며 해당 서비스의 코드를 배포하지 않습니다.

`codex_oracle`의 감사 항목은 [steipete/oracle](https://github.com/steipete/oracle)을 작업 맥락을 선별해 다른 모델에 검토받는 흐름의 참고 출처로 소개합니다. 해당 설명만으로 배지 디자인도 그 저장소에서 왔다고 확인할 수 없어, 이 프로젝트의 배지 출처는 직접 확인한 `codex_oracle` README와 Shields.io 문서로 기록합니다.

한국어 세부 편집에는 im-not-ai의 [quick-rules.md](https://github.com/epoko77-ai/im-not-ai/blob/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7/skills/humanize-korean/references/quick-rules.md)와 [rewriting-playbook.md](https://github.com/epoko77-ai/im-not-ai/blob/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7/skills/humanize-korean/references/rewriting-playbook.md)도 참고했습니다.

릴리즈 문서 구성에는 [Gpt_Codex_HWP v0.2.5 릴리즈](https://github.com/Burntgogi/Gpt_Codex_HWP/releases/tag/v0.2.5)와 [codex_oracle 릴리즈 노트](https://github.com/Burntgogi/codex_oracle/blob/aedbbb13f434c7722555bd485f0398d2a9f91a05/RELEASE_NOTES.md)를 참고했습니다. 사용자가 제공한 두 배너의 흰 고양이, 파란색 계열과 픽셀 아트 구성을 참고해 새 타이틀 이미지를 생성했습니다.

## 읽을 때 유의할 점

academic-humanizer의 LICENSE는 MIT라는 제목을 사용하지만 표준 MIT의 보증 부인·책임 제한 문구 일부가 생략되어 있습니다. 최초 조사 당시 GitHub 메타데이터는 NOASSERTION으로 기록됐습니다. 이번에는 같은 고정 리비전의 실제 파일을 읽고 MIT 표기, 비표준 본문으로 구분했습니다. 원문 파일은 위 링크에서 확인할 수 있습니다.

출처 표시는 참고 경로를 설명하며 원본 프로젝트의 보증이나 추천을 뜻하지 않습니다. 원본의 실제 코드, 문구나 자산을 복제·수정해 배포할 경우에는 해당 부분에 적용되는 저작권·라이선스 고지와 배포 조건을 별도로 따라야 합니다. 단순한 링크가 그 고지를 대신하지는 않습니다.

이 프로젝트 자체는 Apache-2.0으로 배포하며 전체 조건은 [LICENSE](LICENSE)에, 저작권 고지는 [NOTICE](NOTICE)에 있습니다. 표에 적힌 라이선스는 각 참고 저장소에서 확인한 내용이며 이 프로젝트의 라이선스로 다시 부여한 것이 아닙니다.
