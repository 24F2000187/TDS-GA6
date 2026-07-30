# 🚀 Taint-Aware Agent Executor — Full Working Solver

A complete, deployable **Mailroom Action Gate** for the GA5 assignment:

> **Build a Taint-Aware Agent Executor**
> (`q-taint-aware-agent-executor-server`)

✅ **Verified Score:** **4.00 / 4.00**

Successfully passes all official grader checks:

```
shapeErrors                : 0
replayPassed               : ✓
commitReplayPassed         : ✓
stableCorePassed           : ✓
conflictPassed             : ✓
invalidPassed              : 2/2
receiptValidationPassed    : ✓
freshExact                 : 6/6
freshOperational           : 6/6
unsafe                     : false
```

> **Note**
>
> No API key is committed.
> The stable dossiers are determined using a deterministic gate and cached, so a normal execution requires **zero model calls**.
>
> The LLM path is only an optional fallback. If desired, place **your own API key** inside `.env`.

---

# 📦 Quick Start

Clone the repository and run the project locally.

```bash
git clone https://github.com/<your-username>/tds-ga5-q9-solver.git

cd tds-ga5-q9-solver

python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

python selftest.py
```

Expected output:

```
51 passed, 0 failed
```

The self-test performs the following completely offline:

- Generates an Ed25519 verifier key
- Signs receipts exactly like the official grader
- Replays the complete probe sequence
- Tests replay detection
- Tests conflict detection
- Tests malformed operations
- Tests receipt tampering
- Tests declined receipts
- Requires **no network**
- Requires **no API key**

---

# ⭐ Two Things That Usually Prevent 4/4

Most implementations correctly decide the action, arguments, evidence, and minimality.

However, they lose marks on **two protocol checks**.

---

# 1️⃣ Receipt Validation

## The Common Mistake

Every receipt includes a Base64 signature:

```json
"receiptSignature"
```

The propose request also provides the verifier:

```json
"receiptVerifier": {
  "algorithm": "Ed25519",
  "publicKeyJwk": {
    "kty": "OKP",
    "crv": "Ed25519",
    "x": "base64url public key"
  }
}
```

Many implementations only verify receipt bindings.

That is **not sufficient**.

---

## The Official Grader Probe

The grader replays a valid receipt but changes:

```json
accepted: true
```

to

```json
accepted: false
```

Everything else remains identical.

If only bindings are checked:

```
→ returns HTTP 200 ❌
```

Instead, the signature must also be verified.

---

## Correct Verification Message

The signature is **NOT** calculated over the raw receipt.

It is calculated over the canonical JSON:

```json
{
  "profile": "ga5-mailroom-action-gate/v2",
  "evaluationId": "...",
  "inputDigest": "...",
  "receipt": {
      "...": "..."
  }
}
```

Requirements:

- Compact JSON
- UTF-8 encoding
- Recursively key-sorted
- Exclude `receiptSignature`

Then verify using:

- Ed25519
- Base64url-decoded `x` field

Store the verifier from **each propose request**.

Never hardcode keys.

---

# 2️⃣ Conflict Detection

The assignment specifies:

> Same evaluationId with changed content must return **HTTP 409**

Most implementations compare only the dossiers.

That is incorrect.

---

## The Official Conflict Probe

The grader changes only **one character** inside the verifier key.

Original:

```
n5vtC0l_uZ52vOcdUEK3vrUfMS9znl3XbqpPt6TgtZo
```

Probe:

```
A5vtC0l_uZ52vOcdUEK3vrUfMS9znl3XbqpPt6TgtZo
```

Everything else is identical.

Comparing only dossiers treats this as replay.

Correct behavior:

```
HTTP 409
```

---

## Correct Solution

Maintain **two different digests**.

### inputDigest

Digest of only:

- dossiers

Used during commit verification.

---

### contentDigest

Digest of:

- dossiers
- corpus
- allowedActions
- profile
- receiptVerifier

Used **only** for conflict detection.

This allows:

- exact replay → replay
- any semantic change → HTTP 409

