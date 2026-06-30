# How to Test

## 1. Run the failing fixture

```powershell
.\scripts\run-scan.ps1
```

Expected result: scanner exits with code `1` because unsafe migration examples are present.

## 2. Confirm evidence was generated dynamically

```powershell
Test-Path .\artifacts\migration-safety-evidence.json
Get-Content .\artifacts\migration-safety-evidence.json
```

## 3. Test a passing case

```powershell
New-Item -ItemType Directory -Force .\ignored-migrations
Move-Item .\db\migrations\004_contract_drop_legacy_status.sql .\ignored-migrations\
Move-Item .\db\migrations\005_direct_rename_customer_column.sql .\ignored-migrations\
Move-Item .\db\migrations\006_direct_drop_audit_events.sql .\ignored-migrations\
.\scripts\run-scan.ps1
```

Expected result: scanner exits with code `0`.

## 4. Restore failing examples

```powershell
Move-Item .\ignored-migrations\*.sql .\db\migrations\
```

## 5. Clean generated files

```powershell
.\scripts\clean-generated.ps1
```
