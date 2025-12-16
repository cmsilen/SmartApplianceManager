import os
import plotly.graph_objects as go


class BalancingReport:

    def __init__(self):
        self.fig = None

    def generate_balancing_report(self, dataset, tolerance_percentage=10):
        # Extract labels
        labels = [row[-1] if isinstance(row, tuple) else row['label'] for row in dataset]

        # Count occurrences of each label
        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1

        classes = list(label_counts.keys())
        counts = [label_counts[c] for c in classes]

        # Compute average count
        avg_count = sum(counts) / len(counts)

        # Compute tolerance range
        tol_lower = avg_count * (1 - tolerance_percentage / 100)
        tol_upper = avg_count * (1 + tolerance_percentage / 100)

        # Create bar chart
        fig = go.Figure()

        # Add bars for each class
        fig.add_trace(go.Bar(
            x=classes,
            y=counts,
            name="Class Counts"
        ))

        # Add tolerance band
        fig.add_trace(go.Scatter(
            x=classes,
            y=[tol_upper] * len(classes),
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Tolerance Upper'
        ))

        fig.add_trace(go.Scatter(
            x=classes,
            y=[tol_lower] * len(classes),
            mode='lines',
            line=dict(color='black', dash='dash'),
            name='Tolerance Lower'
        ))

        # Layout
        fig.update_layout(
            title=f"Balancing Report (tolerance ±{tolerance_percentage}%)",
            xaxis_title="Class",
            yaxis_title="Count",
            yaxis=dict(range=[0, max(counts + [tol_upper]) * 1.1]),
            template="plotly_white"
        )

        # Save as PNG
        self.fig = fig

    def show_balancing_report(self, output_file="~/balancing_report.png"):
        output_file = os.path.expanduser(output_file)
        self.fig.write_image(output_file)
