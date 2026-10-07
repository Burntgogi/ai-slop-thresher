# 하네스별 설치와 배포

공통 윤문 지침은 `skills/`에 한 번만 작성한다. 이 디렉터리는 `SKILL.md`와 참고 문서로 구성되며 Codex 메타데이터를 포함하지 않는다. Codex용 표시 이름과 기본 프롬프트는 `integrations/codex/agents/`에서 관리한다. 빌드 스크립트가 두 원본을 합쳐 `plugins/codex/ai-slop-thresher/`를 만든다. 생성된 플러그인 내부 파일을 직접 편집하지 않는다.

```text
skills/                             공통 원본
  ai-slop-thresher/SKILL.md
  ai-slop-thresher/references/
  thresh/SKILL.md                    공통 원본을 읽는 단축 호출
integrations/codex/agents/           Codex 전용 원본
  ai-slop-thresher/openai.yaml
  thresh/openai.yaml
plugins/codex/ai-slop-thresher/       생성된 Codex 플러그인
  .codex-plugin/plugin.json
  skills/
  LICENSE, NOTICE, ATTRIBUTIONS.md
.agents/plugins/marketplace.json     저장소용 Codex 카탈로그
```

Python 3.10 이상이면 설치·빌드 스크립트를 실행할 수 있다. 외부 Python 패키지는 필요하지 않다. 아래 명령은 저장소 루트에서 실행한다.

현재 배포는 v1.2.1이다. 이전 버전과의 전환·복구는 [버전 선택 안내](version-choice.md)를 따른다. 두 버전을 동일한 스킬 경로에 동시에 설치하지 않는다.

## Codex 플러그인

```sh
python scripts/distribute.py build --apply
python scripts/distribute.py check
```

`build`는 공통 원본·Codex 메타데이터·법적 고지를 복사하고 호환 형식 `.codex-plugin/plugin.json`을 만든다. `check`는 생성 파일이 현재 원본과 바이트 단위로 일치하는지, 상대 참조가 해결되는지, 카탈로그 경로가 맞는지 검사한다. 스킬이나 메타데이터를 변경한 뒤에는 다시 빌드한다.

생성물 교체와 기존 생성물 복원에 모두 실패하면 기존 파일은 출력 디렉터리 옆 `.thresher-old-*` 백업에 보존되고 오류에 그 경로가 표시된다. 같은 상위 디렉터리에 이 백업이 남아 있으면 다음 빌드는 중단한다. 스크립트는 백업을 자동으로 선택하거나 삭제하지 않는다. 내용을 확인한 뒤 비어 있는 원래 출력 경로로 복원하거나 별도 안전한 위치로 옮겨 보관한 후 다시 실행한다. 새 생성물 교체가 성공한 경우에만 이전 백업을 정리한다.

이 저장소의 `.agents/plugins/marketplace.json`은 저장소 루트 기준 `./plugins/codex/ai-slop-thresher`를 가리킨다. 저장소 카탈로그를 사용하는 Codex 데스크톱 앱에서는 앱을 다시 시작하고 Plugins Directory에서 **AI Slop 탈곡기 로컬 배포** 소스를 선택해 설치한다. CLI로 카탈로그를 명시적으로 등록하려는 경우 다음 명령을 사용한다.

```sh
codex plugin marketplace add .
```

이 CLI 명령은 카탈로그 등록을 수행한다. 본 저장소의 Python 스크립트는 이를 자동 실행하거나 Codex 설정을 수정하지 않는다. 실제 플러그인 설치·활성화는 사용자가 Plugins Directory에서 수행한다. 플러그인 방식과 아래의 직접 스킬 설치를 함께 사용하면 같은 이름이 중복 표시될 수 있으므로 한 방식을 선택한다.

## Claude Code 플러그인

저장소 루트의 `.claude-plugin/marketplace.json`이 루트 자체를 플러그인으로 가리킨다. Claude Code는 루트의 `skills/`에서 두 공통 스킬을 찾으며 Codex 메타데이터는 읽지 않는다. 별도 빌드 단계가 없으므로 공통 원본을 고치면 그대로 반영된다. Claude Code 안에서 다음 명령으로 설치한다.

```text
/plugin marketplace add Burntgogi/ai-slop-thresher
/plugin install ai-slop-thresher@ai-slop-thresher
```

터미널에서는 `claude plugin marketplace add Burntgogi/ai-slop-thresher`와 `claude plugin install ai-slop-thresher@ai-slop-thresher`를 사용한다. 플러그인 스킬은 `/ai-slop-thresher:thresh`, `/ai-slop-thresher:ai-slop-thresher`처럼 플러그인 이름을 붙여 호출한다. `/thresh`로 짧게 부르려면 플러그인 대신 아래의 `--target claude-code` 직접 설치를 사용한다. 두 방식을 함께 쓰면 같은 스킬이 두 번 표시된다.

