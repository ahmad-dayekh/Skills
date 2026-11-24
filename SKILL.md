---
name: mx-pm-guide
description: Writes and checks the plain-English guide for product managers on how the PeopleSoft quality system works (defects, dev plans, fixes, merge requests, version planning, release notes, Jira, APIs, notifications), from the decoded PeopleCode and the read-only database. Use for anything under docs/, and whenever asked to explain PeopleSoft behaviour to non-technical readers.
---

# PM guide to the PeopleSoft quality system

## Goal

Product managers who know neither PeopleSoft nor the functional domain must be able to read, object by object, everything the system does, in plain English, and rely on it.

Priorities, in this order: **accurate**, then **complete**, then **easy to read**. A short page that is right beats a long page with guesses.

## Three layers — keep them separate

| Layer | Where | For | What it is |
|---|---|---|---|
| Map | `.github/skills/mx-pcode-navigator/references/` (catalog, domains, status_values, messages, tables …) | engineers | Existing notes, written **without database access**. Leads to check, not facts. |
| Rules | `docs/rules/<domain>.md` | engineers, reviewers | One entry per business rule, with code location, configuration, data check and confidence. **The source of truth.** |
| Guide | `docs/pm/<domain>.md`, `docs/pm/glossary.md`, `docs/pm/overview.md`, `docs/pm/README.md` | PMs | Plain English, written **only** from the rules files. |

Supporting files: `docs/evidence/<domain>.md` (every query and its result), `docs/evidence/_*.md` (Phase 0 ground truth), `docs/open-questions.md`, `docs/progress.md`.

Rule ID prefixes: API, DEFECT, DEVPLAN, FIX, JIRA, MR, NOTIF, RELEASE, SMART, VPLAN (e.g. `FIX-012`). Query IDs: `Q-<PREFIX>-<rule number>-<letter>` (e.g. `Q-FIX-012-a`); Phase 0 queries use the prefix `GT`.

## Non-negotiable rules

1. **Trace everything.** Every sentence in a guide cites rule IDs. Every rule cites code you opened (file and lines) and, when data can show it, a recorded query. No trace → don't write it.
2. **Re-read the code.** Never copy a claim from the map without opening the code behind it. When the map and the code disagree, the code wins: correct the map and log the correction in `docs/progress.md`.
3. **Describe what the system does, not what it should do.** A bug is documented as behaviour, then listed under Known issues.
4. **Intent only from evidence.** "So that…", "to prevent…" only when a comment, change log or ticket says so; otherwise the rule is Inferred.
5. **Don't fill gaps.** If the code and the data don't settle a point, leave it out of the guide and add it to `docs/open-questions.md` with what you checked.
6. **Keep every condition and exception.** No "usually", "typically", "in most cases" unless a query gives the share.
7. **Files are the memory, not the chat.** Work in batches of at most 10 rules; after each batch, save the files and update `docs/progress.md`. In a new chat, read `docs/progress.md` first.
8. **Database: read-only, no secrets, no personal data** (see Database).

## Phase 0 — once, before any domain

