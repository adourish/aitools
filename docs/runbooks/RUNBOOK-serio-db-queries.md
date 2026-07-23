# Runbook — SERIO Oracle DB: user & entry lookup queries

**What this is:** a cookbook of SQL for the SERIO Oracle DB (OASIS schema) — look up a **user** from a
`PRSN_ID` (or name / login / EASE number), check whether an **OASIS user profile** exists (the
`401 "An OASIS user profile was not found"` blocker), trace an **entry** (activity log, workflow,
collections, quantities), and follow a **Label-Exam AI (CV)** document from its `flowInstanceId` back to
the entry and the reviewer.

**Connect:** SQL Developer (or `sqlcl`) against the Dev/Test endpoints in
[`RUNBOOK-serio-dev-db.md`](RUNBOOK-serio-dev-db.md) — Dev `gi-22040-22041.fda.gov:1523/ORAD1T23`, user
`oasis_er`, password from KeePass `Database/SERIO Oracle DB (oasis_er) Dev-Test`. Schema owner is
**`OASIS`**.

**Verification:** table/column names are `cross-checked` against the dev schema dump
(`logs/serio-schema-dev-20260715-135535.txt`, 438 tables) and the entry queries against the SQL
Developer screenshots the team ran. Exact result shapes are `single-source` — run them and adjust.

> Read-only lookups. Nothing here writes. `PRSN_ID` is the person key used across the whole schema
> (`COLLECTIONS`, `ACTION_HOURS`, `ASSIGNED_PEOPLE`, `DECISIONS`, `serio_cv_document_ref`, …).

---

## 1. Who is this person? (`PRSN_ID` → user info)

The richest single source is **`FDA_USER_INFO`**; **`SERIO_USERS_MVW`** adds title/phone/port.

```sql
-- Full user info for a PRSN_ID (e.g. 482630 from a serio_cv_document_ref row)
SELECT prsn_id, oracle_user_name, first_name, last_name, email_adrs,
       dstrct_office_name, asgnd_office_name, ease_emp_num,
       user_profile_end_date
FROM   fda_user_info
WHERE  prsn_id = 482630;

-- More detail (title, phone, port, EASE building/district)
SELECT prsn_id, first_name, last_name, email_adrs, phone_num,
       pos_title_text, oracle_user_name, port_id,
       ease_bldg_dstrct_name, facts_end_date
FROM   serio_users_mvw
WHERE  prsn_id = 482630;
```

## 2. Find a user by name / login / email / EASE number

```sql
-- by name (case-insensitive, partial)
SELECT prsn_id, first_name, last_name, oracle_user_name, email_adrs, dstrct_office_name
FROM   fda_user_info
WHERE  UPPER(last_name)  = UPPER('&last')          -- e.g. Dourish
  AND  UPPER(first_name) LIKE UPPER('&first' || '%');

-- by Oracle / login name
SELECT prsn_id, first_name, last_name, email_adrs
FROM   fda_user_info
WHERE  UPPER(oracle_user_name) = UPPER('&oracle_user');

-- by LDAP login id  (SERIO_LDAP_USERS maps PRSN_ID <-> LDAP_USERID)
SELECT prsn_id, ldap_userid, email_adrs, ease_emp_num
FROM   serio_ldap_users
WHERE  UPPER(ldap_userid) = UPPER('&ldap_id');

-- by EASE employee number
SELECT prsn_id, first_name, last_name, email_adrs
FROM   fda_user_info
WHERE  ease_emp_num = '&ease_num';
```

## 3. Does an OASIS user profile exist? (the `401` blocker)

The hosted apps and local dev fail with `401 "An OASIS user profile was not found"` until the DBA
provisions the user (FS-012). Check whether a profile row exists and is **not end-dated**:

```sql
-- profile present and still active?  (end date NULL or in the future = active)
SELECT prsn_id, oracle_user_name, first_name, last_name,
       user_profile_end_date,
       CASE WHEN user_profile_end_date IS NULL OR user_profile_end_date > SYSDATE
            THEN 'ACTIVE' ELSE 'ENDED' END AS profile_status
FROM   fda_user_info
WHERE  UPPER(oracle_user_name) = UPPER('&oracle_user');
```

No row back → the profile hasn't been created yet (chase Kaustav → Soumen). A row with an
`ENDED` status → the profile lapsed and needs re-activating.

## 4. Trace an entry (the queries the team runs)

