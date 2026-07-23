# Runbook — Elsa / SIRCE access and the privileged account (e3530)

**What this is:** how a new person on the FDA Imports / SIRCE program gets the accounts they need
to actually do the work — in particular the **privileged account** (an ALT-PIV / `AD_APP`
account) that gets you into the WODC and ADC Citrix environments.

**Two different things, often confused:**

| You need… | Do this |
|-----------|---------|
| Software installed on your own laptop (VS Code, Java, etc.) | Open an **ERIC Help Desk ticket**. This is *local admin*, and the e3530 process below is **not** for it. |
| Access to WODC / ADC Citrix resources | The **e3530 privileged account** process below. |

If you need local admin for some other reason, contact the Security Lead or your delivery team
point of contact.

**Roughly how long:** the training is 30–45 minutes. After you submit the form, account creation
takes **3–5 business days**, and there is a badging appointment on top of that. Start early.

**Related:** [`RUNBOOK-onboarding-piv-laptop-training.md`](RUNBOOK-onboarding-piv-laptop-training.md)
(badge, laptop, and the separate security-awareness training) ·
[`RUNBOOK-dev-workstation-setup.md`](RUNBOOK-dev-workstation-setup.md) (developer software) ·
[`RUNBOOK-ai-agent-coding-tools.md`](RUNBOOK-ai-agent-coding-tools.md) (AI coding plugins).

---

## The program in one line

The official FDA system name is **SIRCE**. You will also see **SCAIL** — that is a newer program
name, and the two get confused; on FDA security and implementation forms, use **SIRCE**.

**Team SharePoint:** the *OIMT Imports SIRCE ALM Hub* site on `fda.sharepoint.com`
(`/sites/OIMT-Imports-SIRCE-ALM-Hub`). You need FDA network access to open it.

---

## Step 1 — Finish the training first

You cannot submit the account request without a training certificate to attach.

1. Log on to the **FDA Compliance Training System**. Chrome is the recommended browser. (There is
   a password reset link on the page if you need it.)
2. Go to **Learning** → **Browse for training**.
3. Find **"Information Security for IT Administrators"** (IT Admin RBT). It takes about 30–45
   minutes. The **Rules of Behavior (ROB)** for IT Admins is part of the same course, so you do
   not need to hunt for it separately.
4. Once it is on your transcript, click **Launch** and complete it.
5. **Save the certificate** — you attach it to the ticket in Step 2.

> **If the course does not show up in *Browse for training*:** it usually has to be *assigned* to
> your LMS profile, or the exact title has changed (this course name comes from a 2024 SOP and is
> worth re-confirming). First search the box for `IT Admin`, `RBT`, or `Rules of Behavior` (not just
> the full title), and check your **Transcript** as well as the catalog. If it still isn't there,
> email the **FDA Learning help desk — `fdalearning_help@tacg.com`** (TACG operates the training
> system) to request enrollment; the request is typically routed via **Mehvish Ali**
> (`Mehvish.Ali@fda.hhs.gov`) with **Amlan Das** (PM) cc'd, and **James Stachowski** on the LMS side.
> (`CybersecurityAwareness@fda.hhs.gov` is for CSAT / password resets, *not* for assigning this
> course.) Confirm your **CSAT** is complete first — a missing prerequisite can hide this course.

Also make sure your **Cybersecurity Awareness Training (CSAT)** is already done before you go any
further. That is a different course; see the onboarding runbook linked above.

---

## Step 2 — Submit the e3530 form

Submit it through **ERIC in ServiceNow** (Service Catalog). Most of Section 1 (your employee
information) fills itself in.

Fill in the rest as follows:

| Field | What to enter |
|-------|---------------|
| **Role** | The one that matches your job |
| **Center** | `ORA` |
| **Official FDA System Name** | `SIRCE` |
| **Account Type** | `Privileged Account` |
| **Account type (second field)** | `AD_APP` |
| **Supervisor** | Crasta, Belinda — then select the **"I confirmed"** option (REI staff only) |
| **ROB/RBT confirmation** | Tick to confirm you completed the training |
| **Attachment** | Your training transcript / certificate from Step 1 |

**Justification** — adapt this sentence:

> I am currently working on the FDA Imports/SIRCE program as a **[Business Analyst / Developer /
> Database Administrator / Tester / Tier 3 Helpdesk / Product Lead / Technical Manager]** in the
> **[Imports / SIRCE / LABS-OCI / Shared Services]** team. I am requesting a new privileged
> account to access WODC/ADC Citrix resources to perform my job duties.

