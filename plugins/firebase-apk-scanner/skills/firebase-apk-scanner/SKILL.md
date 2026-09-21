---
name: firebase-apk-scanner
description: Scan authorized Android APKs for Firebase misconfigurations, including exposed databases, storage, authentication, functions, and Remote Config.
argument-hint: [apk-file-or-directory]
allowed-tools: Bash({baseDir}/scanner.sh:*) Bash(apktool:*) Bash(curl:*) Bash(jq:*) Read Grep Glob
disable-model-invocation: true
---

# Firebase APK Security Scanner

Scan only APKs the user is authorized to test. Do not scan production Firebase
projects without written permission.

## Rationalizations to Reject

- “The database is read-only” — exposed data is still a critical finding.
- “Anonymous auth is not real accounts” — its tokens can bypass `auth != null` rules.
- “The API key is public anyway” — that does not justify open backend rules.
- “There is no sensitive data yet” — insecure rules remain vulnerabilities.
- “It is an internal app” — APKs can be extracted from devices.
- “We will fix it before launch” — document the finding now.

## Workflow

1. Confirm the supplied APK path exists. If the path is empty, ask for it.

   ```bash
   ls -la "APK_PATH"
   ```

2. Run the bundled scanner. It decompiles the APK, extracts Firebase
   configuration, tests discovered endpoints, and writes text and JSON reports.

   ```bash
   {baseDir}/scanner.sh "APK_PATH"
   ```

3. Read the JSON report, not the text report. Extract only the summary,
   status, non-secret configuration locators, and vulnerability identifiers:

   ```bash
   jq '{total_apks, vulnerable_apks, failed_apks, untested_apks,
        total_vulnerabilities,
        results: [.results[] | {apk, status,
          config: (.config // {} | {project_ids, database_urls, storage_buckets, function_names}),
          vulnerabilities}]}' firebase_scan_*/scan_report.json
   ```

4. Report the scan summary, extracted configuration, vulnerabilities, and
   specific remediation. Read [vulnerabilities.md](references/vulnerabilities.md)
   only when explaining a finding or its remediation.

   `failed_apks` and `untested_apks` were not tested. Report both explicitly;
   neither is vulnerable nor clean. A `NO_CONFIG` result means Firebase may be
   absent, or the configuration may be obfuscated or packed beyond extraction.

5. If the scanner is unavailable or fails, read
   [manual-fallback.md](references/manual-fallback.md). Keep tests authorized,
   clean up any created test data, test all discovered projects, and report the
   failure or untested state rather than calling it clean.

## Scope

Use this for Android Firebase assessments: Firebase configuration extraction,
Realtime Database, Firestore, Storage, authentication, Cloud Functions, and
Remote Config. Do not use it for iOS, web targets, or APKs that do not use
Firebase.