플러그인 소스가 저장소 루트이므로 설치 캐시에는 평가 자료와 기존 배포 ZIP을 포함한 저장소 전체(약 8MB)가 복사된다. 실제로 읽는 것은 `skills/`의 두 스킬이다.

`.claude-plugin/plugin.json`의 `version`은 Claude Code가 업데이트 여부를 판단하는 값이다. 스킬의 `metadata.version`을 올릴 때 함께 올리며, 두 값이 다르면 `tests/test_claude_plugin.py`가 실패한다. 매니페스트 형식은 `claude plugin validate --strict .`로 확인한다.

## 직접 스킬 설치

`install`은 두 스킬을 함께 복사한다. 단축 스킬 `thresh`가 이웃한 `ai-slop-thresher/SKILL.md`를 읽으므로 둘을 함께 설치해야 한다. `--target codex`는 Codex 전용 표시 메타데이터 `agents/openai.yaml`도 추가한다. 다른 target은 하네스 중립 공통 파일만 복사한다. 직접 Codex 스킬 설치는 플러그인 manifest나 marketplace를 설치하지 않는다.

| target | 개인 설치 경로 | 프로젝트 설치 경로 |
|---|---|---|
| `codex` | `~/.agents/skills/` | `<project>/.agents/skills/` |
| `claude-code` | `~/.claude/skills/` | `<project>/.claude/skills/` |
| `opencode` | `~/.config/opencode/skills/` | `<project>/.opencode/skills/` |
| `cursor` | `~/.cursor/skills/` | `<project>/.cursor/skills/` |
| `generic` | `--destination`으로 지정 | `--destination`으로 지정 |

모든 설치 명령은 기본적으로 계획만 출력한다. 실제 복사는 `--apply`를 붙인 경우에만 수행한다. `--dry-run`으로 기본 동작을 명시할 수도 있다.

```sh
# 쓰기 없이 개인 설치 위치와 파일 수 확인
python scripts/distribute.py install --target claude-code

# 검토한 뒤 실제 개인 설치
python scripts/distribute.py install --target claude-code --apply

# 프로젝트 설치 계획 확인 후 설치
python scripts/distribute.py install --target opencode --scope project --project /path/to/project
python scripts/distribute.py install --target opencode --scope project --project /path/to/project --apply

# 경로를 직접 지정하는 다른 하네스
python scripts/distribute.py install --target generic --destination /path/to/skills
python scripts/distribute.py install --target generic --destination /path/to/skills --apply
```

`--destination`은 **스킬 폴더 두 개가 들어갈 상위 디렉터리**다. 이를 `--project` 또는 `--scope project`와 함께 지정하면 모호한 경로 선택을 막기 위해 오류를 반환한다. 기존 `ai-slop-thresher`나 `thresh` 폴더가 하나라도 있으면 설치를 시작하지 않는다. 사용자 파일을 덮어쓰는 옵션은 제공하지 않는다. 기존 설치를 교체하려면 내용을 비교하고 백업한 뒤 별도로 정리한다.

원본·목적지·상위 경로의 심볼릭 링크와 Windows junction/reparse point는 거부한다. 소유한 파일을 다른 경로로 우회하여 덮어쓰지 않기 위한 설치기 정책이다. Python 스크립트는 인증, 모델 설정, 하네스 설정, 사용자 홈의 다른 파일을 수정하지 않는다. 다만 `--apply` 설치 중 갑작스러운 프로세스 종료나 파일 시스템 장애가 발생하면 일부 새 파일이 남을 수 있다. 동시 악의적 경로 변경까지 방어하는 샌드박스는 아니다.

호출 방식은 하네스에 따른다. Codex에서는 `$ai-slop-thresher` 또는 `$thresh`, Claude Code·Cursor에서는 `/ai-slop-thresher` 또는 `/thresh`를 사용할 수 있다. OpenCode에서는 요청에 스킬 이름을 적거나 해당 하네스의 스킬 도구로 로드한다. 공통 본문은 특정 접두사를 필수로 요구하지 않는다.

`thresh`는 이름을 직접 부를 때 쓰는 단축 호출이다. Codex에서는 `allow_implicit_invocation: false`로 자동 선택 대상에서 제외했고, 다른 하네스에서는 스킬 설명으로 직접 호출 전용임을 알린다. 이름 없이 윤문을 요청하면 `ai-slop-thresher`가 선택된다. 본 스킬을 읽지 못한 `thresh`는 누락된 경로와 설치 방법을 알리고 윤문을 시작하지 않는다.

Gemini CLI, GitHub Copilot, Amp, Goose와 Windsurf도 개인 스킬 경로 `~/.agents/skills`를 읽는다. 이 경로는 `--target codex`의 설치 위치와 같으므로 Codex와 함께 쓰면 한 번만 설치한다. Codex를 쓰지 않으면 `--target generic --destination ~/.agents/skills`로 Codex 메타데이터 없이 설치할 수 있다. Cursor, OpenCode, Amp와 Goose는 `~/.claude/skills`도 읽으므로 `claude-code`와 다른 target에 모두 설치하면 같은 스킬이 두 번 표시될 수 있다. Copilot과 Cursor는 `/thresh`, Windsurf는 `@thresh`로 부르며 Gemini CLI, Amp와 Goose는 요청에 스킬 이름을 적는다.

