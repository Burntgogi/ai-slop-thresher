# Codex 최종 감수 · 2026-09-30 · R3

현재 R3의 고정된 51개 파일 범위에서 미해결 결함을 발견하지 못했다. R2 대비 설치 문서 한 파일만 변경됐음을 직접 확인했다. R1의 P2 복구 결함 수정과 R2 행동 검사 결과는 동일한 구현에 이어 적용한다. 아래 R2 기록을 보존하고 마지막 R3 부록에 현재 후보 ID·변경 대조·승인 범위를 기록했다.

## R2 후보와 검토자 기록

- 후보: `1.2.0-unreleased`, R2
- 기준 커밋: `1ce5dddaff01c4353a71bbaf2abcb03f66dd4965`
- 정확한 후보 ID: `af0ccaa2222069a380b9a48be8d1861a6f9d5b69100a868fbeff1a0dac70ac9d`
- 파일 목록: [review-manifest.json](../evaluation/improvement-20260930/review-manifest.json), 51개
- 검토자: 구현에 참여하지 않은 별도 Codex 감수 에이전트 `/root/codex_review`. 동일 모델 계열의 에이전트 감수이며 독립 인간 평가가 아니다.

`manifest_sha256`는 manifest JSON 파일 자체의 해시가 아니라, `files` 맵을 `sort_keys=True`, `ensure_ascii=False`, `separators=(",", ":")`로 직렬화한 UTF-8 바이트의 SHA-256이다. 이 계산을 직접 반복하고 51개 실제 파일의 길이·SHA-256을 전부 대조했다. 불일치는 없었다. `review-packet.json`의 manifest와 51개 `utf8` 본문도 원본 바이트의 길이·해시와 일치했다.

| 주요 원본 | R2 SHA-256 |
| --- | --- |
| `scripts/distribute.py` | `28db41a95a73cced1a30294dcd8a41cf19c7404de8058f97e0e1692846248975` |
| `tests/test_distribution.py` | `5abb14b9d3c8b9f1a63b0ada9818748b7dd9181092dd5e487b3789a9563001d4` |
| `docs/installation.md` | `f3045bc6e9a43b2bf5c210ce00d660ab8847f18f50c4036f4edfbbf4ccef48c5` |
| canonical `SKILL.md` | `c286b555ef09b6aad44b58885bee1a8f8919ebba9ece34880e8c4f4ce18d7d53` |
| alias `SKILL.md` | `c5e56ff1c821fa8ee3238e5f3b13eea1fc0613844b27f210cbe52654d212c5e9` |

## 발견 사항과 처리

**[P2 · 수정 확인] R1의 이중 rename 실패가 이전 생성물을 삭제했다.** R1 `build_plugin`은 기존 출력을 backup으로 옮긴 뒤 staging 승격과 backup 복원이 모두 실패해도 `finally`에서 backup을 삭제했다. Dot이 발견한 상황을 이 감수자도 임시 경로에서 독립 재현했다. 이전 생성물 11개 파일이 있었지만 실패 뒤 출력도 backup도 남지 않았다. R1 후보 ID는 `904c60b56fe35b1a86ea91e714a4f96ca85eff1e9795ea19179930a4f96d9475`였다.

R2에 같은 두 rename 실패를 주입했다. 출력은 비어 있었으나 backup 1개가 남았고 11개 파일은 실패 전과 바이트 단위로 같았다. 오류에는 보존 경로가 표시됐으며 staging은 정리됐다. 추가 build는 backup을 변경하지 않고 중단했다. 주입을 해제하고 backup을 원래 출력으로 명시적으로 복원한 뒤에는 build가 성공했다. 복원 성공·이중 실패·성공한 교체·추가 cleanup 실패에 관한 네 회귀 사례도 통과했다. [후속 복구 기록](../evaluation/improvement-20260930/post-review-recovery.json)의 결과와 직접 재현이 일치한다.

현재 R2에서 추가 P1·P2·P3 결함이나 명확한 주장·증거 불일치는 발견하지 못했다. R1 예비 검사에서 관측했던 stale projection과 `SHA256SUMS`의 CRLF 검사 실패도 현재 후보에서는 재현되지 않는다.

## R2에서 실제 실행한 검사

작업 디렉터리는 `H:/work2/Dot_Muse/workspaces/ai-slop-thresher`였다. 보고서 외 구현 파일을 쓰거나 사용자 하네스에 설치하지 않았다.

