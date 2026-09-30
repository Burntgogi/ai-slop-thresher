# Dot cloud VM 감수 원문

출처: Dot cloud 하위 감수 에이전트 `01a0f26c-1a4b-74b9-82b5-b19fa8731013`, 완료 turn `01a0f273-3dda-74e5-a6fe-d38b147c35de`. Codex가 read_thread로 받은 실제 최종 응답을 아래에 보존했다. R2 파일 감수이며 R3는 설치 문서의 ZIP 재현성 조건만 교정한다.

R2 review: static_review plus temporary-fixture regression tests

Candidate 1.2.0-unreleased
Manifest: af0ccaa2222069a380b9a48be8d1861a6f9d5b69100a868fbeff1a0dac70ac9d
scripts/distribute.py SHA-256: 28db41a95a73cced1a30294dcd8a41cf19c7404de8058f97e0e1692846248975

Independent integrity verification passed: all 51 packet entries match their UTF-8 byte counts, entry hashes, manifest identities, and materialized files. Recomputed manifest matches exactly.

Environment: Python 3.12.14; Linux 6.18.44 x86_64; glibc 2.41.

1. Previous data-loss defect resolved

Command:
PYTHONDONTWRITEBYTECODE=1 python /workspace/shared/dm-thresh-rollback-probe.py /workspace/shared/dm-thresh-r2

Exit 0. Both publication and restoration rename failures were injected into an isolated temporary copy.

Observed:
- output_exists: false
- remaining_backup_count: 1
- original_backup_retained_byte_identical: true
- frozen_tree_unchanged: true
- Error identifies both failures and the preserved recovery path

The absent output is expected after both renames fail. R2 retains the original backup rather than deleting it. The fixture is removed after measurement; the reported temporary recovery path is evidence, not a persistent user recovery location.

2. Distribution tests passed

Command:
PYTHONDONTWRITEBYTECODE=1 python -O -m unittest discover -s /workspace/shared/dm-thresh-r2/tests -p test_distribution.py -v

Exit 0. Ran 33 tests in 0.119 seconds: 32 passed, one Windows junction test skipped on Linux. All three symlink tests passed.

All four added regressions passed:
- Publication failure restores the original
- Double rename failure preserves backup and blocks retry
- Successful replacement cleans its superseded backup
- Cleanup failure retains the backup and preserves the recovery error

3. Projection and historical guard checked

Commands:
PYTHONDONTWRITEBYTECODE=1 python /workspace/shared/dm-thresh-r2/scripts/distribute.py check
PYTHONDONTWRITEBYTECODE=1 python /workspace/shared/dm-thresh-r2/scripts/distribute.py package

Both exited 0. Projection matched all 10 generated files, references resolved, marketplace path resolved. Packaging used its no-write default.

Historical generator execution returned its expected exit 1 and:
“Historical generator requires the v1.1.0 skill tree; no files written. See docs/verification.md for candidate checks.”

The complete legacy-report test was not run because its three historical baseline files are absent from this selected packet. Do not add this direct guard check to the unittest count.

4. Remaining verified reproducibility limitation

archive_bytes() fixes timestamps and permissions but leaves ZipInfo.create_system at the host default.

Linux package output:
- Portable: 16461 bytes, d81258a30c1ec4a79bdcc1e74e3a582fc8ebd5323849817c9ca146d9d86f0756
- Codex plugin: 17767 bytes, 79c7c27310b0d490a25196c0f2cbc40a9955ef1a1e762e6f14f9b9fb0b96694c

An in-memory reproduction explicitly setting create_system=0 exactly recovered the submitted Windows hashes:
- Portable: 8a1c63859cd67192c08b6672f3efe24ff538d023c1bdebf0e70665b82f44996a
- Codex plugin: d340704d9c75df2ec03271790a57f8f2654bbaa92fb04b05b187318d35e69bb2

This is ZIP metadata variability, not changed source contents. Qualify the documentation’s same-source/same-checksum claim to the same toolchain/environment, or normalize create_system and separately address compression-version variability.

Conclusion: the reported recovery blocker is corrected. No further concrete user-overwrite or recovery blocker was found in the reviewed paths. Cross-platform archive reproducibility remains a documented-claim limitation needing qualification.

These results establish file integrity and tested distribution behavior. They do not establish model quality, actual harness/UI installation, or all 82 model-output records; the selected packet still omits the complete per-round snapshots and intermediate outputs needed for record.py verify.
