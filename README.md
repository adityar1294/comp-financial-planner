# Retirement Corpus Planner 📈

A professional retirement planning tool built for Indian financial advisors, using Streamlit + Plotly.

## Features (v1)
- SIP corpus projection with annual step-up
- Inflation-adjusted real value
- Monthly SWP estimate (4% rule)
- Scenario comparison across all 4 risk profiles
- Year-by-year breakdown table with CSV export
- Export / import client plan as JSON

## Planned (upcoming)
- Asset bucket strategy (equity / debt / liquid)
- Monte Carlo stress-test simulator
- Old vs new tax regime comparison
- PDF report export

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy to Streamlit Community Cloud (free)

1. Push this folder to a GitHub repository (public or private).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo → set main file path to `app.py`.
4. Click **Deploy** — done. You get a public URL instantly.

---

## Deploy to Vercel

Vercel doesn't natively run Streamlit, but you can wrap it:

1. Install the Vercel CLI: `npm i -g vercel`
2. Add a `vercel.json` in this folder:

```json
{
  "builds": [{ "src": "app.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "app.py" }]
}
```

> ⚠️ Streamlit on Vercel is non-trivial due to WebSocket requirements.  
> **Streamlit Community Cloud is strongly recommended** — it's purpose-built, free, and deploys in under 2 minutes.

---

## Project structure

```
retirement_planner/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Disclaimer
This tool is for illustrative and advisory-support purposes only. It does not constitute investment advice. 
Returns on market-linked instruments are not guaranteed. 
Consult a SEBI-registered investment advisor before making investment decisions.
Verify current tax slabs at [incometaxindia.gov.in](https://incometaxindia.gov.in).
