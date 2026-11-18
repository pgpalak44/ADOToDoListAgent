import base64
import requests

API_VERSION = "7.1"

class AdoClient:
    def __init__(self, organization: str, project: str, pat: str, assigned_to: str = "", project_filter: bool = True):
        self.organization = organization
        self.project = project
        self.base = f"https://dev.azure.com/{organization}"
        self.session = requests.Session()
        token = base64.b64encode(f":{pat}".encode()).decode()
        self.session.headers.update({"Authorization": f"Basic {token}", "Content-Type": "application/json"})
        self.assigned_to = assigned_to.strip()
        self.project_filter = project_filter

    def _request(self, method, url, **kwargs):
        response = self.session.request(method, url, timeout=45, **kwargs)
        if not response.ok:
            raise RuntimeError(f"Azure DevOps request failed ({response.status_code}): {response.text[:1000]}")
        return response.json() if response.content else {}

    def _base_clause(self):
        project_clause = f"AND [System.TeamProject] = '{self.project.replace(chr(39), chr(39)*2)}'" if self.project_filter else ""
        if self.assigned_to:
            identity = self.assigned_to.replace("'", "''")
            assignee_clause = f"[System.AssignedTo] = '{identity}'"
        else:
            assignee_clause = "[System.AssignedTo] = @Me"
        return f"{assignee_clause} {project_clause}"

    def fetch_items(self, excluded_states=None):
        excluded_states = excluded_states or ["Closed", "Removed", "Done"]
        state_clause = " AND ".join(
            f"[System.State] <> '{s.replace(chr(39), chr(39)*2)}'" for s in excluded_states
        )
        wiql = (
            "SELECT [System.Id] FROM WorkItems WHERE "
            f"{self._base_clause()} "
            f"AND {state_clause} ORDER BY [System.CreatedDate] ASC"
        )
        # Also drop any state ADO classifies as finished (e.g. Test Plan "Inactive",
        # Test Suite "Completed"), whatever the process template calls it.
        categories = self._state_categories()
        return [i for i in self._items_for(wiql)
                if categories.get((i["type"], i["state"])) not in ("Completed", "Removed")]

    def fetch_completed_items(self, days=30):
        """Items assigned to the user in a Completed-category state, changed in the last `days` days."""
        wiql = (
            "SELECT [System.Id] FROM WorkItems WHERE "
            f"{self._base_clause()} "
            f"AND [System.ChangedDate] >= @Today - {int(days)} ORDER BY [System.ChangedDate] DESC"
        )
        categories = self._state_categories()
        if not categories:
            return []
        done = [i for i in self._items_for(wiql) if categories.get((i["type"], i["state"])) == "Completed"]
        return sorted(done, key=lambda i: i.get("closed_date") or i.get("changed_date") or "", reverse=True)

    def _items_for(self, wiql):
        result = self._request(
            "POST", f"{self.base}/{requests.utils.quote(self.project, safe='')}/_apis/wit/wiql",
            params={"api-version": API_VERSION}, json={"query": wiql}
        )
        ids = [x["id"] for x in result.get("workItems", [])]
        if not ids:
            return []
        items = []
        # ADO work-items batch endpoint accepts at most 200 IDs per request.
        fields = [
            "System.Id", "System.WorkItemType", "System.Title", "System.State",
            "System.AssignedTo", "System.CreatedDate", "System.ChangedDate",
            "System.Description", "Microsoft.VSTS.Common.Priority",
            "Microsoft.VSTS.Common.Severity", "Microsoft.VSTS.Scheduling.DueDate",
            "Microsoft.VSTS.Scheduling.TargetDate", "Microsoft.VSTS.Common.AcceptanceCriteria",
            "System.Tags", "System.AreaPath", "System.IterationPath",
            "Microsoft.VSTS.Common.ClosedDate"
        ]
        for start in range(0, len(ids), 200):
            batch = ids[start:start+200]
            data = self._request(
                "GET", f"{self.base}/_apis/wit/workitems",
                params={"ids": ",".join(map(str, batch)), "fields": ",".join(fields),
                        "api-version": API_VERSION}
            )
            for raw in data.get("value", []):
                f = raw.get("fields", {})
                items.append({
                    "id": raw["id"],
                    "url": f"{self.base}/{requests.utils.quote(self.project, safe='')}/_workitems/edit/{raw['id']}",
                    "type": f.get("System.WorkItemType", "Work Item"),
                    "title": f.get("System.Title", "(untitled)"),
                    "state": f.get("System.State", ""),
                    "assigned_to": (f.get("System.AssignedTo") or {}).get("displayName", "") if isinstance(f.get("System.AssignedTo"), dict) else f.get("System.AssignedTo", ""),
                    "created_date": f.get("System.CreatedDate", ""),
                    "changed_date": f.get("System.ChangedDate", ""),
                    "description": f.get("System.Description", ""),
                    "acceptance_criteria": f.get("Microsoft.VSTS.Common.AcceptanceCriteria", ""),
                    "priority": f.get("Microsoft.VSTS.Common.Priority"),
                    "severity": f.get("Microsoft.VSTS.Common.Severity"),
                    "due_date": f.get("Microsoft.VSTS.Scheduling.DueDate") or f.get("Microsoft.VSTS.Scheduling.TargetDate"),
                    "tags": f.get("System.Tags", ""),
                    "area_path": f.get("System.AreaPath", ""),
                    "iteration_path": f.get("System.IterationPath", ""),
                    "closed_date": f.get("Microsoft.VSTS.Common.ClosedDate", "")
                })
        return items

    def _state_categories(self):
        """Return {(work item type, state): category} e.g. ("Test Plan", "Inactive"): "Completed"."""
        if getattr(self, "_categories", None) is not None:
            return self._categories
        try:
            data = self._request(
                "GET", f"{self.base}/{requests.utils.quote(self.project, safe='')}/_apis/wit/workitemtypes",
                params={"api-version": API_VERSION}
            )
        except RuntimeError:
            return {}  # fall back to the WIQL state exclusions only
        self._categories = {
            (t.get("name"), s.get("name")): s.get("category")
            for t in data.get("value", [])
            for s in t.get("states", [])
        }
        return self._categories

    def test_connection(self):
        url = f"{self.base}/{requests.utils.quote(self.project, safe='')}/_apis/wit/fields"
        self._request("GET", url, params={"api-version": API_VERSION})
        return True