1. **Database access.** Use `DbQuery.java` as set up in `mx-pcode-navigator`. Connection settings come only from environment variables. Check that no credential is in the repository (`git grep -n -i -e password -e "jdbc:"`), then run one test query.
2. **Create** the `docs/` folders, `docs/progress.md` and `docs/open-questions.md`.
3. **Ground truth.** These are mechanical. Write small scripts in `.github/skills/mx-pm-guide/scripts/` that find the references in `DEV\` and query the database, so they can be re-run later. One file each in `docs/evidence/`:
   - `_labels.md` — every field whose codes the code compares or displays (statuses, types, flags): each code, its on-screen label, active or not (`PSXLATITEM`). Then correct `status_values.md`.
   - `_messages.md` — every message number used (`MsgGet`, `MsgGetText`, `MsgGetExplainText`, `MessageBox`, `Error`/`Warning` with a message): catalog text, explain text, severity (`PSMSGCATDEFN`), and the default text in the code when it differs. **Users see the catalog text.** Then correct `messages.md`.
   - `_templates.md` — every email template ID used in code (e.g. `templateId = "120"`): subject, body, active flag, sender type and recipient rows. Read `NOTIFICATION_MX:Notification` and document how recipient codes (RM, PPLS, …) and sender types turn into email addresses. An inactive template means the email is never sent.
   - `_views.md` — every view the code or pages read: its SQL, its filters, and joins that can drop or duplicate rows.
   - `_hardcoded.md` — every hard-coded version ID, product, company, user ID, role, email address, URL or date in the code: what it is (name, type), whether it is still active, when it was last used.
   - `_batches.md` — every batch program (Application Engine): how it starts (button, schedule, another program) and its run history.
   - `_setup.md` — every setup or parameter table the code reads (notification setups, mailing lists, URL definitions): its current rows, summarised.
4. **Report** in `docs/progress.md` every difference with the map files, then stop.

## Phase 1 — glossary and overview (draft)

Draft `docs/pm/glossary.md` and `docs/pm/overview.md` from the Phase 0 files and the map. Everything stays Inferred until a domain verifies it; update both after each domain.

- **Glossary:** every business term a PM will meet: objects (defect, dev plan, fix, merge request, version planning, release note), version kinds (mainstream, release branch, patch, customer-specific, temporary QA, temporary development), changelist, build, statuses, roles, tools (Perforce merge tool, Jira, MXtrack, Mule, Talend, scheduled jobs). Per term: plain meaning in one or two sentences · as shown on screen · also called · not to be confused with · rule IDs.
- **Overview:** each object in one line; a Mermaid diagram of how they connect; the journey of a change from defect to release note, step by step; the actors (people's roles, tools, scheduled jobs).

## Phase 2 — one domain at a time

Do the pilot domain the owner names, then stop for review. Do the other domains only after the owner approves the pilot.

1. **Inventory.** Take the domain's program list (e.g. `list_fix.txt`). Every program must appear in the coverage table at the top of the rules file, with its rule IDs or with "no business rule" and why (display only, disabled by comments, never called, duplicate of <ID>). Use the same paths as the list.
2. **Extract rules.** Open each program and write one entry per business rule in `docs/rules/<domain>.md` (format below). One rule = one trigger, one decision, one effect. When several programs implement the same rule: one entry listing every location, and any differences between them.
3. **Where it runs.** For each rule: the event, the component(s) or record, and whether it runs for people on pages, for APIs, for batches (see Reading PeopleCode).
4. **Configuration.** Replace codes, message numbers, template IDs and hard-coded values with what they mean, from the Phase 0 files.
5. **Data check.** For each rule, decide whether data can confirm it. If so, write the query, run it, record it in `docs/evidence/<domain>.md` and cite it (see Checking against data).
6. **Confidence.** Verified, Code only, Inferred or Never happens (definitions below).
7. **Guide.** Write `docs/pm/<domain>.md` from the rules file only (format and style below).
8. **Lint.** From the repository root: `python .github/skills/mx-pm-guide/scripts/lint_pm.py --coverage <program list> docs/rules/<domain>.md`. Fix every ERROR; look at every WARN.
9. **Review** in a new chat (see Review).
10. **Close.** Open questions into `docs/open-questions.md`; glossary and overview updated; `docs/progress.md` updated with the number of rules per confidence, the corrections made to the map, and 10 random rule IDs for the owner to spot-check against the code.

## Reading PeopleCode correctly

### When code runs

- **Record PeopleCode** (`Record_PeopleCode\<RECORD>\<FIELD>\<Event>`) runs in every component that uses the record, including APIs built on components. **Component** PeopleCode runs only in its component. **Page** PeopleCode (`Activate`) runs only when a person opens the page.
- **Events:** FieldDefault (default value) · FieldEdit, FieldChange (a field was changed, by a person or by an API setting it) · RowInit (data loaded) · RowInsert, RowDelete (a row added or removed in a grid) · RowSelect (rows being loaded; can skip rows) · PreBuild, PostBuild (component opened) · SearchInit, SearchSave (search page) · SaveEdit (checks during save: `Error` blocks the save, `Warning` lets the person continue) · SavePreChange (just before the data is written) · Workflow (during save) · SavePostChange (after the data is written; emails and integrations usually run here).
- **FieldFormula** programs are mostly function libraries: a function runs only when another program declares and calls it (`Declare Function … PeopleCode <RECORD>.<FIELD> FieldFormula`). Find the callers before saying when it runs.
- **Application packages** run only when called: find the callers. **Integration handlers** (`OnRequest`, `OnNotify`) and Subscription PeopleCode run when a message arrives.
- **Batches** (Application Engine) run none of the page or record PeopleCode unless they call it or go through a component interface. A rule enforced on a page does not apply to batch or SQL updates: say so.
- `%CompIntfcName <> ""` means the code is running for an API (component interface), not a person on a page. `%OperatorId` is the logged-in user; for APIs it is the integration user (e.g. `mxmerge`). `%Mode = "A"` means a new record. `.IsChanged` and `.OriginalValue` compare with the value before this save.

### Traps — each has already caused a wrong conclusion here

- **Commented-out code is not behaviour:** `REM …;`, `rem …;`, `/* … */`, and `<* … *>`, which can hide hundreds of lines. Use comments and change logs only for history and intent.
- **`SQLExec` returns the first row only.** If the query can match several rows, the result is arbitrary. Check in the data whether several rows exist.
- **Users see the message catalog text,** not the default text in the code.
- **Users see labels, not codes** (`PSXLATITEM`); `LongTranslateValue` prints the label.
- **Blank is a space.** PeopleSoft stores empty text fields as one space; `None()` and `All()` treat blank and 0 as empty. In Oracle SQL `''` is NULL, so `= ''` and `<> ''` never match.
- **Views decide what a rule sees.** Read the view's SQL. A lookup in a view that excludes the IDs being looked up returns nothing, silently.
- **Joins without SETID, EFFDT or BUSINESS_UNIT** can duplicate rows.
- **Variables not reset in a loop** keep the previous row's value.
- **Copied logic** in several programs often differs slightly: compare the copies.
- **Configuration changes behaviour without code changes** (setup tables, templates, mailing lists, roles, URLs): describe today's configuration and say it is configurable.

## Checking against data

- **Does it happen?** Count the records meeting the condition, all time and in the last 12 months; name the date column used.
- **Is it enforced?** For a rule that blocks something, count the records that break it. More than 0 means it is bypassed (API, batch, SQL, or data older than the rule): find out which.
- **Replay lookups.** Take about 100 recent real records, run the lookup the code runs, and count how often it finds a row. A lookup that never finds anything means the rule never applies.
- **Hard-coded values:** does the ID exist, is it active, when was it last used?
- **First-row-only risk:** count how many rows the `SQLExec` query can match.
- **Who does it:** split counts between integration users and people (counts only, no names).
- **Batches:** run history, and how far back the history goes (no rows may mean purged, not never run).
- **Integrations:** are the service operation and its routing active?

Record each query in `docs/evidence/<domain>.md`:

````markdown
### Q-FIX-012-a · <what it checks>
- **Purpose:** <which rule, which question>
- **SQL:**
  ```sql
  SELECT COUNT(*) FROM …
  ```
- **Result:** <counts only, e.g. "<n> of <total> fixes since <date>">
- **Run:** <YYYY-MM-DD>
````

## Rules file format — `docs/rules/<domain>.md`

````markdown
# Merge requests — rules

## Coverage
| Program | Rules |
|---|---|
| `DEV\App_Package_PeopleCode\RQ_MERGE_REQ_MX\Notification\OnExecute.pcode` | MR-031, … |
| `DEV\Page_PeopleCode\…\Activate.pcode` | no business rule: display only |

### MR-031 · Subject line of merge request emails
- **Trigger:** a merge request is saved with a new status (page or API)
- **Conditions:** first submission or later change; defect title longer than 100 characters
- **Effect:** first submission: `[<release patch>] [<client>][<defect>]-<title>: Merge requested`; later changes: `<defect>-<title>: Merge requested`; a title over 100 characters is cut to 97 characters plus `...`; line breaks removed
- **Runs for:** pages and APIs
- **Code:** `…\RQ_MERGE_REQ_MX\Notification\OnExecute.pcode` L<from>–<to> (PrepareRecipient), L<from>–<to> (Send)
- **Config:** none
- **Data check:** compared with a real email (<date>)
- **Confidence:** Code only
- **History:** TOD_1910 (2018): the "first email" test changed from status Initiated to "submitted"
- **Notes:** `<` in the title is replaced by `&lt;`, which shows literally in mail clients
````

Fields Trigger, Effect, Code and Confidence are required. A Verified or Never happens rule must cite a query in Data check. IDs are permanent: never renumber or reuse; a rule that disappears keeps its ID with `- **Status:** removed (<why>)`.

**Confidence**
- **Verified** — code read, and the data shows it happening or is consistent with it (with counts).
- **Code only** — code read; the data can't show it (e.g. a message on screen), or it wasn't checked yet.
- **Inferred** — relies on intent, naming or code that wasn't found; a person must confirm.
- **Never happens** — the code is live but the data shows the condition is never met (say since when).

## Guide format — `docs/pm/<domain>.md`

````markdown
# Fixes — how they work

> For product managers. Plain English. Last verified: <date>.
> Tags: [Verified] seen in code and in live data · [Code only] seen in code, can't be seen in data · [Inferred] needs confirmation · [Never happens] exists in code, never applies in practice.

## In short
Three to five sentences: what it is, why it exists, who uses it, what it connects to.

## Key terms
Links to the glossary entries this page uses.

## Life cycle
A Mermaid `stateDiagram-v2` with on-screen status labels (`state "Pending review" as Pending`), then:
| Status (as on screen) | What it means | Set by | What can happen next | How common | Rules |

## Who can do what
| Role (business name) | Can | Cannot | Rules |

## Business rules
### When <a fix is created>
1. <The rule in one or two sentences.> [Verified] [FIX-012]
   - Only when: …
   - Except when: …
   - Why: <reason and year, if the change history gives one>

## What happens automatically
### Emails
| Email | Sent when | To / Cc | What it says | Rules |
### Scheduled jobs
| Job | What it does | How often it actually runs | Rules |
### Other systems
| System | What is exchanged | Direction | Triggered by | Rules |

## Links with other objects

## Common questions
**Can a fix be linked to two defects?** <answer> [FIX-0xx]

## Rules that no longer apply
| Rule | Why it never applies | Since | Rules |

## Known issues and oddities
| What happens | Impact | How often | Rules |

## Open questions
````

Numbered lists are only for rules (and overview steps); each numbered item ends its **first line** with a tag and rule IDs. Use bullets everywhere else.

## Writing style

Write for someone who has never used PeopleSoft and doesn't know the process.

- What and why first, then how.
- One idea per sentence, about 25 words at most. Active voice, present tense.
- Name the actor: a developer, a tester, the merge tool, a nightly job, the system.
- Say what people see: messages in quotes exactly as in the message catalog; page titles, buttons and field labels in quotes as on screen; statuses by their label, never their code.
- Use glossary terms: the same word for the same thing everywhere; link the first use.
- Say which kind of rule it is: the system **blocks** (can't save), **warns** (can continue), or **does automatically**.
- More than two conditions → sub-bullets "Only when:" / "Except when:".
- Numbers carry a date ("as of 24 Nov 2026"); give both counts the first time ("227,771 of 227,948").
- "Why:" gives the reason and the year from the change history, without ticket IDs.
- Known issues: impact first, neutral tone.

**Never in a guide:** record, field, table, view, component or package names; file paths; PeopleCode or SQL terms; ticket IDs; people's names or personal email addresses; customer names; defect titles. **Allowed:** on-screen names, status labels, mailing-list addresses, product and version names people use, defect numbers as examples.

| Don't | Do |
|---|---|
| PrepareRecipient: non-submit → SUBJECT = R_DEFECT_ID \| "-" \| R_SUBJECT \| ": Merge requested"; Len > 100 → Substring(1, 97) \| "..." | Every email after the first has the subject "<defect number>-<defect title>: Merge requested". Titles longer than 100 characters are cut to 97 characters followed by "...". [Code only] [MR-031] |
| The system validates the fix. | When a fix is saved, the system blocks the save if <condition>, with the message "<catalog text>". [Code only] [FIX-0xx] |
| Fixes are usually created by the merge tool. | <n> of <total> fixes created in the last 12 months came from the merge tool; people created the rest. [Verified] [FIX-0xx] |
| Bug: the merged lookup on the version view fails for REL IDs. | The email is meant to grey out fixes already merged into the release branch, but it almost never does: the check looks for the release patch in a list that holds only versions, finds nothing, and greys nothing. This affects 227,771 of 227,948 merge requests (99.9%, as of 23 Nov 2026). [Verified] [MR-0xx] |

## Review — in a new chat, before saying "done"

Read the files cold, not from memory of writing them.

1. For each guide sentence, open the rule it cites: does the sentence say exactly that — every condition, nothing more?
2. Every number has a date and a query behind it.
3. The lint has no errors.
4. Read it as a PM: is any term used before it's explained? Does any sentence need PeopleSoft knowledge?
5. Every program in the coverage table, and every point in the map file for this domain, is covered by a rule or explained.
6. Write the result in `docs/progress.md`.

## Database

- Read-only: `SELECT` only. No INSERT, UPDATE, DELETE, MERGE, DDL, `FOR UPDATE` or procedure calls.
- Credentials only from environment variables; never print, log or commit them.
- Small queries: filters, `ROWNUM <= n`, `COUNT` and `GROUP BY` rather than dumping rows. If a query runs longer than about 30 seconds, stop and ask before running heavier ones (and run those off-peak).
- Check column names with `SELECT * FROM <table> WHERE ROWNUM <= 1` instead of guessing.
- Query results go to the model just like code does: query configuration and counts, not people's names, customer data or defect contents.

### Useful queries (check column names on this PeopleTools version)

```sql
-- On-screen labels of codes
SELECT fieldvalue, xlatlongname, eff_status, effdt
FROM psxlatitem WHERE fieldname = 'REQUEST_STATUS_MX' ORDER BY fieldvalue, effdt;

