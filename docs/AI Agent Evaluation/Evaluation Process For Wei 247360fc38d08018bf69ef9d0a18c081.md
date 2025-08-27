# Evaluation Process For Wei

This document outlines the strategy for evaluating our **Wei AI Agent** using a prepared dataset of DAO governance proposals and a curated set of evaluation questions. Our goal is to ensure **consistent, transparent, and automatable** benchmarking of the agent's performance.

Related documents:

[Good Proposals](../Good%20Proposals%20examples/Good%20Proposals%20246360fc38d080d4b904ec3aa558ae8e.md)

[Questions To Decide whether Wei Works Well](../Questions%20To%20Decide%20If%20The%20Agent%20Is%20Good/Questions%20To%20Decide%20whether%20Wei%20Works%20Well%20247360fc38d0804fb467ebb1b2726053.md)

### 1. Evaluation Strategy Design

We will:

- Use **three evaluation stages**:
    - **Fine-tuning** – Train and optimize the model on the training dataset with hyperparameter tuning and model selection. (Not a part of the CI)
    - **Validation (Dev branch)** – 10 proposals tested automatically after each merge to `dev`.
    - **Final Testing (Main branch)** – 5 unseen proposals tested only on `main` releases to check for overfitting.
- Evaluation criteria:
    - Proposal clarity, completeness, assumptions, missing elements, and community adaptability.
    - Submitter identity, interests, activity, and strategic positioning.
- **Output format**: Fixed JSON structure → parsed & scored automatically.

### 2. Proposal Dataset Preparation

We will prepare **15 proposals**:

- **5 Training**
- **10 Validation/Test** (run after each merge to `dev`)
- **5 Final Test Only** (run on `main` releases)

For each proposal, we will store:

- **Proposal details** (title, description, funding request, goals)
- **Submitter information** (name, profile links, role in DAO)

Dataset format: **JSON + SQL (for querying with pgvector)**

### **User Entity** (stored in Redis, referenced in VectorDB metadata)

- `user_id` (UUID)
- `name`
- `contacts` (Map – e.g., `{"twitter": "", "telegram": ""}`)
- `title` (optional)
- `number_of_votes` (Integer)
- `token_holdings` (Float – number of governance tokens)

### **Proposal Entity** (stored in Postgres with pgvector for embeddings)

- `proposal_id` (UUID)
- `submitter_id` (foreign key to `user_id`)
- `description` (Text – used to generate vector embedding)
- `embedding` (Vector – pgvector column for semantic search)
- `votes`:
    - `for` (Integer)
    - `against` (Integer)
- `timestamp` (Datetime)
- `metadata`:
    - `submitter_name`
    - `submitter_title` (optional)
    - `submitter_contacts` (Map)

### **Relationships:**

- One **User** can submit multiple **Proposals**.
- Each **Proposal** references exactly one **User** via `submitter_id`.

### **Evaluation with pgvector**

1. **Embedding Storage**
    - Each proposal `description` is embedded using an LLM embedding model (e.g., `text-embedding-3-small`).
    - The resulting vector is stored in the `embedding` column in Postgres (via `pgvector`).
2. **Context Retrieval**
    - When a new proposal is submitted, its embedding is computed.
    - pgvector similarity search retrieves **top-K most similar proposals** based on cosine distance.
    - Retrieved proposals include `metadata` (submitter, role, votes, outcome).
3. **AI Agent Evaluation**
    - Input = new proposal + retrieved similar proposals (context).
    - Agent generates structured output: `{ verdict, justification, recommendations }`.
    - This evaluation is stored in a separate `evaluations` table linked to `proposal_id`.

### Example JSON Entry

```json
{
  "proposal_id": "proposal-001",
  "submitter_id": "user-123",
  "description": "The proposal requests authorization to use $89,980 USD ...",
  "embedding": [0.012, -0.233, ...],
  "votes": {
    "for": 1200,
    "against": 300
  },
  "timestamp": "2025-07-15T14:30:00Z",
  "metadata": {
    "submitter_name": "Max Lomu",
    "submitter_title": "Community Builder",
    "submitter_contacts": {
      "x": "https://x.com/max",
      "telegram": "@maxlomu"
    }
  }
}

```

### 3. Evaluation Questions

**Proposal Quality**

1. Goal clear? (✅/⚠️/❌)
2. Sections complete? (✅/⚠️/❌)
3. Detail sufficient? (✅/⚠️/❌)
4. Assumptions reasonable? (Yes/No)
5. Community adaptable? (Yes/No)

**Submitter Intent**

1. Identity matches DAO records? (Yes/No)
2. Interests aligned with DAO goals? (Yes/No)
3. Strong DAO participation history? (Yes/No)
4. Personal gain or DAO benefit? (Categorical)

**Selection Criteria for 15 Governance Proposals:**

- Variety in complexity (simple, moderate, complex)
- Diversity in proposal types (funding, protocol changes, governance)
- Range of submitter profiles (known entities, new participants)

**Metadata Collection:**

- **Proposal Details:** ID, title, submission date, requested amount, implementation timeline
- **Submitter Information:** Name, social profiles, previous proposals, reputation
- **User Associations:** Known affiliations, voting history

### 4. Plan for Automating Output

**Rust Pipeline**

- `reqwest` → send proposals to AI endpoint.
- Store in Postgres/VectorDB (`sqlx`, `serde_json`).
- Compare with gold-standard expert answers.
- Metrics: Accuracy (binary), F1 score (categorical), gap reports.

**CI/CD**

- **Dev branch** → Run tests on 10 validation proposals after each merge.
- **Main branch** → Run tests on 5 final-only proposals before release.

**Tools**

- `cargo test` for schema & output validation.
- `cargo clippy` + `rustfmt` for code quality.
- GitHub Actions for automated runs.

## 5.0 **Scoring Logic**

Each evaluation question produces a **point value**:

| Question Type | Possible Answers | Points Awarded |
| --- | --- | --- |
| **Binary (Yes/No)** | Correct answer = 1 | 1 |
| **Ternary (✅/⚠️/❌)** | ✅ = 1, ⚠️ = 0.5, ❌ = 0 | 1 |
| **Categorical** | Exact match to gold answer = 1 | 1 |

> Note: All answers are compared to a data set we provide
> 

## 5.1 **Proposal-Level Score**

For each proposal:

**Proposal Score (%)** = (Points Earned ÷ Max Possible Points) × 100

**Example:**

- 9 correct binary answers, 1 partial (⚠️) → **9.5 ÷ 10 × 100 = 95%**

## 5.2 Agent Performance Metrics

- **Average Accuracy (%)** → Mean proposal score across the test set.
- **F1 Score** → For categorical/multi-class answers.
- **Error Rate** → % of proposals where score < 80%.
- **Consistency Index** → Standard deviation of proposal scores (lower = more consistent).

## 5.3  **Performance Bands**

| Band | Score Range | Meaning |
| --- | --- | --- |
| **Excellent** | ≥ 90% | Reliable and ready for prod. |
| **Good** | 80–89% | Minor fine-tuning needed. |
| **Fair** | 65–79% | Needs improvement on certain question types. |
| **Poor** | < 65% | Not ready for release. |

## 5. **Automation in CI/CD**

- **Dev branch** → Pass if average score ≥ 80%.
- **Main branch** → Pass if average score ≥ 90% *and* no single proposal < 80%.
- Score reports are stored in `/evaluation/reports/YYYY-MM-DD.json` for trend tracking.