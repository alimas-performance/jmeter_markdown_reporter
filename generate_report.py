import os
import sys
from typing import List

import pandas as pd
import matplotlib.pyplot as plt

# Constants
GRAPH_FILES = [
    'error_rate_pie.png',
    'response_code_distribution_pie.png',
    'avg_response_time_by_label.png',
    'error_rate_over_time.png',
    'response_time_over_time_by_label.png',
    'p90_response_time_by_label.png',
]


class JTLReader:
    """Reads and preprocesses JMeter JTL (JMeter Test Log) files.

    This class handles the loading and initial preprocessing of JMeter test results,
    including timestamp conversion and success flag standardization.

    Attributes:
        filepath (str): Path to the JTL file to be processed.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def read(self) -> pd.DataFrame:
        """Reads the JTL CSV file into a pandas DataFrame.

        Performs initial data preprocessing including:
        - Converting timestamps to datetime objects
        - Converting success column to boolean type

        Returns:
            pd.DataFrame: Processed DataFrame with columns:
                - timeStamp (datetime): Request timestamp
                - elapsed (int): Response time in milliseconds
                - label (str): Name of the request
                - responseCode (str): HTTP response code
                - success (bool): Whether the request was successful
                - ... (other columns from JMeter output)

        Raises:
            FileNotFoundError: If the JTL file doesn't exist
            ValueError: If the JTL file is empty

        Example:
            >>> reader = JTLReader('results.jtl')
            >>> df = reader.read()
            >>> print(df.columns)
        """
        if not os.path.isfile(self.filepath):
            raise FileNotFoundError(f"❌ JTL file not found: {self.filepath}")

        df = pd.read_csv(self.filepath)
        if df.empty:
            raise ValueError(f"❌ JTL file is empty: {self.filepath}")

        df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='ms')
        df['success'] = df['success'].astype(bool)
        return df


class GraphGenerator:
    """Generates and saves performance analysis graphs from JMeter JTL data.

    This class creates various visualizations to analyze performance test results,
    including response times, error rates, and distribution charts.

    Attributes:
        df (pd.DataFrame): Preprocessed JMeter data
        output_dir (str): Directory where generated graphs will be saved
    """

    def __init__(self, df: pd.DataFrame, output_dir: str):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_avg_response_time_by_label(self) -> None:
        data = self.df.groupby('label')['elapsed'].mean().sort_values()
        fig, ax = plt.subplots(figsize=(12, 6))
        data.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title('Average Response Time by Label')
        ax.set_ylabel('Avg Response Time (ms)')
        plt.tight_layout()
        self._save_plot('avg_response_time_by_label.png')

    def plot_error_rate_over_time(self) -> None:
        df = self.df.set_index('timeStamp')
        errors = (~df['success']).resample('1s').sum()
        total = df['success'].resample('1s').count()
        error_rate = (errors / total).fillna(0)

        fig, ax = plt.subplots(figsize=(12, 6))
        error_rate.plot(color='red', ax=ax)
        ax.set_title('Error Rate Over Time')
        ax.set_ylabel('Error Rate')
        plt.tight_layout()
        self._save_plot('error_rate_over_time.png')

    def plot_response_time_over_time_by_label(self) -> None:
        df = self.df.set_index('timeStamp')
        fig, ax = plt.subplots(figsize=(12, 6))
        for label, group in df.groupby('label'):
            ax.plot(group.index, group['elapsed'], label=label)
        ax.legend()
        ax.set_title('Response Time Over Time by Label')
        ax.set_ylabel('Response Time (ms)')
        plt.tight_layout()
        self._save_plot('response_time_over_time_by_label.png')

    def plot_p90_response_time_by_label(self) -> None:
        p90 = self.df.groupby('label')['elapsed'].quantile(0.90).sort_values()
        fig, ax = plt.subplots(figsize=(12, 6))
        p90.plot(kind='bar', color='orange', ax=ax)
        ax.set_title('90th Percentile Response Time by Label')
        ax.set_ylabel('P90 Response Time (ms)')
        plt.tight_layout()
        self._save_plot('p90_response_time_by_label.png')

    def plot_error_rate_pie(self) -> None:
        counts = self.df['success'].value_counts()
        labels = ['Success', 'Failure']
        fig, ax = plt.subplots(figsize=(6, 6))
        counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, labels=labels, ax=ax)
        ax.set_title('Error Rate: Success vs Failure')
        ax.set_ylabel('')
        plt.tight_layout()
        self._save_plot('error_rate_pie.png')

    def plot_response_code_distribution_pie(self) -> None:
        codes = self.df['responseCode'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 8))
        codes.plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax)
        ax.set_title('Response Code Distribution')
        ax.set_ylabel('')
        plt.tight_layout()
        self._save_plot('response_code_distribution_pie.png')

    def _save_plot(self, filename: str) -> None:
        """Save the current Matplotlib figure."""
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath)
        plt.close()


class ReportGenerator:
    """Generates a comprehensive Markdown report containing performance graphs and metrics.

    This class processes the JMeter test results and creates a detailed report including:
    - Performance graphs visualization
    - Summary statistics per API endpoint
    - Error rate analysis
    - Response time distributions

    Attributes:
        df (pd.DataFrame): Preprocessed JMeter data
        output_dir (str): Directory where the report and assets will be saved
    """

    def __init__(self, df: pd.DataFrame, output_dir: str):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_summary_table(self) -> pd.DataFrame:
        """Compute performance metrics per label."""
        summary = self.df.groupby('label').agg(
            avg_response_time=('elapsed', 'mean'),
            p90_response_time=('elapsed', lambda x: x.quantile(0.9)),
            max_response_time=('elapsed', 'max'),
            successes=('success', lambda x: (x == True).sum()),
            failures=('success', lambda x: (x == False).sum()),
        )
        return summary.round(2)

    def create_markdown_report(self, graph_files: List[str]) -> None:
        """Create a Markdown report summarizing graphs and metrics."""
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


def main(filepath: str, output_dir: str = 'output'):
    """Main entry point for generating the performance analysis report.

    Args:
        filepath (str): Path to the JMeter JTL file to analyze
        output_dir (str, optional): Directory where the report and graphs will be saved.
            Defaults to 'output'.

    Example:
        >>> python generate_report.py results.jtl ./reports
    """
    try:
        reader = JTLReader(filepath)
        df = reader.read()

        graphs = GraphGenerator(df, output_dir)
        graphs.plot_avg_response_time_by_label()
        graphs.plot_error_rate_over_time()
        graphs.plot_response_time_over_time_by_label()
        graphs.plot_p90_response_time_by_label()
        graphs.plot_error_rate_pie()
        graphs.plot_response_code_distribution_pie()

        report = ReportGenerator(df, output_dir)
        report.create_markdown_report(GRAPH_FILES)

        print(f"✅ Report generated successfully in '{output_dir}/report.md'")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <path_to_jtl_file> [output_dir]")
        sys.exit(1)

    jtl_file = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else 'output'
    main(jtl_file, output_directory)
