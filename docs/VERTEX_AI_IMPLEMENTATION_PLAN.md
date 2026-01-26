# Vertex AI Integration Plan for Certify Intel

## Comprehensive Implementation Strategy

**Version:** v5.3.0-VERTEX
**Date:** January 26, 2026
**Status:** PROPOSED (Pending Approval)

---

## Executive Summary

This plan outlines the integration of Google Cloud Vertex AI into Certify Intel to enhance competitive intelligence capabilities with enterprise-grade AI features. The migration from the consumer Google AI SDK (`google-generativeai`) to Vertex AI will unlock:

- **Enterprise Security:** VPC Service Controls, CMEK encryption, HIPAA compliance
- **RAG Engine:** Grounded responses from competitor knowledge bases
- **Agent Builder:** Autonomous competitive intelligence agents
- **Vector Search:** Semantic search across competitor data
- **Model Fine-Tuning:** Custom models trained on healthcare competitive intelligence
- **Multi-Agent Systems:** Coordinated agents for research, analysis, and reporting

**Estimated Effort:** 6-8 weeks across 5 phases
**ROI:** Enhanced accuracy, reduced hallucinations, enterprise compliance, automated intelligence gathering

---

## Research Summary

### Sources Consulted

| Source | Key Information |
|--------|-----------------|
| Vertex AI Platform | Core platform capabilities, 200+ models |
| Vertex AI RAG Engine | RAG architecture, grounding, Vector Search |
| Vertex AI Agent Builder | Agent development, MCP support, ADK |
| Vertex AI for Healthcare | HIPAA compliance, MedLM, healthcare search |
| Vertex AI Security Controls | VPC-SC, CMEK, audit logging, data residency |
| Vertex AI Pricing | Token costs, enterprise features pricing |
| Vertex AI Fine-Tuning | SFT for Gemini 2.5/3, preference tuning |

### Key Vertex AI Capabilities (2025-2026)

| Capability | Description | Certify Intel Application |
|------------|-------------|---------------------------|
| Gemini 3 Flash | State-of-the-art reasoning, agentic problems | Complex competitor analysis |
| RAG Engine | Managed retrieval-augmented generation | Ground responses in competitor knowledge base |
| Vector Search | Hybrid search with sparse/dense embeddings | Semantic competitor document search |
| Agent Builder | Build autonomous AI agents | Auto-research, monitoring agents |
| MCP Support | Model Context Protocol for tool integration | Connect agents to scrapers, databases |
| Agent Memory | Short-term and long-term agent memory (GA) | Persistent research context |
| Model Garden | 200+ models including DeepSeek-V3.2 | Multi-model competitive analysis |
| HIPAA Compliance | Healthcare data protection | Certify Health data security |
| VPC Service Controls | Network isolation | Enterprise deployment |
| Fine-Tuning | SFT for Gemini 2.5 Pro/Flash | Custom CI extraction model |

---

## Current State vs. Proposed State

### Current Implementation (Google AI SDK)

```
┌─────────────────────────────────────────────────────────┐
│                 CURRENT ARCHITECTURE                     │
├─────────────────────────────────────────────────────────┤
│  backend/gemini_provider.py                             │
│  ├── Uses: google-generativeai SDK                      │
│  ├── Auth: GOOGLE_AI_API_KEY (API key)                  │
│  ├── Models: gemini-2.5-flash, gemini-2.5-pro           │
│  ├── Features: Text, multimodal, grounding (limited)    │
│  └── Security: Basic API key authentication             │
│                                                          │
│  Limitations:                                            │
│  ✗ No RAG Engine (custom implementation required)       │
│  ✗ No Vector Search (semantic search limited)           │
│  ✗ No Agent Builder (manual orchestration)              │
│  ✗ No VPC Service Controls (public API only)            │
│  ✗ No fine-tuning support (API deprecation)             │
│  ✗ No audit logging (limited visibility)                │
│  ✗ No HIPAA BAA available                               │
└─────────────────────────────────────────────────────────┘
```

### Proposed Implementation (Vertex AI)

