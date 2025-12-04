import os
import plotly.graph_objects as go


class CoverageReport:

    def __init__(self):
        self.fig = None

    def generate_coverage_report(self, dataset):
        """
        Generates a coverage report radar chart based on feature distributions.

        Parameters:
        - dataset: list of tuples or dicts containing the features:
            mean_current, mean_voltage, mean_temperature, mean_external_temperature,
            mean_external_humidity, mean_occupancy
        - output_file: filename to save the PNG chart.
        """
        features = [
            "mean_current",
            "mean_voltage",
            "mean_temperature",
            "mean_external_temperature",
            "mean_external_humidity",
            "mean_occupancy"
        ]

        # Initialize sums
        feature_sums = {f: 0 for f in features}
        n = len(dataset)
        if n == 0:
            print("[WARNING] Dataset is empty. No chart will be generated.")
            return

        # Aggregate values
        for row in dataset:
            for i, f in enumerate(features):
                value = row[i + 1] if isinstance(row, tuple) else row[f]
                feature_sums[f] += value

        # Compute averages
        feature_avg = [feature_sums[f] / n for f in features]

        # Create radar chart
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=feature_avg,
            theta=features,
            fill='toself',
            name='Average Feature Values',
            line=dict(color='royalblue')
        ))

        # Layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    # optional: automatically scale
                )
            ),
            showlegend=True,
            title="Coverage Report (Radar Chart)",
            template="plotly_white"
        )

        self.fig = fig

    def show_coverage_report(self, output_file="~/coverage_report.png"):
        output_file = os.path.expanduser(output_file)
        self.fig.write_image(output_file)
