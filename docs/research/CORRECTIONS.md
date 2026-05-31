## 2026‑05‑22 – Secret `.env` removal
- The file `deploy/infra/.env` contained trivial test passwords (`REDIS_PASSWORD=omega`, `POSTGRES_PASSWORD=omega`).
- It was committed in the founding commit (`d848aae`).
- The file has now been **deleted from the working tree** and is ignored via `.gitignore`.
- For full remediation the repository history should be rewritten (e.g. `git filter-repo --path deploy/infra/.env --invert-paths`).
- A reminder has been added to `HANDOFF_OPENCODE.md` with the exact `git filter-repo` command for future maintainers.
