---
name: salesforce-development
description: Salesforce development for the BPHC/HRSA orgs — Apex classes and triggers, Lightning Web Components, SOQL/SOSL, field-level security, the REST API, deployments with sf CLI or sfsync, cache busting, and Apex test patterns. Use for "write an LWC", "add an Apex class", "deploy to the org", "query the org", "fix FLS", or any request naming Apex, LWC, SOQL, a sandbox, or an sf CLI command.
---

# Salesforce Development

Target org and team conventions come from the project's own `CLAUDE.md` (for BPHC-GAM2010 that
is the `team` repo). This skill is the reference library.

## Pick the guide

| Task | Guide |
|------|-------|
| Apex + LWC workflows, project structure | `development/skill_salesforce_development.md` |
| LWC components, SLDS, templates | `development/skill_lwc_development.md` |
| Apex test classes, coverage, assertions | `development/skill_apex_testing.md` |
| SOQL / SOSL query patterns | `development/skill_soql_sosl.md` |
| Field-level security automation | `development/skill_salesforce_fls_automation.md` |
| Salesforce REST API | `development/skill_salesforce_rest_api.md` |
| Deploying (sf CLI) | `development/skill_salesforce_deployment.md` |
| Deploying with sfsync | `development/skill_sfsync_deployment.md` (script: `_scripts/sfsync.ps1`) |
| Stale metadata / cached components after deploy | `development/skill_salesforce_cache_busting.md` |
| Developer activity reporting | `development/skill_salesforce_developer_activity_report.md` |
| Definition of Done before you call it finished | `development/skill_dev_complete.md` |

Copado CI/CD is its own skill — see `copado-cicd`.

## House rules that bite

- **Relationships:** lookup only on custom objects, never master-detail.
- **Accessibility:** every UI change must pass Section 508 / WCAG — see the `section-508` skill.
  Never use red/green as the only signal; the palette is cyan / yellow / magenta.
- **Org logins** come from the KeePass vault (`Salesforce/...` group), never from a file.
