# 실행 비교 도구

릴리즈 사이에 편집 지침을 바꿨을 때 이전 버전과 새 지침을 같은 모델로 실행해 비교한다. 2026년 10월 7일의 [1.2.0·1.2.1 비교](../regression-20261007/README.md)를 다시 쓸 수 있게 일반화했다.

## 실행

```powershell
$env:CODEX_BIN = "C:\path\to\codex.exe"
python -B evaluation/regression/run.py --work ../regression-work --refs v1.2.2 WORKTREE
python -B evaluation/regression/analyze.py --work ../regression-work --refs v1.2.2 WORKTREE --out ../regression-work/results.json
```

`--refs`에는 태그나 커밋을 주며 `WORKTREE`는 현재 `skills/` 폴더를 뜻한다. 작업 폴더는 저장소 밖에 둔다. 기본값은 Codex `gpt-6.1-sol`, 추론 강도 xhigh, 사례당 2회이며 `--model`, `--effort`, `--runs`, `--cases`로 바꾼다. 실행이 중단되면 같은 명령으로 남은 사례만 이어서 실행한다. Codex `exec`는 0.160.1 이상에서 확인했다.

각 버전의 `skills/`만 작업 폴더에 꺼내고 그 SKILL.md만 따르도록 요청한다. 실행 이벤트에 사용자 설치본 스킬 경로가 나오면 analyze.py가 오염으로 표시한다.

## 사례와 판정

고정 사례 20개(`cases.json`, `transfer-cases.json`)와 위험 지점을 겨냥한 [탐침 7개](probes.json)를 쓴다. 판정은 `evaluation/check_results.py`가 맡는다. 고정 사례 파일은 바꾸지 않고 [수치 관계](../number-bindings.json)와 [같은 뜻으로 인정하는 표현](../anchor-alternatives.json)을 별도 파일로 더한다. 탐침은 금지 표현, 필수 표현 묶음, 패턴 최소 횟수, 원문 유사도 하한을 쓴다.

자동 판정은 문자 수준이다. 실패는 모두 직접 읽어 실제 손실인지 표현 차이인지 가려 기록하고, 같은 뜻의 표현이 반복해 걸리면 대안 파일에 더한다. 통과는 문체가 좋다는 뜻이 아니다. 결과는 `evaluation/regression-YYYYMMDD/`에 판정과 함께 남기고, 작업 PC 경로가 든 이벤트 로그는 공개하지 않는다.

2026-10-07 출력 118개를 이 판정기로 다시 판정하면 v1.2.0은 54/54, v1.2.1은 52/54, v1.2.2는 10/10이다. 남는 실패 2건은 실제 퇴보였던 C08의 따옴표 모양 변경이다.
