# 재검증 방법

스킬 사용에는 Python이 필요하지 않습니다. 아래 명령은 제작 자료의 저장된 출력과 배포 파일을 확인할 때 사용합니다.

저장소 또는 전체 제작 자료 ZIP의 압축을 푼 폴더에서 Python 3으로 실행하세요.

```powershell
python evaluation/run_checks.py
python evaluation/build_report.py
python evaluation/package_artifacts.py
```

첫 명령은 5회 개선 과정과 추가 예문의 문자 검사를 다시 실행합니다. 수치, 보호해야 할 문자열과 필수 내용의 누락 등을 살피며, 고의로 잘못 바꾼 사례 4개를 잡는지도 확인합니다. 두 번째 명령은 저장된 결과로 보고서와 스킬 파일 목록을 만듭니다. 세 번째 명령은 배포 ZIP을 다시 만들고 소스 파일과 바이트 단위로 대조합니다.

이 명령들은 새 윤문을 생성하지 않습니다. 새로운 글을 평가하려면 원문과 스킬 지침으로 수정문을 만든 뒤 의미와 문체를 별도로 비교해야 합니다.

## 검증 기록

| 기록 | 확인할 수 있는 것 |
| --- | --- |
| [검사 요약](../evaluation/checks/summary.json) | 5회 개선 기록, 추가 예문과 오류 검출용 사례의 검사 결과 |
| [의미 검토](../evaluation/semantic-review.json) | 문맥과 주장 강도에 대한 자체 검토 |
| [스킬 형식 검사](../research/skill-validation.json) | 두 스킬의 형식과 짧은 호출의 참조 경로 |
| [배포 파일 검사와 체크섬](../research/package-validation.json) | 스킬 ZIP과 소스 파일의 일치, 스킬 ZIP의 SHA-256 |

평가 예문과 윤문은 같은 에이전트가 작성했습니다. 문자 검사 통과는 독립적인 품질 평가나 모든 의미의 보존을 보장하지 않습니다.
