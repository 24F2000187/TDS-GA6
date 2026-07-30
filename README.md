# TDS-GA6

# Taint-Aware Agent Executor — Safe AI Mailroom Agent

A complete, deployable **Mailroom Action Gate** for the TDS Graded Assignment question *"Build a Taint-Aware Agent Executor"* (`q-taint-aware-agent-executor-server`, 4 marks).

## 🚀 Key Features

- **Deterministic Decision Gate**: Fast, zero-model-call deterministic evaluation for stable dossiers.
- **Ed25519 Receipt Verification**: Verifies base64-encoded receipt signatures against JWK public keys according to protocol rules.
- **Conflict Handling**: Strict HTTP 409 conflict detection for changed dossier contents or verifier keys on known evaluation IDs.
- **Canary & Vault Defense**: Automatic scrubbing of canary values, tokens, and vault references from tool payload outputs.
- **Atomic Operations**: Validates entire batch proposals and commits before applying any state changes.

---

## 🛠️ Quick Start

### 1. Installation

```bash
git clone https://github.com/<your-username>/tds-ga5-q9-solver.git
cd tds-ga5-q9-solver

python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

2. Run Self-Tests
bash


python selftest.py
All 51 offline unit tests will run, asserting signature verification, replay, conflict handling, and malformed request rejection.

📋 Protocol & Status Codes
Probe Event	Expected HTTP Status
Valid Propose / Commit	200 OK
Duplicate dossierId on Propose	400 Bad Request / 422
Unknown operation	400 Bad Request / 422
Receipt Signature Tampering / Missing Signature	409 Conflict
Changed Payload or Verifier Key on Known Evaluation	409 Conflict
Unknown evaluationId on Commit	409 Conflict


🌐 Deployment (Render / Vercel)
Push this repository to your GitHub account.
Create a new Web Service on render.com.
Set the following configuration:
Build Command: pip install -r requirements.txt
Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
Environment Variable: MAILROOM_DB=/tmp/mailroom.db
Submit your live HTTPS endpoint URL (e.g., https://your-app.onrender.com/q9/mailroom).
📂 Project Structure
text


├── app.py              # FastAPI entrypoint exposing /q9/mailroom and alias routes
├── mailroom.py         # Core gate engine (decisions, receipt verification, storage, conflict detection)
├── ed25519_verify.py   # Cryptographic Ed25519 signature verification module
├── llm.py              # Optional LLM fallback integration
└── selftest.py         # 51 offline assertions covering all grader probe paths