-- Message text users actually see
SELECT message_text, msg_severity, descrlong
FROM psmsgcatdefn WHERE message_set_nbr = 22000 AND message_nbr = 2;

-- Kind of record. RECTYPE: 0 table, 1 view, 2 work record (no data), 3 sub-record, 5 dynamic view, 6 query view, 7 temporary table
SELECT recname, rectype FROM psrecdefn WHERE recname = 'RQ_FIX_MX';

-- SQL of a view that exists in the database (dynamic views: PSSQLTEXTDEFN, SQLID = record name)
SELECT text FROM all_views WHERE view_name = 'PS_RQ_VER_VW_MX';

-- Menu path of a component
SELECT menuname, barname, itemname FROM psmenuitem WHERE pnlgrpname = 'RQ_FIX';

-- Roles that can open a component, with user counts (no names)
SELECT rc.rolename, COUNT(DISTINCT ru.roleuser) AS users
FROM psmenuitem mi
JOIN psauthitem ai ON ai.menuname = mi.menuname AND ai.barname = mi.barname AND ai.baritemname = mi.itemname
JOIN psroleclass rc ON rc.classid = ai.classid
JOIN psroleuser ru ON ru.rolename = rc.rolename
WHERE mi.pnlgrpname = 'RQ_FIX'
GROUP BY rc.rolename ORDER BY users DESC;

