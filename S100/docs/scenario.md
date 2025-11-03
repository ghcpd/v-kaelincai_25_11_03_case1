# Smart Permission Aggregation Feature

## Overview
The new feature evaluates the effective permissions for a support engineer in a complex enterprise system. It merges **direct user grants**, **group-based privileges**, and **role-based templates** while honoring explicit denials and global constraints.

## Input contract
The evaluator consumes a JSON/Python dictionary with the following shape:

```json
{
  "user": {
    "id": "user-123",
    "direct": {
      "allow": ["read:docs"],
      "deny": ["delete:docs"]
    },
    "groups": [
      {
        "name": "docs-team",
        "allow": ["read:docs", "comment:docs"],
        "deny": []
      }
    ],
    "roles": [
      {
        "name": "admin-lite",
        "allow": ["read:docs", "edit:docs"],
        "deny": ["delete:docs"]
      }
    ]
  },
  "constraints": {
    "environment": "prod",
    "lockdown": false,
    "suspended_actions": ["share:docs"]
  }
}
```

- All allow/deny collections accept either strings or nested objects with a `name` field. Improper types must trigger a validation error.
- Missing optional sections (e.g., groups) are treated as empty; missing required sections raise a descriptive error.

## Expected Output
The evaluator returns a dictionary containing:

```json
{
  "allowed": ["read:docs", "comment:docs", ...],
  "denied": ["delete:docs", ...],
  "decision_map": {
    "read:docs": {"status": "allow", "source": "direct"},
    "delete:docs": {"status": "deny", "source": "role"}
  },
  "metadata": {
    "lockdown_active": false,
    "coverage": {
      "tested_cases": 5,
      "edge_cases": 2
    }
  }
}
```

- Deny decisions take precedence over allow decisions.
- Suspended actions from constraints must appear in the denied set with source `constraint`.
- The metadata section captures evaluation stats that the automated tests can aggregate into accuracy, coverage, and edge-case success metrics.

## Test categories
1. **Baseline functionality** – verifies correct aggregation of mixed direct, group, and role grants.
2. **Conflict resolution** – ensures denials override allows even when they come from different scopes.
3. **Scalability** – assesses performance on hundreds of nested grants and validates measured execution time.
4. **Malformed payloads** – confirms graceful handling of missing or mistyped sections.
5. **Stress + constraint handling** – tests suspended actions and non-string grant descriptors.

## Optimization targets
- Reduce redundant traversals by normalizing inputs once and using set arithmetic.
- Cache role templates and group lookups to avoid repeated scans for identical entries.
- Produce structured metrics (execution time, per-case accuracy) without re-evaluating decisions for every aggregation stage.