| 검사 | 종료 코드 | 직접 관측한 결과 |
| --- | --- | --- |
| 독립 manifest·packet 해시 검사, `python -B -` | 0 | 51개 파일·51개 패킷 본문 일치 |
| `python -B -O -m unittest discover -s tests -v` | 0 | 34개 중 31 통과, 3 건너뜀, 실패 0 |
| `python -B scripts/distribute.py check` | 0 | 생성 projection 10개 파일이 원본과 일치, 상대 참조·marketplace 경로 해결 |
| `python -B evaluation/improvement-20260930/record.py verify` | 0 | 5회 기록, 매회 16건의 완결성과 입력·출력·검토 해시 연결 확인 |
| `git diff --check` | 0 | 출력 없음 |
| 독립 이중 rename 실패·재시도·명시적 복원 검사, `python -B -` | 0 | backup 보존과 복원 후 build 확인; 모든 쓰기는 임시 경로 |
| `python -B -O evaluation/package_artifacts.py`, 임시 저장소 복사본 | 0 | ZIP 4개 생성, portable·Codex ZIP은 현재 원본과 현재 dist의 바이트에 일치; workbench 주요 원본·두 README 포함 및 ZIP·SHA-256 검사 통과 |

세 건너뜀은 destination ancestor symlink, dangling skill symlink, source symlink 생성 권한을 이 Windows 환경에서 확보하지 못한 경우다. Windows junction 거부 테스트는 실제 실행해 통과했다. 따라서 symlink 세 경우의 행동 검증을 통과했다고 기록하지 않는다.

## 검토 범위와 판정의 한계

