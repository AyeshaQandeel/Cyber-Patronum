# Cyber-Patronum: Magical Threat Intelligence Agent

**Open Agent Hackathon 2026, Track 02: The Agent That Can Explain Why**

An AI agent that investigates any domain, URL or IP address, decides for itself which checks to run, and explains exactly why it gave the score it did.

## The problem
Checking whether a domain or IP is suspicious means jumping between many separate sources by hand: DNS, registration records, TLS certificates, IP reputation, blocklists, and what the site does when you visit it. Then the analyst still has to justify the verdict. Most scanners return a single number or a black-box "malicious / clean" label with no explanation, so people cannot tell why, or how much to trust it.

## What it does
Enter a domain, subdomain, full URL, IPv4 or IPv6 address.

- **The agent chooses the investigation.** A language model decides which tool to run next, reacts to what it finds (for example a very new domain, a proxy flag, or a redirect to another domain), and decides when it has enough evidence. Different targets produce different step sequences.
- **Explainable score.** The risk score is the sum of named signals, each with its points (for example "+20 Certificate fails validation"). The model never invents the number. It explains it in plain English from those signals.
- **Spell log.** Every agent step is shown: its thought, the tool it ran, and what came back.
- **Honest about uncertainty.** Blind spots are listed, and a result with too little evidence is labelled inconclusive, not clean.
- **A serious finding cannot be averaged away.** Any signal worth 10 or more points sets a minimum score of 20%, so minor good signals cannot push a site with a red flag into the "low" band.
- **Safe by design.** Active probes are skipped for private or internal addresses. Text returned by tools is treated as untrusted data, never as instructions. The model can only choose from a fixed list of tools and cannot pick which hosts to contact.
- **Fallback mode.** With no API key, or if the model fails, the fixed pipeline of all checks runs instead, so the app still works.

## Architecture
```
Streamlit UI (app.py)
      |
      v
Agent loop (agent_llm.py)  <-- Nemotron model picks the next tool, or finishes
      |
      +--> Tools: dns_lookup, registration_lookup (RDAP), ip_intel, blocklist_check,
      |           tls_check, web_probe, follow_redirect
      v
Evidence record --> Deterministic signal scoring (agent_core.py)
      |
      v
Model writes the plain-English "why" from the scored signals
      |
      v
Report: score, verdict, flags, spell log, full evidence scroll
```
Data sources are free and need no keys: Google DNS-over-HTTPS, rdap.org, ip-api.com, public DNS blocklists (Spamhaus ZEN, SpamCop, DroneBL, best effort), and direct TLS and HTTP probes.

## Sponsor technology: honest status
| Sponsor | Status | How it is used |
|---|---|---|
| NVIDIA Nemotron | Integrated | Nemotron (`nvidia/nemotron-3.5-lightning:free`) plans the investigation (tool choice, follow-ups, when to stop) and writes the explanation. It is accessed **through OpenRouter's OpenAI-compatible API**, not through NVIDIA's own hosted endpoint, because NVIDIA's key sign-up was unavailable in my country. |
| Meterless | Not integrated | The model is called through OpenRouter directly, not through Nightshift. Memory of past investigations (H-MEM) is planned work. |
| Zetaris | Not integrated | Planned: expose the live sources plus a table of past cases and a threat-intel list as virtual tables, and join them in one SQL query. Not built, because the platform needs more RAM than the development machine has. |

The agent talks to any OpenAI-compatible endpoint, so pointing it at Nightshift or NVIDIA's hosted endpoint only needs three environment variables (below).

## Tested
Run live on `google.com` (clean, very low score) and `expired.badssl.com` (expired certificate, moderate score of 22% with the certificate failure as the named driver). The agent chose and ordered its own steps in both runs.

## Run it
```
pip install -r requirements.txt
```
Set three environment variables in the same terminal window, then start the app. Never put your key in the code or commit it.

Windows PowerShell:
```
$env:NVIDIA_API_KEY="your-key"
$env:NVIDIA_BASE_URL="https://openrouter.ai/api/v1"
$env:NEMOTRON_MODEL="nvidia/nemotron-3.5-lightning:free"
streamlit run app.py
```
Mac or Linux:
```
export NVIDIA_API_KEY="your-key"
export NVIDIA_BASE_URL="https://openrouter.ai/api/v1"
export NEMOTRON_MODEL="nvidia/nemotron-3.5-lightning:free"
streamlit run app.py
```
The variable is named `NVIDIA_API_KEY` for historical reasons. It holds whichever provider's key you use. For NVIDIA's own endpoint, omit `NVIDIA_BASE_URL` and use a model id from build.nvidia.com. Without a key the app still works in fixed-pipeline mode, and the spell log will say so.

## Demo targets
- `google.com`: clean
- `expired.badssl.com`, `self-signed.badssl.com`: certificate failures (intentional test sites)
- `paypa1-secure-login.xyz`: look-alike name patterns
- A Tor exit IP from `check.torproject.org/torbulkexitlist`: proxy signal

## Limits
- The score is a heuristic read of public signals. A low score does not prove a site is safe, and a high score does not prove it is malicious.
- Name-based checks can misfire on legitimate hyphenated, brand-like domains.
- Free services are rate limited (ip-api about 45 requests per minute), and free language models can be slow or busy. Spamhaus often refuses queries through public resolvers, which are then treated as "not checked".
- The explanation text is written by a language model from the scored signals. The score and signals themselves are deterministic.

## What is next
Live streaming of agent steps, a chat follow-up so the analyst can steer the investigation, memory of past investigations, and the Zetaris and Meterless integrations.

## Files
`app.py` (UI), `agent_llm.py` (agent loop and tools), `agent_core.py` (checks and scoring), `harry.png`, `clouds.png`, `requirements.txt`.