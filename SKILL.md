---
name: mx-pm-guide
description: Writes and checks the plain-English guide for product managers on how the PeopleSoft quality system works (defects, dev plans, fixes, merge requests, version planning, releases, Jira, APIs, notifications, smart reports), from the decoded PeopleCode and the read-only database. Use for anything under docs\, and whenever asked to explain PeopleSoft behaviour to non-technical readers. Uses the tools of mx-pcode-navigator.
---

# PM guide to the PeopleSoft quality system

## Goal

Product managers who know neither PeopleSoft nor the functional domain must be able to read, object by object, everything the system does, in plain English, and rely on it.

Priorities, in this order: **accurate**, then **complete**, then **easy to read**. A short page that is right beats a long page with guesses.

This skill builds on **mx-pcode-navigator**: use its query tool (`find.py`), its database runner (`DbQuery.java`) and its references. Where the two skills differ on output, this one wins for anything under `docs\`.

## Layers — keep them separate

| Layer | Where | Written by | What it is |
|---|---|---|---|
| Narrative | `.github\skills\mx-pcode-navigator\references\domains\*.md`, `repo-layout.md` | hand | Engineer notes, written **without database access**. Leads to check, not facts. |
| Inventory | `references\catalog\<domain>.md`, `index.tsv`, `status_values.md`, `messages.md`, `tables.md`, `functions.md`, `tickets.md` | `build_catalog.py` | What code exists and what it references, extracted from the code. **Never edit**: regeneration overwrites it. |
| Rules | `docs\rules\<domain>.md` | this skill | One entry per business rule: code location, configuration, data check, confidence. **The source of truth.** |
| Guide | `docs\pm\<domain>.md`, `docs\pm\glossary.md`, `docs\pm\overview.md`, `docs\pm\README.md` | this skill | Plain English for PMs, written **only** from the rules files. |

Supporting files: `docs\rules\<domain>.programs.txt` (file list of the domain), `docs\evidence\<domain>.md` (every query and its result), `docs\evidence\_*.md` (Phase 0 ground truth), `docs\open-questions.md`, `docs\progress.md`.

### Domains

Rules and guides follow the catalog domains, so every file of the code belongs to exactly one domain.

| Domain | Rule ID prefix | Guide title | Narrative to read first |
|---|---|---|---|
| defect | DEFECT | Defects | `domains\defect.md`, `domains\defect-satellites.md` |
| fix | FIX | Fixes | `domains\fix.md` |
| mr | MR | Merge requests | `domains\mr.md` |
| devplan | DEVPLAN | Dev plans | `domains\devplan.md` |
| vplanning | VPLAN | Version planning | `domains\vplanning-release.md` |
| release | RELEASE | Releases and versions | `domains\vplanning-release.md` |
| jira | JIRA | Jira | `domains\api-jira.md` |
| api | API | Links with other systems | `domains\api-jira.md` |
| notif | NOTIF | Emails and notifications | `domains\notifications-smart-batch.md` |
| smart | SMART | Smart reports | `domains\notifications-smart-batch.md` |

The narratives are **unfinished and still being written** in a separate task. Use what exists for orientation; where a narrative is missing or stops short, work from the catalog and the code. Never write, extend or edit a narrative unless the owner asks.

IDs: rules `FIX-012`; queries `Q-FIX-012-a` (Phase 0 queries use `GT`, e.g. `Q-GT-001-a`).

## Non-negotiable rules

1. **Trace everything.** Every sentence in a guide cites rule IDs. Every rule cites the full path and lines of code you opened and, when data can show it, a recorded query. No trace → don't write it.
2. **Re-read the code.** Never copy a claim from the narrative or the inventory without opening the code behind it. When the narrative and the code disagree, the code wins: list the correction under "Narrative corrections" in `docs\progress.md` (don't edit the narrative).
3. **Describe what the system does, not what it should do.** A bug is documented as behaviour, then listed under Known issues.
4. **Intent only from evidence.** "So that…", "to prevent…" only when a comment, change log or ticket says so; otherwise the rule is Inferred.
5. **Don't fill gaps.** If the code and the data don't settle a point, leave it out of the guide and add it to `docs\open-questions.md` with what you checked.
6. **Keep every condition and exception.** No "usually", "typically", "in most cases" unless a query gives the share.
7. **Files are the memory, not the chat.** Work in batches of at most 10 rules; after each batch, save the files and update `docs\progress.md`. In a new chat, read `docs\progress.md` first.
8. **Never edit the inventory files** (`references\catalog\`, `index.tsv`, `status_values.md`, `messages.md`, `tables.md`, `functions.md`, `tickets.md`). Record their gaps in `docs\progress.md`; the database versions live in `docs\evidence\`.
9. **File paths and tickets belong in rules files only.** mx-pcode-navigator says to quote paths and tickets in answers: that applies to rules files and engineer answers, never to guide pages.
10. **Search with `find.py`,** not grep (grep times out on this OneDrive folder). `find.py grep … --code` skips comments and dead code.
11. **Database: read-only, no secrets, no personal data** (see Database).

## Phase 0 — once, before any domain

1. **Database access** is set up in mx-pcode-navigator §2b (Java runner, credentials in `DecodePC.properties`). Check the credentials aren't tracked: `git ls-files "*DecodePC.properties"` must print nothing. Run one test query. Python's `oracledb` doesn't work with this database: a script that needs data calls the Java runner.
2. **Create** the `docs\` folders, `docs\progress.md` and `docs\open-questions.md`.
3. **Ground truth.** Start from the inventory (it lists what the code uses) and add what only the database knows. Keep the scripts you write in `.github\skills\mx-pm-guide\scripts\` so they can be re-run. One file each in `docs\evidence\`:
   - `_labels.md` — for every code in `status_values.md` (statuses, types, flags): its on-screen label and whether it is active (`sysadm.PSXLATITEM`).
   - `_messages.md` — for every message number in `messages.md`: catalog text, explain text and severity (`sysadm.PSMSGCATDEFN`), and the default text in the code when it differs. **Users see the catalog text.**
   - `_templates.md` — merge request status emails: who receives them for each status (`sysadm.PS_RQ_MR_NOTIF_MX`). Template emails: every template ID used in code (`find.py grep "templateId" --code`), with subject, body and active flag (find the table holding them with `find.py`) and recipients (`sysadm.PS_HTML_ADDRESS_MX`). Read `NOTIFICATION_MX:Notification` and document how recipient codes (RM, PPLS, …) and sender types turn into addresses. An inactive template means the email is never sent.
   - `_views.md` — every view the code or pages read: its SQL, its filters, and joins that can drop or duplicate rows.
   - `_hardcoded.md` — every hard-coded version ID, product, company, user ID, role, email address, URL or date in the code: what it is (name, type), whether it is still active, when it was last used.
   - `_batches.md` — every batch program (each folder under `DEV\Application_Engine_PeopleCode\`; the job catalogue in `notifications-smart-batch.md` may help but is unfinished): how it starts (button, schedule, another program) and its run history.
   - `_setup.md` — every setup or parameter table the code reads: its current rows, summarised.
4. **Report** in `docs\progress.md` every gap or difference found in the inventory files, then stop. Don't compare with the narratives here: they're unfinished, so a missing topic isn't a gap.

## Phase 1 — glossary and overview (draft)

Draft `docs\pm\glossary.md` and `docs\pm\overview.md` from the glossary in `repo-layout.md`, the Phase 0 files and the narratives. Everything stays Inferred until a domain verifies it; update both after each domain.

- **Glossary:** every business term a PM will meet: objects (defect, dev plan, fix, merge request, version planning, release note), version kinds (mainstream, release branch, patch, customer-specific, temporary QA, temporary development), changelist, build, statuses, roles, tools (Perforce merge tool, Jira, MXtrack, Mule, Talend, scheduled jobs). Per term: plain meaning in one or two sentences · as shown on screen · also called · not to be confused with · rule IDs.
- **Overview:** each object in one line; a Mermaid diagram of how they connect; the journey of a change from defect to release note, step by step; the actors (people's roles, tools, scheduled jobs).

## Phase 2 — one domain at a time

Do the pilot domain the owner names, then stop for review. Do the other domains only after the owner approves the pilot.

1. **Inventory.** Save the output of `python .github\skills\mx-pcode-navigator\scripts\find.py domain <domain>` to `docs\rules\<domain>.programs.txt`. Every file in it must appear in the `## Coverage` table at the top of the rules file, with its rule IDs or with "no business rule" and why: display only · whole file commented out ([DEAD]) · never called · duplicate of <ID> · backup object (`*_BK*`, dated names — confirm with data that it isn't reachable or run any more before saying so).
2. **Extract rules.** Read the narrative for orientation, then open each file and write one entry per business rule in `docs\rules\<domain>.md` (format below). One rule = one trigger, one decision, one effect. When several files implement the same rule: one entry listing every location, and any differences between them.
3. **Where it runs.** For each rule: the event, the component(s) or record, and whether it runs for people on pages, for APIs, for batches. Run `find.py writes <TABLE>` and `find.py field <RECORD.FIELD>` to find every other place applying the same rule (page, component interface, API_MX service, batch): rules are often duplicated across them. Follow calls as described in mx-pcode-navigator §3.
4. **Configuration.** Replace codes, message numbers, template IDs and hard-coded values with what they mean, from the Phase 0 files.
5. **Data check.** For each rule, decide whether data can confirm it. If so, write the query, run it, record it in `docs\evidence\<domain>.md` and cite it (see Checking against data).
6. **Confidence.** Verified, Code only, Inferred or Never happens (definitions below).
7. **Guide.** Write `docs\pm\<domain>.md` from the rules file only (format and style below).
8. **Lint.** From the repository root: `python .github\skills\mx-pm-guide\scripts\lint_pm.py --coverage docs\rules\<domain>.programs.txt docs\rules\<domain>.md`. It also checks that every file cited in a rule exists and that its line numbers are inside the file. Fix every ERROR; look at every WARN.
9. **Review** in a new chat (see Review).
10. **Close.** Open questions into `docs\open-questions.md`; glossary and overview updated; narrative corrections listed; `docs\progress.md` updated with the number of rules per confidence, the corrections made, and 10 random rule IDs for the owner to spot-check against the code.