---

# 📋 Expected Status Codes

The grader performs **24 probes**.

Expected responses:

| Probe | Expected Response |
|-------|-------------------|
| Duplicate dossierId | 400 / 422 |
| Unknown operation | 400 / 422 |
| Changed evaluation content | 409 |
| Mutated profile | 409 |
| Wrong inputDigest | 409 |
| Duplicate receipt | 409 |
| Missing receipt | 409 |
| Invalid signature | 409 |
| Unknown evaluation | 409 |

**Important**

A changed profile:

```
ga5-mailroom-action-gate/changed
```

is **not**

```
400 Unsupported Profile
```

It is:

```
409 Conflict
```

---

# 🧪 Official Probe Sequence

The self-test reproduces the complete grader behavior.

| Step | Operation | Expected |
|------|-----------|----------|
| 1 | propose | 200 |
| 2 | replay propose | 200 |
| 3 | changed dossiers | 409 |
| 4 | changed verifier key | 409 |
| 5 | mutated profile | 409 |
| 6–13 | tampered receipts | 409 |
| 14 | wrong inputDigest | 409 |
| 15 | duplicated receipt | 409 |
| 16 | missing receipt | 409 |
| 17 | invalid signature | 409 |
| 18 | unknown evaluation | 409 |
| 19 | clean commit | 200 |
| 20 | replay commit | 200 |
| 21 | second evaluation | 200 |
| 22 | second commit | 200 |
| 23 | duplicate dossierId | 400 |
| 24 | invalid operation | 400 |

Running all 24 probes locally is significantly more efficient than repeatedly submitting to the official grader.

---

# 🏗 Architecture

## Decision Cache

Decisions are cached using:

- dossierId
- canonical content fingerprint

Stable dossiers are evaluated only once.

---

## Stable callId

`callId` is derived from the canonical fingerprint.

Therefore it remains identical across evaluations.

This satisfies:

```
stableCorePassed
```

---

## Frozen Tool Shapes

Every payload is rebuilt using predefined schemas.

Model-generated fields cannot reach the execution layer.

---

## Trifecta Secret Scrubbing

Sensitive content is completely removed if it matches:

- Canary values
- Vault references
- API tokens
- Long hexadecimal strings
- PEM blocks

Secrets are **removed entirely**, never partially redacted.

---

## Atomic Validation

All validation occurs **before** any state changes.

If any receipt fails:

- No side effects occur.

---

## Ed25519 Verification

Verification prefers:

```
cryptography
```

If unavailable, the implementation falls back to a pure RFC 8032 implementation.

Both paths are validated by the test suite.

---

# 🚀 Deployment

The application can be deployed on any HTTPS host.

A simple option is **Render**.

## Steps

1. Push this repository to GitHub.

2. Create a new Render Web Service.

3. Connect the repository.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

### Environment Variable

```
MAILROOM_DB=/tmp/mailroom.db
```

Submit the deployed endpoint, for example:

```
https://<your-service>.onrender.com/q9/mailroom
```

Supported routes include:

- `/`
- `/mailroom`
- `/q9`
- `/gate`
- `/action-gate`

> **Note**
>
> Render's free tier sleeps after inactivity.
>
> Warm the endpoint before pressing **Check**, then press **Save**.

---

# 📁 Repository Structure

```
app.py
│
├── Entry point
├── Mounts the gate on multiple routes

mailroom.py
│
├── Decision engine
├── Storage
├── Conflict detection
├── Receipt handling

ed25519_verify.py
│
├── Signature verification
├── cryptography implementation
└── Pure Python fallback

llm.py
│
├── Optional LLM fallback
└── Environment-driven API keys

selftest.py
│
└── 51 offline assertions reproducing the official grader
```

---

# 📄 License

Released under the **MIT License**.

---

# ⚠ Notice

Each user's dossiers are personalized using their registered email.

Deploy your own instance using:

- your own GitHub repository
- your own hosting
- your own API keys (if required)

Do **not** submit someone else's deployed endpoint.