canonical·alias 지침과 references, 배포·설치 스크립트, 테스트, Codex 메타데이터·생성 projection·marketplace, 양언어 README와 설치·검증 안내, 호환 packager 및 역사 보고서 보호, 새 평가 protocol·선정된 증거를 읽었다. 하네스 경로·호환 manifest·marketplace 설명은 [OpenAI 공식 패키징 안내](https://developers.openai.com/plugins/build/plugins), [Claude Code 스킬 안내](https://code.claude.com/docs/en/skills), [OpenCode 안내](https://opencode.ai/docs/skills/), [Cursor 안내](https://prod.cursor.com/docs/skills)와 대조했다. 문서 대조는 실제 제품 UI에서의 설치나 활성화를 뜻하지 않는다.

저장된 최종 16개 출력과 B01/B02를 원문·요청과 직접 대조했다. 명제, 수치의 귀속, 정정·책임, 조건·의무, 저자의 평가, 인용과 진단·비교 요청에서 명확한 의미 누락이나 모드 위반을 발견하지 못했다. 특히 N09의 모호한 핵심 배제, B01의 `7일 이내에만`, B02의 미수정 오류와 공개 전 수정 의무가 남아 있다. 이는 이 감수자의 사례별 판단이며 새 모델 실행이나 객관적 문체 점수가 아니다. R2의 윤문 지침과 출력 해시는 R1에서 유지됐다.

`record.py verify`는 기록의 해시·연결·누락을 검사한다. 원출력의 실제 생성 과정을 독립 인증하거나 의미·자연스러움을 자동 증명하지 않는다. 같은 에이전트·대화의 재사용, 합성 사례, 케이스 간 맥락, 알려진 입력의 반복, 구체적 모델·샘플링 정보 부재를 protocol이 명시한다. 기존 버전과의 paired 실행, 홀드아웃, 인간 평가, 다른 모델의 일반화 검증을 수행했다는 주장은 하지 않는다. 회차 4와 5의 출력 해시가 같은 것은 기록된 사실이며 품질 향상 근거로 사용하지 않는다. 과거 제작 보고서·문자 검사 결과도 이번 후보의 새 품질 증거로 취급하지 않았다.

검증 환경은 Windows의 Python 3.13.5였다. Python 3.10 및 다른 운영체제에서 실제 실행한 호환성 보증은 아니다. 실제 Codex·Claude Code·OpenCode·Cursor UI 설치, 자동 스킬 선택, 원격 VM 동기화, 악의적인 동시 경로 변경은 검사하지 않았다. 복구 실패는 임시 경로에서 예외를 주입한 시험이다.

## R2에서 적용한 승인 범위

고정된 R2 51개 파일 범위에서는 추가 수정 요구 없이 감수 통과로 판단한다. 이후 추가되는 Dot·Muse 최종 응답, 종합 개선 보고서와 최종 workbench ZIP은 manifest 밖이며 이 판정의 검토 대상이 아니다. 배포 전에 README·검증 안내가 링크하는 종합 보고서를 실제로 추가하고, 최종 자료를 포함한 workbench와 체크섬을 재생성·검사하는 작업은 별도로 남아 있다. 이 감수는 커밋·푸시·공개·사용자 설치에 대한 실행 승인이나 완료 기록이 아니다.

보고서 작성 후 R2 manifest의 51개 파일 길이·SHA-256과 후보 ID를 다시 확인했다. 고정 파일 변경은 없었다.
## R3 부록 · 최종 현재 후보

현재 후보는 `1.2.0-unreleased` R3이며 정확한 후보 ID는 `b65968890cd7abfd03872b78b89765892727d0bd478d7ae5c19e49cc10d3de2c`다. 현재 [review-manifest.json](../evaluation/improvement-20260930/review-manifest.json)의 `files` 맵 직렬화 해시를 독립 재계산했고, 51개 실제 파일의 길이·SHA-256과 패킷의 51개 UTF-8 본문을 직접 확인했다. 모두 일치했다. 이전 R2는 [review-manifest-r2.json](../evaluation/improvement-20260930/review-manifest-r2.json)과 `review-packet-r2.json`에 보존돼 있다.

두 manifest의 파일명 집합은 같고, 길이·해시가 바뀐 파일은 `docs/installation.md` 하나뿐이었다. R3의 이 파일 SHA-256은 `3eebebd153aef997eaa37d18283375305ef64637b40a01b19c4c698cc549a792`다. 패킷의 R2 원문과 현재 문서를 대조한 결과 ZIP 설명 한 문단에 동일 체크섬의 조건과 환경 차이에 따른 변동 한계만 추가됐다. 구현, 테스트, 윤문 지침, 출력과 나머지 50개 파일은 R2와 동일하다.

**[P3 · 문서 교정 확인] ZIP 재현성의 환경 조건.** 타임스탬프 고정만으로 운영체제·Python·압축 라이브러리 버전을 넘는 ZIP 해시 일치를 보장하지 않는다. 현재 안내는 같은 원본과 같은 환경에서의 재현성을 설명하고, 운영체제별 메타데이터나 압축 라이브러리 버전이 달라지면 내부 파일이 같아도 ZIP 체크섬이 달라질 수 있음을 명시한다. 이 감수자는 Windows에서 같은 payload·타임스탬프·압축 조건의 메모리 ZIP 두 개를 만들고 `ZipInfo.create_system`을 0과 3으로 달리했을 때 member 바이트는 같지만 ZIP 해시가 달라지는 것을 직접 확인했다. 이 probe는 `python -B -`, 종료 코드 0이며 파일 쓰기나 Linux 실행을 수행하지 않았다. 본문 조건과 현재 구현 사이에 명확한 불일치는 없다.

R3에서 full suite, 실패 주입 복구, 전체 패키징을 새로 반복하지 않았다. 이 실행들이 검사한 구현·테스트의 해시가 R2와 동일하므로 위 R2의 34개 중 31 통과·3 건너뜀 및 복구·패키징 결과를 동일 구현에 이어 적용한다. R3에서 새로 실행한 것은 manifest·packet·변경 파일 대조와 메모리 ZIP 메타데이터 probe, `git diff --check`이며 모두 종료 코드 0이다. R2 결과를 R3에서 새로 실행한 테스트로 표시하지 않는다. 다른 감수자가 보고한 Linux 테스트는 이 감수자의 직접 실행 결과에 합산하지 않는다.

R3의 고정된 51개 파일 범위는 추가 수정 요구 없이 감수 통과로 판단한다. 이후 추가되는 삼자 응답, 종합 보고서와 최종 workbench ZIP은 계속 이 고정 감수 범위 밖이다. 실제 하네스 UI 설치·자동 선택·원격 동기화, 새로운 윤문 생성, 인간 평가와 모델 간 품질 일반화에 관한 검증 범위도 확대되지 않았다.

R3 부록 작성 후 현재 manifest의 후보 ID와 51개 파일의 길이·SHA-256을 다시 확인했다. 고정 파일 변경은 없었다. 이 감수자가 변경한 저장소 파일은 본 보고서 하나다.
