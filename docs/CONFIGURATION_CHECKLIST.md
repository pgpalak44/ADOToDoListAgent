# Configuration checklist

Before the first run, confirm these with your ADO administrator/team:

- [ ] Organization URL and exact project name.
- [ ] Whether the digest should include only one project or all projects.
- [ ] Exact user identity associated with the PAT; `@Me` is recommended where possible.
- [ ] Which work-item states count as active (update `ADO_EXCLUDED_STATES`).
- [ ] Which field is authoritative for due dates: Due Date, Target Date, or a custom field.
- [ ] Whether Bug Severity uses 1 as highest severity.
- [ ] Whether Priority uses 1 as highest priority.
- [ ] Whether severity should outrank priority, or vice versa.
- [ ] Whether older created items should outrank newer items when earlier criteria tie.
- [ ] Approved Claude Code / Anthropic provider usage for project data.
- [ ] Approved SMTP sender and recipient.
- [ ] Where the scheduled process will run reliably at 8:00 AM.

## Ranking customization

Edit `src/ranker.py`. The default sort order is severity -> priority -> due date -> created date. If your process treats priority as more important than severity, swap those two keys. If your project uses custom fields, add their reference names to the `fields` list and map them in `src/ado_client.py`.
