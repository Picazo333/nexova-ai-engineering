# Change Verification

## Objective
Determine whether a repository change is ready for commit/PR by executing the validations that apply to the affected scope and returning evidence-backed `PASS`, `FAIL`, or `UNVERIFIED`.

This Skill has one objective only: **verify change readiness**.

## Inputs
- changed files or diff;
- current task/context mode;
- affected app/package/service paths;
- applicable rubric criteria or quality claims;
- available validation commands for the affected surface.

## Workflow
1. Identify the changed claim surfaces from the diff.
2. Map those surfaces to required structural, type/lint, test, build, runtime and rubric checks.
3. Execute every applicable deterministic check that is available.
4. Record command/result evidence and any limitations.
5. Mark affected prior evidence as current, stale, superseded or not affected.
6. Return one final readiness status.

## Output contract
Return:
- `status: PASS | FAIL | UNVERIFIED`;
- affected scope;
- checks executed;
- evidence/results;
- failures or missing verification;
- required repair/re-run steps.

## Acceptance criteria
The Skill passes its own acceptance criteria only when:
1. every changed file is covered by the declared affected scope;
2. every applicable available check is either executed or explicitly marked unavailable with a reason;
3. any failed check produces `FAIL`;
4. any required but unavailable/unexecuted check produces `UNVERIFIED`;
5. `PASS` is returned only when all required applicable checks have successful evidence;
6. the output identifies any evidence made stale by the change;
7. the Skill does not modify unrelated files or broaden task scope.

## Non-goals
- repairing code automatically;
- deciding product architecture;
- replacing rubric evaluation;
- replacing human creative approval.
