# v1.1.0 / v1.2.0 A/B 방법·무결성 독립 감사

2026-09-30. 감사자는 출력 생성·판정에 참여하지 않았다. 버전별 결과의 우열과 판정의 내용적 타당성은 이 감사의 대상이 아니다. 원출력·판정·스킬·프로토콜은 수정하지 않았다.

**결론:** 현재 보존된 실행 산출물에서 버전 바뀜, 사례 누락·중복, 페어 출력 바뀜, 잘못된 arm·suite 연결, 해시 불일치를 발견하지 않았다. 최초 집계 코드의 검증 공백은 수정본에서 해결되었다. 이 결론은 기록된 파일들의 일관성에 관한 것으로, 실제 모델 실행과 블라인드 성공을 독립 인증하지 않는다.

## 실제 대상과 계획의 일치

`protocol.md`, 준비·익명화·집계 코드, manifest, receipt, 4개 generator run/outputs, 2개 익명 packet/mapping을 읽었다. 추가 제공된 dispatch와 judge run, 완성된 judgments의 구조·연결, summary/integrity를 검사했다. 입력·추출 스킬·ZIP member는 bytes와 해시 및 구조 대조에 사용했으며 의미 품질을 평가하지 않았다. judgments의 이유 문구나 버전별 성적은 보고하지 않는다.

| arm | 버전 / GitHub annotated tag가 가리키는 commit | 평가한 asset | ZIP SHA-256 |
|---|---|---|---|
| q | v1.1.0 / `3861b63c17426a0935a5928943be655d83362781` | `ai-slop-thresher.zip`, 15,598 bytes | `0ae43505167bd7ba0b5e7cd5bbb96ffc3fd9b8b8e2694e0c2ade7297e46856c5` |
| r | v1.2.0 / `3513a87649eb43005003f1251359592ecb415f26` | `ai-slop-thresher-portable.zip`, 16,461 bytes | `8a1c63859cd67192c08b6672f3efe24ff538d023c1bdebf0e70665b82f44996a` |

