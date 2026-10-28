
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Afficionado Coffee | Product Analytics",
    page_icon="☕",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
    .stApp {
        background-color: #faf7f2;
    }
    h1, h2, h3 {
        color: #4b2e22;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e6d8c8;
        padding: 17px;
        border-radius: 12px;
        box-shadow: 0 2px 7px rgba(60, 40, 20, 0.05);
    }
    div[data-testid="stMetricLabel"] {
        color: #765541;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
DATA_FILE = "Afficionado Coffee Roasters.csv - Transactions.csv"

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)

    required_columns = [
        "transaction_id", "transaction_qty", "store_location",
        "unit_price", "product_category", "product_type",
        "product_detail"
    ]

    missing_columns = [c for c in required_columns if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    numeric_columns = ["transaction_qty", "unit_price"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=numeric_columns).copy()
    df["Revenue"] = df["transaction_qty"] * df["unit_price"]
    df["Product"] = df["product_detail"].fillna("Unknown Product")
    df["Category"] = df["product_category"].fillna("Unknown Category")
    df["Store"] = df["store_location"].fillna("Unknown Store")
    df["Quantity"] = df["transaction_qty"]

    return df

try:
    if not Path(DATA_FILE).exists():
        st.error(f"Dataset not found: {DATA_FILE}")
        st.info(
            "Keep the CSV file and app.py in the same project folder. "
            "Check the dataset filename carefully."
        )
        st.stop()

    df = load_data(DATA_FILE)

except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()

# ---------------- HEADER ----------------
st.title("☕ Afficionado Coffee Roasters")
st.subheader("Product Optimization & Revenue Contribution Analysis")
st.caption(
    "Interactive business intelligence dashboard | "
    "Product performance • Revenue trends • Store comparison"
)

st.divider()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("Dashboard Controls")
st.sidebar.caption("Filter the data to explore business performance.")

stores = sorted(df["Store"].unique().tolist())
categories = sorted(df["Category"].unique().tolist())

selected_stores = st.sidebar.multiselect(
    "Select Store Locations",
    options=stores,
    default=stores
)

selected_categories = st.sidebar.multiselect(
    "Select Product Categories",
    options=categories,
    default=categories
)

filtered = df[
    df["Store"].isin(selected_stores)
    & df["Category"].isin(selected_categories)
].copy()

if filtered.empty:
    st.warning("No data matches the selected filters. Please select a store and category.")
    st.stop()

top_n = st.sidebar.slider(
    "Number of Products to Display",
    min_value=5,
    max_value=20,
    value=10
)

# ---------------- KPI CARDS ----------------
total_revenue = filtered["Revenue"].sum()
total_quantity = filtered["Quantity"].sum()
total_transactions = filtered["transaction_id"].nunique()
avg_revenue_per_transaction = (
    total_revenue / total_transactions if total_transactions else 0
)
unique_products = filtered["Product"].nunique()

st.markdown("### Business Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
c2.metric("Units Sold", f"{total_quantity:,.0f}")
c3.metric("Transactions", f"{total_transactions:,}")
c4.metric("Unique Products", f"{unique_products:,}")

st.caption(
    f"Average revenue per transaction: ₹{avg_revenue_per_transaction:,.2f}"
)

st.divider()

# ---------------- REVENUE BY CATEGORY ----------------
st.markdown("### 1. Revenue Contribution by Category")

category_sales = (
    filtered.groupby("Category", as_index=False)
    .agg(Revenue=("Revenue", "sum"), Quantity=("Quantity", "sum"))
    .sort_values("Revenue", ascending=False)
)
category_sales["Revenue Share (%)"] = (
    category_sales["Revenue"] / total_revenue * 100
)

left, right = st.columns(2)

with left:
    fig_category = px.bar(
        category_sales.sort_values("Revenue", ascending=True),
        x="Revenue",
        y="Category",
        orientation="h",
        text_auto=".2s",
        title="Revenue by Product Category",
        color="Revenue",
        color_continuous_scale="YlOrBr",
        labels={"Revenue": "Revenue (₹)", "Category": "Category"}
    )
    fig_category.update_layout(
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )
    st.plotly_chart(fig_category, use_container_width=True)

with right:
    fig_share = px.pie(
        category_sales,
        names="Category",
        values="Revenue",
        hole=0.48,
        title="Category Revenue Share",
        color_discrete_sequence=px.colors.sequential.Oranges
    )
    fig_share.update_traces(
        textposition="inside",
        textinfo="percent"
    )
    fig_share.update_layout(template="plotly_white", height=430)
    st.plotly_chart(fig_share, use_container_width=True)

st.dataframe(
    category_sales.style.format({
        "Revenue": "₹{:,.2f}",
        "Quantity": "{:,.0f}",
        "Revenue Share (%)": "{:.2f}%"
    }),
    use_container_width=True,
    hide_index=True
)

st.divider()

# ---------------- TOP PRODUCTS ----------------
st.markdown("### 2. Product Performance Analysis")

product_sales = (
    filtered.groupby("Product", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        Quantity=("Quantity", "sum")
    )
)

product_sales["Revenue Share (%)"] = (
    product_sales["Revenue"] / total_revenue * 100
)

col1, col2 = st.columns(2)

with col1:
    top_revenue = product_sales.nlargest(top_n, "Revenue").sort_values("Revenue")
    fig_top_revenue = px.bar(
        top_revenue,
        x="Revenue",
        y="Product",
        orientation="h",
        text_auto=".2s",
        title=f"Top {top_n} Products by Revenue",
        color="Revenue",
        color_continuous_scale="Oranges"
    )
    fig_top_revenue.update_layout(
        template="plotly_white",
        coloraxis_showscale=False,
        height=520
    )
    st.plotly_chart(fig_top_revenue, use_container_width=True)

with col2:
    top_quantity = product_sales.nlargest(top_n, "Quantity").sort_values("Quantity")
    fig_top_quantity = px.bar(
        top_quantity,
        x="Quantity",
        y="Product",
        orientation="h",
        text_auto=True,
        title=f"Top {top_n} Products by Quantity Sold",
        color="Quantity",
        color_continuous_scale="YlOrBr"
    )
    fig_top_quantity.update_layout(
        template="plotly_white",
        coloraxis_showscale=False,
        height=520
    )
    st.plotly_chart(fig_top_quantity, use_container_width=True)

st.divider()

# ---------------- PRODUCT OPTIMIZATION ----------------
st.markdown("### 3. Product Optimization Opportunities")

median_quantity = product_sales["Quantity"].median()
median_revenue = product_sales["Revenue"].median()

product_sales["Performance Segment"] = "Other Products"
product_sales.loc[
    (product_sales["Quantity"] >= median_quantity)
    & (product_sales["Revenue"] >= median_revenue),
    "Performance Segment"
] = "High Volume / High Revenue"

product_sales.loc[
    (product_sales["Quantity"] >= median_quantity)
    & (product_sales["Revenue"] < median_revenue),
    "Performance Segment"
] = "High Volume / Lower Revenue"

product_sales.loc[
    (product_sales["Quantity"] < median_quantity)
    & (product_sales["Revenue"] >= median_revenue),
    "Performance Segment"
] = "Lower Volume / High Revenue"

fig_scatter = px.scatter(
    product_sales,
    x="Quantity",
    y="Revenue",
    color="Performance Segment",
    hover_name="Product",
    size="Revenue",
    size_max=28,
    title="Product Portfolio: Sales Volume vs Revenue",
    color_discrete_sequence=["#b87333", "#6b8e23", "#d2691e", "#8b7355"]
)

fig_scatter.add_vline(
    x=median_quantity,
    line_dash="dash",
    line_color="gray"
)
fig_scatter.add_hline(
    y=median_revenue,
    line_dash="dash",
    line_color="gray"
)
fig_scatter.update_layout(template="plotly_white", height=520)
st.plotly_chart(fig_scatter, use_container_width=True)

opportunities = product_sales[
    product_sales["Performance Segment"] == "High Volume / Lower Revenue"
].sort_values("Quantity", ascending=False)

if not opportunities.empty:
    st.markdown("**High-volume, lower-revenue products to investigate**")
    st.dataframe(
        opportunities[[
            "Product", "Quantity", "Revenue",
            "Revenue Share (%)", "Performance Segment"
        ]].style.format({
            "Quantity": "{:,.0f}",
            "Revenue": "₹{:,.2f}",
            "Revenue Share (%)": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No products match this segment under the current filters.")

st.caption(
    "Note: High-volume/lower-revenue classification compares products against "
    "the median quantity and median revenue. It identifies products for further "
    "investigation; it does not by itself prove low profitability."
)

st.divider()

# ---------------- STORE COMPARISON ----------------
st.markdown("### 4. Store Performance Comparison")

store_sales = (
    filtered.groupby("Store", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("transaction_id", "nunique")
    )
    .sort_values("Revenue", ascending=False)
)

store_sales["Revenue Share (%)"] = (
    store_sales["Revenue"] / total_revenue * 100
)

fig_store = px.bar(
    store_sales.sort_values("Revenue", ascending=True),
    x="Revenue",
    y="Store",
    orientation="h",
    text_auto=".2s",
    title="Revenue by Store Location",
    color="Revenue",
    color_continuous_scale="YlOrBr"
)
fig_store.update_layout(
    template="plotly_white",
    coloraxis_showscale=False,
    height=350
)
st.plotly_chart(fig_store, use_container_width=True)

st.dataframe(
    store_sales.style.format({
        "Revenue": "₹{:,.2f}",
        "Quantity": "{:,.0f}",
        "Transactions": "{:,.0f}",
        "Revenue Share (%)": "{:.2f}%"
    }),
    use_container_width=True,
    hide_index=True
)

st.divider()

# ---------------- PARETO ANALYSIS ----------------
st.markdown("### 5. Product Revenue Contribution (Pareto Analysis)")

pareto = product_sales.sort_values("Revenue", ascending=False).copy()
pareto["Cumulative Revenue"] = pareto["Revenue"].cumsum()
pareto["Cumulative Revenue (%)"] = (
    pareto["Cumulative Revenue"] / total_revenue * 100
)
pareto["Product Rank"] = range(1, len(pareto) + 1)

fig_pareto = go.Figure()

fig_pareto.add_trace(go.Bar(
    x=pareto["Product Rank"],
    y=pareto["Revenue"],
    name="Product Revenue",
    marker_color="#c17b42"
))

fig_pareto.add_trace(go.Scatter(
    x=pareto["Product Rank"],
    y=pareto["Cumulative Revenue (%)"],
    name="Cumulative Revenue (%)",
    yaxis="y2",
    mode="lines+markers",
    line=dict(color="#4b2e22", width=3)
))

fig_pareto.add_hline(
    y=80,
    yref="y2",
    line_dash="dash",
    line_color="red",
    annotation_text="80% Revenue Target"
)

fig_pareto.update_layout(
    title="Revenue Concentration Across Products",
    template="plotly_white",
    xaxis_title="Product Rank (highest revenue first)",
    yaxis=dict(title="Revenue (₹)"),
    yaxis2=dict(
        title="Cumulative Revenue (%)",
        overlaying="y",
        side="right",
        range=[0, 105]
    ),
    height=480,
    legend=dict(orientation="h", y=1.12)
)

st.plotly_chart(fig_pareto, use_container_width=True)

products_for_80 = int(
    (pareto["Cumulative Revenue (%)"] < 80).sum() + 1
) if not pareto.empty else 0

products_for_80 = min(products_for_80, len(pareto))

p1, p2 = st.columns(2)
p1.metric("Unique Products Analysed", f"{len(pareto):,}")
p2.metric("Products to Reach 80% Revenue", f"{products_for_80:,}")

st.caption(
    "Pareto analysis ranks products by revenue and calculates cumulative "
    "contribution. The 80% threshold is an analytical reference, not a guarantee."
)

st.divider()

# ---------------- AUTOMATED BUSINESS INSIGHTS ----------------
st.markdown("### 6. Key Business Insights & Recommendations")

top_category = category_sales.iloc[0]
top_product = product_sales.sort_values("Revenue", ascending=False).iloc[0]
top_store = store_sales.iloc[0]

st.markdown(f"""
**Insight 1 — Leading Category:** {top_category['Category']} is the
highest-revenue category in the selected data, contributing
**{top_category['Revenue Share (%)']:.2f}%** of revenue.

**Insight 2 — Leading Product:** {top_product['Product']} is the
highest-revenue product under the current filters, generating
**₹{top_product['Revenue']:,.2f}**.

**Insight 3 — Store Performance:** {top_store['Store']} generates the
highest revenue among the selected stores, with
**₹{top_store['Revenue']:,.2f}**.

**Recommendation 1:** Review product-level revenue and quantity together
before deciding which products to promote.

**Recommendation 2:** Compare category and store performance to identify
where additional promotions or product availability reviews may be useful.

**Recommendation 3:** Investigate high-volume/lower-revenue products using
pricing, product size, discounts and cost data before making pricing decisions.
""")

st.divider()

# ---------------- DATA TABLE & DOWNLOAD ----------------
with st.expander("View Filtered Transaction Data"):
    st.dataframe(filtered, use_container_width=True, hide_index=True)

csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="afficionado_filtered_analysis.csv",
    mime="text/csv"
)

st.caption(
    "Afficionado Coffee Roasters | Product Optimization & Revenue Contribution Analysis"
)
