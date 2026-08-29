from datetime import datetime
from pathlib import Path


def produce_html_report(validation_results):
    """
    Generate an HTML data quality report from validation results.
    """

    dataset_name = validation_results["meta"]["name"]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path(f"../reports/validation/{dataset_name}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{dataset_name}_{timestamp}.html"
    
    df = validation_results["meta"]["df"]

    total_records = len(df)

    # ---------------------------------------------------------
    # Determine overall status
    # ---------------------------------------------------------

    schema = validation_results["schema"]
    structural = validation_results["structural"]
    business_issues = validation_results["business"]["issues"]
    quality_issues = validation_results["quality"]["issues"]

    schema_pass = (
        not schema["missing_cols"]
        and not schema["unexpected_cols"]
        and not schema["invalid_dtypes"]
    )

    structural_pass = (
        structural["invalid_rows"].any(axis=1).sum() == 0
        and len(structural["duplicate_ids"]) == 0
    )

    business_pass = not business_issues
    quality_pass = not quality_issues

    report_status = (
        schema_pass
        and structural_pass
        and business_pass
        and quality_pass
    )

    # ---------------------------------------------------------
    # Record counts
    # ---------------------------------------------------------

    invalid_records = validation_results["overall_invalid"].sum()
    valid_records = total_records - invalid_records

    # ---------------------------------------------------------
    # Helper functions
    # ---------------------------------------------------------

    def status_badge(status):
        if status:
            return '<span class="badge pass">PASS</span>'
        return '<span class="badge fail">FAIL</span>'

    def issue_count(value):
        try:
            return int(value.sum())
        except AttributeError:
            return len(value)

    # ---------------------------------------------------------
    # Schema validation
    # ---------------------------------------------------------

    missing_cols = schema["missing_cols"]
    unexpected_cols = schema["unexpected_cols"]
    invalid_dtypes = schema["invalid_dtypes"]

    schema_rows = ""

    for column in validation_results["meta"]["expected_dtypes"]:
        if column in invalid_dtypes:
            schema_rows += f"""
                <tr>
                    <td>{column}</td>
                    <td>{status_badge(False)}</td>
                </tr>
            """
        else:
            schema_rows += f"""
                <tr>
                    <td>{column}</td>
                    <td>{status_badge(True)}</td>
                </tr>
            """

    # ---------------------------------------------------------
    # Structural validation
    # ---------------------------------------------------------

    required_fields = validation_results["meta"]["required_fields"]
    invalid_rows = structural["invalid_rows"]

    structural_rows = ""

    for column in required_fields:
        failed = invalid_rows[column].any()

        structural_rows += f"""
            <tr>
                <td>{column}</td>
                <td>{status_badge(not failed)}</td>
            </tr>
        """

    pk = validation_results["meta"]["pk"]

    missing_ids = int(invalid_rows[pk].sum())
    duplicate_ids = len(structural["duplicate_ids"])
    structural_invalid_records = int(
        invalid_rows.any(axis=1).sum()
    )

    # ---------------------------------------------------------
    # Business rule issues
    # ---------------------------------------------------------

    business_rows = ""

    if business_issues:
        for key, value in business_issues.items():
            business_rows += f"""
                <tr>
                    <td>{key.upper()}</td>
                    <td>{issue_count(value)}</td>
                </tr>
            """
    else:
        business_rows = """
            <tr>
                <td colspan="2">No business rule violations found.</td>
            </tr>
        """

    # ---------------------------------------------------------
    # Data quality issues
    # ---------------------------------------------------------

    quality_rows = ""

    if quality_issues:
        for key, value in quality_issues.items():
            quality_rows += f"""
                <tr>
                    <td>{key.upper()}</td>
                    <td>{issue_count(value)}</td>
                </tr>
            """
    else:
        quality_rows = """
            <tr>
                <td colspan="2">No data quality issues found.</td>
            </tr>
        """

    # ---------------------------------------------------------
    # Overall status
    # ---------------------------------------------------------

    overall_status_text = "PASS" if report_status else "FAIL"
    overall_class = "pass" if report_status else "fail"

    # ---------------------------------------------------------
    # HTML document
    # ---------------------------------------------------------

    html = f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{dataset_name} Data Quality Report</title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f6f8;
            color: #1f2937;
            margin: 0;
            padding: 40px;
        }}

        .container {{
            max-width: 1100px;
            margin: auto;
        }}

        .header {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        h1 {{
            margin: 0 0 10px 0;
            font-size: 30px;
        }}

        h2 {{
            margin-top: 0;
        }}

        .metadata {{
            color: #6b7280;
            line-height: 1.8;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }}

        .card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        .card-title {{
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 8px;
        }}

        .card-value {{
            font-size: 28px;
            font-weight: bold;
        }}

        .status-card {{
            text-align: center;
        }}

        .status-card .card-value {{
            font-size: 24px;
        }}

        .pass {{
            color: #15803d;
        }}

        .fail {{
            color: #dc2626;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }}

        .badge.pass {{
            background: #dcfce7;
            color: #15803d;
        }}

        .badge.fail {{
            background: #fee2e2;
            color: #dc2626;
        }}

        .section {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th {{
            background: #f3f4f6;
            text-align: left;
            padding: 12px;
            font-size: 14px;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}

        .two-column {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .issue-box {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }}

        .footer {{
            text-align: center;
            color: #6b7280;
            margin-top: 30px;
            font-size: 13px;
        }}

        @media (max-width: 800px) {{
            .summary {{
                grid-template-columns: 1fr 1fr;
            }}

            .two-column {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 500px) {{
            body {{
                padding: 15px;
            }}

            .summary {{
                grid-template-columns: 1fr;
            }}
        }}

    </style>
</head>

<body>

<div class="container">

    <!-- Header -->

    <div class="header">

        <h1>FinTech ETL — Data Quality Report</h1>

        <div class="metadata">
            <strong>Dataset:</strong> {dataset_name}.csv<br>
            <strong>Generated:</strong>
            {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
            <strong>Primary Key:</strong> {pk}
        </div>

    </div>


    <!-- Summary -->

    <div class="summary">

        <div class="card status-card">
            <div class="card-title">OVERALL STATUS</div>
            <div class="card-value {overall_class}">
                {overall_status_text}
            </div>
        </div>

        <div class="card">
            <div class="card-title">TOTAL RECORDS</div>
            <div class="card-value">
                {total_records:,}
            </div>
        </div>

        <div class="card">
            <div class="card-title">VALID RECORDS</div>
            <div class="card-value pass">
                {valid_records:,}
            </div>
        </div>

        <div class="card">
            <div class="card-title">INVALID RECORDS</div>
            <div class="card-value fail">
                {invalid_records:,}
            </div>
        </div>

    </div>


    <!-- Validation Summary -->

    <div class="section">

        <h2>Validation Summary</h2>

        <table>

            <thead>
                <tr>
                    <th>Validation Layer</th>
                    <th>Status</th>
                </tr>
            </thead>

            <tbody>

                <tr>
                    <td>Schema Validation</td>
                    <td>{status_badge(schema_pass)}</td>
                </tr>

                <tr>
                    <td>Structural Validation</td>
                    <td>{status_badge(structural_pass)}</td>
                </tr>

                <tr>
                    <td>Business Rule Validation</td>
                    <td>{status_badge(business_pass)}</td>
                </tr>

                <tr>
                    <td>Data Quality Validation</td>
                    <td>{status_badge(quality_pass)}</td>
                </tr>

            </tbody>

        </table>

    </div>


    <!-- Schema Validation -->

    <div class="section">

        <h2>1. Schema Validation</h2>

        <p>
            Missing Columns:
            <strong>{missing_cols if missing_cols else "None"}</strong>
        </p>

        <p>
            Unexpected Columns:
            <strong>{unexpected_cols if unexpected_cols else "None"}</strong>
        </p>

        <table>

            <thead>
                <tr>
                    <th>Column</th>
                    <th>Status</th>
                </tr>
            </thead>

            <tbody>
                {schema_rows}
            </tbody>

        </table>

    </div>


    <!-- Structural Validation -->

    <div class="section">

        <h2>2. Structural Validation</h2>

        <div class="two-column">

            <div>

                <h3>Required Fields</h3>

                <table>

                    <thead>
                        <tr>
                            <th>Field</th>
                            <th>Status</th>
                        </tr>
                    </thead>

                    <tbody>
                        {structural_rows}
                    </tbody>

                </table>

            </div>

            <div>

                <h3>Primary Key</h3>

                <div class="issue-box">
                    Missing IDs:
                    <strong>{missing_ids}</strong>
                </div>

                <div class="issue-box">
                    Duplicate IDs:
                    <strong>{duplicate_ids}</strong>
                </div>

                <div class="issue-box">
                    Invalid Records:
                    <strong>{structural_invalid_records}</strong>
                </div>

            </div>

        </div>

    </div>


    <!-- Business Rules -->

    <div class="section">

        <h2>3. Business Rule Validation</h2>

        <table>

            <thead>
                <tr>
                    <th>Rule</th>
                    <th>Invalid Records</th>
                </tr>
            </thead>

            <tbody>
                {business_rows}
            </tbody>

        </table>

    </div>


    <!-- Data Quality -->

    <div class="section">

        <h2>4. Data Quality Validation</h2>

        <table>

            <thead>
                <tr>
                    <th>Issue</th>
                    <th>Records</th>
                </tr>
            </thead>

            <tbody>
                {quality_rows}
            </tbody>

        </table>

    </div>


    <!-- Footer -->

    <div class="footer">

        FinTech ETL Data Quality Pipeline<br>
        Report generated automatically

    </div>

</div>

</body>
</html>
"""

    # ---------------------------------------------------------
    # Write report
    # ---------------------------------------------------------

    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        html,
        encoding="utf-8"
    )

    print(f"HTML report generated: {output_path}")