## Reading PeopleCode correctly

### When code runs

- **Record PeopleCode** (`Record_PeopleCode\<RECORD>\<FIELD>\<Event>`) runs in every component that uses the record, including APIs built on components. **Component** PeopleCode runs only in its component. **Page** PeopleCode (`Activate`) runs only when a person opens the page. Logic for one screen element can be split between record and component level, and across events: check both levels.
- **Events:** FieldDefault (default value) · FieldEdit, FieldChange (a field was changed, by a person or by an API setting it) · RowInit (data loaded) · RowInsert, RowDelete (a row added or removed in a grid) · RowSelect (rows being loaded; can skip rows) · PreBuild, PostBuild (component opened) · SearchInit, SearchSave (search page) · SaveEdit (checks during save: `Error` blocks the save, `Warning` lets the person continue) · SavePreChange (just before the data is written) · Workflow (during save) · SavePostChange (after the data is written; emails and integrations usually run here).
- **FieldFormula** programs are mostly function libraries: a function runs only when another program declares and calls it (`Declare Function … PeopleCode <RECORD>.<FIELD> FieldFormula`). Find the callers (`find.py fn <name>`) before saying when it runs.
- **Application packages** run only when called: find the callers. **Integration handlers** (`OnRequest`, `OnNotify`) and Subscription PeopleCode run when a message arrives.
- **Batches** (Application Engine) run none of the page or record PeopleCode unless they call it or go through a component interface. A rule enforced on a page does not apply to batch or SQL updates: say so.
- `%CompIntfcName <> ""` means the code is running for an API (component interface), not a person on a page. `%OperatorId` is the logged-in user; for APIs it is the integration user (e.g. `mxmerge`). `%Mode = "A"` means a new record. `.IsChanged` and `.OriginalValue` compare with the value before this save.

