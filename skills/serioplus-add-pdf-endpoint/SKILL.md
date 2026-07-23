---
name: serioplus-add-pdf-endpoint
description: Add a new PDF-generating endpoint to the SERIO+ document service (Thymeleaf -> HTML -> iText). Use when building any "generate a memo/report/notice PDF" feature in SERIOPlusDataServices. Covers the DTO, service, controller, template, auth whitelist, and the wiring you must not forget. Modelled on the OGA report and the SERIO-39310 seizure memo.
metadata:
  version: "1.0.0"
  repository: fda-serio
  last_updated: "2026-07-17"
  type: reference
---

# SERIO+ — add a PDF-generating endpoint

**The repeatable recipe for "click a button → generate a PDF" in SERIO+.** SERIO+ renders a
**Thymeleaf** HTML template from a data DTO, converts it to a PDF with **iText `html2pdf`**, and
streams it back (and/or stores it in S3/DRMS). Copy the OGA report; don't invent a new pipeline.

> Built proof: the seizure memo (SERIO-39310) — design in
> [`docs/features/FS-018-serioplus-seizure-memo-pdf.md`](../../docs/features/FS-018-serioplus-seizure-memo-pdf.md),
> scaffold + patches in [`handoff/serio-39310/`](../../handoff/serio-39310/). To run/build it, use
> the [`serioplus-local-run`](../serioplus-local-run/SKILL.md) skill.

---

## Quick reference

**Use when:** adding a document/memo/report PDF endpoint to `serioplus-document-service`.
**Analog to copy:** `OGAReportPDFService` + `OGA-template.html` (single template, simplest). For
batch/high-volume, `PrintNoticePDFService`.
**Home:** `SERIOPlusDataServices/serioplus-document-service`, package `gov.fda.oii.serioplus.dataservice`.

---

## The 6 pieces (and the 3 that are easy to forget)

| # | Piece | Where |
|---|-------|-------|
| 1 | **DTO** — the data the template needs. **Compose existing DTOs**, don't duplicate fields. | `SERIOPlusCommonLibraries/.../common/dto/<area>/XxxDto.java` |
| 2 | **Service** — build a Thymeleaf `Context`, `templateEngine.process(name, ctx)` → HTML → `HtmlConverter.convertToPdf(html, out, props)`. **License-gate first** with `ITextLicenseService.validateLicense()`. | `.../service/XxxPDFService.java` |
| 3 | **Controller** — `@PostMapping("/api/generate-xxx")` returning `ResponseEntity<InputStreamResource>` as an attachment. | `.../controller/XxxController.java` |
| 4 | **Template** — `.../resources/templates/pdf/xxx-template.html` (Thymeleaf; `th:each`, `th:text`). | resources |
| ⚠️5 | **Auth whitelist** — add `/api/generate-xxx` to `noUserApis` in `FilterConfig` **if the endpoint doesn't need a user** (like OGA). Skip this → **403**. | `.../configuration/FilterConfig.java` |
| ⚠️6 | **persistence.xml** — only if you touch a JPA repo: register any common-lib entity in `META-INF/persistence.xml` (`<class>…</class>`). Skip → `No [ManagedType]` at boot. | resources |

**The two "forgets" that cost hours** (both hit on SERIO-39310):
- Not adding the path to `noUserApis` → 403 (looks like an auth problem, is a wiring problem).
- Missing controller in the built jar → 404 *"No static resource api/…"* — usually because the
  scaffold files weren't on the branch you built. Verify with `jar tf <jar> | Select-String Xxx`.

---

## Font gotcha — don't scan system fonts
In the converter, use the project's **bundled Arial** (fast) — not `new DefaultFontProvider(true, true, true)`, whose system-font scan makes the **first** conversion hang ~30-60s:
```java
FontProvider fp = new FontProvider();
fp.addFont(FontProgramFactory.createFont("/templates/fonts/Arial-Regular.ttf"));
fp.addFont(FontProgramFactory.createFont("/templates/fonts/Arialbd-Bold.ttf"));
fp.addFont(FontProgramFactory.createFont("/templates/fonts/Ariali-Itaclic.ttf"));
fp.addFont(FontProgramFactory.createFont("/templates/fonts/Arialbi-Bold-Italic.ttf"));
ConverterProperties props = new ConverterProperties();
props.setFontProvider(fp); props.setCharset("UTF-8");
HtmlConverter.convertToPdf(html, outputStream, props);
```

## Controller shape (mirror OGAController)
```java
@Controller @CrossOrigin(origins="*") @RequestMapping(path="/api")
public class XxxController {
  @Autowired private XxxPDFService svc;
  @PostMapping("/generate-xxx")
  public ResponseEntity<InputStreamResource> generate(@RequestBody XxxDto dto) {
    try (ByteArrayOutputStream out = new ByteArrayOutputStream()) {
      svc.generateXxxPDF(dto, out);
      var isr = new InputStreamResource(new ByteArrayInputStream(out.toByteArray()));
      var headers = new HttpHeaders();
      headers.setContentDispositionFormData("attachment", svc.buildFileName(dto));
      headers.setContentType(DocumentManagementService.determineMediaTypeFromFilename("x.pdf"));
      return new ResponseEntity<>(isr, headers, HttpStatus.OK);
    } catch (IOException e) { throw new SerioPlusSystemException("...", e); }
  }
}
```

## Test it
Endpoint (document-service): `POST http://localhost:8095/serioplus/ds/document-data-service/api/generate-xxx`.
Build + run + POST a sample DTO — see [`serioplus-local-run`](../serioplus-local-run/SKILL.md).
Expected: **200 + `application/pdf`**, or **500 "iText license validation failed"** (license path — a
wiring win), or your own validation 400/500 (reached correctly).

## Design questions to confirm with the team
- Should the endpoint really skip the user check (`noUserApis`), or capture the logged-in user from
  the token? (For the seizure memo we whitelisted it to match OGA — flagged for review.)
- The **exact template** should come from the customer/working-group file (SharePoint), not a
  placeholder — see [`docs/runbooks/RUNBOOK-sharepoint-access.md`](../../docs/runbooks/RUNBOOK-sharepoint-access.md).
- Storage: stream-only, or S3 + DRMS like the notice pipeline.
