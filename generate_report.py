import os
from typing import List

import pandas as pd
import matplotlib.pyplot as plt


class JTLReader:
    """Reads and preprocesses JMeter JTL files."""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def read(self) -> pd.DataFrame:
        """Read and prepare the JTL data."""
        df = pd.read_csv(self.filepath)
        df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='ms')
        df['success'] = df['success'].astype(bool)
        return df


class GraphGenerator:
    """Generates graphs based on processed JTL data."""

    def __init__(self, df: pd.DataFrame, output_dir: str):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_avg_response_time_by_label(self):
        data = self.df.groupby('label')['elapsed'].mean().sort_values()
        plt.figure(figsize=(12, 6))
        data.plot(kind='bar', color='skyblue')
        plt.title('Average Response Time by Label')
        plt.ylabel('Avg Response Time (ms)')
        plt.tight_layout()
        self._save_plot('avg_response_time_by_label.png')

    def plot_error_rate_over_time(self):
        self.df.set_index('timeStamp', inplace=True)
        errors = (~self.df['success']).resample('10S').sum()
        total = self.df['success'].resample('10S').count()
        error_rate = (errors / total).fillna(0)

        plt.figure(figsize=(12, 6))
        error_rate.plot(color='red')
        plt.title('Error Rate Over Time')
        plt.ylabel('Error Rate')
        plt.tight_layout()
        self._save_plot('error_rate_over_time.png')

    def plot_response_time_over_time_by_label(self):
        plt.figure(figsize=(12, 6))
        for label, group in self.df.groupby('label'):
            plt.plot(group.index, group['elapsed'], label=label)
        plt.legend()
        plt.title('Response Time Over Time by Label')
        plt.ylabel('Response Time (ms)')
        plt.tight_layout()
        self._save_plot('response_time_over_time_by_label.png')

    def plot_p90_response_time_by_label(self):
        p90 = self.df.groupby('label')['elapsed'].quantile(0.90).sort_values()
        plt.figure(figsize=(12, 6))
        p90.plot(kind='bar', color='orange')
        plt.title('90th Percentile Response Time by Label')
        plt.ylabel('P90 Response Time (ms)')
        plt.tight_layout()
        self._save_plot('p90_response_time_by_label.png')

    def plot_error_rate_pie(self):
        counts = self.df['success'].value_counts()
        plt.figure(figsize=(6, 6))
        counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, labels=['Success', 'Failure'])
        plt.title('Error Rate: Success vs Failure')
        plt.ylabel('')
        plt.tight_layout()
        self._save_plot('error_rate_pie.png')

    def plot_response_code_distribution_pie(self):
        codes = self.df['responseCode'].value_counts()
        plt.figure(figsize=(8, 8))
        codes.plot(kind='pie', autopct='%1.1f%%', startangle=140)
        plt.title('Response Code Distribution')
        plt.ylabel('')
        plt.tight_layout()
        self._save_plot('response_code_distribution_pie.png')

    def _save_plot(self, filename: str):
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath)
        plt.close()


class ReportGenerator:
    """Generates a Markdown report containing all graphs and a summary table."""

    def __init__(self, df: pd.DataFrame, output_dir: str):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_summary_table(self) -> pd.DataFrame:
        summary = self.df.groupby('label').agg(
            avg_response_time=('elapsed', 'mean'),
            p90_response_time=('elapsed', lambda x: x.quantile(0.9)),
            max_response_time=('elapsed', 'max'),
            successes=('success', lambda x: (x == True).sum()),
            failures=('success', lambda x: (x == False).sum())
        )
        summary = summary.round(2)
        return summary

    def create_markdown_report(self, graph_files: List[str]):
        summary_table = self.generate_summary_table()
        report_path = os.path.join(self.output_dir, 'report.md')

        with open(report_path, 'w') as f:
            f.write('# JMeter Test Report\n\n')

            f.write('## Summary Table\n\n')
            f.write(summary_table.to_markdown())
            f.write('\n\n')

            for graph in graph_files:
                f.write(f'## {graph.replace("_", " ").replace(".png", "").title()}\n\n')
                f.write(f'![{graph}]({graph})\n\n')


def main():
    filepath = 'results.jtl'
    output_dir = 'output'

    # Step 1: Read data
    reader = JTLReader(filepath)
    df = reader.read()

    # Step 2: Generate graphs
    graphs = GraphGenerator(df, output_dir)
    graphs.plot_avg_response_time_by_label()
    graphs.plot_error_rate_over_time()
    graphs.plot_response_time_over_time_by_label()
    graphs.plot_p90_response_time_by_label()
    graphs.plot_error_rate_pie()
    graphs.plot_response_code_distribution_pie()

    # Step 3: Generate report
    report = ReportGenerator(df, output_dir)
    graph_files = [
        'avg_response_time_by_label.png',
        'error_rate_over_time.png',
        'response_time_over_time_by_label.png',
        'p90_response_time_by_label.png',
        'error_rate_pie.png',
        'response_code_distribution_pie.png'
    ]
    report.create_markdown_report(graph_files)

    print(f"✅ Report generated in '{output_dir}/report.md'")


if __name__ == '__main__':
    main()