감사 시 GitHub 공개 API를 읽기 전용으로 조회했다. 두 릴리즈의 공개·정식 상태, 공개 시각, asset 이름·크기·digest와 annotated tag의 최종 commit이 manifest와 일치했다. v1.2.0 release ID와 commit은 `release-receipt.json`에도 일치했다. receipt에 나열된 나머지 배포물의 로컬 dist 검증까지 이 감사가 다시 수행한 것은 아니다. 근거: [v1.1.0 공개 metadata](https://api.github.com/repos/Burntgogi/ai-slop-thresher/releases/tags/v1.1.0), [v1.2.0 공개 metadata](https://api.github.com/repos/Burntgogi/ai-slop-thresher/releases/tags/v1.2.0), [v1.1.0 tag object](https://api.github.com/repos/Burntgogi/ai-slop-thresher/git/tags/6ef8e17f4698568e3a18be9cf1b835d811876617), [v1.2.0 tag object](https://api.github.com/repos/Burntgogi/ai-slop-thresher/git/tags/aa314ce0a772e596c3169659a33e3194c48b3989).

로컬 ZIP 전체와 모든 manifest member의 크기·해시가 일치했다. 실제 arm의 `SKILL.md`와 `edge-cases.md`는 각각 지정 ZIP member와 byte 단위로 일치했다. 이 실험은 두 파일을 instruction으로 제공한 비교이며 패키지 설치·플러그인 발견·자동 호출의 비교가 아니다.

## 사례·반복·페어링 확인

- 총 28개 고유 사례: development 18개, new 10개. 각 arm이 두 번씩 생성하여 출력 112개, 익명 쌍 56개가 존재한다.
- manifest의 사전 동결 파일 5개 SHA-256이 모두 일치했다. 기록상 prepared 시각은 `14:16:09 UTC`, 첫 generator 시작은 `14:17:01 UTC`이다. 이는 로컬 기록상의 선후관계다.
- 각 반복의 generation input 순서가 manifest와 일치하고, 양 arm의 출력 ID 순서도 해당 generation 순서와 일치했다. 사례의 source/request도 원 입력과 같았다.
- 각 packet에는 고유 pair 28개와 고유 case 28개가 있다. mapping의 case·suite, 서로 다른 q/r 배치, 실제 좌우 문자열이 원출력과 일치했다. mapping의 output 해시 4개도 일치했다.
- `assignment_seed ^ (repetition * 104729)`로 재구성한 익명화 순서·좌우 배치가 실제 mapping과 완전히 일치했다. 좌측 q는 반복 1에서 17/28개, 반복 2에서 10/28개였다. 독립 무작위 배치이므로 각 반복의 균형은 보장하지 않는다. 이 불균형을 오류나 성능 신호로 해석하지 않는다.
- packet 키는 `pair_id`, `case_id`, `request`, `source`, `left`, `right`뿐이다. 버전·생성자 ID·매핑 필드는 없었다. 두 judge run의 rubric/packet 입력 해시는 실제 파일과 같았다.

## 새 문맥과 실행 기록

dispatch는 `/root/ab_q1`, `/root/ab_r1`, `/root/ab_q2`, `/root/ab_r2`, `/root/ab_judge1`, `/root/ab_judge2`를 기록한다. 모든 spawn의 `fork_turns`는 `none`, 모델 override는 없다고 기록되어 있으며, 생성자와 판정자는 서로 다른 agent ID다. generator run의 지정 세 입력 해시는 각 arm·반복과 맞고, `self_edits_after_generation`은 모두 false다. 두 judge run은 `version_mapping_not_provided: true`를 기록한다.

generator 시작 순서는 q1→r1→q2→r2이며 q1·r1·q2는 일부 시간에 겹쳤다. r2는 q2 완료 뒤 시작했다. 반복 1 judge는 해당 출력 두 개의 완료 뒤 시작했고, 반복 2 judge도 해당 두 출력 완료 뒤 시작했다. 완료 시각은 generator run과 judge run에 남아 있다.

dispatch는 주 실행자가 실제 spawn 호출을 옮겨 적은 관측 기록이고, run은 agent 자기보고다. 서버가 서명한 실행 trace, 전체 읽기 로그, 모델 API 응답 기록은 아니다. 따라서 새 문맥·다른 arm 미열람·재시도 없음·출력 무수정·판정자 매핑 미열람을 독립적으로 입증했다고 표현해서는 안 된다. 공유 파일시스템의 allowlist는 지시이며 OS 접근 제한이 아니다. 부모 모델 설정의 상속은 기록되었으나 실제 모델명·temperature·model seed는 제공되지 않았고 추정하지 않는다.

## 최초 코드 결함과 수정본 검증

최초 `aggregate.py`는 dict 변환 전 packet의 고유 pair/case 범위, mapping의 고유 연결·반복·서로 다른 q/r·suite 일치, output 해시 필수 키, generator 입력 해시 필수 키와 agent ID, judge 입력 해시와 agent ID, 릴리즈 ZIP→추출 지침의 byte 연결, evidence/style_reason의 문자열·공백 여부를 충분히 검사하지 않았다. 이 상태에서 `coverage_verified` 같은 포괄적 보증을 쓰는 것은 부적절했다.

주 실행자가 이 검사를 보완한 최종 구현을 다시 읽었다. 감사자는 `write`를 메모리 수집 함수로 바꾸어 원본을 읽기 전용으로 재검증했다. 생성된 summary가 저장된 summary와 같고 unblinded row 수는 56개였다. 현재 integrity의 36개 inventory 해시가 모두 실제 파일과 일치했다. 판정 성적은 출력하지 않았다.

원본을 바꾸지 않는 메모리 복사본에서 다음 10가지 오류를 각각 주입했으며 모두 `RuntimeError`로 거부되었다: 중복 pair, 중복 case, suite 오귀속, 좌우 동일 arm, output 해시 누락, generator 입력 해시 누락, generator ID 오연결, judge 입력 해시 누락, judge ID 오연결, 공백 style_reason. 최초에 확인한 공백은 이 수정본에서 해결되었고 현재 자료에 남은 필수 수정 사항은 발견하지 않았다.

## 반드시 보고할 한계

1. development 18개는 개선에 사용한 사례이고 new 10개도 새 합성 사례다. new를 독립 외부 코퍼스나 외부 검증으로 표현할 수 없다.
2. 각 generator 문맥에 28개 사례가 함께 들어갔다. 사례 간 문맥 영향이 가능하고, 같은 28개를 두 번 생성한 관측은 독립 표본 56개가 아니다. 사람 평가·통계적 유의성·일반화·다른 기반 모델·AI 탐지 성능을 입증하지 않는다.
3. 공통 system/developer 문체 지침과 같은 Codex 하네스가 두 arm에 영향을 줄 수 있다. 정확한 모델 식별자·temperature·model seed를 통제하거나 확인하지 못했다.
4. 주 실행자는 버전 매핑을 알고 있다. 판정자는 매핑을 제공받지 않았다고 기록되었지만, 출력 특징으로 버전을 추측할 가능성과 공유 파일 접근 가능성이 남는다. 블라인드 성공을 시험하지 않았다. 이 감사자도 manifest를 읽었으므로 내용 판정을 추가로 수행하지 않았다.
5. SHA-256은 저장된 파일의 일관성을 확인한다. manifest와 run 자체의 독립 서명·외부 사전등록·생성 시점 원출력 hash 증명은 없다. 최종 `integrity.json`도 명시된 대로 사후 inventory이며 실제 실행과 무수정의 독립 증명이 아니다.
6. 사람의 문체 선호, 제품별 설치 환경, alias·플러그인·UI의 자동 선택 성능은 이 실험 밖에 있다. 감사의 통과를 특정 버전 우세의 근거로 사용해서는 안 된다.

프로토콜은 이러한 주요 한계를 사전에 대부분 명시했다. 평가 결과와 별개로 방법 보고서에서도 같은 범위를 유지해야 한다.
