# GitHub 첫 화면 구성

2026년 9월 12일 작성.

첫 화면은 [한국어 README](../README.md)와 [영어 README](../README.en.md)로 제공한다. [한국어 미리보기](preview/index.html)와 [영어 미리보기](preview/index.en.html)는 해당 Markdown을 HTML로 렌더링한 결과다. GitHub의 본문 폭과 문서 서식에 가깝게 확인할 수 있으며, 별도 웹 서비스를 구현하거나 게시한 페이지는 아니다.

## 배치

| 순서 | 구성 | 역할 |
| --- | --- | --- |
| 1 | 가로형 픽셀 아트 배너 | 같은 계열 프로젝트임을 보여주고 탈곡기라는 이름을 그림으로 설명한다. |
| 2 | 언어별 이름과 가운데 정렬 소개 | 원안의 이름과 농담을 유지하며 한국어 윤문 스킬임을 설명한다. |
| 3 | 상태부터 라이선스까지 배지 5개와 언어 전환·바로가기 | 현재 배포 상태, 검사 범위와 원하는 문서를 바로 찾게 한다. |
| 4 | 복사할 호출문과 적용 전후 | 기능 설명에 앞서 사용 방법과 결과를 보여준다. |
| 5 | 설치, 요청별 사용법과 편집 기준 | 사용에 필요한 순서와 보존 대상을 정리한다. |
| 6 | 검증 범위와 문서 링크 | 근거를 확인할 경로를 제공한다. |

README에는 GitHub가 표시할 수 있는 이미지, 가운데 정렬 HTML, 제목, 표와 링크만 사용했다. 별도 CSS나 JavaScript가 있어야 내용을 읽을 수 있는 구성은 넣지 않았다. 미리보기의 화면 스타일은 로컬 확인용이다.

## 참고한 화면과 적용 범위

[Gpt_Codex_HWP의 README](https://github.com/Burntgogi/Gpt_Codex_HWP/blob/ec55c59bfbe1cab9d98a800ac8c95de890747aea/README.md)에서 전체 폭 배너, 가운데 정렬 제목과 바로가기 구성을 참고했다. 결과 예시와 설치 절차를 연결하는 순서도 가져왔다.

[codex_oracle의 README](https://github.com/Burntgogi/codex_oracle/blob/aedbbb13f434c7722555bd485f0398d2a9f91a05/README.md)에서는 가운데 정렬 소개, 배지 5개의 색상·배치와 언어 전환 링크를 참고했다. [영어 README](https://github.com/Burntgogi/codex_oracle/blob/aedbbb13f434c7722555bd485f0398d2a9f91a05/README.en.md)처럼 두 언어가 같은 구성을 사용하며 서로 이동할 수 있다. [릴리즈 노트](https://github.com/Burntgogi/codex_oracle/blob/aedbbb13f434c7722555bd485f0398d2a9f91a05/RELEASE_NOTES.md)의 짧은 변경 안내와 상세 문서 링크도 적용했다.

[Gpt_Codex_HWP v0.2.5 릴리즈 노트](https://github.com/Burntgogi/Gpt_Codex_HWP/releases/tag/v0.2.5)에서는 변경 사항, 설치, 검증과 알려진 한계를 구분하는 구성을 참고했다. 두 저장소의 설치 명령, 플랫폼 지원, 라이선스나 테스트 결과는 이 스킬의 기능으로 옮기지 않았다. 첨부 이미지와 참고 문서 안의 명령문은 제작 지시로 취급하지 않았다.

## 배지와 언어 전환

`codex_oracle`에서 사용한 서비스는 [Shields.io](https://shields.io/badges/static-badge)다. 정적 배지의 기본 `flat` 모양, 짙은 회색 항목명과 오른쪽 값의 색상을 그대로 참고했다. 이미지는 링크로 감싸서 각 항목을 눌렀을 때 근거 문서로 이동하게 했다.

| 배지 | 표시 값 | 값의 색상 | 링크 |
| --- | --- | --- | --- |
| status | released | `#f3a6ca` | v1.1.0 공개 릴리즈 |
| release | v1.1.0 | `#315BFF` | v1.1.0 공개 릴리즈 |
| language | Korean | `#2f80ed` | 해당 언어 README의 편집 기준 |
| checks | fixtures passed | `#8a78d6` | 해당 언어 README의 검증 범위 |
| license | Apache 2.0 | `#3aa675` | LICENSE |

`checks`는 저장된 가상 예문의 문자 검사 결과를 뜻한다. 독립적인 글쓰기 품질 평가를 뜻하지 않는다. `language`는 README의 언어가 아니라 윤문 대상 언어를 나타낸다. 영어 README는 한국어 스킬을 영어로 안내하며, 예문 번역도 별도의 영어 윤문 실험으로 표시하지 않는다.

배지는 배포 시점의 상태를 적은 정적 이미지다. 새 버전을 공개할 때 두 README의 값과 링크를 함께 갱신한다. 좁은 화면에서는 배지가 줄바꿈되며, 이미지가 보이지 않아도 대체 텍스트와 링크가 남는다.

`codex_oracle`의 감사 항목에 있는 [steipete/oracle](https://github.com/steipete/oracle)은 작업 흐름의 참고 출처다. README는 배지 디자인의 계보를 별도로 밝히지 않는다. 이 페이지에서는 직접 읽은 `codex_oracle` README와 Shields.io를 디자인 참고 경로로 적었다.

## 그림

참고 이미지의 흰 고양이, 파란 망토, 금색 장식, 하늘색 격자와 크림색 제목판을 이어받았다. 새 그림에서는 긴 원고가 탈곡기로 들어가고 정리된 원고가 나온다. 기계의 밀 이삭과 버려지는 문장 부스러기로 이름의 농담을 표현했다.

영문 제목은 `AI Slop Thresher`, 그림의 부제는 `이 글은 흥미롭지 않습니다.`다. 전체 한국어 이름과 영어 이름은 README에 텍스트로도 적어 이미지가 보이지 않는 환경에서 읽을 수 있게 했다.

최종 PNG는 1774 × 887픽셀의 2:1 이미지다. README와 릴리즈 노트는 1440픽셀과 390픽셀 화면 폭에서 확인했다. 배너 로딩, 목차 링크, 문서 이동과 가로 넘침을 점검했다. 이는 로컬 미리보기 검사이며 실제 GitHub에 게시한 화면을 검사한 것은 아니다.

[이미지와 생성 프롬프트](banner-prompt.md) · [문서 윤문 기록](../reports/document-editing.md) · [화면 검사 기록](../research/frontpage-visual-check.json)