```
┌─────────────────────────────────────────────────────────┐
│                 PROPOSED ARCHITECTURE                    │
├─────────────────────────────────────────────────────────┤
│  backend/vertex_ai_provider.py (NEW)                    │
│  ├── Uses: google-cloud-aiplatform SDK                  │
│  ├── Auth: Service Account / ADC                        │
│  ├── Models: Gemini 3/2.5, MedLM, DeepSeek, custom      │
│  └── Security: VPC-SC, CMEK, IAM, audit logging         │
│                                                          │
│  backend/vertex_rag_engine.py (NEW)                     │
│  ├── RAG Corpus management                              │
│  ├── Vector Search integration                          │
│  ├── Grounded generation                                │
│  └── Multi-corpus competitor knowledge bases            │
│                                                          │
│  backend/vertex_agent_builder.py (NEW)                  │
│  ├── Competitive Intelligence Agent                     │
│  ├── News Monitoring Agent                              │
│  ├── Research Agent with MCP tools                      │
│  └── Agent memory and sessions                          │
│                                                          │
│  Benefits:                                               │
│  ✓ RAG Engine with grounded responses                   │
│  ✓ Vector Search for semantic competitor search         │
│  ✓ Agent Builder for autonomous intelligence            │
│  ✓ VPC Service Controls for enterprise security         │
│  ✓ Fine-tuning for custom CI models                     │
│  ✓ Comprehensive audit logging                          │
│  ✓ HIPAA BAA for healthcare compliance                  │
└─────────────────────────────────────────────────────────┘
```

---

## Integration Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CERTIFY INTEL + VERTEX AI                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐     ┌──────────────────┐     ┌─────────────────┐  │
│  │   Frontend SPA   │────▶│   FastAPI        │────▶│  Vertex AI      │  │
│  │   (Existing)     │     │   Backend        │     │  Platform       │  │
│  └──────────────────┘     └──────────────────┘     └─────────────────┘  │
│                                   │                         │            │
│                                   ▼                         ▼            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    VERTEX AI SERVICES                             │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │   │
│  │  │ Gemini 3    │  │ RAG Engine  │  │ Agent       │               │   │
│  │  │ Flash/Pro   │  │             │  │ Builder     │               │   │
│  │  │             │  │ ┌─────────┐ │  │             │               │   │
│  │  │ • Analysis  │  │ │ Vector  │ │  │ • CI Agent  │               │   │
│  │  │ • Summary   │  │ │ Search  │ │  │ • News      │               │   │
│  │  │ • Extraction│  │ │         │ │  │ • Research  │               │   │
│  │  │ • Multimodal│  │ └─────────┘ │  │ • Monitor   │               │   │
│  │  └─────────────┘  │             │  └─────────────┘               │   │
│  │                   │ ┌─────────┐ │         │                      │   │
│  │                   │ │ Corpus  │ │         │                      │   │
│  │  ┌─────────────┐  │ │ Per     │ │  ┌──────▼──────┐               │   │
│  │  │ Fine-Tuned  │  │ │Competitor│ │  │ MCP Tools   │               │   │
│  │  │ CI Model    │  │ └─────────┘ │  │             │               │   │
│  │  │             │  └─────────────┘  │ • Scrapers  │               │   │
│  │  │ Trained on: │                   │ • Database  │               │   │
│  │  │ • Battlecards│                  │ • News APIs │               │   │
│  │  │ • Dimensions │                  │ • SEC/USPTO │               │   │
│  │  │ • Extraction │                  └─────────────┘               │   │
│  │  └─────────────┘                                                 │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    SECURITY & COMPLIANCE                          │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │  • VPC Service Controls  • CMEK Encryption  • Audit Logging      │   │
│  │  • IAM Policies          • Data Residency   • HIPAA BAA          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Feature Integration Plan

### A. Enhance Existing Features

#### 1. AI Extraction Enhancement (gemini_provider.py → vertex_ai_provider.py)

| Current Feature | Vertex AI Enhancement |
|-----------------|----------------------|
| Text extraction | RAG-grounded extraction with competitor corpus |
| Multimodal analysis | Gemini 3 Flash for superior image/video analysis |
| Executive summaries | Grounded summaries citing competitor documents |
| Dimension scoring | Fine-tuned model for healthcare CI dimensions |

**Implementation:**

```python
# backend/vertex_ai_provider.py (NEW)
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview import rag

class VertexAIProvider:
    """Enterprise Vertex AI provider replacing google-generativeai."""

    def __init__(self, project_id: str, location: str = "us-central1"):
        aiplatform.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-3-flash")
        self.rag_corpus = None

    def extract_with_grounding(self, text: str, competitor_id: int) -> dict:
        """Extract competitor data grounded in RAG corpus."""
        # Use competitor-specific corpus for grounded extraction
        rag_resource = rag.RagResource(
            rag_corpus=f"projects/{self.project_id}/locations/{self.location}/ragCorpora/competitor_{competitor_id}"
        )
        response = self.model.generate_content(
            text,
            tools=[rag.Retrieval(source=rag_resource)]
        )
        return self._parse_grounded_response(response)
```

#### 2. News Monitor Enhancement

| Current Feature | Vertex AI Enhancement |
|-----------------|----------------------|
| Sentiment analysis | MedLM for healthcare-specific sentiment |
| News aggregation | Agent-based autonomous news monitoring |
| Dimension tagging | Vector Search for semantic dimension matching |

**Implementation:**

