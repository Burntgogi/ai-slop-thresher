# 재검증 방법

스킬 사용에는 Python이 필요하지 않습니다. 아래 명령은 제작 자료의 저장된 출력과 배포 파일을 확인할 때 사용합니다.

저장소 또는 전체 제작 자료 ZIP의 압축을 푼 폴더에서 Python 3으로 실행하세요.

```powershell
python -B evaluation/run_checks.py
python -B evaluation/improvement-20260930/record.py verify
python -B evaluation/ab-20260930/aggregate.py
python -B scripts/verify_release.py --artifacts dist
python -B scripts/distribute.py check
python -B -m unittest discover -s tests -v
```

앞의 세 명령은 저장된 예문, 개선 기록과 A/B 입력·출력·판정을 읽어 검사하고 결과만 출력합니다. 첫 명령은 보고서에 쓰인 최종 결과 12개도 직접 검사합니다. `evaluation/number-bindings.json`에 지정한 사례에서는 수치가 원래 대상과 순서대로 남았는지 확인하고, 같은 뜻으로 인정하는 표현은 `evaluation/anchor-alternatives.json`에 따로 둡니다. 일부러 망가뜨린 출력 6개와 검사기 회귀 사례 10개가 의도대로 판정되는지 봅니다. 회귀 사례는 윤문 사례의 통과 수에 합산하지 않습니다. 관계 검사는 같은 문장에서 대상어 뒤, 다음 대상어 앞에 수치가 순서대로 있는지만 봅니다. 늘었다·줄었다처럼 동사로 정한 방향, 수치가 대상어 앞에 오는 어순, 목록에 없는 다른 대상에 붙은 수치는 확인하지 못하며 한 문장에서라도 관계가 맞으면 통과합니다. 새 출력에 적용할 때 정상 편집을 실패로 볼 수 있으므로 실패 사유를 직접 읽어 판단합니다. 기록을 다시 쓰거나 새로운 윤문을 생성하지 않습니다. ZIP 검사는 기록된 체크섬과 ZIP 무결성을 확인하며 파일을 쓰지 않습니다. 플러그인 검사는 현재 소스와 생성물의 일치 여부를 확인합니다. 단위 테스트는 임시 디렉터리의 설치·패키징과 실패 대조군, 두 하네스 매니페스트의 버전, README와 미리보기의 링크·앵커와 미리보기가 현재 Markdown으로 만들어졌는지를 검사합니다. 같은 검사가 GitHub Actions에서도 실행됩니다. 지침을 바꾼 릴리즈의 실행 비교는 [실행 비교 도구](../evaluation/regression/README.md), 릴리즈 전후 점검은 [릴리즈 절차](releasing.md)를 따릅니다. Python 캐시 파일 생성을 피하려고 -B를 사용합니다.

현재 소스가 미공개 후보로 바뀌어도 기존 dist의 ZIP은 원래 체크섬으로 검사합니다. 같은 후보 소스와 ZIP의 내부 바이트까지 대조하려면 verify_release.py --artifacts <후보 폴더> --source .를 사용합니다. 이전 릴리즈가 현재 후보와 다르다는 이유로 훼손됐다고 판단하지 않습니다. 체크섬 검사는 출처 인증이나 윤문 품질의 증명이 아닙니다.

## 후보 재빌드

다음 명령은 검사와 별도의 생성 작업입니다. 출력은 소스 밖의 존재하지 않는 새 폴더를 지정합니다. 기본 실행은 계획만 출력하고 --apply에서만 ZIP 4개, SHA256SUMS와 build-report.json을 만듭니다. 기존 소스의 plugins/, research/, dist/는 쓰지 않습니다.

```powershell
python -B evaluation/package_artifacts.py --output ../release-candidates/v1.2.3
python -B evaluation/package_artifacts.py --output ../release-candidates/v1.2.3 --apply
python -B scripts/verify_release.py --artifacts ../release-candidates/v1.2.3 --source .
```

Git 체크아웃에서는 추적된 탈곡기 파일을 포함합니다. 미커밋 새 파일은 자동 포함하지 않고 --include scripts/verify_release.py처럼 소스 상대 경로를 명시합니다. 전체 작업 ZIP에는 포함 목록을 저장해 압축을 푼 자료에서도 Git 없이 재빌드할 수 있습니다. 협업 도구의 코드·DB·로컬 원응답은 탈곡기 배포 범위에 포함하지 않습니다.

단독 portable·Codex ZIP을 생성하는 scripts/distribute.py package --apply도 새 --output 폴더가 필요합니다. 저장된 사례 검사나 A/B 재집계 결과를 파일로 보관할 경우에만 --apply --output <평가 원본 밖의 새 폴더>를 지정합니다. 기존 검사 JSON과 판정은 덮어쓰지 않습니다. 생성물 자체의 갱신은 scripts/distribute.py build --apply로 따로 수행합니다.

`evaluation/build_report.py`는 v1.1.0 당시 보고서 생성기입니다. 현재 후보에서 실행하면 과거 버전으로 잘못 표시되는 것을 막기 위해 파일을 쓰기 전에 중단합니다. 과거 보고서와 평가 원본을 현재 후보의 결과로 다시 쓰지 않습니다.

이 명령들은 새 윤문을 생성하지 않습니다. 새로운 글을 평가하려면 원문과 스킬 지침으로 수정문을 만든 뒤 의미와 문체를 별도로 비교해야 합니다.

v1.2.0 당시 프로토콜과 삼자 감수는 [개선 기록](../evaluation/improvement-20260930/protocol.md)과 [당시 보고서](../reports/improvement-20260930.md)에 있습니다. v1.2.1의 문서 A/B/C와 한계는 [가독성 개선 보고서](../reports/abc-readability-20261001.md)에 기록합니다. 저장소의 기존 research JSON은 당시 배포 기록입니다. 새 후보의 파일 검증은 새 출력 폴더의 SHA256SUMS·build-report.json·readiness-check.json을 확인하세요. 설치 방법은 [하네스별 안내](installation.md)에 있습니다.

## 검증 기록

| 기록 | 확인할 수 있는 것 |
| --- | --- |
| [검사 요약](../evaluation/checks/summary.json) | v1.1.0 당시 기록. 5회 개선 기록, 추가 예문과 오류 검출용 사례의 검사 결과이며 최종 결과 검사와 수치 관계 검사는 run_checks.py 실행 출력에서 확인 |
| [의미 검토](../evaluation/semantic-review.json) | 문맥과 주장 강도에 대한 자체 검토 |
| [스킬 형식 검사](../research/skill-validation.json) | 두 스킬의 형식과 짧은 호출의 참조 경로 |
| [배포 파일 검사와 체크섬](../research/package-validation.json) | 스킬 ZIP과 소스 파일의 일치, 스킬 ZIP의 SHA-256 |

평가 예문과 윤문은 같은 에이전트가 작성했습니다. 문자 검사 통과는 독립적인 품질 평가나 모든 의미의 보존을 보장하지 않습니다.
