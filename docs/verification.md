# 재검증 방법

스킬 사용에는 Python이 필요하지 않습니다. 아래 명령은 제작 자료의 저장된 출력과 배포 파일을 확인할 때 사용합니다.

저장소 또는 전체 제작 자료 ZIP의 압축을 푼 폴더에서 Python 3으로 실행하세요.

```powershell
python evaluation/run_checks.py
python evaluation/improvement-20260930/record.py verify
python -m unittest discover -s tests -v
python evaluation/package_artifacts.py
```

첫 명령은 과거 제작의 5회 개선 과정과 추가 예문의 문자 검사를 다시 실행합니다. 두 번째는 2026-09-30 후보의 다섯 회차 입력·출력·검토 기록의 해시와 완결성을 확인합니다. 세 번째는 임시 디렉터리 설치·패키징과 역사 자료 보호를 검사합니다. 마지막은 현재 후보의 portable·Codex 플러그인·전체 자료 ZIP을 재생성하고 소스와 바이트 단위로 대조합니다.

`evaluation/build_report.py`는 v1.1.0 당시 보고서 생성기입니다. 현재 후보에서 실행하면 과거 버전으로 잘못 표시되는 것을 막기 위해 파일을 쓰기 전에 중단합니다. 과거 보고서와 평가 원본을 현재 후보의 결과로 다시 쓰지 않습니다.

이 명령들은 새 윤문을 생성하지 않습니다. 새로운 글을 평가하려면 원문과 스킬 지침으로 수정문을 만든 뒤 의미와 문체를 별도로 비교해야 합니다.

현재 후보의 프로토콜과 한계는 [새 개선 기록](../evaluation/improvement-20260930/protocol.md), 삼자 감수와 요약은 [이번 보고서](../reports/improvement-20260930.md)에 있습니다. 이전 JSON은 당시 배포 기록이며, 새 배포 검증은 `research/package-validation-current.json`과 `research/bundle-checksum-current.json`을 확인하세요. 설치 방법은 [하네스별 안내](installation.md)에 있습니다.

## 검증 기록

| 기록 | 확인할 수 있는 것 |
| --- | --- |
| [검사 요약](../evaluation/checks/summary.json) | 5회 개선 기록, 추가 예문과 오류 검출용 사례의 검사 결과 |
| [의미 검토](../evaluation/semantic-review.json) | 문맥과 주장 강도에 대한 자체 검토 |
| [스킬 형식 검사](../research/skill-validation.json) | 두 스킬의 형식과 짧은 호출의 참조 경로 |
| [배포 파일 검사와 체크섬](../research/package-validation.json) | 스킬 ZIP과 소스 파일의 일치, 스킬 ZIP의 SHA-256 |

평가 예문과 윤문은 같은 에이전트가 작성했습니다. 문자 검사 통과는 독립적인 품질 평가나 모든 의미의 보존을 보장하지 않습니다.
