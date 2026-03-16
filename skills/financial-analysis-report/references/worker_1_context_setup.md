# Worker 1: Company Overview (Section I)

## Data Access

Your data is **PRE-LOADED** in your prompt. Company metadata and financial data are in the JSON bundle below.

For qualitative context (business overview, corporate info, industry), read `text_blocks.jsonl` from the path in your bundle:

```python
import json
text_blocks = []
with open(text_blocks_path, 'r') as f:
    for line in f:
        text_blocks.append(json.loads(line))
```

**Do NOT** read `fs_index.json`, `data_bundles.json`, or any other `.json` files — your metrics are already provided.

---

You write the opening section that sets context for the entire report. Be concise and factual.

## Canonical Data Ownership

**You own**: Company profile, analysis purpose, data description.
**Do NOT restate**: Any financial metrics — those belong to Sections III, V, VII, VIII.

---

## Your Section

### Section I: Company Overview

**Purpose**: Establish context for the analysis — who is this company, why are we analyzing them, what data are we using.

**Structure** (3 sub-sections, ~30 lines total):

**Company Profile** (100-150 words):
- Company name and ticker
- Industry/sector
- Core business description
- Geographic footprint
- Market position

**Analysis Purpose** (50-100 words):
- Why this analysis is being conducted
- Key questions to answer
- Analytical focus areas
- Stakeholder perspective (investor, management, creditor)

**Data Description** (100-150 words):
- Data sources (annual reports, years covered)
- Metrics extracted (236 line items + calculated ratios)
- Currency and units
- Data quality notes
- Comparison period

**Example**:
```markdown
# Ⅰ. Company Overview

Chin Hin Group Berhad (CHINHIN:MK) is a leading Malaysian building materials conglomerate with operations across Peninsula Malaysia and East Malaysia. The company operates through three core divisions: construction materials (60% of revenue), property development (25%), and trading (15%). Chin Hin holds market-leading positions in concrete and steel fabrication, with an integrated supply chain from raw material sourcing to end-product delivery.

**Key operations**: Manufacturing, construction, property development
**Geographic focus**: Malaysia (Peninsula 70%, East Malaysia 30%)
**Market position**: Top 3 in Malaysian building materials sector

---

**Analysis Purpose**: This analysis evaluates Chin Hin's FY2024 financial performance to assess the company's growth trajectory, profitability sustainability, and financial health following its East Malaysia expansion. Key questions: (1) Is revenue growth translating to profit quality? (2) Can operating cash flow support expansion? (3) Are leverage levels manageable? The analysis is conducted from an equity investor perspective.

---

**Data Description**:
- **Sources**: Chin Hin Group Berhad Annual Report 2024 and 2023
- **Metrics**: 236 line items from balance sheet, income statement, and cash flow statement, plus 25+ calculated financial ratios
- **Currency**: Malaysian Ringgit (RM'000 unless otherwise stated)
- **Quality**: Audited, unqualified opinion. Extracted via finanalysis CLI with 100% accuracy.
- **Comparison**: YoY (FY2024 vs FY2023)
```

---

## Output Format

Write ONLY markdown for Section I.

## Task

Write Section I using the data bundle.

**Output file**: `workspace/worker_1_sections.md`

Output ONLY markdown for this section.
