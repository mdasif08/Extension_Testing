.PHONY: scan clean

scan:
	python3 tools/migration_safety_scan.py db/migrations --evidence-file artifacts/migration-safety-evidence.json

clean:
	rm -rf artifacts migration-safety-evidence.json *.evidence.json
