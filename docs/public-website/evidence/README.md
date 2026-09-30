# Lighthouse mobile evidence

- Audited source commit: `2162745a4537cc1034d54264330c68d693348b13`
- Runtime: local preview served with `npx --yes serve -l 3000`
- Performance: **100**
- Accessibility: **100**
- Best Practices: **96**
- SEO: **91**
- FCP: **0.7 s**
- LCP: **0.7 s**
- TBT: **10 ms**
- CLS: **0**

Permanent evidence:
- Screenshot: `docs/public-website/evidence/lighthouse-mobile.png`
- Raw Lighthouse report: `docs/public-website/evidence/lighthouse-mobile.report.json`

The official 4Geeks rubric requires Performance ≥80 and explicitly allows Chrome/Lighthouse evidence when PageSpeed Insights cannot reach the preview. During final verification, PageSpeed's external run could not complete reliably, so this accepted fallback was used. The audited source matches the website code in the delivery branch; the subsequent evidence-only commits do not alter the site.