```python
# Enhance news_monitor.py with Vertex AI
class VertexNewsMonitor:
    """News monitoring with Vertex AI Vector Search."""

    async def semantic_dimension_match(self, article_text: str) -> List[DimensionMatch]:
        """Use Vector Search to match articles to dimensions."""
        # Embed article
        embedding = self.embedding_model.get_embeddings([article_text])

        # Search dimension corpus
        results = self.vector_search_index.find_neighbors(
            deployed_index_id="dimension_index",
            queries=embedding,
            num_neighbors=3
        )
        return [DimensionMatch(dim_id=r.id, score=r.distance) for r in results]
```

#### 3. Battlecard Generator Enhancement

| Current Feature | Vertex AI Enhancement |
|-----------------|----------------------|
| Static templates | RAG-grounded dynamic content |
| Manual updates | Agent-triggered auto-updates |
| Single competitor | Multi-competitor comparison with grounding |

**Implementation:**

```python
# Enhance battlecard_generator.py
class VertexBattlecardGenerator:
    """Battlecards grounded in competitor RAG corpus."""

    def generate_grounded_battlecard(self, competitor_id: int) -> Battlecard:
        """Generate battlecard with citations from competitor corpus."""
        rag_resource = self._get_competitor_corpus(competitor_id)

        prompt = """Generate a sales battlecard for this competitor.
        For each claim, provide a citation from the retrieved documents.
        Include: key weaknesses, objection handlers, killer questions."""

        response = self.model.generate_content(
            prompt,
            tools=[rag.Retrieval(source=rag_resource, similarity_top_k=10)]
        )
        return self._build_battlecard_with_citations(response)
```

#### 4. Win/Loss Tracker Enhancement

| Current Feature | Vertex AI Enhancement |
|-----------------|----------------------|
| Manual logging | Agent-assisted deal analysis |
| Dimension correlation | Predictive win probability |
| Static reports | RAG-grounded deal insights |

---

### B. New Features with Vertex AI

#### 1. RAG-Powered Competitor Knowledge Base

**Purpose:** Create persistent, searchable knowledge bases per competitor that ground all AI responses.

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│              RAG CORPUS PER COMPETITOR                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Competitor: Epic Systems                                │
│  Corpus ID: competitor_epic_systems                      │
│                                                          │
│  Documents Indexed:                                      │
│  ├── SEC Filings (10-K, 10-Q, 8-K)                      │
│  ├── News Articles (last 12 months)                     │
│  ├── G2/Glassdoor Reviews                               │
│  ├── Product Documentation                              │
│  ├── Press Releases                                     │
│  ├── Patent Filings                                     │
│  ├── KLAS Reports                                       │
│  └── HIMSS Conference Materials                         │
│                                                          │
│  Vector Index: Hybrid (dense + sparse)                  │
│  Embedding Model: textembedding-gecko@003               │
│  Chunk Size: 512 tokens with overlap                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

```python
# backend/vertex_rag_engine.py (NEW)
from vertexai.preview import rag

class CompetitorRAGEngine:
    """Manage RAG corpora for competitor intelligence."""

    def create_competitor_corpus(self, competitor_id: int, competitor_name: str) -> str:
        """Create a new RAG corpus for a competitor."""
        corpus = rag.create_corpus(
            display_name=f"competitor_{competitor_id}_{competitor_name.lower().replace(' ', '_')}",
            description=f"Competitive intelligence corpus for {competitor_name}"
        )
        return corpus.name

    def ingest_documents(self, corpus_name: str, documents: List[Document]):
        """Ingest competitor documents into corpus."""
        for doc in documents:
            rag.import_files(
                corpus_name=corpus_name,
                paths=[doc.path],
                chunk_size=512,
                chunk_overlap=100
            )

    def query_with_grounding(self, corpus_name: str, query: str) -> GroundedResponse:
        """Query corpus with grounded generation."""
        rag_resource = rag.RagResource(rag_corpus=corpus_name)
        response = self.model.generate_content(
            query,
            tools=[rag.Retrieval(
                source=rag_resource,
                similarity_top_k=10,
                vector_distance_threshold=0.5
            )]
        )
        return self._extract_grounded_response(response)
```

**API Endpoints:**

```
POST /api/vertex/rag/corpus/create          # Create competitor corpus
POST /api/vertex/rag/corpus/{id}/ingest     # Ingest documents
POST /api/vertex/rag/corpus/{id}/query      # Query with grounding
GET  /api/vertex/rag/corpus/{id}/documents  # List indexed documents
DELETE /api/vertex/rag/corpus/{id}          # Delete corpus
```

#### 2. Competitive Intelligence Agent

**Purpose:** Autonomous agent that continuously monitors competitors and generates intelligence.

