# Assessment & Proposal: Autonomous Competitor Discovery

## Does the current system search the ENTIRE internet for NEW competitors?

**NO.**
The current system is a **Targeted Intelligence Engine**, not an **Autonomous Discovery Engine**. It excels at monitoring *known* entities (provided by you or the database) but does not actively crawl the open web to identify *unknown* competitors from scratch.

- **Current State**: It scrapes specific URLs you provide or looks up specific company names in news feeds (e.g., "Find news for Phreesia").
- **Missing Capability**: It lacks a reliable "Discovery Loop" that searches for generic terms (e.g., "Patient Intake Startups") and qualifies them against Certify Health's business model.

---

## Proposal: The "Certify Scout" Discovery Engine

To achieve 100% autonomous discovery, we need to implement a new backend module (e.g., `discovery_agent.py`) that executes the following **Search -> Qualify -> Extract** loop:

### 1. The "Certify Health" Context Core

We must first digitize Certify Health's identity so the AI knows what it's looking for.

- **Input**: A structured profile (e.g., `certify_context.json`).
- **Content**:
  - **Core Solutions**: "Patient Intake, Digital Registration, Biomedical ID, Revenue Cycle Management".
  - **Target Market**: "Large Health Systems, Ambulatory Centers".
  - **Exclusions**: "Pharmaceuticals, Insurance Providers" (to avoid false positives).

### 2. Autonomous Search Layer (The "Broad Net")

Instead of searching for *companies*, the system will search for *problems* and *solutions*.

- **Tools**: Google Custom Search API, Bing Search API, or Serper.dev.
- **Dynamic Queries**: The AI generates queries such as:
  - "Top patient intake software 2025"
  - "Competitors to Phreesia and Kyruus"
  - "New digital health startups in revenue cycle"
  - "Biometric patient authentication vendors"

### 3. The Intelligent Qualification Gate (The "Filter")

This is the critical "AI Reasoning" step to ensure accuracy.

- **Action**: For every new URL found:
    1. **Scrape**: Lightly scrape the homepage and "About" page.
    2. **Analyze (LLM)**: Feed the scraped text + `certify_context.json` to GPT-4.
    3. **Prompt**: "Does this company offering compete with Certify Health's core solutions? Answer YES/NO and provide a 'Threat Score' (0-100)."
    4. **Decision**:
        - **Score < 50**: Ignore (Irrelevant).
        - **Score > 80**: **NEW COMPETITOR DETECTED**.

### 4. Integration & Tracking

- **Auto-Add**: Automatically create a database entry for the new company with `status="Detected"`.
- **Deep Dive**: Trigger the existing `CompetitorScraper` to build the full profile (Stock, Pricing, Products).
- **Alert**: Send a webhook/email to the Admin: "New Competitor Discovered: [Company Name] - 85% Match".

### Implementation Roadmap

1. **Phase 1 (Setup)**: Create `certify_context.json` and obtain a Search API Key (SerpApi).
2. **Phase 2 (Agent)**: Build `discovery_agent.py` to run weekly search jobs.
3. **Phase 3 (AI Logic)**: Implement the "Qualification Gate" using OpenAI.
4. **Phase 4 (UI)**: Add a "Discovered" tab to the dashboard to review AI findings.

This architecture turns the system from a **Monitor** into a true **Hunter**.
