import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# Set Page Config (Inter font, Wide Layout, and Premium Page Title)
st.set_page_config(
    page_title="Emerald Financial Visualizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS matching the Stitch-generated "Emerald Fidelity" design system
def inject_custom_css():
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Public+Sans:wght@300;400;500;600;700&display=swap');

        /* Foundational Dark Theme Styles */
        .stApp {
            background-color: #0e1511 !important;
            color: #dde5dd !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #09100c !important;
            border-right: 1px solid rgba(78, 222, 163, 0.15) !important;
            padding-top: 2rem !important;
        }
        
        /* Typography overrides */
        h1, h2, h3, h4, h5, h6 {
            color: #dde5dd !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
        }
        
        label, p, span, div {
            font-family: 'Public Sans', sans-serif !important;
            color: #dde5dd;
        }

        /* Customize File Uploader Widget */
        [data-testid="stFileUploader"] {
            border: 1px dashed rgba(78, 222, 163, 0.3) !important;
            background-color: #161d19 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: #0fb981 !important;
            box-shadow: 0 0 10px rgba(78, 222, 163, 0.1) !important;
        }

        /* Buttons Styling */
        .stButton > button {
            background-color: #0fb981 !important;
            color: #003824 !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.3s ease !important;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #4edea3 !important;
            color: #003824 !important;
            box-shadow: 0 0 10px rgba(78, 222, 163, 0.3) !important;
        }
        
        /* Download Link Button Override */
        .stDownloadButton > button {
            background-color: transparent !important;
            color: #4edea3 !important;
            border: 1px solid rgba(78, 222, 163, 0.4) !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            width: 100%;
            transition: all 0.3s ease !important;
        }
        .stDownloadButton > button:hover {
            background-color: rgba(78, 222, 163, 0.1) !important;
            border-color: #4edea3 !important;
        }

        /* KPI Card Container Styling */
        .kpi-card {
            background-color: #1a211d !important;
            border: 1px solid rgba(78, 222, 163, 0.15) !important;
            border-radius: 8px !important;
            padding: 1.25rem !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
            text-align: left;
            margin-bottom: 1rem;
        }
        .kpi-title {
            font-size: 0.75rem !important;
            color: #bbcabf !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 500 !important;
        }
        .kpi-value {
            font-size: 1.85rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            margin: 0.25rem 0 !important;
        }
        .kpi-delta {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }
        .kpi-delta.up {
            color: #4edea3 !important;
        }
        .kpi-delta.down {
            color: #fc7c78 !important;
        }
        .kpi-delta.neutral {
            color: #bbcabf !important;
        }

        /* Selectboxes & Input Styling */
        div[data-baseweb="select"] > div {
            background-color: #161d19 !important;
            border: 1px solid rgba(78, 222, 163, 0.15) !important;
            color: #dde5dd !important;
            border-radius: 8px !important;
        }
        div[role="listbox"] {
            background-color: #161d19 !important;
            color: #dde5dd !important;
        }
        
        /* Table / Dataframe styling overlay */
        div[data-testid="stTable"] table {
            background-color: #1a211d !important;
            color: #dde5dd !important;
            border-collapse: collapse !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        
        /* Custom footer style */
        .footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(78, 222, 163, 0.15);
            text-align: center;
            font-size: 0.8rem;
            color: #bbcabf;
        }
        </style>
    """, unsafe_allow_html=True)

# ----------------- DATA PROCESSING ENGINE -----------------

def clean_and_parse_excel(uploaded_file):
    """
    Cleans, parses, and standardizes an Excel sheet of financial data.
    Auto-detects layout formats (Metrics-as-rows vs Metrics-as-columns),
    cleans values (removes commas, %, $ symbols, handles negative brackets),
    and enforces a numeric float64 representation with period columns.
    """
    try:
        # Read the raw Excel file, ignoring header parsing initially
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # Drop completely empty rows and columns
        df_raw = df_raw.dropna(how='all').dropna(how='all', axis=1)
        
        # Reset indexes
        df_raw = df_raw.reset_index(drop=True)
        df_raw.columns = range(df_raw.shape[1])
        
        if df_raw.empty:
            return None, "The uploaded file contains no data."

        # Helper: check if a cell can represent a number
        def is_numeric_value(val):
            if pd.isna(val):
                return False
            try:
                if isinstance(val, (int, float)):
                    return True
                s = str(val).replace('$', '').replace(',', '').replace('%', '').replace('(', '').replace(')', '').strip()
                if s == '-' or s == '':
                    return True
                float(s)
                return True
            except ValueError:
                return False

        # Determine layout structure:
        # Row 0 and Column 0 numerical composition analysis
        row0 = df_raw.iloc[0]
        col0 = df_raw.iloc[:, 0]
        
        row0_numeric_count = sum(1 for x in row0[1:] if is_numeric_value(x))
        col0_numeric_count = sum(1 for x in col0[1:] if is_numeric_value(x))
        
        row0_numeric_ratio = row0_numeric_count / max(1, len(row0) - 1)
        col0_numeric_ratio = col0_numeric_count / max(1, len(col0) - 1)
        
        # Format B (Transposed): columns represent metrics, rows represent periods
        # characterized by having a column of periods (col 0 is numeric periods/years)
        is_transposed = col0_numeric_ratio > row0_numeric_ratio
        
        if is_transposed:
            # Format B: Rows as Periods, Columns as Metrics
            headers = list(df_raw.iloc[0])
            # Find period column name (e.g. Year, Date, Period)
            period_col_idx = 0
            for idx, h in enumerate(headers):
                if str(h).lower() in ['year', 'date', 'period', 'quarter', 'time']:
                    period_col_idx = idx
                    break
            
            # Setup columns
            df_raw.columns = headers
            df = df_raw.iloc[1:].copy()
            
            period_col_name = headers[period_col_idx]
            df = df.set_index(period_col_name)
            
            # Transpose to standardize internally to Metrics-as-Rows, Periods-as-Columns
            df = df.T
        else:
            # Format A: Metrics as Rows, Periods as Columns
            period_headers = list(df_raw.iloc[0, 1:])
            period_headers = [str(p).strip() for p in period_headers]
            
            metric_names = list(df_raw.iloc[1:, 0])
            metric_names = [str(m).strip() for m in metric_names]
            
            data = df_raw.iloc[1:, 1:].copy()
            data.index = metric_names
            data.columns = period_headers
            df = data

        # Values cleaning: strip symbols ($ , % ), handle parentheses negative numbers
        def clean_val(val):
            if pd.isna(val):
                return 0.0
            if isinstance(val, (int, float)):
                return float(val)
            s = str(val).strip()
            # Handle brackets as negative numbers e.g. (1,234.50) -> -1234.50
            is_negative = False
            if s.startswith('(') and s.endswith(')'):
                is_negative = True
                s = s[1:-1]
            s = s.replace('$', '').replace(',', '').replace('%', '').strip()
            if s == '-' or s == '' or s.lower() == 'nan':
                return 0.0
            try:
                num = float(s)
                return -num if is_negative else num
            except ValueError:
                return 0.0

        # Apply mapping element-wise safely
        if hasattr(df, 'map'):
            df = df.map(clean_val)
        else:
            df = df.applymap(clean_val)

        # Drop rows with empty metric names
        df.index = [str(idx).strip() for idx in df.index]
        df = df[df.index != ""]
        df.columns = [str(col).strip() for col in df.columns]
        
        # Chronological column sorting
        def get_sort_val(col):
            try:
                return float(col)
            except ValueError:
                return col
        try:
            sorted_cols = sorted(df.columns, key=get_sort_val)
            df = df[sorted_cols]
        except Exception:
            pass # Keep original if sorting fails
            
        return df, None
    except Exception as e:
        return None, f"Parsing Error: {str(e)}"

# ----------------- FINANCIAL CALCULATION ENGINE -----------------

def calculate_growth_rates(df):
    """
    Calculates year-over-year (YoY) growth percentages for each metric.
    """
    growth_df = pd.DataFrame(index=df.index, columns=df.columns)
    # The first period has no prior period for growth calculation
    growth_df.iloc[:, 0] = 0.0
    for i in range(1, df.shape[1]):
        prev_col = df.iloc[:, i-1]
        curr_col = df.iloc[:, i]
        growth = []
        for p, c in zip(prev_col, curr_col):
            if p == 0:
                growth.append(100.0 if c > 0 else (0.0 if c == 0 else -100.0))
            else:
                growth.append(((c - p) / abs(p)) * 100.0)
        growth_df.iloc[:, i] = growth
    return growth_df

def calculate_common_size(df, base_metric):
    """
    Normalizes all financial metrics as a percentage of a baseline metric (e.g. Revenue)
    using vectorized pandas division.
    """
    if base_metric not in df.index:
        return df
    
    # Extract baseline row, taking the first instance in case of duplicate indices
    base_row = df.loc[base_metric]
    if isinstance(base_row, pd.DataFrame):
        base_row = base_row.iloc[0]
        
    # Perform vectorized division along columns axis (axis=1) and scale by 100
    common_size_df = df.div(base_row, axis=1) * 100.0
    
    # Replace infinite values (from division by zero) and fill NaNs gracefully
    common_size_df = common_size_df.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    
    return common_size_df

# ----------------- SAMPLE DATA GENERATION -----------------

def get_sample_excel_bytes():
    """
    Generates a sample professional Income Statement and exports it to Excel binary bytes.
    """
    data = {
        "Financial Metric": [
            "Revenue", 
            "Cost of Goods Sold (COGS)", 
            "Gross Profit", 
            "Research & Development (R&D)", 
            "Sales & Marketing (S&M)", 
            "General & Administrative (G&A)",
            "Operating Expenses",
            "Operating Income (EBIT)",
            "Taxes & Interest",
            "Net Income"
        ],
        "2020": [1000000, 300000, 700000, 150000, 250000, 100000, 500000, 200000, 40000, 160000],
        "2021": [1500000, 420000, 1080000, 220000, 350000, 130000, 700000, 380000, 76000, 304000],
        "2022": [2200000, 580000, 1620000, 310000, 500000, 170000, 980000, 640000, 128000, 512000],
        "2023": [3100000, 780000, 2320000, 410000, 680000, 220000, 1310000, 1010000, 202000, 808000],
        "2024": [4200000, 1000000, 3200000, 500000, 850000, 280000, 1630000, 1570000, 314000, 1256000],
        "2025": [5500000, 1250000, 4250000, 600000, 1100000, 340000, 2040000, 2210000, 442000, 1768000]
    }
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Income Statement')
    return output.getvalue()

def load_default_dataframe():
    """
    Creates the default pandas DataFrame for local preview.
    """
    data = {
        "Revenue": [1000000, 1500000, 2200000, 3100000, 4200000, 5500000],
        "Cost of Goods Sold (COGS)": [300000, 420000, 580000, 780000, 1000000, 1250000],
        "Gross Profit": [700000, 1080000, 1620000, 2320000, 3200000, 4250000],
        "Research & Development (R&D)": [150000, 220000, 310000, 410000, 500000, 600000],
        "Sales & Marketing (S&M)": [250000, 350000, 500000, 680000, 850000, 1100000],
        "General & Administrative (G&A)": [100000, 130000, 170000, 220000, 280000, 340000],
        "Operating Expenses": [500000, 700000, 980000, 1310000, 1630000, 2040000],
        "Operating Income (EBIT)": [200000, 380000, 640000, 1010000, 1570000, 2210000],
        "Taxes & Interest": [40000, 76000, 128000, 202000, 314000, 442000],
        "Net Income": [160000, 304000, 512000, 808000, 1256000, 1768000]
    }
    df = pd.DataFrame(data, index=["2020", "2021", "2022", "2023", "2024", "2025"]).T
    return df

# Helper to identify metrics dynamically (case-insensitive fuzzy match)
def get_metric_by_name(df, name_queries):
    for q in name_queries:
        for idx in df.index:
            if q.lower() in idx.lower():
                return idx
    return None

# Helper to format numbers dynamically
def format_large_number(val):
    sign = "-" if val < 0 else ""
    val = abs(val)
    if val >= 1_000_000_000:
        return f"{sign}${val / 1_000_000_000:.2f} B"
    elif val >= 1_000_000:
        return f"{sign}${val / 1_000_000:.2f} M"
    elif val >= 1_000:
        return f"{sign}${val / 1_000:.1f} K"
    else:
        return f"{sign}${val:.2f}"

# ----------------- MAIN UI RENDER -----------------

def main():
    # Inject design custom CSS
    inject_custom_css()
    
    # Header Banner Area
    st.markdown('<h1 style="color: #4edea3; margin-bottom: 0.1rem;">📈 Emerald Analytics Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #bbcabf; font-size: 0.95rem; margin-bottom: 2rem;">Interactive Financial Data Visualization & Common Size Engine</p>', unsafe_allow_html=True)
    
    # ---------------- Sidebar Panel ----------------
    st.sidebar.markdown('<h2 style="color: #4edea3; font-size: 1.25rem;">Controls</h2>', unsafe_allow_html=True)
    
    # Excel Template File Uploader
    uploaded_file = st.sidebar.file_uploader(
        "Upload Financial Excel (.xlsx)",
        type=["xlsx"],
        help="Upload an Excel workbook containing financial statement data (Format A or Format B)"
    )
    
    # Load and Parse dataset
    if uploaded_file is not None:
        df, parse_error = clean_and_parse_excel(uploaded_file)
        if parse_error:
            st.sidebar.error(parse_error)
            st.sidebar.warning("Falling back to default sample dataset.")
            df = load_default_dataframe()
        else:
            st.sidebar.success("Excel uploaded & parsed successfully!")
    else:
        df = load_default_dataframe()
        st.sidebar.info("Using preloaded sample Income Statement data.")

    # Excel Download Template helper
    sample_excel = get_sample_excel_bytes()
    st.sidebar.download_button(
        label="📥 Download Excel Template",
        data=sample_excel,
        file_name="financial_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Download this template to format your own inputs correctly."
    )
    
    st.sidebar.markdown("<hr style='border-color: rgba(78, 222, 163, 0.15);'/>", unsafe_allow_html=True)
    
    # Toggle Selector for View Modes
    view_mode = st.sidebar.radio(
        "Select Visualization Mode",
        options=["Raw Values", "YoY Growth %", "Common Size %"],
        index=0,
        help="Toggle view between raw currency values, period-over-period growth rates, and normalized common-size metrics."
    )
    
    # Common Size denominator selector (only active when Common Size mode selected)
    common_size_base = None
    if view_mode == "Common Size %":
        common_size_base = st.sidebar.selectbox(
            "Select Base Metric (Denominator)",
            options=df.index,
            index=0,
            help="All financial lines for each period will be expressed as a percentage of this metric."
        )

    st.sidebar.markdown("<hr style='border-color: rgba(78, 222, 163, 0.15);'/>", unsafe_allow_html=True)
    
    # Dropdown for Graph Type Selector
    graph_type = st.sidebar.selectbox(
        "Select Graph Type",
        options=["Line", "Bar Charts (Grouped)", "Bar Charts (Stacked)", "Scatter", "Area"],
        index=0,
        help="Choose standard line/scatter or column layouts."
    )
    
    # Multi-select dropdown for Metrics filter
    selected_metrics = st.sidebar.multiselect(
        "Select Metrics to Display",
        options=list(df.index),
        default=list(df.index)[:3] if len(df.index) > 3 else list(df.index),
        help="Pick which lines/categories to project on the chart."
    )

    # ---------------- KPI Row (Main Content Area) ----------------
    # Compute base metrics to show on top KPI cards
    revenue_key = get_metric_by_name(df, ['revenue', 'sales'])
    net_income_key = get_metric_by_name(df, ['net income', 'net profit'])
    cogs_key = get_metric_by_name(df, ['cogs', 'cost of goods'])
    gross_profit_key = get_metric_by_name(df, ['gross profit'])

    latest_period = df.columns[-1]
    prev_period = df.columns[-2] if len(df.columns) > 1 else None
    
    kpi_cols = st.columns(3)
    
    # KPI 1: Revenue Card
    with kpi_cols[0]:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        if revenue_key:
            rev_latest = df.loc[revenue_key, latest_period]
            st.markdown(f'<div class="kpi-title">Revenue ({latest_period})</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{format_large_number(rev_latest)}</div>', unsafe_allow_html=True)
            
            if prev_period:
                rev_prev = df.loc[revenue_key, prev_period]
                rev_growth = ((rev_latest - rev_prev) / abs(rev_prev)) * 100 if rev_prev != 0 else 0
                arrow = "↑" if rev_growth >= 0 else "↓"
                cls = "up" if rev_growth >= 0 else "down"
                st.markdown(f'<div class="kpi-delta {cls}">{arrow} {abs(rev_growth):.1f}% YoY vs. {prev_period}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="kpi-delta neutral">Initial Period</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="kpi-title">Revenue</div>', unsafe_allow_html=True)
            st.markdown('<div class="kpi-value">$0.00</div>', unsafe_allow_html=True)
            st.markdown('<div class="kpi-delta neutral">Metric not detected</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # KPI 2: Gross Profit Card / Gross Margin
    with kpi_cols[1]:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-title">Gross Margin ({latest_period})</div>', unsafe_allow_html=True)
        
        # Calculate Gross Margin
        gm_latest = 0.0
        gm_prev = 0.0
        has_gm = False
        
        if revenue_key:
            rev_latest = df.loc[revenue_key, latest_period]
            if gross_profit_key:
                gp_latest = df.loc[gross_profit_key, latest_period]
                gm_latest = (gp_latest / rev_latest * 100) if rev_latest != 0 else 0
                has_gm = True
            elif cogs_key:
                cogs_latest = df.loc[cogs_key, latest_period]
                gm_latest = ((rev_latest - cogs_latest) / rev_latest * 100) if rev_latest != 0 else 0
                has_gm = True
                
            if prev_period and has_gm:
                rev_prev = df.loc[revenue_key, prev_period]
                if gross_profit_key:
                    gp_prev = df.loc[gross_profit_key, prev_period]
                    gm_prev = (gp_prev / rev_prev * 100) if rev_prev != 0 else 0
                elif cogs_key:
                    cogs_prev = df.loc[cogs_key, prev_period]
                    gm_prev = ((rev_prev - cogs_prev) / rev_prev * 100) if rev_prev != 0 else 0
        
        if has_gm:
            st.markdown(f'<div class="kpi-value">{gm_latest:.1f}%</div>', unsafe_allow_html=True)
            if prev_period:
                gm_diff = gm_latest - gm_prev
                arrow = "↑" if gm_diff >= 0 else "↓"
                cls = "up" if gm_diff >= 0 else "down"
                st.markdown(f'<div class="kpi-delta {cls}">{arrow} {abs(gm_diff):.1f} pp vs. {prev_period}</div>', unsafe_allow_html=True)
            else:
                 st.markdown('<div class="kpi-delta neutral">Initial Period</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="kpi-value">0.0%</div>', unsafe_allow_html=True)
            st.markdown('<div class="kpi-delta neutral">Metrics not detected</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # KPI 3: Net Income Card
    with kpi_cols[2]:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        if net_income_key:
            net_latest = df.loc[net_income_key, latest_period]
            st.markdown(f'<div class="kpi-title">Net Income ({latest_period})</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{format_large_number(net_latest)}</div>', unsafe_allow_html=True)
            
            if prev_period:
                net_prev = df.loc[net_income_key, prev_period]
                if net_prev != 0:
                    net_growth = ((net_latest - net_prev) / abs(net_prev)) * 100
                    arrow = "↑" if net_growth >= 0 else "↓"
                    cls = "up" if net_growth >= 0 else "down"
                    st.markdown(f'<div class="kpi-delta {cls}">{arrow} {abs(net_growth):.1f}% YoY vs. {prev_period}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="kpi-delta neutral">0.0% YoY</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="kpi-delta neutral">Initial Period</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="kpi-title">Net Income</div>', unsafe_allow_html=True)
            st.markdown('<div class="kpi-value">$0.00</div>', unsafe_allow_html=True)
            st.markdown('<div class="kpi-delta neutral">Metric not detected</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ---------------- Data Transformations ----------------
    # Apply selected transformation
    if view_mode == "YoY Growth %":
        transformed_df = calculate_growth_rates(df)
        y_label = "YoY Growth (%)"
    elif view_mode == "Common Size %":
        transformed_df = calculate_common_size(df, common_size_base)
        y_label = f"% of {common_size_base}"
    else:
        transformed_df = df.copy()
        y_label = "Currency Value ($)"

    # Filter by user-selected metrics
    if not selected_metrics:
        st.warning("Please select at least one metric in the sidebar to visualize.")
        filtered_df = pd.DataFrame(columns=df.columns)
    else:
        filtered_df = transformed_df.loc[selected_metrics]

    # ---------------- Chart Canvas ----------------
    st.markdown(f'<h3 style="margin-bottom: 1rem;">📊 {view_mode} Analysis Projection</h3>', unsafe_allow_html=True)
    
    # Create the Plotly chart
    if not filtered_df.empty:
        fig = create_plotly_chart(filtered_df, graph_type, y_label)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available to display on the chart.")

    # ---------------- Tabular Section ----------------
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown('<h3 style="margin-bottom: 1rem;">📋 Granular Data Ledger</h3>', unsafe_allow_html=True)
    
    # Formatting helper for dataframe display based on selected mode
    try:
        if view_mode == "Raw Values":
            # Show formatted dollars
            style_df = df.style.format(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)
        elif view_mode == "YoY Growth %":
            # Show YoY percentage changes
            growth_raw = calculate_growth_rates(df)
            style_df = growth_raw.style.format(lambda x: f"{x:+.2f}%" if isinstance(x, (int, float)) else x)
        elif view_mode == "Common Size %":
            # Show normalized common size percentage
            common_raw = calculate_common_size(df, common_size_base)
            style_df = common_raw.style.format(lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) else x)
        
        st.dataframe(style_df, use_container_width=True)
    except Exception as e:
        # Graceful fallback if styling fails
        st.dataframe(df, use_container_width=True)

    # Footer
    st.markdown('<div class="footer">Emerald Financial Visualizer &copy; 2026. Built with Streamlit, Pandas, and Plotly. Styled under the Emerald Fidelity Theme.</div>', unsafe_allow_html=True)

# ----------------- PLOTLY CONFIG -----------------

def create_plotly_chart(df_plot, chart_type, y_axis_label):
    fig = go.Figure()
    periods = list(df_plot.columns)
    
    # Color palette coordinating with Stitch's Emerald theme
    colors = ['#0fb981', '#38bdf8', '#fb7185', '#9ed2b5', '#fbbf24', '#a78bfa', '#6366f1', '#ec4899']
    
    for idx, metric in enumerate(df_plot.index):
        row_data = df_plot.loc[metric]
        if isinstance(row_data, pd.DataFrame):
            row_data = row_data.iloc[0]
        values = list(row_data)
        color = colors[idx % len(colors)]
        
        if chart_type == 'Line':
            fig.add_trace(go.Scatter(
                x=periods, y=values, name=metric,
                mode='lines+markers',
                line=dict(color=color, width=3),
                marker=dict(size=8, color=color, line=dict(color='#0e1511', width=1)),
                hovertemplate=f"<b>{metric}</b><br>Period: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>"
            ))
        elif chart_type in ['Bar Charts (Grouped)', 'Bar Charts (Stacked)']:
            fig.add_trace(go.Bar(
                x=periods, y=values, name=metric,
                marker_color=color,
                hovertemplate=f"<b>{metric}</b><br>Period: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>"
            ))
        elif chart_type == 'Scatter':
            fig.add_trace(go.Scatter(
                x=periods, y=values, name=metric,
                mode='markers',
                marker=dict(size=12, color=color, line=dict(color='#0e1511', width=1)),
                hovertemplate=f"<b>{metric}</b><br>Period: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>"
            ))
        elif chart_type == 'Area':
            fig.add_trace(go.Scatter(
                x=periods, y=values, name=metric,
                mode='lines',
                line=dict(color=color, width=2.5),
                fill='tozeroy',
                fillcolor=f"rgba({int(color[1:3], 16) if len(color) == 7 else 15},{int(color[3:5], 16) if len(color) == 7 else 185},{int(color[5:7], 16) if len(color) == 7 else 129}, 0.15)",
                hovertemplate=f"<b>{metric}</b><br>Period: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>"
            ))
            
    barmode = 'group'
    if chart_type == 'Bar Charts (Stacked)':
        barmode = 'stack'
        
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(26, 33, 29, 0.8)',
        plot_bgcolor='rgba(26, 33, 29, 0.8)',
        font=dict(family='Inter, sans-serif', color='#dde5dd'),
        xaxis=dict(
            title='Time Period',
            gridcolor='rgba(78, 222, 163, 0.08)',
            zeroline=False,
            tickmode='array',
            tickvals=periods,
            title_font=dict(size=12, color='#bbcabf')
        ),
        yaxis=dict(
            title=y_axis_label,
            gridcolor='rgba(78, 222, 163, 0.08)',
            zeroline=True,
            zerolinecolor='rgba(78, 222, 163, 0.15)',
            title_font=dict(size=12, color='#bbcabf')
        ),
        legend=dict(
            bgcolor='#161d19',
            bordercolor='rgba(78, 222, 163, 0.15)',
            borderwidth=1,
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        barmode=barmode,
        margin=dict(l=40, r=40, t=50, b=40),
        hovermode='x unified',
        plot_bgcolor_opacity=0 # sets backdrop transparent
    )
    return fig

if __name__ == '__main__':
    main()