**Agent Capabilities:**
- Autonomous web research using MCP tools
- News monitoring and alerting
- Document analysis and extraction
- Battlecard auto-updates
- Dimension score suggestions
- Threat level assessment

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│           COMPETITIVE INTELLIGENCE AGENT                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Agent Type: Research & Analysis                         │
│  Model: Gemini 3 Flash (agentic reasoning)              │
│  Memory: Long-term (Agent Engine Memory Bank)           │
│                                                          │
│  MCP Tools Connected:                                    │
│  ├── WebScraperTool (Firecrawl integration)             │
│  ├── SECFilingTool (SEC EDGAR API)                      │
│  ├── NewsSearchTool (GNews, MediaStack, NewsData)       │
│  ├── PatentSearchTool (USPTO API)                       │
│  ├── DatabaseTool (SQLite competitor data)              │
│  ├── GoogleSearchTool (real-time grounding)             │
│  └── RAGQueryTool (competitor corpus)                   │
│                                                          │
│  Scheduled Tasks:                                        │
│  ├── Daily: News scan for all competitors               │
│  ├── Weekly: Deep research on high-threat competitors   │
│  ├── Monthly: Full battlecard refresh                   │
│  └── On-demand: User-triggered research                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

```python
# backend/vertex_agent_builder.py (NEW)
from vertexai.preview import agent_builder
from vertexai.preview.agent_builder import Agent, Tool, Session

class CompetitiveIntelligenceAgent:
    """Autonomous CI agent using Vertex AI Agent Builder."""

    def __init__(self, project_id: str):
        self.agent = Agent(
            model="gemini-3-flash",
            system_instruction="""You are a competitive intelligence analyst for Certify Health.
            Your role is to research competitors in the healthcare IT space, analyze their
            strengths and weaknesses across 9 competitive dimensions, and provide actionable
            insights for sales and marketing teams.

            The 9 dimensions are:
            1. Product Modules & Packaging
            2. Interoperability & Integration Depth
            3. Customer Support & Service Model
            4. Retention & Product Stickiness
            5. User Adoption & Ease of Use
            6. Implementation & Time to Value
            7. Reliability & Enterprise Readiness
            8. Pricing Model & Commercial Flexibility
            9. Reporting & Analytics Capability

            Always cite your sources and provide confidence levels.""",
            tools=[
                self._create_web_scraper_tool(),
                self._create_sec_filing_tool(),
                self._create_news_search_tool(),
                self._create_database_tool(),
                self._create_rag_query_tool()
            ]
        )
        self.memory = agent_builder.MemoryBank()

    async def research_competitor(self, competitor_name: str) -> ResearchReport:
        """Conduct comprehensive competitor research."""
        session = Session(memory=self.memory)

        response = await self.agent.send_message(
            session=session,
            message=f"""Research {competitor_name} comprehensively:
            1. Find recent news and announcements (last 30 days)
            2. Analyze their product offerings and pricing
            3. Review customer feedback from G2, Glassdoor, KLAS
            4. Check SEC filings for financial health
            5. Identify patents for technology insights
            6. Score them on all 9 competitive dimensions
            7. Generate talking points for sales team

            Provide a structured report with citations."""
        )

        return self._parse_research_report(response)

    async def monitor_news(self, competitor_ids: List[int]) -> List[Alert]:
        """Monitor news for specified competitors."""
        alerts = []
        for competitor_id in competitor_ids:
            response = await self.agent.send_message(
                message=f"Check for breaking news about competitor {competitor_id}. "
                        f"Flag anything related to: product launches, pricing changes, "
                        f"leadership changes, funding, partnerships, or customer wins/losses."
            )
            if response.has_alerts:
                alerts.extend(self._parse_alerts(response))
        return alerts
```

**API Endpoints:**

```
POST /api/vertex/agent/research/{competitor_id}    # Trigger research
POST /api/vertex/agent/monitor/start               # Start monitoring
POST /api/vertex/agent/monitor/stop                # Stop monitoring
GET  /api/vertex/agent/alerts                      # Get pending alerts
POST /api/vertex/agent/chat                        # Interactive chat with agent
GET  /api/vertex/agent/memory/{session_id}         # Get agent memory
```

#### 3. Vector Search for Semantic Competitor Queries

**Purpose:** Enable natural language queries across all competitor data.

**Use Cases:**
- "Which competitors have weak integration with Epic?"
- "Find all mentions of AI pricing models"
- "Show me competitors struggling with implementation times"
- "Who has the best customer support reviews?"

**Implementation:**

