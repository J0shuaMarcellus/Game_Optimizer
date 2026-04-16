# Release Checklist

## Before Building

- Close any running `GameOptimizer.exe` windows.
- Open a normal `Command Prompt`, not an elevated admin one, for the build step.
- Confirm the active code changes are the ones you want to ship.
- Check that no secrets, tokens, or machine-specific files were added accidentally.

## Clean Project State

- Keep virtual environments out of source control: `.venv/`, `.venv-build/`, `.venv-win/`
- Keep build artifacts out of source control: `build/`, `dist/`
- Keep local runtime state out of source control: `whitelist.json`, `hardware_config.json`, `error_log.txt`

## Rebuild

Run from the project root:

```cmd
.\.venv-build\Scripts\python.exe build.py
```

## Smoke Test

- Launch `dist\GameOptimizer.exe`
- Confirm the app opens as a desktop window
- Confirm the setup or dashboard loads without `localhost` showing offline
- Confirm the latest UI changes appear
- Confirm process scanning still works
- Confirm setup detection still returns sensible hardware matches

## If Build Fails

- Make sure `dist\GameOptimizer.exe` is not still running
- End leftover `GameOptimizer.exe`, `python.exe`, or `msedgewebview2.exe` processes in Task Manager
- Re-run the build
- If startup fails after build, check `dist\error_log.txt`

## Optional Manual Review

- Check `build\GameOptimizer\warn-GameOptimizer.txt` for suspicious missing modules
- Verify `dist\GameOptimizer.exe` has a fresh timestamp
- If sharing the project, copy only the files that belong in source, not the generated folders
