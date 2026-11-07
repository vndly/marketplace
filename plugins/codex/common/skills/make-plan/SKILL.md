---
name: make-plan
description: Writes the plan settled in this session to markdown files in the project root — one file, or one file per stage when the work splits into ordered stages that can each be finished and verified on their own. Every file is split into phases of checkbox steps, so progress is ticked off while implementing. Stops and suggests grill-me when something that could be settled now is still open. Use only when the user invokes it by name.
---

Write the plan settled in this session to files in the root of the project.

Write the plan files and nothing else: don't implement the plan, change any other file, edit `.gitignore`, or commit.

## 1. Gather

- The source is this session. Text after the skill name is an optional name or focus for the plan: use it to name the plan or to pick which part of the session to plan. It never changes the rules below.
- The project root is `git rev-parse --show-toplevel`; with no repository, the current folder.
- If the session holds nothing to plan, say so and stop.
- Read the code the plan touches, and the project's `AGENTS.md` / `CLAUDE.md`, so the steps follow its conventions (tests, localization, docs, formatting).
- List the root's existing `plan-*.md` and `stage-*.md` files and read them, only to find interactions. Never change them.

## 2. Check the design is settled

A point is **open** when it could be settled now and a different answer would change the steps, the scope, or the order. A point that depends on a result from an earlier phase (a measurement, a prototype, a go/no-go) is **deferred**, not open.

- If any point is open, write nothing. List each one in plain words with the options and your recommendation, suggest running `grill-me`, and stop.
- Never invent a decision. Every decision in the plan comes from this session or from the code.

## 3. Choose one file or several

- Split into stages only when the work breaks into ordered chunks where each one leaves the project working and can be implemented and verified on its own. Otherwise write one file, however long it is. Size alone is not a reason to split.
- **Nothing depends on anything later.** Inside a file, each phase uses only what earlier phases build. Across files, each stage uses only what earlier stages build. Before writing, list what each phase and stage needs and confirm it exists today or is built earlier. If something points backward, reorder, split, or merge until nothing does.

## 4. Name the files

- One file: `plan-[name].md`. Several: `stage-N-[name].md`, with N counting from 1 in implementation order.
- `[name]` is short lowercase kebab-case: the plan's name for one file, what the stage delivers for several.
- Files go in the project root, never in a subfolder.
- Check every target name before writing any file. If one exists, write nothing, say which exist, and ask the user whether to overwrite, use a different name, or cancel. Never overwrite or merge on your own.
- When `request_user_input` is available, ask with it: put the different name first as the recommended option, append `(Recommended)` to its label, and keep the header to 12 characters or fewer. Do not add an `Other` option; the tool supplies the free-form choice.
- When `request_user_input` is unavailable, ask in one numbered message with the three options and the recommendation, allow a free-form answer, then end the turn and wait.

## 5. Write each file

Each file is read on its own, later, by someone who has not seen this session. Make it complete: no "as discussed", no references to the conversation, every term spelled out. Use plain, everyday words, and keep the real file names, commands, and identifiers the work needs.

Use these sections in this order. Leave out a section marked *if any* when it has nothing.

1. `# [Title]`, then one line: `Tick a box when the step is implemented and verified.` For several files, add a second line: `Stage N of M, after stage-<N-1>-<name>.md, before stage-<N+1>-<name>.md` (leave out the part that does not exist).
2. **Goal and scope**: what exists when this is done and what is included. For a stage file, also one sentence on the whole plan.
3. **Out of scope**: what this plan does not do, including what you noticed but left alone.
4. **Decisions**: the choices settled in this session that shape this file, each with its reason. In a stage file, include every decision that applies to it, even when another stage file repeats it.
5. **Facts checked in the code**: what you read or measured, with the date: sizes, current behavior, constraints. Mark anything not verified as unverified.
6. **What the user sees** *(only for user-facing work)*: a step-by-step walkthrough of the result from the user's side.
7. **Phases**: see below.
8. **Tests**: the tests to add and the checks to run, named precisely (unit, integration, manual, device).
9. **Risks**: what could go wrong, how to notice early, and any unverified assumption.
10. **Interactions with other planned features** *(if any)*: how this plan touches the other plan files found in step 1.
11. **Open decisions** *(if any)*: deferred points only, each with the options, what each costs, and a recommendation.
12. **Done when**: a checklist of testable conditions; the plan is finished only when every box is ticked.
13. **Go/no-go points** *(if any)*: results that would change this plan or a later stage, and what would change.

### Phases

Split every file into phases, each with checkbox substeps:

```markdown
## Phase 1 — [title]

One line: what is true when this phase is done.

- [ ] **Short title.** What changes, where (files), and how it is checked.
- [ ] **Verify.** The exact test, command, or manual check to run before starting the next phase.
```

- Number phases from 1 in each file, in implementation order.
- Every substep gets a checkbox and is small enough to finish and check in one sitting.
- The last box of every phase is its verification.
- Add the docs, localization, or `AGENTS.md` updates the project needs as a step in the phase that makes them necessary.
- Write every box unticked, except a step already done and verified in this session.

## 6. Check and report

- Re-read the files you wrote. Confirm every required section is there, every phase ends with a verification box, nothing refers to the conversation, and nothing depends on anything later. Fix what fails.
- Report the outcome the way the user's instructions define. List the files with their phase counts, and give the reason for splitting into stages when you did. Don't repeat the plan's content.
