# Source: a finding

A finding is an entry in `BUG_FINDINGS.md`, the report `apocalypse-bug-review` writes. `BUG_FINDINGS.md` means `$(git rev-parse --show-toplevel)/BUG_FINDINGS.md`, or the file in the working directory outside a git repository. A finding is always a defect claim.

## Start

Entries are the `### [<id>] <title>` blocks of the report, where `<id>` looks like `a/error-handling/file-operations/failure-reported-as-success`. Read the argument as:

- **Nothing, or `next`:** the first entry in the report. The report lists entries by severity, then likelihood, so this is the most important one left. If the report is missing or has no entries, say so and stop.
- **An ID**, with or without brackets: the entry whose heading carries exactly that ID. If the report is missing or no heading matches, say so and stop.
- **Anything else:** the pasted text of one whole entry. It must contain exactly one entry heading and a `**Location:**` line; otherwise say what is missing and stop. Assess the pasted text. If its ID is still in the report, that entry is the one Finish removes; if not, leave the report alone.

The entry is the claim: its locations, trigger, and evidence are what step 2 reads.

## Ask

- **Confirmed:** fix as planned (recommended), each other reasonable fix, or leave the entry.
- **Not a bug** or **Already fixed:** delete the entry (recommended), or leave it. When the entry was pasted and its ID is not in the report, there is nothing to delete: ask nothing, and go to step 6.
- **Can't confirm:** ask nothing. Leave the entry, say what would settle it, and go to step 6.

## Finish

Leaving the entry changes nothing. Otherwise — the fix held, or the user chose to delete the entry:

- Re-read `BUG_FINDINGS.md`. If the entry is gone or has changed since step 1, or was pasted and its ID is not in the report, leave the file alone and say so.
- Delete the entry's whole block, from its heading up to the next `###` or `##` heading outside a code block, and nothing else. Delete a severity section left with no entries.
- Recalculate `## Summary` from the entries that remain, keeping its layout: counts by severity, counts by confidence, the severity × confidence table, and the likelihood counts. When no entries remain, keep the `# Bug Findings` heading and a Summary of zero counts.

## Report

Add:

- whether the entry was deleted, or why it stayed;
- remaining entries whose locations are in the files you changed, as possibly affected — never delete them;
- the ID of the first entry left in the report other than the one just handled, with the prompt to fix it: `$fix <id>`. When the handled entry stayed, add that `next` would pick it again.
