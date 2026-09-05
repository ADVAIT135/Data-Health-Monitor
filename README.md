# Data Health Monitor

> A privacy-first, browser-based data quality and insight dashboard for teams that need fast, explainable dataset validation.

Data Health Monitor profiles common business datasets, calculates a quality score, highlights data risks, and generates decision-ready visual insights. It runs as a static site on Netlify, so uploaded files are processed in the browser without requiring an application server.

## Features

### Data quality monitoring

- Missing-value analysis by column
- Duplicate-row detection
- IQR-based numeric outlier detection
- Weighted health score out of 100
- Configurable alert thresholds
- Actionable issue recommendations
- Column types, missing counts, and unique-value summaries

### Data insights

- Automatic chart selection based on dataset structure
- Category-count bar charts
- Distribution histograms
- Relationship/scatter plots
- Pie charts
- Violin-style distribution plots
- Coordinate plots for numeric location data
- Hover tooltips with exact values
- Optional persistent value labels
- Zoom, width, height, and reset controls
- Responsive labels that rotate or truncate to avoid overlap
- Executive interpretation describing business impact and decision caveats

### File support

- CSV
- TSV
- TXT
- JSON
- XLSX
- XLS

Excel parsing uses the SheetJS browser library. The first worksheet is analyzed.

### Multiple files and folders

Use the file picker to select multiple supported files or an entire folder. The dataset selector lets you switch between files without refreshing the page. Each file is profiled independently.

### Reports

- Downloadable CSV health report
- Printable report with browser **Save as PDF** support
- Report includes quality metrics, rates, thresholds, and column summaries

## Quick start

### Run locally

The Netlify version is a zero-build static site. Open `index.html` directly in a browser, or serve the folder with any static web server:

```bash
python -m http.server 8000
```

Open <http://localhost:8000>.

### Optional Streamlit version

The original Python MVP is also available:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Performance and limitations

- There is no application-level file-size threshold. Browser memory, device capacity, and hosting/browser limits still apply to very large files.
- Large relationship and coordinate plots sample up to 2,000 points for responsive rendering; quality calculations still use the full dataset.
- Coordinate maps are numeric coordinate plots, not geographic basemaps.
- Historical monitoring, authentication, scheduled ingestion, team collaboration, and datasets larger than browser limits require a backend service.
- Automatic insights are analytical signals, not causal conclusions. Validate important decisions with domain experts and source-system context.

## Validation results

The application was validated with the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), using the CSV files in the local `archive/` folder.

| File | Rows | Health score |
| --- | ---: | ---: |
| `olist_customers_dataset.csv` | 99,441 | 100/100 |
| `olist_geolocation_dataset.csv` | 1,000,163 | 90.7/100 |
| `olist_orders_dataset.csv` | 99,441 | 99.7/100 |
| `olist_order_items_dataset.csv` | 112,650 | 98.8/100 |
| `olist_order_payments_dataset.csv` | 103,886 | 99.1/100 |
| `olist_order_reviews_dataset.csv` | 99,224 | 86.6/100 |
| `olist_products_dataset.csv` | 32,951 | 98.6/100 |
| `olist_sellers_dataset.csv` | 3,095 | 100/100 |
| `product_category_name_translation.csv` | 71 | 100/100 |

All nine files loaded successfully through the folder uploader, including the 1,000,163-row geolocation file. Dataset switching, profiling, chart rendering, and executive insight generation completed without application errors.

### Automatically generated Olist insights

The validation run suggests these high-value analysis opportunities:

1. **Review quality risk:** `olist_order_reviews_dataset.csv` received the lowest health score at **86.6/100**. Review completeness, duplicate review records, and extreme rating patterns before using reviews for customer-experience decisions or sentiment modelling.
2. **Geolocation scale and performance:** `olist_geolocation_dataset.csv` contains **1,000,163 rows** and scored **90.7/100**. Use sampling or aggregation for charts, and validate whether repeated customer coordinates represent genuine coverage or duplicated location records.
3. **Order-to-fulfilment funnel:** Join orders, order items, payments, reviews, customers, and sellers using their documented identifiers to analyze delivery performance, payment mix, cancellations, and post-purchase satisfaction.
4. **Revenue and basket economics:** Combine item prices, freight values, payments, and product categories to create average order value, freight burden, basket size, and category contribution metrics.
5. **Regional operations:** Connect customer, seller, and geolocation tables to compare delivery reach, seller concentration, freight exposure, and service quality by geography. Treat coordinate plots as exploratory unless latitude/longitude reference systems are verified.
6. **Data-model readiness:** The files form a relational dataset rather than one flat table. Preserve table grain and validate join cardinality before aggregating; joining at the wrong grain can inflate revenue, order counts, or review volumes.

These are decision-oriented hypotheses generated from the available tables, file sizes, and quality results. They should be validated with joins, time-period analysis, and domain review before being used for commercial decisions.

## Security and privacy

The static app parses selected files in the browser and does not upload them to an application server. Do not treat this as a substitute for organizational data-governance controls, endpoint security, or regulated-data review.

## License
[Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)