```python
# backend/vertex_vector_search.py (NEW)
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel

class CompetitorVectorSearch:
    """Semantic search across competitor intelligence."""

    def __init__(self, project_id: str, index_endpoint: str):
        self.embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
        self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint)

    def semantic_search(self, query: str, filters: dict = None) -> List[SearchResult]:
        """Search competitor data semantically."""
        # Generate query embedding
        query_embedding = self.embedding_model.get_embeddings([query])[0].values

        # Search with optional filters
        response = self.index_endpoint.find_neighbors(
            deployed_index_id="competitor_data_index",
            queries=[query_embedding],
            num_neighbors=20,
            filter=self._build_filter(filters) if filters else None
        )

        return self._format_results(response)

    def find_similar_competitors(self, competitor_id: int) -> List[Competitor]:
        """Find competitors similar to a given one based on profile embeddings."""
        # Get competitor profile embedding
        profile_embedding = self._get_competitor_embedding(competitor_id)

        # Find similar
        response = self.index_endpoint.find_neighbors(
            deployed_index_id="competitor_profile_index",
            queries=[profile_embedding],
            num_neighbors=5
        )

        return self._load_competitors(response)
```

**API Endpoints:**

```
POST /api/vertex/search/semantic           # Natural language search
POST /api/vertex/search/similar/{id}       # Find similar competitors
POST /api/vertex/search/dimension/{dim}    # Search by dimension
GET  /api/vertex/search/index/status       # Index health status
```

#### 4. Fine-Tuned Competitive Intelligence Model

**Purpose:** Train a custom Gemini model specifically for healthcare competitive intelligence extraction.

**Training Data:**
- Historical battlecards (labeled)
- Dimension scoring examples
- Competitor extraction examples
- Healthcare terminology dataset

**Implementation Plan:**

```python
# backend/vertex_fine_tuning.py (NEW)
from vertexai.preview.tuning import sft

class CIModelTuner:
    """Fine-tune Gemini for competitive intelligence tasks."""

    def prepare_training_data(self) -> str:
        """Prepare JSONL training data from existing battlecards."""
        training_examples = []

        # Example: Dimension scoring
        training_examples.append({
            "input": "Review: 'Epic's implementation took 18 months and required extensive customization'",
            "output": json.dumps({
                "dimension": "implementation_ttv",
                "score": 2,
                "evidence": "18-month implementation with extensive customization indicates slow TTV",
                "confidence": "high"
            })
        })

        # Export to Cloud Storage
        return self._upload_to_gcs(training_examples)

    def start_tuning_job(self, training_data_uri: str) -> str:
        """Start supervised fine-tuning job."""
        tuning_job = sft.train(
            source_model="gemini-2.5-flash",
            train_dataset=training_data_uri,
            tuned_model_display_name="certify-intel-ci-model",
            epochs=3,
            learning_rate_multiplier=1.0
        )
        return tuning_job.name
```

#### 5. Enterprise Security & Compliance

**Features:**
- VPC Service Controls for network isolation
- Customer-Managed Encryption Keys (CMEK)
- Comprehensive audit logging
- Data residency controls
- HIPAA Business Associate Agreement

**Implementation:**

```python
# backend/vertex_security.py (NEW)
class VertexSecurityConfig:
    """Security configuration for Vertex AI integration."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.vpc_sc_perimeter = None
        self.cmek_key = None

    def configure_vpc_service_controls(self, perimeter_name: str):
        """Configure VPC-SC perimeter for Vertex AI."""
        # Restrict Vertex AI to VPC perimeter
        self.vpc_sc_perimeter = perimeter_name
        # Configure in aiplatform init
        aiplatform.init(
            project=self.project_id,
            network=f"projects/{self.project_id}/global/networks/certify-intel-vpc"
        )

    def configure_cmek(self, key_name: str):
        """Configure customer-managed encryption."""
        self.cmek_key = key_name
        # Use in all Vertex AI resources

    def enable_audit_logging(self):
        """Enable comprehensive audit logging."""
        # Configure Cloud Audit Logs for:
        # - Admin Activity (always on)
        # - Data Access (configurable)
        # - System Event (automatic)
        pass
```

---

## Implementation Phases

### Phase 1: Core Vertex AI Migration (Week 1-2)

| Task ID | Task | Priority | Details |
|---------|------|----------|---------|
| VERTEX-1.1 | Set up GCP project with Vertex AI | HIGH | Enable APIs, configure IAM |
| VERTEX-1.2 | Create vertex_ai_provider.py | HIGH | Replace google-generativeai |
| VERTEX-1.3 | Migrate existing AI calls | HIGH | Update gemini_provider.py imports |
| VERTEX-1.4 | Add service account auth | HIGH | Replace API key with ADC |
| VERTEX-1.5 | Update .env configuration | HIGH | Add GCP project, location |
| VERTEX-1.6 | Create provider abstraction | MEDIUM | Support both providers |

**Files to Create:**
- `backend/vertex_ai_provider.py` (~800 lines)
- `backend/vertex_config.py` (~200 lines)