Then submit (the button is top-right).

---

## Step 3 — What happens next

You get an automated email with a Request ID, and ServiceNow starts the approval chain:

1. Supervisor / COR approval
2. Personnel Security approval
3. ISSO approval
4. Account creation

Then, in order:

- The **Active Directory team** creates your `AD_APP` account (**3–5 business days**) and emails
  you the account name.
- **You** then add your new account name to the tracking spreadsheet on the team SharePoint.
- The **REI Security / Infrastructure team** adds your account to the Role Based Access Control
  (RBAC) form.
- **You** visit an FDA badging office to collect your **ALT-PIV card** — the FDA Security Office
  arranges the appointment. See the onboarding runbook for what to bring.
- Once you have the ALT-PIV card, you will be given guidance to verify you can log in to the
  **WODC and ADC Citrix portals**.

> **Status — Anthony Dourish (2026-07-21):** the privileged `AD_APP` account
> **`ad_app_a.dourish`** has been **created** (this is the AWS-GovCloud / WODC-ADC Citrix elevated
> login). ServiceNow **RITM1063573** (request **REQ1061472**), close note *"Created ad_app_a.dourish -
> Notified requester"*; assignment group **OIMT DT ALT PIVCARD**. Approval chain complete:
> Supervisor/COR (Belinda Crasta) → Personnel Security → ISSO (Alex Maymir) → Account Creation
> (Karen Parsons / Shannan Gullett).
> **Remaining:** ① **send the account name `ad_app_a.dourish` to Kaustav Lahiri** — he adds you to
> the **AWS IAM role** (per KT 2026-07-21; this is what actually gets you into AWS GovCloud); ② add it
> to the team SharePoint tracking sheet; ③ get it onto the **RBAC** form (REI Security/Infra);
> ④ collect the **ALT-PIV card**; ⑤ verify WODC/ADC Citrix login.
> The `ADAP_`/`ad_app_` prefix marks it as an **elevated-access** account.
> **AWS dev/test login (once you're in the IAM role):**
> `https://sso2.fda.gov/idp/startSSO.ping?PartnerSpId=FDA_AWS_GovCloud` — sign in with PIV / ALT-PIV.
> (Also in `RUNBOOK-run-serio.md` under Hosted environments.)
> The account **password is not stored here** — put it in the automation KeePass (by entry title,
> e.g. `DevOps/FDA AD_APP ad_app_a.dourish`), never in this repo.

---

## The development environment

For reference, the SIRCE stack — the workstation runbook installs all of this:

| | |
|---|---|
| **Java** | 17 and 21 |
| **WebLogic** | 14.1.0 *(see note)* |
| **Node / npm** | Node 22.2.2 *(see note)* / npm 10.9.7 |
| **Maven** | any current version |
| **Eclipse** | any version — used for the **Java backend** |
| **VS Code** | used for the **Angular** front end (and Java too, if you prefer) |
| **SQL Developer** | any version |

> **Two version numbers in the request do not exist.** WebLogic **14.1.0** is not a real Oracle
> release (Oracle ships 14.1.1.0 and 14.1.2.0), and Node **22.2.2** is not a real release
> (22.2.x stops at 22.2.0). Both need confirming with the requester — this is tracked as an open
> question on FS-006. Do not treat the numbers above as verified.

**Open question:** the host `108.28.150.170:33890` appears in the same request with no
explanation. Nobody has confirmed what it is. Do not connect to it until someone does.

---

## Useful links

Both need you to be on the FDA network and signed in.

| Link | What it's for |
|------|---------------|
| [SIRCE ALM Hub (SharePoint)](https://fda.sharepoint.com/sites/OIMT-Imports-SIRCE-ALM-Hub) | The OIMT Imports SIRCE application-lifecycle hub — the team's SharePoint home. |
| [Elsa — token usage](https://elsa.fda.gov/beta/#/embed/token-usage) | How many tokens you have used against the Elsa AI models. |

More in the [repo README](../../README.md#useful-links).

---

## Support

Infrastructure and access: **Vijay Bhagwati**.

---

## Where this came from

Two FDA sources, combined:

- *"e3530 SOP for Privileged Accounts"*, version 3.0, dated 2024-05-14. Earlier versions:
  1.0 (2021-10-21), 2.0 (2021-11-02, which is where the SCAIL-vs-SIRCE naming note comes from).
- FDA Service Portal request **REQ1061439** (the software list and the SharePoint link).

Rewritten in plain English; the steps and values are unchanged. The original SOP has screenshots
of the e3530 form at several steps — not reproduced here.
