# Worker 1: Context Setup (Sections I-III)

**🚫 CRITICAL FILE ACCESS RESTRICTIONS 🚫**

Your data is **PRE-LOADED** in your prompt below. **ABSOLUTELY DO NOT**:
- ❌ Read `fs_index.json`
- ❌ Read `data_bundles.json`
- ❌ Read any `.json` files
- ❌ Use the Read tool for any data access
- ❌ Attempt to access the filesystem for metrics

**Why?** Your coordinator has already extracted and pre-loaded your specific data bundle. Reading files wastes time, duplicates work, and can cause errors.

**What to do instead**: Use the JSON data provided directly below in your prompt.

---

### 📂 **Optional: Deep-Dive Access** (10% of cases)

If you need additional context beyond the pre-loaded data, file paths are provided in your bundle under `source_files`:

**When to use**:
- ✅ Need complete company background (not just summary)
- ✅ Need full board of directors details
- ✅ Need all corporate governance information

**How to access** (ONLY if needed):
```python
# Read text_blocks.jsonl for specific pages
text_blocks = []
with open(text_blocks_path, 'r') as f:
    for line in f:
        block = json.loads(line)
        if block.get('page_number') in [1, 2, 3]:  # First 3 pages
            text_blocks.append(block)
```

**Note**: 90% of the time, the pre-loaded data is sufficient. Only access files when absolutely necessary.

---

You are responsible for writing the first three sections of the financial analysis report that establish context and scope.

## Your Sections

### Section Ⅰ: Company Profile (~100 words)

**Purpose**: Establish context for the analysis

**What to include**:
- Brief business description (what they do, not ticker symbols)
- Core segments and revenue mix
- Geographic footprint
- Market position (leader/challenger/niche)
- Recent strategic shifts (if material)

**How to write it**:
- Use information from the metadata provided in your data bundle
- Focus on what drives their economics
- Be specific about their competitive position

**Example**:
> Chin Hin Group is a leading building materials conglomerate in Malaysia, operating across three core segments: manufacturing (steel and cement), distribution (wholesale building materials), and property development. The company has integrated backward from trading into manufacturing, creating a value chain from raw materials to end customers. It holds market-leading positions in steel pipes and roofing materials in Peninsular Malaysia, with recent expansion into Sabah and Sarawak to capture East Malaysian growth.

**Common mistakes**:
- ❌ Generic description: "A public listed company in Malaysia"
- ❌ Copy-paste from website without synthesis
- ✅ Specific and analytical: Focus on business model

---

### Section Ⅱ: Analysis Purpose (~80 words)

**Purpose**: Define scope and set expectations

**What to include**:
- Period covered (e.g., "FY2024 annual report")
- Comparison basis (YoY, multi-year trend)
- Data sources (audited annual report, quarterly reports)
- Analytical focus (profitability, liquidity, growth, risk)
- Any limitations or caveats

**How to write it**:
- Be transparent about data availability
- Set realistic expectations
- Highlight any data quality issues upfront

**Example**:
> This analysis covers FY2024 (ended 31 December 2024) compared against FY2023, based on the audited annual report. The focus is on assessing profitability recovery post-pandemic, cash generation quality, and leverage sustainability following recent debt-funded expansion. All figures in RM'000 unless stated. Segment analysis is limited to reported classifications and may not reflect true economic profitability by business line.

---

### Section Ⅲ: Data Description (~60 words)

**Purpose**: Ensure clarity on units and definitions

**What to include**:
- Currency (e.g., RM, USD, SGD)
- Unit convention (thousands, millions)
- Fiscal year definition (calendar year vs. custom)
- Period length (annual vs. interim)
- Any restatements or accounting changes

**Example**:
> All monetary values are in RM'000 (Malaysian Ringgit thousands) unless otherwise indicated. The fiscal year ends on 31 December. This analysis covers the full-year period (12 months). Comparative figures for FY2023 have been restated following adoption of MFRS 17 for lease accounting.

---

## Your Data Bundle

You will receive a JSON object with:

```json
{
  "metadata": {
    "company_name": "Chin Hin Group Berhad",
    "period": "FY2024",
    "currency": "RM",
    "fiscal_year_end": "2024-12-31",
    "data_source": "Audited Annual Report"
  },
  "business_context": {
    "industry": "Building Materials",
    "segments": ["Manufacturing", "Distribution", "Property Development"],
    "geography": "Malaysia (Peninsular, Sabah, Sarawak)",
    "market_position": "Market leader in steel pipes and roofing materials"
  }
}
```

## Output Format

Write **ONLY** the markdown content for Sections I-III. Use this exact structure:

```markdown
# Ⅰ. Company Profile

[Your content here - 2-3 sentences describing the business]

# Ⅱ. Analysis Purpose

[Your content here - numbered list of 2-4 objectives]

# Ⅲ. Data Description

[Your content here - 1-2 sentences on currency, units, fiscal year]
```

## Quality Standards

- ✅ Be specific: Use actual company name, period, currency
- ✅ Be concise: Stay within word limits
- ✅ Be transparent: Acknowledge limitations
- ✅ Use data bundle: All facts should come from provided metadata

**Do NOT**:
- ❌ Invent facts not in the data bundle
- ❌ Write generic descriptions
- ❌ Exceed word limits significantly

## Task

Using the data bundle provided, write Sections I-III following the guidelines above.

**Output file**: `workspace/worker_1_sections.md`

Output ONLY the markdown for these three sections.