### Traps — each has already caused a wrong conclusion here

- **Commented-out code is not behaviour:** `REM …;`, `rem …;`, `/* … */`, and `<* … *>`, which can hide hundreds of lines. Use comments and change logs only for history and intent.
- **Backup objects** (`*_BK*`, dated names) are usually not live, but some old objects still are (e.g. still the "return to search" target): check before ignoring one.
- **`SQLExec` returns the first row only.** If the query can match several rows, the result is arbitrary. Check in the data whether several rows exist.
- **Users see the message catalog text,** not the default text in the code.
- **Users see labels, not codes** (`PSXLATITEM`); `LongTranslateValue` prints the label.
- **Blank is a space.** PeopleSoft stores empty text fields as one space; `None()` and `All()` treat blank and 0 as empty. In Oracle SQL `''` is NULL, so `= ''` and `<> ''` never match.
- **Views decide what a rule sees.** Read the view's SQL. A lookup in a view that excludes the IDs being looked up returns nothing, silently.
- **Joins without SETID, EFFDT or BUSINESS_UNIT** can duplicate rows.
- **Variables not reset in a loop** keep the previous row's value.
- **Copied logic** in several files often differs slightly: compare the copies.
- **Configuration changes behaviour without code changes** (setup tables, templates, mailing lists, roles, URLs): describe today's configuration and say it is configurable.

