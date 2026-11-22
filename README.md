# 💰💰ArthaAgent: your money, run by an AI agent💰💰

**Built by Team Code Catalysts** for Arthaton 2026

![ArthaAgent thumbnail](thumbnail_team_code_catalysts.png)

## 🎥 Demo video

**Watch the demo:** https://youtu.be/YQFipDu2qT4

## What it does

Most people in India track money across UPI apps, bank SMS alerts and spreadsheets, and struggle to see where it goes, whether they are saving enough, which tax regime suits them, or whether a "KYC update" message is a scam. ArthaAgent turns that raw data into clear decisions, explained in plain words in English, Hinglish, Hindi or Marathi.

It is for everyday earners, students, salaried professionals and first-time investors.

| Tab | What you get |
|---|---|
| 🧭 Start Here | 60-second tour, system check, tester checklist and quick answers |
| 🏠 Dashboard | 0-100 money-health score, smart alerts, badges, report download, 3D health towers |
| 🤖 Agent | Chat with a Gemini agent that calls finance tools and shows its work |
| 📸 Snap & Budget | Paste UPI/bank SMS or upload a screenshot, then see a spending breakdown, 3D Spending City and Spending DNA |
| 🔮 Money Twin | Monte Carlo simulation of thousands of futures with life events (wedding, career break, bonus) |
| ⚖️ Decision Lab | Pay cash vs EMI vs invest instead, with a clear verdict |
| 🛡️ Scam Shield | Fraud risk score for texts and screenshots, plus a violence and threat word detector |
| 🧾 Tax | Old vs new regime comparison (FY 2025-26) |
| 🔥 FIRE & Loans | Years to financial independence, and prepay-a-loan vs invest |
| 📰 Market News | Live index charts and headlines with an AI brief |
| 📈 SIP 3D Lab | Eight interactive 3D views of what a SIP can become |
| 👤 Profile | Your details, personal insights, password change and account deletion |

Other features: email and password sign-in (salted and hashed with PBKDF2), a one-click guest mode, a register window with a password-strength meter, and an optional "Roast my spending" agent personality.

## How it uses AI

- **Agent with tools (Gemini function calling):** the agent decides which of 11 finance tools to run (spending summary, profile, scam score, tax compare, SIP projection, goal probability, EMI calculator, affordability check, financial health, FIRE plan, prepay vs invest). Python code does the maths, and Gemini explains the result, so the numbers are never invented. The chat shows each tool call.
- **Vision:** Gemini reads UPI history, bank statement and message screenshots and turns them into transactions or scam verdicts.
- **Generation:** 30-day money plans, report summaries, Spending DNA personas, market briefs and plain-words explanations, in the language you pick.

## Models and APIs used

| Service | Used for |
|---|---|
| **Google Gemini API** via the `google-genai` Python SDK | Agent chat with automatic function calling, vision, JSON output and text generation |
| Model: `gemini-flash-latest` by default | Change it in the sidebar or with the `GEMINI_MODEL` environment variable |
| Yahoo Finance public chart endpoint | Index, USD/INR, gold and crude quotes for Market News (no key needed) |
| Public RSS feeds (Economic Times, Mint, Moneycontrol, Business Standard) | Market headlines (no key needed) |

Libraries: Streamlit, Plotly (2D and 3D), NumPy, pandas, plus custom HTML and CSS for the 3D interface.

## How to run

You need Python 3.9 or newer.

```bash
pip install -r requirements.txt
streamlit run arthaagent_full.py
```

Then open http://localhost:8501.

1. Click **Try instantly as guest** to explore with demo data, or register with your email and a password.
2. For the AI features, paste a free Gemini key into the sidebar. Get one at https://aistudio.google.com/apikey. You can also set it before starting:
   ```bash
   export GEMINI_API_KEY="your_key_here"
   ```
3. Everything except the AI buttons (charts, calculators, scam rules, 3D views, news) works without a key.

### Run in Google Colab

```python
!pip install -q streamlit google-genai plotly pandas numpy
!streamlit run /content/arthaagent_full.py &>/content/log.txt &
```

Then expose port 8501 with a tunnel such as Cloudflare. Upload the file instead of pasting it, so it is not cut off.

## Project files

```
arthaagent_full.py                  the whole app (single file)
requirements.txt                    Python dependencies
thumbnail_team_code_catalysts.png   project thumbnail
README.md                           this file
```

Registered accounts are saved in `artha_users.json` next to the app. Guest mode saves nothing.

## Privacy and disclaimer

Passwords are salted and hashed. AI buttons send Gemini only a summary of your numbers. ArthaAgent is an educational tool and is **not SEBI-registered investment advice**. Projections are estimates and markets can fall. Talk to a SEBI-registered adviser or a CA for big decisions.

---

Made with ❤️ by **Team Code Catalysts**
