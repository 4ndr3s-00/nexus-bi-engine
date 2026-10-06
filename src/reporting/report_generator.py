from datetime import datetime
from typing import Any

class StandaloneHtmlReportGenerator:
    """
    Generates single-file, interactive HTML executive reports styled with modern dark luxury theme.
    Can be opened in any Linux browser, sent via email, or printed to PDF without external servers.
    """
    @classmethod
    def generate_html(cls, report_data: dict[str, Any]) -> str:
        headline = report_data.get("headline", "Informe Ejecutivo de Negocio")
        summary = report_data.get("summary", "")
        kpi_cards = report_data.get("kpi_cards", [])
        highlights = report_data.get("highlights", [])
        recommendations = report_data.get("recommendations", [])
        table_data = report_data.get("table_data", [])
        sql = report_data.get("sql", "")
        latency_ms = report_data.get("latency_ms", 0.0)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build KPI HTML
        kpi_html = ""
        for card in kpi_cards:
            kpi_html += f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-label">{card.get('label', '')}</span>
                    <span class="kpi-badge">{card.get('change', '')}</span>
                </div>
                <div class="kpi-value">{card.get('value', '')}</div>
            </div>
            """

        # Build Highlights HTML
        highlights_html = ""
        for h in highlights:
            clean_h = h.replace("**", "<strong>").replace("**", "</strong>")
            highlights_html += f"<li>{clean_h}</li>"

        # Build Recommendations HTML
        recommendations_html = ""
        for r in recommendations:
            recommendations_html += f"<li>{r}</li>"

        # Build Table HTML
        table_html = ""
        if table_data:
            cols = list(table_data[0].keys())
            header_th = "".join(f"<th>{c.replace('_', ' ').upper()}</th>" for c in cols)
            rows_td = ""
            for row in table_data:
                tds = "".join(f"<td>{f'${v:,.2f}' if isinstance(v, (int, float)) and v > 1000 else v}</td>" for v in row.values())
                rows_td += f"<tr>{tds}</tr>"

            table_html = f"""
            <div class="table-container">
                <table>
                    <thead><tr>{header_th}</tr></thead>
                    <tbody>{rows_td}</tbody>
                </table>
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{headline} | Nexus BI Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0d0e12;
            --card-bg: #151720;
            --border: #222533;
            --text-main: #f1f5f9;
            --text-muted: #8b8fa3;
            --accent-purple: #9333ea;
            --accent-pink: #ec4899;
            --accent-green: #22c55e;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 1000px;
            width: 100%;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 1px solid var(--border);
            padding-bottom: 24px;
            margin-bottom: 30px;
        }}
        .badge {{
            display: inline-block;
            background: rgba(147, 51, 234, 0.15);
            color: #c084fc;
            border: 1px solid rgba(147, 51, 234, 0.3);
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        h1 {{ font-size: 24px; font-weight: 800; color: #fff; }}
        .meta {{ font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }}
        
        /* Grid KPIs */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            background: #191b26;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
        }}
        .kpi-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .kpi-label {{ font-size: 12px; color: var(--text-muted); font-weight: 600; }}
        .kpi-badge {{
            font-size: 11px;
            color: var(--accent-green);
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.2);
            padding: 2px 8px;
            border-radius: 999px;
            font-weight: 700;
        }}
        .kpi-value {{
            font-size: 24px;
            font-weight: 800;
            color: #fff;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Summary Box */
        .summary-box {{
            background: #1b1e2a;
            border: 1px solid #282c3e;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
        }}
        .section-title {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-pink);
            margin-bottom: 8px;
        }}
        .summary-text {{ font-size: 14px; line-height: 1.6; color: #cbd5e1; }}

        /* Two columns */
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .box {{
            background: #191b26;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
        }}
        ul {{ list-style: none; }}
        li {{
            font-size: 12px;
            line-height: 1.6;
            color: #cbd5e1;
            margin-bottom: 10px;
            position: relative;
            padding-left: 16px;
        }}
        li::before {{
            content: "•";
            position: absolute;
            left: 0;
            color: var(--accent-purple);
            font-weight: bold;
        }}

        /* Table */
        .table-container {{
            overflow-x: auto;
            border: 1px solid var(--border);
            border-radius: 16px;
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            text-align: left;
        }}
        th {{
            background: #181a24;
            padding: 12px 16px;
            font-weight: 600;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border);
            font-size: 10px;
        }}
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid #1e212e;
            font-family: 'JetBrains Mono', monospace;
            color: #e2e8f0;
        }}
        tr:last-child td {{ border-bottom: none; }}
        
        /* SQL Code Box */
        .sql-box {{
            background: #000;
            border: 1px solid #282c3e;
            border-radius: 12px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #c084fc;
            overflow-x: auto;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <span class="badge">Nexus BI Engine • Executive Report</span>
                <h1>{headline}</h1>
            </div>
            <div class="meta">
                Generado: {timestamp}<br>
                Latencia OLAP: {latency_ms} ms
            </div>
        </div>

        <div class="kpi-grid">
            {kpi_html}
        </div>

        <div class="summary-box">
            <div class="section-title">Síntesis para la Dirección</div>
            <div class="summary-text">{summary}</div>
        </div>

        <div class="grid-2">
            <div class="box">
                <div class="section-title" style="color: #22c55e;">Hallazgos Principales</div>
                <ul>{highlights_html}</ul>
            </div>
            <div class="box">
                <div class="section-title" style="color: #f59e0b;">Recomendaciones Estratégicas</div>
                <ul>{recommendations_html}</ul>
            </div>
        </div>

        {table_html}

        <div>
            <div class="section-title" style="color: #94a3b8;">Consulta SQL Ejecutada (Zero-Trust Sandbox)</div>
            <div class="sql-box">{sql}</div>
        </div>
    </div>
</body>
</html>"""
