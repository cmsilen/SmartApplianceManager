import os
import plotly.graph_objects as go


class CoverageReport:

    def __init__(self):
        self.fig = None

    def generate_coverage_report(self, dataset):

        features = [
            "mean_current",
            "mean_voltage",
            "mean_temperature",
            "mean_ex_temperature",
            "mean_ex_humidity",
            "mean_occupancy"
        ]

        feature_ranges = {
            "mean_current": (0, 20),
            "mean_voltage": (200, 250),
            "mean_temperature": (20, 100),
            "mean_ex_temperature": (-20, 50),
            "mean_ex_humidity": (0, 1),
            "mean_occupancy": (0, 10)
        }

        def normalize(value, min_v, max_v):
            if max_v == min_v:
                return 0
            return (value - min_v) / (max_v - min_v)

        feature_sums = {f: 0 for f in features}
        n = len(dataset)

        for row in dataset:
            for i, f in enumerate(features):
                value = row[i + 1] if isinstance(row, tuple) else row[f]
                feature_sums[f] += value

        feature_avg = {f: feature_sums[f] / n for f in features}

        normalized_avg = [
            normalize(feature_avg[f], *feature_ranges[f])
            for f in features
        ]

        # Radar chart
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=normalized_avg,
            theta=features,
            fill='toself',
            mode="lines+markers",
            name='Average Feature Values',
            line=dict(color='royalblue')
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title="Coverage Report (Normalized Radar Chart)",
            template="plotly_white"
        )

        self.fig = fig

    def show_coverage_report(self, output_file="~/coverage_report.png"):
        output_file = os.path.expanduser(output_file)
        self.fig.write_image(output_file)