```sql
-- by entry number (the human ENTRY_NUM, e.g. DP4-8637734-5 / ZZZ-4008436-6)
SELECT * FROM workflow      WHERE entry_num = '&entry_num';

-- everything logged for an entry, newest first
SELECT * FROM activity_log  WHERE entry_id = &entry_id ORDER BY create_date DESC;

-- specific activity-log rows
SELECT * FROM activity_log  WHERE actvty_log_id IN (&id1, &id2);

-- line-level quantities for an entry / reference doc / line
SELECT * FROM quantities    WHERE entry_id = &entry_id
                              AND rfrnc_doc_id = &rfrnc_doc_id
                              AND line_num = 1;

-- collections tied to an activity log (PRSN_ID = who collected)
SELECT * FROM collections   WHERE actvty_log_id = &actvty_log_id;
```

## 5. Label-Exam AI (CV) documents — `serio_cv_document_ref`

`DOC_ID` here is the Bedrock **`flowInstanceId`** (joins to the DynamoDB `aiflow-context-table` — see
[`../features/serio-aws-environment.md`](../features/serio-aws-environment.md)). `STATUS` is
`SUCCESS` / `TIMEOUT` / `ERROR`.

```sql
-- newest CV documents (what the team watches during the incident)
SELECT * FROM serio_cv_document_ref ORDER BY created_date DESC;

-- one flow run by its flowInstanceId
SELECT * FROM serio_cv_document_ref WHERE doc_id = '&flow_instance_id';

-- all CV docs for an entry
SELECT * FROM serio_cv_document_ref WHERE entry_id = &entry_id ORDER BY created_date DESC;

-- failure breakdown (how many TIMEOUT vs ERROR vs SUCCESS)
SELECT status, COUNT(*) FROM serio_cv_document_ref
GROUP BY status ORDER BY COUNT(*) DESC;

-- CV docs joined to the reviewer's name (PRSN_ID -> FDA_USER_INFO)
SELECT r.cv_document_ref_id, r.doc_id, r.entry_num, r.product_code, r.status,
       u.first_name, u.last_name, u.email_adrs
FROM   serio_cv_document_ref r
LEFT   JOIN fda_user_info u ON u.prsn_id = r.prsn_id
ORDER  BY r.created_date DESC;
```

---

## Handy reference

| Need | Table / view | Key columns |
|---|---|---|
| User info (name, email, district, login) | `FDA_USER_INFO` | `PRSN_ID`, `ORACLE_USER_NAME`, `FIRST_NAME`, `LAST_NAME`, `EMAIL_ADRS`, `DSTRCT_OFFICE_NAME`, `EASE_EMP_NUM`, `USER_PROFILE_END_DATE` |
| Rich user view (title, phone, port) | `SERIO_USERS_MVW` | `PRSN_ID`, `POS_TITLE_TEXT`, `PHONE_NUM`, `PORT_ID`, `EASE_BLDG_DSTRCT_NAME` |
| LDAP login mapping | `SERIO_LDAP_USERS` | `PRSN_ID`, `LDAP_USERID`, `EMAIL_ADRS` |
| Base person record | `FDA_PERSONNEL` | `PRSN_ID` (FK target of `EMPLOYEE_LIST.PRSN_ID`) |
| Assignment / supervisor | `EMPLOYEE_LIST` | `PRSN_ID`, `AS_PRSN_ID` |
| Entry workflow | `WORKFLOW` | `ENTRY_NUM`, `ENTRY_ID` |
| Entry activity log | `ACTIVITY_LOG` | `ACTVTY_LOG_ID`, `ENTRY_ID`, `CREATE_DATE` |
| Line quantities | `QUANTITIES` | `ENTRY_ID`, `RFRNC_DOC_ID`, `LINE_NUM` |
| Collections | `COLLECTIONS` | `ACTVTY_LOG_ID`, `PRSN_ID` |
| Label-Exam AI docs | `SERIO_CV_DOCUMENT_REF` | `DOC_ID` (=flowInstanceId), `ENTRY_ID`, `ENTRY_NUM`, `PRSN_ID`, `PRODUCT_CODE`, `STATUS` |

> Full schema (438 tables, columns, keys): `logs/serio-schema-dev-20260715-135535.txt` (dev dump,
> generated by `tools/db/Export-SerioSchema.ps1`). Regenerate against Test if column widths matter.