**Files to Modify:**
- `backend/gemini_provider.py` - Add Vertex AI fallback
- `backend/main.py` - Add Vertex AI router
- `backend/.env.example` - Add GCP configuration
- `backend/requirements.txt` - Add google-cloud-aiplatform

### Phase 2: RAG Engine Integration (Week 2-3)

| Task ID | Task | Priority | Details |
|---------|------|----------|---------|
| VERTEX-2.1 | Create RAG corpus management | HIGH | Per-competitor corpora |
| VERTEX-2.2 | Build document ingestion pipeline | HIGH | Index existing documents |
| VERTEX-2.3 | Implement grounded generation | HIGH | Ground all AI responses |
| VERTEX-2.4 | Add RAG API endpoints | HIGH | CRUD for corpora |
| VERTEX-2.5 | Integrate with battlecard generator | MEDIUM | Grounded battlecards |
| VERTEX-2.6 | Add citation extraction | MEDIUM | Show sources in UI |

**Files to Create:**
- `backend/vertex_rag_engine.py` (~600 lines)
- `backend/routers/vertex_rag.py` (~400 lines)

**Files to Modify:**
- `backend/battlecard_generator.py` - Add grounded generation
- `backend/ai_research.py` - Use RAG for research
- `frontend/index.html` - Add RAG corpus management UI

### Phase 3: Vector Search Implementation (Week 3-4)

| Task ID | Task | Priority | Details |
|---------|------|----------|---------|
| VERTEX-3.1 | Create Vector Search index | HIGH | Competitor data embeddings |
| VERTEX-3.2 | Build embedding pipeline | HIGH | Auto-embed new data |
| VERTEX-3.3 | Implement semantic search API | HIGH | Natural language queries |
| VERTEX-3.4 | Add similarity search | MEDIUM | Find similar competitors |
| VERTEX-3.5 | Create search UI component | MEDIUM | Frontend search bar |
| VERTEX-3.6 | Index historical data | LOW | Backfill existing data |

**Files to Create:**
- `backend/vertex_vector_search.py` (~500 lines)
- `backend/routers/vertex_search.py` (~300 lines)
- `frontend/vertex_search.js` (~400 lines)

### Phase 4: Agent Builder Integration (Week 4-6)

| Task ID | Task | Priority | Details |
|---------|------|----------|---------|
| VERTEX-4.1 | Create CI Agent definition | HIGH | System instructions, tools |
| VERTEX-4.2 | Build MCP tool integrations | HIGH | Connect scrapers, APIs |
| VERTEX-4.3 | Implement agent memory | HIGH | Persistent research context |
| VERTEX-4.4 | Add scheduled agent tasks | MEDIUM | Daily/weekly monitoring |
| VERTEX-4.5 | Create agent chat UI | MEDIUM | Interactive research |
| VERTEX-4.6 | Build alert system | MEDIUM | Agent-triggered alerts |

**Files to Create:**
- `backend/vertex_agent_builder.py` (~1,000 lines)
- `backend/vertex_mcp_tools.py` (~600 lines)
- `backend/routers/vertex_agent.py` (~500 lines)
- `frontend/vertex_agent.js` (~600 lines)

### Phase 5: Fine-Tuning & Security (Week 6-8)

| Task ID | Task | Priority | Details |
|---------|------|----------|---------|
| VERTEX-5.1 | Prepare fine-tuning dataset | MEDIUM | Historical battlecards, extractions |
| VERTEX-5.2 | Train custom CI model | MEDIUM | SFT on Gemini 2.5 Flash |
| VERTEX-5.3 | Configure VPC-SC | HIGH | Network isolation |
| VERTEX-5.4 | Set up CMEK | MEDIUM | Customer-managed encryption |
| VERTEX-5.5 | Enable audit logging | HIGH | Compliance logging |
| VERTEX-5.6 | Obtain HIPAA BAA | HIGH | Healthcare compliance |

**Files to Create:**
- `backend/vertex_fine_tuning.py` (~400 lines)
- `backend/vertex_security.py` (~300 lines)

---

## Database Schema Updates

```python
# Add to backend/database.py

class RAGCorpus(Base):
    """Track Vertex AI RAG corpora."""
    __tablename__ = "rag_corpora"

    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=True)
    corpus_name = Column(String, unique=True)  # Vertex AI resource name
    display_name = Column(String)
    document_count = Column(Integer, default=0)
    last_indexed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class RAGDocument(Base):
    """Track documents in RAG corpora."""
    __tablename__ = "rag_documents"

    id = Column(Integer, primary_key=True)
    corpus_id = Column(Integer, ForeignKey("rag_corpora.id"))
    source_type = Column(String)  # sec_filing, news, review, etc.
    source_url = Column(String)
    title = Column(String)
    chunk_count = Column(Integer)
    indexed_at = Column(DateTime)

class AgentSession(Base):
    """Track Agent Builder sessions."""
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True)  # Vertex AI session ID
    user_id = Column(Integer, ForeignKey("users.id"))
    agent_type = Column(String)  # research, monitor, chat
    started_at = Column(DateTime)
    last_activity = Column(DateTime)
    message_count = Column(Integer, default=0)

class AgentAlert(Base):
    """Agent-generated alerts."""
    __tablename__ = "agent_alerts"

    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"))
    alert_type = Column(String)  # news, threat, dimension_change
    severity = Column(String)  # low, medium, high, critical
    title = Column(String)
    content = Column(Text)
    source_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
```