-- Users holding a role the code checks (IsUserInRole)
SELECT COUNT(*) AS users FROM psroleuser WHERE rolename = 'MX_FIX_STATUS_OWNER';

-- Does a batch run? RUNSTATUS 9 = success, 17 = success with warning, 3 = error
SELECT runstatus, COUNT(*) AS runs, MAX(rundttm) AS last_run
FROM psprcsrqst WHERE prcsname = 'MSTFIXREL_MX' GROUP BY runstatus;
SELECT MIN(rundttm) AS history_starts FROM psprcsrqst;

-- URL behind GetURL(URL.P4_WEB)
SELECT url FROM psurldefn WHERE url_id = 'P4_WEB';
```

## Prompts the owner uses to start each step

- **Phase 0:** "Follow the mx-pm-guide skill, Phase 0 only. First show me how DbQuery.java gets its connection settings and confirm no password is in the repo. Then build the ground-truth files one at a time. After each file, list what differs from status_values.md, messages.md and the catalog. Stop at the end of Phase 0."
- **Pilot rules:** "Follow mx-pm-guide, Phase 2 steps 1–6, for the <domain> domain only. Batches of 10 rules; update docs/progress.md after each batch. Don't write the guide yet. When done, show me the coverage table, every rule tagged Never happens, every correction to the catalog, and the open questions."
- **Pilot guide:** "Write docs/pm/<domain>.md from docs/rules/<domain>.md following mx-pm-guide. Run the lint and fix every error. Stop and tell me when it's ready for review."
- **Review (new chat):** "Follow the Review section of mx-pm-guide for docs/pm/<domain>.md. Don't rely on anything from earlier chats. Report every sentence that doesn't match its rule, and fix it."
