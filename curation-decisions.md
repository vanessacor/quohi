# Curation Decisions for Milestone 5 Step 4

Generated from `scripts/fetch_events.py` live run.

---

## 9 Candidates from Wikidata (all ≤ 20, so all *can* be kept)

| # | QID | Title | Kind | Date | Coords | Sitelinks | Notes |
|---|-----|-------|------|------|--------|-----------|-------|
| 1 | **Q47672** | Terracotta Army | landmark | -248 | ✓ | 90 | |
| 2 | **Q1047061** | Giant Wild Goose Pagoda | landmark | 648 | ✓ | 37 | |
| 3 | **Q244941** | Xi'an Incident | event | 1936-12-12 | ✓ | 28 | |
| 4 | **Q1158530** | Daming Palace | landmark | 2010-10-01 | ✓ | 20 | ⚠️ Reconstruction date (original 634) |
| 5 | **Q275515** | Fenghao | landmark | **unreadable** (p7) | ✓ | 13 | ⚠️ No usable date |
| 6 | **Q5370929** | Daci'en Temple | landmark | 1466 | ✓ | 8 | |
| 7 | **Q11061833** | Guangren Temple | landmark | 1705 | ✓ | 6 | |
| 8 | **Q11065242** | Jianguomen (Xi'an) | landmark | 1939 | ✓ | 4 | |
| 9 | **Q10844449** | 2003 NWU controversy | event | 2003-10-29 | ✗ | 2 | ⚠️ No coordinates |

---

## 16 Existing Events → QID Mappings (fix wrong, add missing)

| # | Existing Title | Current Match | Issue / Suggested Fix |
|---|----------------|---------------|------------------------|
| 1 | Banpo Neolithic village inhabited | Q952372 "Banpo Neolithic signs" [approx] | **Wrong.** Correct: **Q790078 Banpo (archaeological site)** |
| 2 | Qin moves its capital to Xianyang | *no match* | Xianyang ≠ Xi'an. Keep? Need QID or drop. |
| 3 | Mausoleum of the First Qin Emperor built | Q910180 ✓ | Same as candidate Q47672 |
| 4 | Weiyang Palace built at Chang'an | Q3051521 ✓ | Not in candidates (lacks P571). **Add Q3051521?** |
| 5 | Zhang Qian departs on his mission to the west | *no match* | Need QID (Zhang Qian departure from Chang'an) |
| 6 | Tang dynasty founded with Chang'an as capital | *no match* | Need QID (Tang founding 618) |
| 7 | Big Wild Goose Pagoda built | Q1047061 ✓ | Same as candidate #2 |
| 8 | Small Wild Goose Pagoda completed | Q1194818 ✓ | Not in candidates (lacks P571). **Add Q1194818?** |
| 9 | Great Mosque of Xi'an founded | Q820842 ✓ | Not in candidates (lacks P571). **Add Q820842?** |
| 10 | Nestorian Stele erected | Q1554020 ✓ | Not in candidates (lacks P571). **Add Q1554020?** |
| 11 | Chang'an dismantled, capital to Luoyang | *no match* | Need QID (c. 25 CE?) |
| 12 | City renamed Xi'an under the Ming | *no match* | Need QID (1369) |
| 13 | Ming city wall built | **Q18169354 Ming City Rockers** ❌ | **Wrong!** Correct: **Q1542604 Xi'an City Wall** |
| 14 | Xi'an Incident | Q244941 ✓ | Same as candidate #3 |
| 15 | Terracotta Army discovered | Q47672 ✓ | Same as candidate #1 |
| 16 | Xi'an Metro opens its first line | *no match* | Need QID (2011?) |

---

## Recommended `scripts/config/curated.json` Structure

```json
{
  "selected": [
    "Q47672",
    "Q1047061",
    "Q244941",
    "Q1158530",
    "Q275515",
    "Q5370929",
    "Q11061833",
    "Q11065242",
    "Q10844449"
  ],
  "title_overrides": {
    "Banpo Neolithic village inhabited": "Q790078",
    "Qin moves its capital to Xianyang": "",
    "Mausoleum of the First Qin Emperor built": "Q910180",
    "Weiyang Palace built at Chang'an": "Q3051521",
    "Zhang Qian departs on his mission to the west": "",
    "Tang dynasty founded with Chang'an as capital": "",
    "Big Wild Goose Pagoda built": "Q1047061",
    "Small Wild Goose Pagoda completed": "Q1194818",
    "Great Mosque of Xi'an founded": "Q820842",
    "Nestorian Stele erected": "Q1554020",
    "Chang'an dismantled and capital moved to Luoyang": "",
    "City renamed Xi'an under the Ming": "",
    "Ming city wall built": "Q1542604",
    "Xi'an Incident": "Q244941",
    "Terracotta Army discovered": "Q47672",
    "Xi'an Metro opens its first line": ""
  },
  "extra_qids": [
    "Q3051521",
    "Q1194818",
    "Q820842",
    "Q1554020",
    "Q1542604"
  ]
}
```

---

## Decision Checklist

- [ ] **Candidates**: Keep all 9? Drop any? (max 20 total)
  drop 5 and 9
- [ ] **Fenghao (Q275515)**: Keep despite unreadable date? (enrichment step may add one)
  drop
- [ ] **Daming Palace (Q1158530)**: Keep with 2010 reconstruction date, or drop?
  keep
- [ ] **2003 NWU controversy (Q10844449)**: Keep despite no coordinates? (enrichment may find coords)
  drop
- [ ] **Existing events with no match**: Find QIDs or drop?
  - [ ] Qin moves capital to Xianyang
        drop
  - [ ] Zhang Qian departs
        keep
  - [ ] Tang dynasty founded
        keep
  - [ ] Chang'an dismantled → Luoyang
        keep
  - [ ] City renamed Xi'an under Ming
        drop
  - [ ] Xi'an Metro opens
        drop
- [ ] **Extra QIDs to add** (landmarks missing P571): Weiyang Palace, Small Wild Goose Pagoda, Great Mosque, Nestorian Stele, Xi'an City Wall
- [ ] **Any other QIDs** to add from knowledge?

---

## How to Proceed

1. Edit this file with your decisions
2. I'll write `scripts/config/curated.json` from your choices
3. Step 5 (`enrich_events.py`) will use the curated list

**Save your edited version** and I'll pick it up.