---

## Configuration Updates

### .env.example Additions

```env
# ============== Vertex AI Configuration (v5.3.0) ==============

# GCP Project Configuration
GCP_PROJECT_ID=certify-intel-prod
GCP_LOCATION=us-central1
GCP_SERVICE_ACCOUNT_KEY=/path/to/service-account.json

# Vertex AI Models
VERTEX_AI_MODEL=gemini-3-flash
VERTEX_AI_EMBEDDING_MODEL=textembedding-gecko@003
VERTEX_AI_FINE_TUNED_MODEL=  # Set after fine-tuning

# RAG Engine
VERTEX_RAG_ENABLED=true
VERTEX_RAG_CHUNK_SIZE=512
VERTEX_RAG_CHUNK_OVERLAP=100
VERTEX_RAG_SIMILARITY_TOP_K=10

# Vector Search
VERTEX_VECTOR_SEARCH_INDEX=projects/certify-intel-prod/locations/us-central1/indexes/competitor-index
VERTEX_VECTOR_SEARCH_ENDPOINT=projects/certify-intel-prod/locations/us-central1/indexEndpoints/competitor-endpoint

# Agent Builder
VERTEX_AGENT_ENABLED=true
VERTEX_AGENT_MEMORY_ENABLED=true
VERTEX_AGENT_MONITOR_SCHEDULE=0 8 * * *  # Daily at 8am

# Security
VERTEX_VPC_SC_PERIMETER=certify-intel-perimeter
VERTEX_CMEK_KEY=projects/certify-intel-prod/locations/us-central1/keyRings/vertex-ai/cryptoKeys/data-key
VERTEX_AUDIT_LOGGING=true

# Provider Selection (hybrid mode)
AI_PROVIDER=hybrid-vertex  # openai, gemini, vertex, hybrid-vertex
VERTEX_BULK_TASKS=true     # Use Vertex for bulk operations
VERTEX_QUALITY_TASKS=true  # Use Vertex for quality operations
```

---

## Cost Analysis

### Vertex AI Pricing (Estimated Monthly)

| Service | Usage Estimate | Unit Cost | Monthly Cost |
|---------|----------------|-----------|--------------|
| Gemini 3 Flash (Input) | 50M tokens | $0.15/1M | $7.50 |
| Gemini 3 Flash (Output) | 25M tokens | $0.60/1M | $15.00 |
| Gemini 2.5 Pro (complex) | 5M tokens | $1.25/1M | $6.25 |
| Vector Search | 100K queries | $0.10/1K | $10.00 |
| Vector Search Storage | 10GB | $0.25/GB | $2.50 |
| RAG Engine | 10 corpora | Included | $0.00 |
| Agent Sessions | 1,000 sessions | $0.02/session | $20.00 |
| Fine-Tuning | 1 job/quarter | ~$50/job | $16.67 |
| **Total Estimated** | | | **~$78/month** |

### Comparison with Current (Google AI SDK)

| Metric | Current (AI SDK) | Vertex AI | Difference |
|--------|------------------|-----------|------------|
| Base token cost | Similar | Similar | ~0% |
| RAG capability | Manual (custom) | Managed | +Value |
| Vector Search | None | Included | +Value |
| Agent Builder | None | Included | +Value |
| Fine-tuning | Not available | Available | +Value |
| Enterprise security | Limited | Full | +Value |
| HIPAA compliance | Not available | Available | +Critical |

**Recommendation:** The ~$78/month Vertex AI cost delivers significantly more value than the current setup through RAG, agents, and enterprise compliance.

---

## API Endpoints Summary (New)

### Vertex AI Provider
```
GET  /api/vertex/status                    # Provider status
GET  /api/vertex/models                    # Available models
POST /api/vertex/generate                  # Text generation
POST /api/vertex/embed                     # Generate embeddings
```

### RAG Engine
```
POST /api/vertex/rag/corpus                # Create corpus
GET  /api/vertex/rag/corpus                # List corpora
GET  /api/vertex/rag/corpus/{id}           # Get corpus details
DELETE /api/vertex/rag/corpus/{id}         # Delete corpus
POST /api/vertex/rag/corpus/{id}/ingest    # Ingest documents
POST /api/vertex/rag/corpus/{id}/query     # Query with grounding
GET  /api/vertex/rag/corpus/{id}/documents # List documents
```

