# 릴리즈 절차

스킬, Codex 플러그인, Claude Code 플러그인은 하나의 버전 번호를 쓴다. 배포 전 후보에는 배포 번호를 붙이지 않고 후보 R1, R2처럼 부른다. 아래 명령은 저장소 루트에서 실행하며 `vX.Y.Z`를 새 태그로 바꾼다.

## 1. 원본과 문서

1. 두 SKILL.md의 `metadata.version`, `integrations/codex/plugin.json`, `integrations/claude-code/plugin.json`의 버전을 함께 올린다. 하나라도 다르면 테스트가 실패한다.
2. 편집 지침 본문을 바꿨다면 이전 태그와 새 지침을 Codex로 실행해 비교한다. [실행 비교 도구](../evaluation/regression/README.md)를 쓰고 결과를 `evaluation/regression-YYYYMMDD/`에 남긴다.
3. `python -B scripts/distribute.py build --apply`로 플러그인 폴더를 다시 만든다.
4. `CHANGELOG.md`에 `## X.Y.Z` 항목, `docs/releases/vX.Y.Z.md`, `RELEASE_NOTES.md`, 두 README의 배지와 다운로드 링크, Codex 설치 명령의 `--ref` 태그를 고친다. `docs/installation.md`의 `--ref`와 현재 배포 번호도 함께 고친다.
5. `node evaluation/build_frontpage.cjs`로 미리보기를 다시 만든다. marked 패키지가 필요하며 저장소 밖의 임시 폴더에 설치해 `NODE_PATH`로 지정해도 된다.

## 2. 검사

```powershell
python -B -m unittest discover -s tests -v
python -B evaluation/run_checks.py
python -B scripts/distribute.py check
claude plugin validate --strict .
claude plugin validate --strict plugins/ai-slop-thresher
python -B scripts/release.py preflight vX.Y.Z
```

`preflight`는 버전, 문서, 미리보기, 플러그인 폴더와 함께 아직 올리지 않은 커밋의 이메일을 확인한다. GitHub은 비공개 이메일로 만든 커밋의 푸시를 거부하므로 이 저장소에서는 `git config user.email 224273819+Burntgogi@users.noreply.github.com`을 쓴다.

## 3. 배포 파일

```powershell
python -B evaluation/package_artifacts.py --output ../release-candidates/vX.Y.Z --apply
python -B scripts/verify_release.py --artifacts ../release-candidates/vX.Y.Z --source .
python -B scripts/release.py body vX.Y.Z --output ../release-candidates/vX.Y.Z/release-body.md
```

Codex 플러그인 ZIP은 공개 디렉터리 제출용이라 Claude 전용 설정을 넣지 않는다. 저장소의 `plugins/ai-slop-thresher/`는 두 호스트가 함께 쓰는 폴더다.

## 4. 공개

푸시, 태그, 릴리즈 작성은 작성자가 직접 실행한다. 릴리즈 브랜치에서 작업했다면 먼저 `main`에 병합한다.

```powershell
git switch main
git merge --ff-only release/X.Y.Z
git push origin main
git tag -a vX.Y.Z -m "AI Slop 탈곡기 vX.Y.Z"
git push origin vX.Y.Z
```

릴리즈 제목은 `AI Slop 탈곡기 vX.Y.Z`, 본문은 `release-body.md`다. ZIP 4개와 `SHA256SUMS`를 첨부하고 `build-report.json`은 첨부하지 않는다.

## 5. 공개 후

```powershell
python -B scripts/release.py verify-published vX.Y.Z --artifacts ../release-candidates/vX.Y.Z
```

공개된 자산의 해시와 본문을 후보 폴더와 대조한다. 설치본을 바꿀 때는 기존 두 스킬 폴더를 스킬 경로 밖에 백업한 뒤 `scripts/distribute.py install --apply`로 설치한다. 실험 입력으로 고정해 둔 사본은 바꾸지 않는다.

Claude Code와 Codex는 마켓플레이스를 추가할 때 저장소 전체를 클론한다. Windows에서 홈 경로가 길어 `Filename too long` 오류가 나면 `git config --global core.longpaths true`를 설정한 뒤 다시 추가한다.
