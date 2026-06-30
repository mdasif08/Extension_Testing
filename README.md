# Migration Safety Fixture

This is a neutral sample repository for testing database migration safety checks in local CI and GitHub Actions.

The repository intentionally includes safe and unsafe SQL migration examples so a pipeline can verify that destructive schema changes are detected before release.

## Important

No evidence JSON file is committed in this repository.

The evidence file is generated dynamically only when the scanner runs. Generated evidence is written under `artifacts/`, and that folder is ignored by Git.

## Run locally with PowerShell

```powershell
.\scripts\run-scan.ps1
```

Expected result: the scanner fails because this fixture intentionally includes unsafe migration examples.

Generated file:

```text
artifacts/migration-safety-evidence.json
```

## Clean generated output

```powershell
.\scripts\clean-generated.ps1
```

## Run locally without PowerShell

```bash
python3 tools/migration_safety_scan.py db/migrations --evidence-file artifacts/migration-safety-evidence.json
```

## Included migration examples

| File | Purpose |
|---|---|
| `001_create_initial_schema.sql` | Safe initial schema |
| `002_expand_add_display_name.sql` | Safe additive change |
| `003_migrate_backfill_display_name.sql` | Safe data backfill |
| `004_contract_drop_legacy_status.sql` | Unsafe direct column removal example |
| `005_direct_rename_customer_column.sql` | Unsafe direct rename example |
| `006_direct_drop_audit_events.sql` | Unsafe direct table removal example |

## How CI uses it

The GitHub Actions workflow runs the scanner and uploads the generated evidence file as a build artifact.

Your own release-gating system can consume that generated artifact and map the generic signal to your internal policy decision flow.