### Vector Search
```
POST /api/vertex/search                    # Semantic search
POST /api/vertex/search/similar/{id}       # Find similar
GET  /api/vertex/search/index/status       # Index status
POST /api/vertex/search/index/rebuild      # Rebuild index
```

### Agent Builder
```
POST /api/vertex/agent/session             # Create session
GET  /api/vertex/agent/session/{id}        # Get session
POST /api/vertex/agent/chat                # Send message
POST /api/vertex/agent/research/{id}       # Research competitor
GET  /api/vertex/agent/alerts              # Get alerts
PUT  /api/vertex/agent/alerts/{id}/ack     # Acknowledge alert
POST /api/vertex/agent/monitor/start       # Start monitoring
POST /api/vertex/agent/monitor/stop        # Stop monitoring
```

---

## Files Summary

### New Files to Create (12)

| File | Lines | Description |
|------|-------|-------------|
| `backend/vertex_ai_provider.py` | ~800 | Core Vertex AI provider |
| `backend/vertex_config.py` | ~200 | Configuration management |
| `backend/vertex_rag_engine.py` | ~600 | RAG corpus management |
| `backend/vertex_vector_search.py` | ~500 | Vector Search integration |
| `backend/vertex_agent_builder.py` | ~1,000 | Agent Builder integration |
| `backend/vertex_mcp_tools.py` | ~600 | MCP tool definitions |
| `backend/vertex_fine_tuning.py` | ~400 | Model fine-tuning |
| `backend/vertex_security.py` | ~300 | Security configuration |
| `backend/routers/vertex_rag.py` | ~400 | RAG API endpoints |
| `backend/routers/vertex_search.py` | ~300 | Search API endpoints |
| `backend/routers/vertex_agent.py` | ~500 | Agent API endpoints |
| `frontend/vertex_agent.js` | ~600 | Agent chat UI |

**Total New Code:** ~6,200 lines

### Files to Modify (8)

| File | Changes |
|------|---------|
| `backend/database.py` | Add RAGCorpus, RAGDocument, AgentSession, AgentAlert tables |
| `backend/main.py` | Include Vertex AI routers |
| `backend/gemini_provider.py` | Add Vertex AI fallback |
| `backend/battlecard_generator.py` | Add grounded generation |
| `backend/ai_research.py` | Use RAG for research |
| `backend/.env.example` | Add Vertex AI configuration |
| `backend/requirements.txt` | Add google-cloud-aiplatform |
| `frontend/index.html` | Add Vertex AI management UI |

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| AI response accuracy | ~85% | >95% | Manual review sampling |
| Hallucination rate | ~15% | <5% | Grounding verification |
| Research time | 30min manual | 5min automated | Agent completion time |
| News monitoring | Manual daily | Real-time automated | Alert latency |
| Battlecard freshness | Weekly manual | Auto-updated | Last update timestamp |
| Enterprise compliance | Not compliant | HIPAA compliant | BAA signed |
| Search relevance | Keyword only | Semantic | User satisfaction |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| GCP service outage | High | Maintain Google AI SDK fallback |
| Cost overruns | Medium | Set budget alerts, optimize queries |
| Fine-tuning quality | Medium | Iterative training, human review |
| Agent hallucinations | Medium | Grounding required for all responses |
| Migration complexity | Medium | Phased rollout, feature flags |

---

## Conclusion

Integrating Vertex AI into Certify Intel will transform the platform from a manual competitive intelligence tool into an autonomous, enterprise-grade intelligence system. Key benefits:

- **RAG Engine:** Ground all AI responses in verified competitor documents
- **Agent Builder:** Autonomous research, monitoring, and alerting
- **Vector Search:** Natural language queries across all competitor data
- **Fine-Tuning:** Custom model optimized for healthcare CI
- **Enterprise Security:** VPC-SC, CMEK, HIPAA compliance

**Recommended Next Step:** Begin Phase 1 with GCP project setup and core Vertex AI provider migration.

---

## Sources

- [Vertex AI Platform](https://cloud.google.com/vertex-ai)
- [Vertex AI RAG Engine Overview](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview)
- [RAG and Grounding on Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview)
- [Vertex AI Agent Builder](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder/overview)
- [Agent Development Kit](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder/adk)
- [Vertex AI for Healthcare](https://cloud.google.com/solutions/healthcare-life-sciences)
- [Vertex AI Security Controls](https://cloud.google.com/vertex-ai/docs/general/vpc-service-controls)
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)
- [Vertex AI Fine-Tuning](https://cloud.google.com/vertex-ai/generative-ai/docs/models/tune-models)
- [Multi-Agent Systems with Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder/multi-agent)
