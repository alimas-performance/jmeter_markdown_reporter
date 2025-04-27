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
├── output_folder/
│   ├── avg_response_time.png
│   ├── error_rate_over_time.png
│   ├── response_time_over_time.png
│   ├── p90_response_time.png
│   ├── error_rate_pie.png
│   ├── response_code_pie.png
│   └── report.md
```

### ⚙️ Configuration YAML
Give your folder name for output in the output_dir yaml field value.
Assign the order of the graps as you prefer in the graph_files, each graph name has to be a member of a list.

```yaml
output_dir: output
resample_frequency: 1s
graph_files:
  - error_rate_pie.png
  - response_code_distribution_pie.png
  - avg_response_time_by_label.png
  - error_rate_over_time.png
  - response_time_over_time_by_label.png
  - p90_response_time_by_label.png
```

### ✅ Instructions to Run
Save your results.jtl in the same folder as generate_report.py.

Run:

```shell
python generate_report.py results.jtl output_folder
```
or

```shell
python generate_report.py results.jtl
```


Your graphs and report.md file will be inside the /output_folder/ folder! or the folder you setup in the config.yaml

### 🐋 Running From Docker Image
First compile the image
```shell
docker build -t jmeter-report-generator .
```
Now use the docker image like this:
```shell
docker run --rm -v ${PWD}/results.jtl:/app/results.jtl -v ${PWD}/output:/app/output jmeter-report-generator results.jtl output
```
