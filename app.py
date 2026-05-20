import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# Set Streamlit Page Config
st.set_page_config(
    page_title="Emerald Financial visualizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- DESIGN SYSTEM CONFIG (EMERALD FIDELITY) -----------------
def inject_custom_css():
    st.markdown("""
        <style>
        /* Google Fonts Import */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Public+Sans:wght@300;400;500;600&display=swap');
        
        /* Global Reset & Body Colors */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0e1511 !important;
            color: #dde5dd !important;
            font-family: 'Public Sans', sans-serif !important;
        }
        
        /* Headers Styling */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
        }
        
        /* Sidebar Styling Override */
        [data-testid="stSidebar"] {
            background-color: #0e1511 !important;
            border-right: 1px solid rgba(78, 222, 163, 0.15) !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #bbcabf !important;
        }
        
        /* Metric Multi-Select & Selector Overrides */
        div[data-baseweb="select"] {
            background-color: #1a211d !important;
            border: 1px solid rgba(78, 222, 163, 0.25) !important;
            border-radius: 8px !important;
        }
        div[data-baseweb="select"] * {
            color: #dde5dd !important;
            font-family: 'Public Sans', sans-serif !important;
        }
        
        /* File Uploader Custom Aesthetics */
        section[data-testid="stFileUploadDropzone"] {
            background-color: #161d19 !important;
            border: 1.5px dashed #0fb981 !important;
            border-radius: 8px !important;
            padding: 1.5rem !important;
            transition: all 0.3s ease;
        }
        section[data-testid="stFileUploadDropzone"]:hover {
            border-color: #4edea3 !important;
            background-color: #1a211d !important;
        }
        
        /* Buttons Override (Template Download) */
        div.stButton > button {
            background-color: #0fb981 !important;
            color: #0e1511 !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.5rem !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            width: 100% !important;
        }
        div.stButton > button:hover {
            background-color: #4edea3 !important;
            box-shadow: 0 0 12px rgba(78, 222, 163, 0.45) !important;
            transform: translateY(-1px) !important;
        }
        
        /* KPI Cards Styling */
        .kpi-card {
            background-color: #1a211d;
            border: 1px solid rgba(78, 222, 163, 0.15);
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            border-color: rgba(78, 222, 163, 0.35);
        }
        .kpi-title {
            font-size: 0.8rem;
            color: #bbcabf;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 500;
        }
        .kpi-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #4edea3;
            margin-top: 0.1rem;
        }
        .kpi-delta {
            font-size: 0.85rem;
            margin-top: 0.3rem;
            font-weight: 600;
        }
        .kpi-delta.up {
            color: #34d399;
        }
        .kpi-delta.down {
            color: #fb7185;
        }
        .kpi-delta.neutral {
            color: #bbcabf;
        }
        
        /* Dataframes & Tables styling */
        .styled-table-container {
            border: 1px solid rgba(78, 222, 163, 0.15);
            border-radius: 8px;
            overflow: hidden;
            margin: 1.5rem 0;
            background-color: #161d19;
        }
        
        /* Custom Footer Style */
        .footer {
            font-size: 0.8rem;
            color: #6a7c70;
            text-align: center;
            padding: 1.5rem 0;
            margin-top: 3rem;
            border-top: 1px solid rgba(78, 222, 163, 0.1);
        }
        
        /* Streamlit Tab Customizer */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #0e1511;
            padding: 5px;
            border-bottom: 2px solid rgba(78, 222, 163, 0.1);
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #161d19;
            border: 1px solid rgba(78, 222, 163, 0.1);
            border-radius: 6px 6px 0 0;
            color: #bbcabf;
            padding: 10px 20px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1a211d !important;
            color: #4edea3 !important;
            border-color: rgba(78, 222, 163, 0.3) rgba(78, 222, 163, 0.3) transparent rgba(78, 222, 163, 0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ----------------- STANDARD METRIC FUZZY MAPPING DICTIONARY -----------------
METRIC_MAPPING = {
    # Income Statement
    "Revenue": ["revenue", "sales", "total revenue", "total sales", "turnover", "operating revenue", "topline"],
    "COGS": ["cogs", "cost of goods sold", "cost of revenue", "cost of sales", "direct costs"],
    "Gross Profit": ["gross profit", "gross margin", "gross income"],
    "R&D": ["r&d", "research & development", "research and development"],
    "S&M": ["s&m", "sales & marketing", "sales and marketing", "selling expenses", "selling & marketing", "marketing"],
    "G&A": ["g&a", "general & administrative", "general and administrative", "g & a", "overhead"],
    "Operating Expenses": ["operating expenses", "total operating expenses", "opex", "indirect expenses"],
    "EBIT": ["ebit", "operating income", "operating profit", "earnings before interest and tax"],
    "Interest Expense": ["interest expense", "interest", "finance costs", "interest and finance expense"],
    "Tax Expense": ["income tax", "tax expense", "taxes", "income tax expense"],
    "Net Income": ["net income", "net profit", "net earnings", "net profit after tax", "bottomline"],
    
    # Balance Sheet
    "Cash": ["cash", "cash & cash equivalents", "cash and equivalents", "cash and cash equivalents", "cash equivalents"],
    "AR": ["accounts receivable", "receivables", "trade receivables", "a/r", "ar"],
    "Inventory": ["inventory", "inventories", "stock"],
    "Current Assets": ["current assets", "total current assets"],
    "PP&E": ["pp&e", "property, plant & equipment", "property, plant and equipment", "fixed assets", "net pp&e"],
    "Total Assets": ["total assets", "assets"],
    "AP": ["accounts payable", "payables", "trade payables", "a/p", "ap"],
    "Short-term Debt": ["short-term debt", "current debt", "short term debt", "current portion of long-term debt", "notes payable"],
    "Current Liabilities": ["current liabilities", "total current liabilities"],
    "Long-term Debt": ["long-term debt", "long term debt", "non-current debt", "long-term borrowing"],
    "Total Liabilities": ["total liabilities", "liabilities"],
    "Retained Earnings": ["retained earnings", "retained profit", "accumulated deficit"],
    "Shareholder Equity": ["shareholder equity", "total equity", "equity", "shareholders equity", "total shareholder equity"],
    "Total Liabilities & Equity": ["total liabilities & equity", "total liabilities and equity", "liabilities and equity", "liabilities & equity"],
    
    # Ratios
    "Current Ratio": ["current ratio", "current"],
    "Quick Ratio": ["quick ratio", "quick", "acid test"],
    "Gross Margin %": ["gross margin %", "gross profit margin", "gross margin percentage", "gross margin", "gp margin %"],
    "Operating Margin %": ["operating margin %", "operating margin", "operating profit margin", "ebit margin", "ebit margin %"],
    "Net Margin %": ["net margin %", "net margin", "net profit margin", "net profit margin %"],
    "Debt to Equity Ratio": ["debt to equity", "debt to equity ratio", "d/e", "d/e ratio", "leverage ratio"],
    "Return on Assets (ROA) %": ["roa", "return on assets", "roa %", "return on assets %", "return on assets percentage"],
    "Return on Equity (ROE) %": ["roe", "return on equity", "roe %", "return on equity %", "return on equity percentage"]
}

def get_mapped_metric(df, standard_name):
    """
    Fuzzy maps standard name to actual row/index label in df using METRIC_MAPPING aliases.
    Returns the mapped index name if found, else None.
    """
    if df is None or df.empty:
        return None
    aliases = METRIC_MAPPING.get(standard_name, [standard_name])
    # Exact/Fuzzy alias matching (case-insensitive)
    for alias in aliases:
        for idx in df.index:
            if alias.lower() == str(idx).lower() or alias.lower() in str(idx).lower():
                return idx
    # Fallback general lower-case check
    for idx in df.index:
        if standard_name.lower() in str(idx).lower():
            return idx
    return None

def get_metric_values(df, standard_name, default_val=0.0):
    """
    Retrieves the row values for a standard metric name.
    If not found, returns a Pandas Series of default_val matching df's columns.
    """
    mapped_name = get_mapped_metric(df, standard_name)
    if mapped_name is not None:
        return df.loc[mapped_name]
    else:
        return pd.Series(default_val, index=df.columns)

# ----------------- MULTI-SHEET DATA PROCESSING ENGINE -----------------

def parse_single_sheet(df_raw):
    """
    Cleans, transposes (if needed), and standardizes a single raw sheet.
    """
    try:
        # Drop completely empty rows and columns
        df_raw = df_raw.dropna(how='all').dropna(how='all', axis=1)
        df_raw = df_raw.reset_index(drop=True)
        df_raw.columns = range(df_raw.shape[1])
        
        if df_raw.empty:
            return None, "Sheet contains no data."

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

        # Determine layout structure: (Rows as Metrics vs Columns as Metrics)
        row0 = df_raw.iloc[0]
        col0 = df_raw.iloc[:, 0]
        
        row0_numeric_count = sum(1 for x in row0[1:] if is_numeric_value(x))
        col0_numeric_count = sum(1 for x in col0[1:] if is_numeric_value(x))
        
        row0_numeric_ratio = row0_numeric_count / max(1, len(row0) - 1)
        col0_numeric_ratio = col0_numeric_count / max(1, len(col0) - 1)
        
        is_transposed = col0_numeric_ratio > row0_numeric_ratio
        
        if is_transposed:
            # Format B: Rows as Periods, Columns as Metrics
            headers = list(df_raw.iloc[0])
            period_col_idx = 0
            for idx, h in enumerate(headers):
                if str(h).lower() in ['year', 'date', 'period', 'quarter', 'time']:
                    period_col_idx = idx
                    break
            df_raw.columns = headers
            df = df_raw.iloc[1:].copy()
            period_col_name = headers[period_col_idx]
            df = df.set_index(period_col_name)
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

        if hasattr(df, 'map'):
            df = df.map(clean_val)
        else:
            df = df.applymap(clean_val)

        df.index = [str(idx).strip() for idx in df.index]
        df = df[df.index != ""]
        df.columns = [str(col).strip() for col in df.columns]
        
        # Sort columns chronologically
        def get_sort_val(col):
            try:
                return float(col)
            except ValueError:
                return col
        try:
            sorted_cols = sorted(df.columns, key=get_sort_val)
            df = df[sorted_cols]
        except Exception:
            pass
            
        return df, None
    except Exception as e:
        return None, f"Parsing Error: {str(e)}"

def clean_and_parse_excel_multi(uploaded_file):
    """
    Reads all sheets from an Excel workbook, fuzzy-matches them to Income Statement,
    Balance Sheet, and Ratios, and cleans/standardizes each sheet individually.
    Returns a dict of DataFrames {statement_type: df} and any parsing warnings/errors.
    """
    try:
        excel_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=None)
        parsed_statements = {}
        errors = []
        
        def match_sheet_name(name, keywords):
            name_lower = str(name).lower()
            return any(k in name_lower for k in keywords)
            
        income_keywords = ['income', 'profit', 'p&l', 'p and l', 'operations', 'performance']
        balance_keywords = ['balance', 'bs', 'condition', 'position', 'assets', 'liability']
        ratio_keywords = ['ratio', 'metrics', 'kpi', 'indicator']
        
        for sheet_name, df_raw in excel_sheets.items():
            df_parsed, err = parse_single_sheet(df_raw)
            if err:
                errors.append(f"Sheet '{sheet_name}' parsing failed: {err}")
                continue
                
            if match_sheet_name(sheet_name, income_keywords):
                parsed_statements["Income Statement"] = df_parsed
            elif match_sheet_name(sheet_name, balance_keywords):
                parsed_statements["Balance Sheet"] = df_parsed
            elif match_sheet_name(sheet_name, ratio_keywords):
                parsed_statements["Financial Ratios"] = df_parsed
        
        # Fallback by position if no fuzzy name matches worked but sheets exist
        if not parsed_statements and len(excel_sheets) > 0:
            sheet_names = list(excel_sheets.keys())
            if len(sheet_names) >= 1:
                df_parsed, _ = parse_single_sheet(excel_sheets[sheet_names[0]])
                if df_parsed is not None:
                    parsed_statements["Income Statement"] = df_parsed
            if len(sheet_names) >= 2:
                df_parsed, _ = parse_single_sheet(excel_sheets[sheet_names[1]])
                if df_parsed is not None:
                    parsed_statements["Balance Sheet"] = df_parsed
            if len(sheet_names) >= 3:
                df_parsed, _ = parse_single_sheet(excel_sheets[sheet_names[2]])
                if df_parsed is not None:
                    parsed_statements["Financial Ratios"] = df_parsed

        if not parsed_statements:
            return None, "Could not identify any valid financial statements or ratios in the uploaded workbook. Please check the sheet structures."
            
        warnings = "; ".join(errors) if errors else None
        return parsed_statements, warnings
    except Exception as e:
        return None, f"Failed to read Excel workbook: {str(e)}"

# ----------------- FINANCIAL CALCULATION ENGINES -----------------

def calculate_growth_rates(df):
    """
    Calculates year-over-year (YoY) growth percentages for each metric using vectorized math.
    """
    growth_df = pd.DataFrame(index=df.index, columns=df.columns)
    growth_df.iloc[:, 0] = 0.0
    for i in range(1, len(df.columns)):
        prev_col = df.columns[i - 1]
        curr_col = df.columns[i]
        
        p = df[prev_col]
        c = df[curr_col]
        
        growth = np.where(
            p == 0,
            np.where(c > 0, 100.0, np.where(c < 0, -100.0, 0.0)),
            ((c - p) / np.abs(p)) * 100.0
        )
        growth_df[curr_col] = growth
    return growth_df

def calculate_common_size(df, base_metric):
    """
    Normalizes all financial metrics as a percentage of a baseline metric (e.g. Revenue)
    using vectorized pandas division.
    """
    if base_metric not in df.index:
        return df
    
    base_row = df.loc[base_metric]
    if isinstance(base_row, pd.DataFrame):
        base_row = base_row.iloc[0]
        
    common_size_df = df.div(base_row, axis=1) * 100.0
    common_size_df = common_size_df.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    
    return common_size_df

# ----------------- PLOTLY VISUALIZATION COMPONENT BUILDERS -----------------

def create_waterfall_chart(df_income, period):
    """
    Creates a P&L Waterfall chart from Revenue to Net Income for a given year.
    """
    rev = get_metric_values(df_income, "Revenue").loc[period]
    cogs = get_metric_values(df_income, "COGS").loc[period]
    gross = get_metric_values(df_income, "Gross Profit").loc[period]
    opex = get_metric_values(df_income, "Operating Expenses").loc[period]
    ebit = get_metric_values(df_income, "EBIT").loc[period]
    interest = get_metric_values(df_income, "Interest Expense").loc[period]
    tax = get_metric_values(df_income, "Tax Expense").loc[period]
    net = get_metric_values(df_income, "Net Income").loc[period]
    
    x_labels = [
        "Revenue", "COGS", "Gross Profit", 
        "Operating Expenses", "Operating Income (EBIT)", 
        "Interest", "Tax", "Net Income"
    ]
    
    y_values = [
        rev, 
        -abs(cogs), 
        gross, 
        -abs(opex), 
        ebit, 
        -abs(interest), 
        -abs(tax), 
        net
    ]
    
    measures = [
        "relative", "relative", "total", 
        "relative", "total", 
        "relative", "relative", "total"
    ]
    
    fig = go.Figure(go.Waterfall(
        name="P&L Flow",
        orientation="v",
        measure=measures,
        x=x_labels,
        y=y_values,
        textposition="outside",
        text=[f"${v/1000:.1f}K" if abs(v) >= 1000 else f"${v:.1f}" for v in y_values],
        connector=dict(line=dict(color="rgba(78, 222, 163, 0.3)", width=1.5)),
        decreasing=dict(marker=dict(color="#fb7185")),
        increasing=dict(marker=dict(color="#34d399")),
        totals=dict(marker=dict(color="#60a5fa"))
    ))
    
    fig.update_layout(
        title=dict(text=f"P&L Waterfall Flow ({period})", font=dict(size=14, color='#dde5dd')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#dde5dd'),
        xaxis=dict(gridcolor='rgba(78, 222, 163, 0.08)'),
        yaxis=dict(gridcolor='rgba(78, 222, 163, 0.08)', title="USD ($)"),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

def create_ratio_gauge(label, value, min_val, max_val, color_theme="green_high"):
    """
    Creates a Plotly Gauge chart for ratio KPIs.
    """
    if color_theme == "green_high":
        steps = [
            {'range': [min_val, min_val + 0.3 * (max_val - min_val)], 'color': 'rgba(239, 68, 68, 0.15)'},
            {'range': [min_val + 0.3 * (max_val - min_val), min_val + 0.6 * (max_val - min_val)], 'color': 'rgba(251, 191, 36, 0.15)'},
            {'range': [min_val + 0.6 * (max_val - min_val), max_val], 'color': 'rgba(16, 185, 129, 0.2)'}
        ]
        bar_color = "#0fb981"
    else:
        steps = [
            {'range': [min_val, min_val + 0.3 * (max_val - min_val)], 'color': 'rgba(16, 185, 129, 0.2)'},
            {'range': [min_val + 0.3 * (max_val - min_val), min_val + 0.6 * (max_val - min_val)], 'color': 'rgba(251, 191, 36, 0.15)'},
            {'range': [min_val + 0.6 * (max_val - min_val), max_val], 'color': 'rgba(239, 68, 68, 0.15)'}
        ]
        bar_color = "#38bdf8"
        
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': label, 'font': {'size': 14, 'color': '#dde5dd'}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': '#bbcabf'},
            'bar': {'color': bar_color},
            'bgcolor': '#161d19',
            'borderwidth': 1.5,
            'bordercolor': 'rgba(78, 222, 163, 0.15)',
            'steps': steps,
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#dde5dd'),
        margin=dict(l=25, r=25, t=45, b=25),
        height=190
    )
    return fig

def create_expense_pie_chart(df, period):
    """
    Sum opex categories and plot breakdown.
    """
    rd = get_metric_values(df, "R&D").loc[period]
    sm = get_metric_values(df, "S&M").loc[period]
    ga = get_metric_values(df, "G&A").loc[period]
    
    total_opex = get_metric_values(df, "Operating Expenses").loc[period]
    captured = rd + sm + ga
    other = max(0.0, total_opex - captured)
    
    labels = ["Research & Development (R&D)", "Sales & Marketing (S&M)", "General & Administrative (G&A)"]
    values = [rd, sm, ga]
    if other > 0:
        labels.append("Other Operating Expenses")
        values.append(other)
        
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=['#0fb981', '#38bdf8', '#a78bfa', '#fb7185']),
        hoverinfo='label+percent+value',
        textinfo='percent'
    )])
    fig.update_layout(
        title=dict(text=f"Operating Expenses Breakdown ({period})", font=dict(size=14, color='#dde5dd')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#dde5dd'),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation='h', y=-0.1)
    )
    return fig

def create_assets_chart(df):
    """
    Stacked bar of Cash, AR, Inventory and Net PP&E.
    """
    periods = list(df.columns)
    cash = list(get_metric_values(df, "Cash"))
    ar = list(get_metric_values(df, "AR"))
    inv = list(get_metric_values(df, "Inventory"))
    ppe = list(get_metric_values(df, "PP&E"))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=periods, y=cash, name="Cash", marker_color='#0fb981'))
    fig.add_trace(go.Bar(x=periods, y=ar, name="Accounts Receivable", marker_color='#34d399'))
    fig.add_trace(go.Bar(x=periods, y=inv, name="Inventory", marker_color='#a7f3d0'))
    fig.add_trace(go.Bar(x=periods, y=ppe, name="Property, Plant & Equipment", marker_color='#38bdf8'))
    
    fig.update_layout(
        title=dict(text="Assets Composition Trend", font=dict(size=14, color='#dde5dd')),
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#dde5dd'),
        xaxis=dict(gridcolor='rgba(78, 222, 163, 0.08)'),
        yaxis=dict(gridcolor='rgba(78, 222, 163, 0.08)', title="USD ($)"),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

def create_liabilities_equity_chart(df):
    """
    Stacked bar of AP, Debt and Equity.
    """
    periods = list(df.columns)
    ap = list(get_metric_values(df, "AP"))
    st_debt = list(get_metric_values(df, "Short-term Debt"))
    lt_debt = list(get_metric_values(df, "Long-term Debt"))
    equity = list(get_metric_values(df, "Shareholder Equity"))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=periods, y=ap, name="Accounts Payable", marker_color='#fb7185'))
    fig.add_trace(go.Bar(x=periods, y=st_debt, name="Short-term Debt", marker_color='#f87171'))
    fig.add_trace(go.Bar(x=periods, y=lt_debt, name="Long-term Debt", marker_color='#ef4444'))
    fig.add_trace(go.Bar(x=periods, y=equity, name="Shareholder Equity", marker_color='#38bdf8'))
    
    fig.update_layout(
        title=dict(text="Liabilities & Equity Composition Trend", font=dict(size=14, color='#dde5dd')),
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#dde5dd'),
        xaxis=dict(gridcolor='rgba(78, 222, 163, 0.08)'),
        yaxis=dict(gridcolor='rgba(78, 222, 163, 0.08)', title="USD ($)"),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

def create_custom_chart(df_plot, chart_type, y_axis_label):
    """
    Dynamic Chart Builder for user-selected metric lists.
    """
    fig = go.Figure()
    periods = list(df_plot.columns)
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
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
        hovermode='x unified'
    )
    return fig

# ----------------- SAMPLE DATA GENERATION & SEEDING -----------------

def get_sample_excel_bytes():
    """
    Generates a sample professional multi-sheet Excel file containing:
    1. Income Statement
    2. Balance Sheet
    3. Financial Ratios
    """
    output = io.BytesIO()
    
    income_data = {
        "Financial Metric": [
            "Revenue", 
            "Cost of Goods Sold (COGS)", 
            "Gross Profit", 
            "Research & Development (R&D)", 
            "Sales & Marketing (S&M)", 
            "General & Administrative (G&A)",
            "Operating Expenses",
            "Operating Income (EBIT)",
            "Interest Expense",
            "Tax Expense",
            "Net Income"
        ],
        "2020": [1000000, 300000, 700000, 150000, 250000, 100000, 500000, 200000, 10000, 30000, 160000],
        "2021": [1500000, 420000, 1080000, 220000, 350000, 130000, 700000, 380000, 15000, 61000, 304000],
        "2022": [2200000, 580000, 1620000, 310000, 500000, 170000, 980000, 640000, 20000, 108000, 512000],
        "2023": [3100000, 780000, 2320000, 410000, 680000, 220000, 1310000, 1010000, 25000, 177000, 808000],
        "2024": [4200000, 1000000, 3200000, 500000, 850000, 280000, 1630000, 1570000, 30000, 284000, 1256000],
        "2025": [5500000, 1250000, 4250000, 600000, 1100000, 340000, 2040000, 2210000, 35000, 407000, 1768000]
    }
    
    balance_data = {
        "Financial Metric": [
            "Cash & Cash Equivalents",
            "Accounts Receivable",
            "Inventory",
            "Total Current Assets",
            "Property, Plant & Equipment (PP&E)",
            "Total Assets",
            "Accounts Payable",
            "Short-term Debt",
            "Total Current Liabilities",
            "Long-term Debt",
            "Total Liabilities",
            "Retained Earnings",
            "Total Shareholder Equity",
            "Total Liabilities & Equity"
        ],
        "2020": [300000, 150000, 100000, 550000, 500000, 1050000, 80000, 50000, 130000, 400000, 530000, 200000, 520000, 1050000],
        "2021": [450000, 200000, 130000, 780000, 650000, 1430000, 110000, 40000, 150000, 350000, 500000, 450000, 930000, 1430000],
        "2022": [600000, 280000, 180000, 1060000, 800000, 1860000, 150000, 30000, 180000, 300000, 480000, 800000, 1380000, 1860000],
        "2023": [850000, 380000, 240000, 1470000, 1000000, 2470000, 200000, 20000, 220000, 250000, 470000, 1300000, 2000000, 2470000],
        "2024": [1200000, 480000, 310000, 1990000, 1200000, 3190000, 260000, 10000, 270000, 200000, 470000, 2000000, 2720000, 3190000],
        "2025": [1600000, 600000, 390000, 2590000, 1500000, 4090000, 320000, 0, 320000, 150000, 470000, 2900000, 3620000, 4090000]
    }
    
    ratios_data = {
        "Financial Metric": [
            "Current Ratio",
            "Quick Ratio",
            "Gross Margin %",
            "Operating Margin %",
            "Net Margin %",
            "Debt to Equity Ratio",
            "Return on Assets (ROA) %",
            "Return on Equity (ROE) %"
        ],
        "2020": [4.23, 3.46, 70.0, 20.0, 16.0, 0.87, 15.2, 30.8],
        "2021": [5.20, 4.33, 72.0, 25.3, 20.3, 0.42, 21.3, 32.7],
        "2022": [5.89, 4.89, 73.6, 29.1, 23.3, 0.24, 27.5, 37.1],
        "2023": [6.68, 5.59, 74.8, 32.6, 26.1, 0.14, 32.7, 40.4],
        "2024": [7.37, 6.22, 76.2, 37.4, 29.9, 0.08, 39.4, 46.2],
        "2025": [8.09, 6.88, 77.3, 40.2, 32.1, 0.04, 43.2, 48.8]
    }
    
    df_income = pd.DataFrame(income_data)
    df_balance = pd.DataFrame(balance_data)
    df_ratios = pd.DataFrame(ratios_data)
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_income.to_excel(writer, index=False, sheet_name='Income Statement')
        df_balance.to_excel(writer, index=False, sheet_name='Balance Sheet')
        df_ratios.to_excel(writer, index=False, sheet_name='Financial Ratios')
        
    return output.getvalue()

def load_default_statements():
    """
    Initializes default financial statement dict for initial load.
    """
    income_data = {
        "Revenue": [1000000, 1500000, 2200000, 3100000, 4200000, 5500000],
        "Cost of Goods Sold (COGS)": [300000, 420000, 580000, 780000, 1000000, 1250000],
        "Gross Profit": [700000, 1080000, 1620000, 2320000, 3200000, 4250000],
        "Research & Development (R&D)": [150000, 220000, 310000, 410000, 500000, 600000],
        "Sales & Marketing (S&M)": [250000, 350000, 500000, 680000, 850000, 1100000],
        "General & Administrative (G&A)": [100000, 130000, 170000, 220000, 280000, 340000],
        "Operating Expenses": [500000, 700000, 980000, 1310000, 1630000, 2040000],
        "Operating Income (EBIT)": [200000, 380000, 640000, 1010000, 1570000, 2210000],
        "Interest Expense": [10000, 15000, 20000, 25000, 30000, 35000],
        "Tax Expense": [30000, 61000, 108000, 177000, 284000, 407000],
        "Net Income": [160000, 304000, 512000, 808000, 1256000, 1768000]
    }
    df_income = pd.DataFrame(income_data, index=["2020", "2021", "2022", "2023", "2024", "2025"]).T
    
    balance_data = {
        "Cash & Cash Equivalents": [300000, 450000, 600000, 850000, 1200000, 1600000],
        "Accounts Receivable": [150000, 200000, 280000, 380000, 480000, 600000],
        "Inventory": [100000, 130000, 180000, 240000, 310000, 390000],
        "Total Current Assets": [550000, 780000, 1060000, 1470000, 1990000, 2590000],
        "Property, Plant & Equipment (PP&E)": [500000, 650000, 800000, 1000000, 1200000, 1500000],
        "Total Assets": [1050000, 1430000, 1860000, 2470000, 3190000, 4090000],
        "Accounts Payable": [80000, 110000, 150000, 200000, 260000, 320000],
        "Short-term Debt": [50000, 40000, 30000, 20000, 10000, 0],
        "Total Current Liabilities": [130000, 150000, 180000, 220000, 270000, 320000],
        "Long-term Debt": [400000, 350000, 300000, 250000, 200000, 150000],
        "Total Liabilities": [530000, 500000, 480000, 470000, 470000, 470000],
        "Retained Earnings": [200000, 450000, 800000, 1300000, 2000000, 2900000],
        "Total Shareholder Equity": [520000, 930000, 1380000, 2000000, 2720000, 3620000],
        "Total Liabilities & Equity": [1050000, 1430000, 1860000, 2470000, 3190000, 4090000]
    }
    df_balance = pd.DataFrame(balance_data, index=["2020", "2021", "2022", "2023", "2024", "2025"]).T
    
    ratios_data = {
        "Current Ratio": [4.23, 5.20, 5.89, 6.68, 7.37, 8.09],
        "Quick Ratio": [3.46, 4.33, 4.89, 5.59, 6.22, 6.88],
        "Gross Margin %": [70.0, 72.0, 73.6, 74.8, 76.2, 77.3],
        "Operating Margin %": [20.0, 25.3, 29.1, 32.6, 37.4, 40.2],
        "Net Margin %": [16.0, 20.3, 23.3, 26.1, 29.9, 32.1],
        "Debt to Equity Ratio": [0.87, 0.42, 0.24, 0.14, 0.08, 0.04],
        "Return on Assets (ROA) %": [15.2, 21.3, 27.5, 32.7, 39.4, 43.2],
        "Return on Equity (ROE) %": [30.8, 32.7, 37.1, 40.4, 46.2, 48.8]
    }
    df_ratios = pd.DataFrame(ratios_data, index=["2020", "2021", "2022", "2023", "2024", "2025"]).T
    
    return {
        "Income Statement": df_income,
        "Balance Sheet": df_balance,
        "Financial Ratios": df_ratios
    }

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

# ----------------- MAIN STREAMLIT UI RENDER -----------------

def main():
    inject_custom_css()
    
    # Header Banner Area
    st.markdown('<h1 style="color: #4edea3; margin-bottom: 0.1rem;">📈 Emerald Analytics Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #bbcabf; font-size: 0.95rem; margin-bottom: 2rem;">Multi-Statement Financial Analysis & Interactive Visualization Dashboard</p>', unsafe_allow_html=True)
    
    # ---------------- Sidebar Panel ----------------
    st.sidebar.markdown('<h2 style="color: #4edea3; font-size: 1.25rem;">Upload & Settings</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload Financial Excel (.xlsx)",
        type=["xlsx"],
        help="Upload an Excel workbook containing Income Statement, Balance Sheet, and Ratios sheets."
    )
    
    statements = {}
    if uploaded_file is not None:
        statements, parse_error = clean_and_parse_excel_multi(uploaded_file)
        if parse_error:
            st.sidebar.warning(f"Warnings during parsing: {parse_error}")
        if not statements:
            st.sidebar.error("Failed to parse statements. Loading sample template dataset.")
            statements = load_default_statements()
        else:
            st.sidebar.success("Excel workbook successfully loaded!")
    else:
        statements = load_default_statements()
        
    st.sidebar.markdown("<hr style='border-color: rgba(78, 222, 163, 0.15);'/>", unsafe_allow_html=True)
    st.sidebar.markdown('<h3 style="color: #dde5dd; font-size: 1rem;">Template Toolbox</h3>', unsafe_allow_html=True)
    
    sample_bytes = get_sample_excel_bytes()
    st.sidebar.download_button(
        label="📥 Download Excel Template",
        data=sample_bytes,
        file_name="Emerald_Financial_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Download the recommended multi-sheet layout template to populate with your own numbers."
    )
    
    # Ensure missing statements are initialized to empty templates to prevent app crashes
    for stkey in ["Income Statement", "Balance Sheet", "Financial Ratios"]:
        if stkey not in statements:
            statements[stkey] = pd.DataFrame()

    df_income = statements.get("Income Statement")
    df_balance = statements.get("Balance Sheet")
    df_ratios = statements.get("Financial Ratios")
    
    # Determine columns/years intersection across statements for global synchronization
    years = []
    if not df_income.empty:
        years = list(df_income.columns)
    elif not df_balance.empty:
        years = list(df_balance.columns)
    elif not df_ratios.empty:
        years = list(df_ratios.columns)
        
    # Main Tabs Interface
    tabs = st.tabs(["Overview Dashboard", "Income Statement", "Balance Sheet", "Financial Ratios"])
    
    # ------------------ TAB 1: OVERVIEW DASHBOARD ------------------
    with tabs[0]:
        st.markdown('<h3 style="color: #4edea3; margin-top: 1rem;">Executive Summary</h3>', unsafe_allow_html=True)
        
        if years:
            latest_year = years[-1]
            prev_year = years[-2] if len(years) > 1 else None
            
            # Fetch latest year values
            rev_series = get_metric_values(df_income, "Revenue")
            net_series = get_metric_values(df_income, "Net Income")
            cr_series = get_metric_values(df_ratios, "Current Ratio")
            
            latest_rev = rev_series.loc[latest_year]
            latest_net = net_series.loc[latest_year]
            latest_cr = cr_series.loc[latest_year]
            
            # Deltas calculation
            rev_delta_str = "No historical baseline"
            rev_class = "neutral"
            if prev_year and rev_series.loc[prev_year] != 0:
                rev_pct = ((latest_rev - rev_series.loc[prev_year]) / abs(rev_series.loc[prev_year])) * 100.0
                rev_delta_str = f"{'+' if rev_pct >= 0 else ''}{rev_pct:.1f}% YoY"
                rev_class = "up" if rev_pct >= 0 else "down"
                
            net_delta_str = "No historical baseline"
            net_class = "neutral"
            if prev_year and net_series.loc[prev_year] != 0:
                net_pct = ((latest_net - net_series.loc[prev_year]) / abs(net_series.loc[prev_year])) * 100.0
                net_delta_str = f"{'+' if net_pct >= 0 else ''}{net_pct:.1f}% YoY"
                net_class = "up" if net_pct >= 0 else "down"
                
            cr_delta_str = "No historical baseline"
            cr_class = "neutral"
            if prev_year:
                cr_diff = latest_cr - cr_series.loc[prev_year]
                cr_delta_str = f"{'+' if cr_diff >= 0 else ''}{cr_diff:.2f} delta"
                cr_class = "up" if cr_diff >= 0 else "down"

            # KPI Grid Row
            kpi_cols = st.columns(3)
            with kpi_cols[0]:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">Total Revenue ({latest_year})</div>
                        <div class="kpi-value">{format_large_number(latest_rev)}</div>
                        <div class="kpi-delta {rev_class}">{rev_delta_str}</div>
                    </div>
                """, unsafe_allow_html=True)
            with kpi_cols[1]:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">Net Income ({latest_year})</div>
                        <div class="kpi-value">{format_large_number(latest_net)}</div>
                        <div class="kpi-delta {net_class}">{net_delta_str}</div>
                    </div>
                """, unsafe_allow_html=True)
            with kpi_cols[2]:
                st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">Current Ratio ({latest_year})</div>
                        <div class="kpi-value">{latest_cr:.2f}x</div>
                        <div class="kpi-delta {cr_class}">{cr_delta_str}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Trends and Gauges Row
            st.markdown("<br/>", unsafe_allow_html=True)
            row1_cols = st.columns([3, 2])
            with row1_cols[0]:
                # Toplines Trend chart
                df_overview = pd.DataFrame(index=["Revenue", "Gross Profit", "Net Income"], columns=years)
                df_overview.loc["Revenue"] = get_metric_values(df_income, "Revenue")
                df_overview.loc["Gross Profit"] = get_metric_values(df_income, "Gross Profit")
                df_overview.loc["Net Income"] = get_metric_values(df_income, "Net Income")
                
                fig_trend = create_custom_chart(df_overview, "Line", "USD ($)")
                fig_trend.update_layout(title="Corporate Performance Trendline", height=420)
                st.plotly_chart(fig_trend, use_container_width=True)
            with row1_cols[1]:
                # Liquidity & Margin Gauges
                st.markdown('<div style="text-align: center; font-weight: 600; margin-bottom: 0.5rem; color: #bbcabf;">Liquidity & Profitability Gauges</div>', unsafe_allow_html=True)
                
                # Fetch margins
                net_margin = get_metric_values(df_ratios, "Net Margin %").loc[latest_year]
                
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    fig_g1 = create_ratio_gauge("Current Ratio", latest_cr, 0.0, 10.0, "green_high")
                    st.plotly_chart(fig_g1, use_container_width=True)
                with col_g2:
                    fig_g2 = create_ratio_gauge("Net Margin %", net_margin, 0.0, 100.0, "green_high")
                    st.plotly_chart(fig_g2, use_container_width=True)
                    
            # Quick summary comment card
            st.markdown(f"""
                <div class="kpi-card" style="margin-top: 1.5rem;">
                    <div style="font-weight: 700; color: #4edea3; margin-bottom: 0.3rem;">📋 Performance Insight ({latest_year})</div>
                    <span style="font-size: 0.9rem; color: #dde5dd;">
                        During the period of {latest_year}, the company generated total sales of <b>{format_large_number(latest_rev)}</b> resulting in a net profit of <b>{format_large_number(latest_net)}</b>. 
                        The organization maintains a healthy liquidity margin with a current ratio of <b>{latest_cr:.2f}x</b>. Check individual sheets to see deep-dives on YoY growth, operating expenses, and asset/liability ratios.
                    </span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No timeline data found. Please check your Excel template format.")

    # ------------------ TAB 2: INCOME STATEMENT ------------------
    with tabs[1]:
        st.markdown('<h3 style="color: #4edea3; margin-top: 1rem;">Income Statement Analyzer</h3>', unsafe_allow_html=True)
        
        if not df_income.empty:
            is_view_mode = st.radio(
                "Metric Valuation Mode",
                options=["Raw Values", "YoY Growth %", "Common Size %"],
                horizontal=True,
                key="is_view_mode"
            )
            
            # Common Size normalization controls
            common_size_base = None
            if is_view_mode == "Common Size %":
                common_size_base = st.selectbox(
                    "Select Common Size Base Metric",
                    options=list(df_income.index),
                    index=0,
                    help="All financial lines for each period will be expressed as a percentage of this metric."
                )
            
            # Calculate values based on mode
            if is_view_mode == "YoY Growth %":
                transformed_df = calculate_growth_rates(df_income)
                y_label = "Growth Rate (%)"
                fmt_string = "{:.2f}%"
            elif is_view_mode == "Common Size %" and common_size_base:
                transformed_df = calculate_common_size(df_income, common_size_base)
                y_label = f"% of {common_size_base}"
                fmt_string = "{:.2f}%"
            else:
                transformed_df = df_income.copy()
                y_label = "USD ($)"
                fmt_string = "${:,.2f}"

            # Sidebar metrics filter (displayed in columns to save space)
            filt_col1, filt_col2 = st.columns([1, 4])
            with filt_col1:
                st.markdown("<br/>", unsafe_allow_html=True)
                default_picks = [get_mapped_metric(df_income, "Revenue"), get_mapped_metric(df_income, "Gross Profit"), get_mapped_metric(df_income, "Net Income")]
                default_picks = [p for p in default_picks if p is not None]
                if not default_picks:
                    default_picks = list(df_income.index)[:3]
                    
                selected_is_metrics = st.multiselect(
                    "Metrics to Plot",
                    options=list(df_income.index),
                    default=default_picks,
                    key="selected_is_metrics"
                )
                
                chart_type = st.selectbox(
                    "Income Chart Type",
                    options=["Line", "Bar Charts (Grouped)", "Bar Charts (Stacked)", "Scatter", "Area"],
                    key="is_chart_type"
                )
            
            with filt_col2:
                if selected_is_metrics:
                    df_plot = transformed_df.loc[selected_is_metrics]
                    fig_is = create_custom_chart(df_plot, chart_type, y_label)
                    fig_is.update_layout(height=380)
                    st.plotly_chart(fig_is, use_container_width=True)
                else:
                    st.warning("Please select at least one metric to visualize.")

            # Grid Display of values
            st.markdown("<h4 style='color: #bbcabf;'>Granular Statement Data</h4>", unsafe_allow_html=True)
            formatted_df = transformed_df.map(lambda x: fmt_string.format(x) if isinstance(x, (int, float)) else str(x))
            st.dataframe(formatted_df, use_container_width=True)
            
            # Bottom Visualizations Section
            st.markdown("<hr style='border-color: rgba(78, 222, 163, 0.15);'/>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #4edea3;'>Advanced Income Visualizations</h4>", unsafe_allow_html=True)
            
            viz_year = st.selectbox("Select Target Year for Advanced Viz", options=years, index=len(years)-1)
            
            viz_cols = st.columns(2)
            with viz_cols[0]:
                fig_waterfall = create_waterfall_chart(df_income, viz_year)
                st.plotly_chart(fig_waterfall, use_container_width=True)
            with viz_cols[1]:
                fig_expense = create_expense_pie_chart(df_income, viz_year)
                st.plotly_chart(fig_expense, use_container_width=True)
        else:
            st.info("Please upload an Income Statement sheet to start analysis.")

    # ------------------ TAB 3: BALANCE SHEET ------------------
    with tabs[2]:
        st.markdown('<h3 style="color: #4edea3; margin-top: 1rem;">Balance Sheet Composition</h3>', unsafe_allow_html=True)
        
        if not df_balance.empty:
            st.markdown("<h4 style='color: #bbcabf;'>Assets & Liabilities Trendlines</h4>", unsafe_allow_html=True)
            
            bs_cols = st.columns(2)
            with bs_cols[0]:
                fig_assets = create_assets_chart(df_balance)
                st.plotly_chart(fig_assets, use_container_width=True)
            with bs_cols[1]:
                fig_liab = create_liabilities_equity_chart(df_balance)
                st.plotly_chart(fig_liab, use_container_width=True)
                
            # Cash vs Debt comparison
            st.markdown("<hr style='border-color: rgba(78, 222, 163, 0.15);'/>", unsafe_allow_html=True)
            cash_vals = get_metric_values(df_balance, "Cash")
            st_debt = get_metric_values(df_balance, "Short-term Debt")
            lt_debt = get_metric_values(df_balance, "Long-term Debt")
            total_debt = st_debt + lt_debt
            
            df_cash_debt = pd.DataFrame(index=["Cash & Equivalents", "Total Borrowings/Debt"], columns=years)
            df_cash_debt.loc["Cash & Equivalents"] = cash_vals
            df_cash_debt.loc["Total Borrowings/Debt"] = total_debt
            
            cash_debt_cols = st.columns([3, 2])
            with cash_debt_cols[0]:
                fig_cd = create_custom_chart(df_cash_debt, "Bar Charts (Grouped)", "USD ($)")
                fig_cd.update_layout(title="Liquidity Reserves vs. Outstanding Debt Liabilities", height=350)
                st.plotly_chart(fig_cd, use_container_width=True)
            with cash_debt_cols[1]:
                st.markdown("<br/>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="kpi-card" style="margin-top: 1rem;">
                        <div style="font-weight: 700; color: #38bdf8; margin-bottom: 0.5rem;">⚖️ Capital Structure Notes</div>
                        <span style="font-size: 0.9rem; color: #dde5dd;">
                            Monitoring the cash reserves against short and long-term liabilities is crucial for solvency analysis. 
                            The business currently holds <b>{format_large_number(cash_vals.iloc[-1])}</b> in cash compared to a total debt burden of <b>{format_large_number(total_debt.iloc[-1])}</b>.
                        </span>
                    </div>
                """, unsafe_allow_html=True)

            # Display raw Balance Sheet values
            st.markdown("<h4 style='color: #bbcabf;'>Balance Sheet Grid</h4>", unsafe_allow_html=True)
            formatted_bs = df_balance.map(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else str(x))
            st.dataframe(formatted_bs, use_container_width=True)
        else:
            st.info("Please upload a Balance Sheet sheet to start analysis.")

    # ------------------ TAB 4: FINANCIAL RATIOS ------------------
    with tabs[3]:
        st.markdown('<h3 style="color: #4edea3; margin-top: 1rem;">Financial Health & Margin Ratios</h3>', unsafe_allow_html=True)
        
        if not df_ratios.empty:
            # Profitability Margins Trend Chart
            df_margins = pd.DataFrame(index=["Gross Margin %", "Operating Margin %", "Net Margin %"], columns=years)
            df_margins.loc["Gross Margin %"] = get_metric_values(df_ratios, "Gross Margin %")
            df_margins.loc["Operating Margin %"] = get_metric_values(df_ratios, "Operating Margin %")
            df_margins.loc["Net Margin %"] = get_metric_values(df_ratios, "Net Margin %")
            
            margin_cols = st.columns([3, 2])
            with margin_cols[0]:
                fig_margins = create_custom_chart(df_margins, "Line", "Percentage (%)")
                fig_margins.update_layout(title="Margin Expansion Trends over Time", height=350)
                st.plotly_chart(fig_margins, use_container_width=True)
            with margin_cols[1]:
                # Leverage Trend
                df_lev = pd.DataFrame(index=["Debt to Equity Ratio"], columns=years)
                df_lev.loc["Debt to Equity Ratio"] = get_metric_values(df_ratios, "Debt to Equity Ratio")
                fig_lev = create_custom_chart(df_lev, "Area", "D/E Ratio")
                fig_lev.update_layout(title="Leverage Ratio Trend (D/E)", height=350)
                st.plotly_chart(fig_lev, use_container_width=True)
                
            # Health Indicator Gauge Row
            st.markdown("<hr style='border-color: rgba(78, 222, 163, 0.15);'/>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #4edea3;'>Health Assessment dials</h4>", unsafe_allow_html=True)
            
            ratio_year = st.selectbox("Select Ratio Target Year", options=years, index=len(years)-1, key="ratio_year")
            
            gauge_cols = st.columns(3)
            with gauge_cols[0]:
                cr_val = get_metric_values(df_ratios, "Current Ratio").loc[ratio_year]
                fig_cr = create_ratio_gauge(f"Current Ratio ({ratio_year})", cr_val, 0.0, 10.0, "green_high")
                st.plotly_chart(fig_cr, use_container_width=True)
            with gauge_cols[1]:
                de_val = get_metric_values(df_ratios, "Debt to Equity Ratio").loc[ratio_year]
                fig_de = create_ratio_gauge(f"Debt to Equity ({ratio_year})", de_val, 0.0, 3.0, "red_high")
                st.plotly_chart(fig_de, use_container_width=True)
            with gauge_cols[2]:
                roe_val = get_metric_values(df_ratios, "Return on Equity (ROE) %").loc[ratio_year]
                fig_roe = create_ratio_gauge(f"ROE % ({ratio_year})", roe_val, 0.0, 100.0, "green_high")
                st.plotly_chart(fig_roe, use_container_width=True)

            # Ratios table display
            st.markdown("<h4 style='color: #bbcabf;'>Financial Ratios Grid</h4>", unsafe_allow_html=True)
            def fmt_ratio_cells(row_name, val):
                if "%" in str(row_name) or "return" in str(row_name).lower() or "margin" in str(row_name).lower():
                    return f"{val:.2f}%"
                return f"{val:.2f}"
                
            formatted_ratios = pd.DataFrame(index=df_ratios.index, columns=df_ratios.columns)
            for idx in df_ratios.index:
                for col in df_ratios.columns:
                    formatted_ratios.loc[idx, col] = fmt_ratio_cells(idx, df_ratios.loc[idx, col])
            st.dataframe(formatted_ratios, use_container_width=True)
        else:
            st.info("Please upload a Financial Ratios sheet to start analysis.")

    # Styled Footer
    st.markdown('<div class="footer">Emerald Financial Analytics &copy; 2026. Powered by Python, Streamlit, and Plotly. Configured under Emerald Fidelity Aesthetics.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
