# README

### ⚙️ Install the dependencies
Run:

```shell
pip install -r requirements.txt
```


### 📂 Project Folder Structure

```
jmeter_markdown_reporter/
├── results.jtl
├── generate_report.py
├── output/
│   ├── avg_response_time.png
│   ├── error_rate_over_time.png
│   ├── response_time_over_time.png
│   ├── p90_response_time.png
│   ├── error_rate_pie.png
│   ├── response_code_pie.png
│   └── report.md
```

### ✅ Instructions to Run
Save your results.jtl in the same folder as generate_report.py.

Run:

```shell
python generate_report.py
```

Your graphs and report.md file will be inside the /output/ folder!
