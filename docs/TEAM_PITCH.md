# Professional team pitch

## Proposed solution: AI-powered Azure DevOps Daily To-Do Assistant

I would like to propose a lightweight AI-assisted daily task-prioritization agent integrated with our Azure DevOps project.

The agent will automatically retrieve all active work items assigned to an individual user—including Tasks, User Stories, Bugs, and other configured work-item types—and generate a consolidated daily to-do list.

It will prioritize the work using the information already available in Azure DevOps, such as bug severity, work-item priority, due or target dates, and creation date. Each item will include its ADO link, a short plain-English summary, and a suggested next action so the user can quickly understand what needs attention.

The agent will then email the prioritized list every day at 8:00 AM, helping team members start the day with a clear view of their most important work.

### Expected benefits
- **Better prioritization:** brings high-severity and high-priority work, upcoming deadlines, and older pending items to the top.
- **Improved visibility:** consolidates assigned work across work-item types into one daily view.
- **Time savings:** reduces the need to manually review multiple ADO boards and queries.
- **Clearer execution:** provides concise summaries and suggested next actions.
- **Consistent routine:** delivers the digest automatically at a fixed time.

### Proposed workflow
1. Connect securely to Azure DevOps using read-only access.
2. Retrieve active items assigned to the user from the selected project.
3. Rank the items using agreed team rules.
4. Use Claude Code to summarize each item without changing its ADO priority.
5. Email the digest at 8:00 AM.
6. Review the ranking during a pilot and refine the rules with team feedback.

### Governance and rollout
The solution will begin with a test project and non-sensitive sample data. Before production use, we will confirm ADO field conventions, PAT/authentication policy, AI data-sharing approval, and the approved email delivery method. The first release will be read-only and will not modify any ADO work items.

### One-line summary
An AI-powered daily assistant that converts assigned Azure DevOps work items into a prioritized, easy-to-understand to-do list and emails it to each user at 8:00 AM.