## Checking against data

- **Does it happen?** Count the records meeting the condition, all time and in the last 12 months; name the date column used.
- **Is it enforced?** For a rule that blocks something, count the records that break it. More than 0 means it is bypassed (API, batch, SQL, or data older than the rule): find out which.
- **Replay lookups.** Take about 100 recent real records, run the lookup the code runs, and count how often it finds a row. A lookup that never finds anything means the rule never applies.
- **Hard-coded values:** does the ID exist, is it active, when was it last used?
- **First-row-only risk:** count how many rows the `SQLExec` query can match.
- **Who does it:** split counts between integration users and people (counts only, no names).
- **Batches:** run history, and how far back the history goes (no rows may mean purged, not never run).
- **Integrations:** outbound calls are logged through `APILOGMX` (find its table with `find.py grep APILOGMX`): count calls per operation and result, and look at the dead-letter queue described in `api-jira.md`.

Record each query in `docs\evidence\<domain>.md`:

````markdown
### Q-FIX-012-a · <what it checks>
- **Purpose:** <which rule, which question>
- **SQL:**
  ```sql
  SELECT COUNT(*) FROM sysadm.PS_… WHERE …
  ```
- **Result:** <counts only, e.g. "<n> of <total> fixes since <date>">
- **Run:** <YYYY-MM-DD>
````

## Rules file format — `docs\rules\<domain>.md`

````markdown
# Merge requests — rules

## Coverage
| Program | Rules |
|---|---|
| `DEV\App_Package_PeopleCode\RQ_MERGE_REQ_MX\Notification\OnExecute.pcode` | MR-031, … |
| `DEV\Page_PeopleCode\<PAGE>\Activate.pcode` | no business rule: display only |

### MR-031 · Subject line of merge request emails
- **Trigger:** a merge request is saved with a new status (page or API)
- **Conditions:** first submission or later change; defect title longer than 100 characters
- **Effect:** first submission: `[<release patch>] [<client>][<defect>]-<title>: Merge requested`; later changes: `<defect>-<title>: Merge requested`; a title over 100 characters is cut to 97 characters plus `...`; line breaks removed
- **Runs for:** pages and APIs
- **Code:** `DEV\App_Package_PeopleCode\RQ_MERGE_REQ_MX\Notification\OnExecute.pcode` L<from>–<to>
- **Config:** none
- **Data check:** compared with a real email (<date>)
- **Confidence:** Code only
- **History:** TOD_1910 (2018): the "first email" test changed from status Initiated to "submitted"
- **Notes:** `<` in the title is replaced by `&lt;`, which shows literally in mail clients
````

- Trigger, Effect, Code and Confidence are required.
- **Code** is one line: full paths from `DEV\` with line ranges (`L12–30`), separated by `;`. No `…` abbreviations: the lint checks each file exists and each range is inside it.
- A Verified or Never happens rule must cite a query in Data check.
- IDs are permanent: never renumber or reuse; a rule that disappears keeps its ID with `- **Status:** removed (<why>)`.

**Confidence**
- **Verified** — code read, and the data shows it happening or is consistent with it (with counts).
- **Code only** — code read; the data can't show it (e.g. a message on screen), or it wasn't checked yet.
- **Inferred** — relies on intent, naming or code that wasn't found; a person must confirm.
- **Never happens** — the code is live but the data shows the condition is never met (say since when).

## Guide format — `docs\pm\<domain>.md`

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
5. Every file in the coverage table, and every point in the narrative for this domain (as far as it is written), is covered by a rule or explained.
6. Write the result in `docs\progress.md`.

## Database

- Run queries with the Java runner from the repository root, as in mx-pcode-navigator §2b:
  `java -cp lib\ojdbc8-19.24.0.0.jar .github\skills\mx-pcode-navigator\scripts\DbQuery.java "<query>" [maxRows]`
- Prefix every table with the schema: record X is `sysadm.PS_X`; PeopleTools tables are `sysadm.<TABLE>` (e.g. `sysadm.PSXLATITEM`).
- `SELECT` and `WITH` only. The default is 200 rows: always filter, and prefer `COUNT` and `GROUP BY` to dumping rows. If a query runs longer than about 30 seconds, stop and ask before running heavier ones (and run those off-peak).
- Check column names with `SELECT * FROM sysadm.<table> WHERE ROWNUM <= 1` instead of guessing.
- Credentials stay in `DecodePC.properties`: never copy them into files, logs or answers.
- Query results go to the model just like code does: query configuration and counts, not people's names or emails (`PSOPRDEFN` and similar), customer data or defect contents.

### Useful queries (check column names on this PeopleTools version)

```sql
-- On-screen labels of codes
SELECT fieldvalue, xlatlongname, eff_status, effdt
FROM sysadm.PSXLATITEM WHERE fieldname = 'REQUEST_STATUS_MX' ORDER BY fieldvalue, effdt;