개인 설치는 원격 VM으로 자동 배포된다는 의미가 아니다. Claude의 Cowork·cloud 세션은 로컬 개인 스킬을 읽지 않으며, Cursor Cloud Agent는 개인 스킬의 별도 동기화 설정을 요구한다. 각 VM에 프로젝트 스킬을 배치하거나 해당 제품의 동기화·계정 스킬 기능을 따로 사용해야 한다.

## 배포 파일

```sh
python scripts/distribute.py package             # 계획만 출력
python scripts/distribute.py package --output ../portable-candidate --apply  # 새 폴더에 생성
```

| 파일 | 포함 내용 |
|---|---|
| `dist/ai-slop-thresher-portable.zip` | 공통 스킬 2개와 상대 참조 문서, 법적 고지 |
| `dist/ai-slop-thresher-codex-plugin.zip` | 독립 Codex 플러그인, 공통 스킬·참고 문서, Codex 메타데이터, 법적 고지 |
| `dist/ai-slop-thresher.zip` | 기존 다운로드 이름. portable ZIP과 동일한 바이트 |
| `dist/ai-slop-thresher-workbench.zip` | 전체 작업·평가 자료. 아래 호환 패키징 명령으로 생성 |

공개 배포물은 GitHub 릴리즈에서 받는다. 저장소 루트의 기존 `dist/`는 이전 릴리즈 기록이며 현재 소스와의 일치를 뜻하지 않는다. 새 ZIP은 명시한 출력 폴더에 만든다.

portable ZIP은 상위 디렉터리에 두 스킬 폴더가 놓이는 기존 구조를 유지한다. Codex ZIP의 압축 루트는 플러그인 자체이며 `.codex-plugin/`와 `skills/`가 같은 위치에 있다. 두 ZIP 모두 `LICENSE`, `NOTICE`, `ATTRIBUTIONS.md`를 포함한다. ZIP 내부 파일과 원본의 바이트 일치 및 상대 참조를 검사하며 ZIP 타임스탬프를 고정한다. 같은 원본과 같은 운영체제·Python·압축 라이브러리 환경에서 재패키징하면 같은 체크섬을 얻는다. 운영체제별 ZIP 메타데이터나 압축 라이브러리 버전이 다르면 내부 파일이 같아도 ZIP 체크섬은 달라질 수 있다. `package --apply`는 명시한 새 `--output` 폴더에 ZIP을 생성하며 기존 ZIP을 덮어쓰지 않는다. 검사는 [재검증 안내](verification.md)의 읽기 전용 명령으로 수행한다.

기존 평가 흐름에서는 다음 명령을 사용할 수 있다. 이 명령은 배포물 생성이 목적이므로 파일을 쓴다.

```sh
python -B evaluation/package_artifacts.py --output ../release-candidate --apply
python -m unittest discover -s tests -p test_distribution.py -v
```

패키지·경로 검사는 설치 형태와 파일 보존을 확인한다. 모델의 윤문 품질, 하네스의 실제 자동 선택, UI에서의 설치 성공을 증명하지 않는다. 현재 자동 검증은 임시 디렉터리에 한정하며 사용자 하네스에 실제 설치하지 않는다.

## 확인한 공식 문서

경로와 패키지 형식은 2026-09-30에 확인했다. 제품 버전별로 discovery·동기화 동작이 달라질 수 있다.

- [OpenAI: Package your plugin](https://developers.openai.com/plugins/build/plugins) — Codex 호환 manifest, `skills` 경로, 저장소 marketplace 경로 규칙.
- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) — Codex 개인·프로젝트 `.agents/skills` 경로.
- [Claude Code: Extend Claude with skills](https://code.claude.com/docs/en/skills) — 개인·프로젝트 경로와 cloud/Cowork 제한.
- [Claude Code: Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) — `.claude-plugin/marketplace.json`과 상대 경로 `source`. 2026-10-07 확인.
- [Gemini CLI: Agent Skills](https://geminicli.com/docs/cli/skills/), [GitHub Copilot: Add skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills), [Amp: Agent Skills](https://ampcode.com/manual/agent-skills), [Windsurf: Skills](https://docs.windsurf.com/windsurf/cascade/skills), [Goose: Using skills](https://goose-docs.ai/docs/guides/context-engineering/using-skills) — 공통 `~/.agents/skills` 경로와 호출 방식. 2026-10-07 확인.
- [OpenCode: Agent Skills](https://opencode.ai/docs/skills/) — 개인 `.config/opencode/skills`, 프로젝트 `.opencode/skills` 경로와 스킬 도구.
- [Cursor: Agent Skills](https://prod.cursor.com/docs/skills) — 개인·프로젝트 `.cursor/skills`, 호출 방식과 Cloud Agent 동기화.
