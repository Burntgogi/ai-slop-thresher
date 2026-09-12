# 이름과 호출명 변경

사용자가 원안 유지를 선택해 다음 이름을 적용했다. 배포 버전은 1.1.0이다.

| 항목 | 이름 |
| --- | --- |
| 한국어 이름과 부제 | AI Slop 탈곡기: 이 글은 흥미롭지 않습니다. |
| 영어 이름과 부제 | AI Slop Thresher: This Text Is Not Interesting. |
| 정식 스킬 이름 | ai-slop-thresher |
| 정식 호출 | $ai-slop-thresher |
| 짧은 호출 | $thresh |
| 이전 이름 | humanizer |

본 스킬의 폴더명, SKILL.md의 name과 표시 이름, UI 기본 요청, 문서 및 배포 ZIP을 변경했다. thresh 폴더는 본 스킬의 SKILL.md를 상대 경로로 읽는 짧은 호출용 스킬이다. 두 폴더는 같은 개인 스킬 폴더에 함께 설치한다. 편집 규칙은 본 스킬에서만 관리한다.

[OpenAI Docs의 Build skills](https://learn.chatgpt.com/docs/build-skills)는 name과 description을 가진 SKILL.md, 명시적 스킬 호출, 별도 UI 메타데이터를 설명한다. 해당 문서에 별도의 호출 alias 필드는 제시되어 있지 않아, 짧은 이름은 실제로 로드할 수 있는 스킬로 구성했다. 로컬 설치 경로는 이 작업에서 이미 등록된 개인 스킬 폴더를 유지한다.

원래 5회 개선 스냅샷과 당시 평가 결과는 역사 기록으로 이름과 버전을 바꾸지 않았다. 핵심 편집 지침이 이전 본문과 동일한지 비교하고 두 스킬의 YAML, 상대 경로, 압축본과 설치본의 파일 일치를 검사한다. 부제는 브랜드 소개용이며 윤문 결과에 자동으로 붙이지 않는다.