-- Message text users actually see
SELECT message_text, msg_severity, descrlong
FROM sysadm.PSMSGCATDEFN WHERE message_set_nbr = 22000 AND message_nbr = 2;

-- Kind of record. RECTYPE: 0 table, 1 view, 2 work record (no data), 3 sub-record, 5 dynamic view, 6 query view, 7 temporary table
SELECT recname, rectype FROM sysadm.PSRECDEFN WHERE recname = 'RQ_FIX_MX';

-- SQL of a view that exists in the database (dynamic views: sysadm.PSSQLTEXTDEFN, SQLID = record name)
SELECT text FROM all_views WHERE owner = 'SYSADM' AND view_name = 'PS_RQ_VER_VW_MX';

-- Menu path of a component
SELECT menuname, barname, itemname FROM sysadm.PSMENUITEM WHERE pnlgrpname = 'RQ_FIX';

-- Roles that can open a component, with user counts (no names)
SELECT rc.rolename, COUNT(DISTINCT ru.roleuser) AS users
FROM sysadm.PSMENUITEM mi
JOIN sysadm.PSAUTHITEM ai ON ai.menuname = mi.menuname AND ai.barname = mi.barname AND ai.baritemname = mi.itemname
JOIN sysadm.PSROLECLASS rc ON rc.classid = ai.classid
JOIN sysadm.PSROLEUSER ru ON ru.rolename = rc.rolename
WHERE mi.pnlgrpname = 'RQ_FIX'
GROUP BY rc.rolename ORDER BY users DESC;

-- Users holding a role the code checks (IsUserInRole)
SELECT COUNT(*) AS users FROM sysadm.PSROLEUSER WHERE rolename = 'MX_FIX_STATUS_OWNER';

-- Does a batch run? RUNSTATUS 9 = success, 17 = success with warning, 3 = error
SELECT runstatus, COUNT(*) AS runs, MAX(rundttm) AS last_run
FROM sysadm.PSPRCSRQST WHERE prcsname = 'MSTFIXREL_MX' GROUP BY runstatus;
SELECT MIN(rundttm) AS history_starts FROM sysadm.PSPRCSRQST;

-- URL behind GetURL(URL.P4_WEB)
SELECT url FROM sysadm.PSURLDEFN WHERE url_id = 'P4_WEB';
```

## Prompts the owner uses to start each step

- **Phase 0:** "Follow the mx-pm-guide skill, Phase 0 only. Confirm DecodePC.properties isn't tracked by git and run a test query. Then build the ground-truth files one at a time, with find.py and the Java runner. After each file, list what it shows that the inventory files (status_values.md, messages.md, the catalog) don't, or get wrong. Don't compare with or edit the domain narratives: they're unfinished. Stop at the end of Phase 0."
- **Pilot rules:** "Follow mx-pm-guide, Phase 2 steps 1–6, for the <domain> domain only. Batches of 10 rules; update docs\progress.md after each batch. Don't write the guide yet. When done, show me the coverage table, every rule tagged Never happens, the narrative corrections you listed, and the open questions."
- **Pilot guide:** "Write docs\pm\<domain>.md from docs\rules\<domain>.md following mx-pm-guide. Run the lint and fix every error. Stop and tell me when it's ready for review."
- **Review (new chat):** "Follow the Review section of mx-pm-guide for docs\pm\<domain>.md. Don't rely on anything from earlier chats. Report every sentence that doesn't match its rule, and fix it."
