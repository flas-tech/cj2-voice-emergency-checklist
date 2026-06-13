# Pre-Filing Checklist — Provisional Patent Application (Patent Center)

> **NOT LEGAL ADVICE.** Prepared by an AI assistant, not a patent attorney. A provisional locks your priority date but is only as strong as its disclosure. Strongly consider a registered patent practitioner review before filing — especially for the entity-status, assignment, and prior-art items below.
>
> **DEMO/TRAINING POSTURE:** This product is positioned as DEMO/TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS. That does not affect patentability, but keep cert claims (NORSEE path, avoid DO-178) out of the patent and in your engineering/business docs.

---

## 0. TL;DR — can you file today?

**Yes, you *can* file a provisional today to lock the priority date** — the spec, 14 figures, and forms are drafted. But two decisions and one verification must happen first:

1. **Decide entity status** (Small $160 = safe, vs Micro $65 = needs LLC income certification). See `USPTO_Inventor_Applicant_Declaration.md` §B.
2. **Fill the [FILL] blanks** in the two form drafts (inventor residence, correspondence email, citizenship, title choice).
3. **Verify current fees** on uspto.gov (they change annually).

**Do NOT skip the new-feature prior-art search before the *nonprovisional*** — see §6. It does not block the provisional, but it is mandatory before you spend money on the nonprovisional.

---

## 1. Required documents (the upload set)

| # | Document | Status | File |
|---|---|---|---|
| 1 | **Specification** (the body — your disclosure) | ✅ drafted, sections 1–17 + claims 1–30 | `provisional_patent_application.md` → export to PDF |
| 2 | **Drawings** — FIG. 1–14 | ✅ generated | `figures/patent_figures.pdf` |
| 3 | **Cover Sheet PTO/SB/16** | ✅ draft (has [FILL]s) | `USPTO_SB16_Provisional_Cover_Sheet.md` → transcribe into official fillable PDF |
| 4 | **Micro-Entity Cert PTO/SB/15A** | ⛔ only if claiming MICRO | download blank from uspto.gov, fill if applicable |
| 5 | **Filing fee** | ⛔ pay at submission | $65 micro / $160 small / $320 large |

> A provisional does **NOT** require: claims (optional — yours are included as bonus disclosure), an inventor oath/declaration, or an Information Disclosure Statement. Those come at the nonprovisional stage.

---

## 2. Official form sources (download the live fillable PDFs)

- **PTO/SB/16** (cover sheet): https://www.uspto.gov/sites/default/files/documents/sb0016.pdf
- **PTO/SB/15A** (micro-entity, gross-income basis): https://www.uspto.gov/sites/default/files/documents/sb0015a.pdf
- **Current fee schedule** (37 CFR 1.16(d)): https://www.uspto.gov/learning-and-resources/fees-and-payment/uspto-fee-schedule
- **Current micro-entity income limit:** https://www.uspto.gov/patents/laws/micro-entity-status

---

## 3. Decisions to lock before filing

- [ ] **Title:** pick the long technical title or the short one — must match spec exactly (`SB16` §2).
- [ ] **Entity status:** Small (safe) vs Micro (needs LLC income test). (`Declaration` §B).
- [ ] **Pro se vs attorney:** filing yourself or through a registered practitioner?
- [ ] **Correspondence:** Customer Number, or direct address + valid email.
- [ ] **Inventor residence + citizenship** (Toronto reference vs South Florida — use actual).
- [ ] **Assignment** Gravalec → Flite Line Aviation Services, LLC drafted (attorney) — execute at/after filing.

---

## 4. Patent Center e-filing sequence (the actual steps)

> The USPTO retired EFS-Web. All e-filing is now via **Patent Center**: https://patentcenter.uspto.gov

1. **Create / log into** a USPTO.gov account with **two-step authentication**. (Set this up in advance — verification can take time.)
2. Select **"File a new application"** → **"Provisional application under 35 U.S.C. 111(b)"**.
3. **Enter application data** (Web ADS-style screens): inventor name + residence, applicant (Flite Line Aviation Services, LLC), correspondence, title, entity status.
4. **Upload documents** (PDF, text-searchable preferred):
   - Specification PDF
   - Drawings PDF (FIG. 1–14)
   - Cover sheet SB/16 PDF
   - SB/15A PDF (only if micro)
5. **Review the validation / page counts** Patent Center auto-generates.
6. **Calculate fees** → select entity status → confirm the provisional filing fee.
7. **Pay** (credit card, USPTO deposit account, or EFT).
8. **Submit** → download the **Acknowledgement Receipt** with your **application number and official filing date** = your **priority date**. Save it.

---

## 5. After filing — critical dates

- [ ] **Save the filing receipt** (application # + filing date).
- [ ] **12-month clock starts.** You must file a **nonprovisional (and/or PCT)** claiming priority within **12 months** of the provisional filing date, or you lose the priority benefit. Calendar this hard deadline.
- [ ] **Execute + record the assignment** (Gravalec → LLC) via EPAS.
- [ ] Decide on **PCT** if foreign protection is wanted (also within the 12-month window).

---

## 6. ⚠️ MANDATORY before the NONPROVISIONAL — new-feature prior-art search

The original prior-art search (26 references in `prior_art_findings.md`) covered the **lead novelties** (dual-isolated-channel, receive-only tap, dual-card cross-consistency, revert-to-unopened). It did **NOT** cover the 8 new features added this session. Each needs its own search before you invest in the nonprovisional:

- [ ] **Active output-injection safeguards** (keying-aware inhibit, mute-on-fault, output-isolation self-test, playback watchdog) — the previously-flagged **white-space gap**; search hardest here.
- [ ] **No-mask audio arbitration**
- [ ] **Crew readback verification**
- [ ] **Cryptographic card integrity / authentication**
- [ ] **Tamper-evident hash-chained audit trail**
- [ ] **Multi-aircraft / fleet data card**
- [ ] **Alternate isolation embodiments** (optical / capacitive / digital)
- [ ] **Non-aircraft / training embodiments**

> Treat the new features as **combination-claim material** layered on the lead novelties rather than standalone claims, unless a search shows clear white space. Active patents to keep distinguishing: **Boeing US7289890B2, Honeywell US9550578B2 (expires 2034), Collins US11829589B2.** Expired/free-to-practice: **Garmin US7912592B2 / US20070288129A1**.

---

## 7. Trademark (parallel track, not part of the patent)

- ✅ **AviVox** — recommended commercial mark (clear).
- ⛔ **VoxPilot** — AVOID (conflicts with Reg. No. 4551726).
- "CheckM8" — fine as a project/docket reference; keep brand names out of the patent spec/title.

---

## 8. What an AI assistant CANNOT do for you

- Cannot file the application (requires your USPTO.gov account + signature).
- Cannot give legal advice or act as your attorney.
- Cannot certify entity status or sign forms on your behalf.
- Cannot guarantee patentability — only a search + examiner can.
