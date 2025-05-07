# GSC Audit Automation Tool

A comprehensive, configurable Python script to automate Google Search Console (GSC) audits. Fetches performance data, segments by branded vs. non-branded, generates multi-level folder analyses, MoM comparisons, anomaly detection, and rich visual reports (Excel, Markdown, DOCX, and charts).

---

## 🚀 Features

- **OAuth2 or Service Account** authentication  
- Fetch **all** GSC rows with automatic pagination  
- **Branded vs. Non-Branded** segmentation via regex  
- **Low-hanging opportunity** detection (high impressions, low CTR)  
- **Multi-level folder** analysis (URL counts + metrics)  
- **Top pages & queries** tables  
- **Month-over-Month** performance & anomalies  
- **Device breakdown** pies per segment  
- **Automated reports**: Excel (`.xlsx`), Markdown (`.md`), Word (`.docx`)  
- **Configurable** via `config.yaml`  
- **Rich CLI logging** with RichHandler  

---

## 📋 Prerequisites

- Python 3.8+  
- A GSC property you have access to  
- OAuth client secret JSON or Service Account key  

---

## ⚙️ Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/yourorg/gsc-audit.git
   cd gsc-audit
   ```
2. Create & activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/macOS
   venv\Scriptsctivate         # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔧 Configuration

Copy and edit `config.yaml` in the project root:

```yaml
auth:
  type: "oauth"                          # or "service_account"
  oauth_credentials_file: "oauth_client_secrets.json"
  oauth_scope:
    - "https://www.googleapis.com/auth/webmasters.readonly"
  credentials_file: "token.pickle"
  sa_keyfile: "service_account.json"
  sa_scopes:
    - "https://www.googleapis.com/auth/webmasters.readonly"

dates:
  start_date: "2023-01-01"               # YYYY-MM-DD
  end_date: ""                           # leave blank to auto-detect last available

branded:
  regex: '(?i)^(?:cba|c ba)'             # case-insensitive prefix match for branded queries

filters:
  country: "US"                          # ISO 3166-1 alpha-2; blank = all

thresholds:
  low_hanging:
    min_impressions: 1000                # only pages/queries ≥ this
    max_ctr: 0.015                       # CTR < this for low-hanging
  ctr_decay_days: 30                     # window for anomaly rolling stats
  position_drop_threshold: 5             # rank volatility threshold

output:
  formats:
    excel: true
    markdown: true
    docx: true
  excel_path: "reports/gsc_audit.xlsx"
  markdown_path: "reports/summary.md"
  docx_path: "reports/summary.docx"

visualization:
  pie_charts: true
  line_charts: true

logging:
  level: "INFO"
  file: "logs/gsc_audit.log"

interactive: true                         # prompt to select GSC property
```

- **`auth`**: choose OAuth2 or Service Account.  
- **`dates`**: define your audit date range.  
- **`branded.regex`**: single regex to classify branded queries.  
- **`filters.country`**: restrict by country.  
- **`thresholds`**: set opportunity and anomaly rules.  
- **`output`**: paths & formats for reports.  
- **`visualization`**: toggle chart types.  
- **`interactive`**: if `true`, will prompt for property selection.

---

## ▶️ Usage

Run the audit with:

```bash
python main.py --config config.yaml --property https://example.com/
```

- Omit `--property` to list and choose interactively.  
- Results and charts will be written under `reports/` with timestamped filenames.

---

## 📂 Output Structure

- **Excel**:  
  - `RawFull`, `RawBranded`, `RawNonBranded`  
  - `Summary`, `MonthlyAverages`, `TopPages`, `TopQueries`  
  - `Folders_Multi`, `Folder_URLs`  
  - `MoM_Overall`, `MoM_Branded`, `MoM_NonBranded`  
  - `LowHanging`, `Anomalies_<metric>`

- **Markdown** (`summary_TIMESTAMP.md`): human-readable summary & insights  
- **Word** (`summary_TIMESTAMP.docx`): formatted report  
- **Charts** (`.png`): line, bar, pie visualizations

---

## 🚧 Troubleshooting

- **KeyError: 'clicks'** → ensure `gsc_fetcher.py` returns `clicks` column even when API returns zero rows.  
- **Infinite loop paging** → use the latest `fetch_performance` which stops when `< page_size`.  
- **Slow anomaly charts** → switch to aggregating daily totals before plotting.

---

## 🤝 Contributing

1. Fork & branch  
2. Make your changes  
3. Submit a Pull Request  

---

## 📄 License

[MIT License](LICENSE)

---

> _Empower your SEO audits with automated insights and proactive anomaly detection!_
