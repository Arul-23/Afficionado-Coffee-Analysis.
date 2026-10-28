
import pandas as pd

# Load the dataset
df = pd.read_csv("Afficionado Coffee Roasters.csv - Transactions.csv")

# Display basic information
print("FIRST 5 ROWS:")
print(df.head())

print("\nDATASET SHAPE (ROWS, COLUMNS):")
print(df.shape)

print("\nCOLUMN NAMES:")
print(df.columns.tolist())

print("\nMISSING VALUES:")
print(df.isnull().sum())

print("\nDATA TYPES:")
print(df.dtypes)


# --------------------------------
# 1. DATA CLEANING
# --------------------------------

print("\n--- DATA CLEANING ---")

print("Duplicate rows:", df.duplicated().sum())

# Remove duplicate rows
df = df.drop_duplicates()

print("Rows after removing duplicates:", len(df))


# --------------------------------
# 2. REVENUE CALCULATION
# --------------------------------

df["revenue"] = df["transaction_qty"] * df["unit_price"]

print("\n--- TOTAL REVENUE ---")
print(round(df["revenue"].sum(), 2))

print("\n--- TOTAL QUANTITY SOLD ---")
print(df["transaction_qty"].sum())


# --------------------------------
# 3. TOP 10 PRODUCTS BY REVENUE
# --------------------------------

product_sales = df.groupby("product_detail").agg(
    total_quantity=("transaction_qty", "sum"),
    total_revenue=("revenue", "sum"),
    transaction_count=("transaction_id", "count")
).reset_index()

product_sales = product_sales.sort_values(
    by="total_revenue",
    ascending=False
)

print("\n--- TOP 10 PRODUCTS BY REVENUE ---")
print(product_sales.head(10).to_string(index=False))


# --------------------------------
# 4. TOP 10 PRODUCTS BY QUANTITY
# --------------------------------

print("\n--- TOP 10 PRODUCTS BY QUANTITY SOLD ---")

top_quantity = product_sales.sort_values(
    by="total_quantity",
    ascending=False
)

print(top_quantity.head(10).to_string(index=False))


# --------------------------------
# 5. BOTTOM 10 PRODUCTS BY REVENUE
# --------------------------------

print("\n--- BOTTOM 10 PRODUCTS BY REVENUE ---")

bottom_revenue = product_sales.sort_values(
    by="total_revenue",
    ascending=True
)

print(bottom_revenue.head(10).to_string(index=False))


# --------------------------------
# 6. CATEGORY-WISE REVENUE
# --------------------------------

category_sales = df.groupby("product_category").agg(
    total_quantity=("transaction_qty", "sum"),
    total_revenue=("revenue", "sum")
).reset_index()

category_sales["revenue_share_percent"] = (
    category_sales["total_revenue"]
    / df["revenue"].sum()
) * 100

category_sales = category_sales.sort_values(
    by="total_revenue",
    ascending=False
)

print("\n--- CATEGORY-WISE REVENUE ---")
print(category_sales.round(2).to_string(index=False))


# --------------------------------
# 7. STORE-WISE REVENUE
# --------------------------------

store_sales = df.groupby("store_location").agg(
    total_quantity=("transaction_qty", "sum"),
    total_revenue=("revenue", "sum")
).reset_index()

store_sales = store_sales.sort_values(
    by="total_revenue",
    ascending=False
)

print("\n--- STORE-WISE REVENUE ---")
print(store_sales.round(2).to_string(index=False))


# --------------------------------
# 8. SAVE ANALYSIS RESULTS
# --------------------------------

product_sales.to_csv("product_sales_analysis.csv", index=False)
category_sales.to_csv("category_sales_analysis.csv", index=False)
store_sales.to_csv("store_sales_analysis.csv", index=False)

print("\nAnalysis completed successfully!")
print("Saved: product_sales_analysis.csv")
print("Saved: category_sales_analysis.csv")
print("Saved: store_sales_analysis.csv")


# --------------------------------
# 9. PRODUCT EFFICIENCY ANALYSIS
# --------------------------------

product_sales["revenue_per_unit"] = (
    product_sales["total_revenue"]
    / product_sales["total_quantity"]
)

product_sales["revenue_share_percent"] = (
    product_sales["total_revenue"]
    / product_sales["total_revenue"].sum()
) * 100

print("\n--- HIGH VOLUME, LOW REVENUE PRODUCTS ---")

median_quantity = product_sales["total_quantity"].median()
median_revenue = product_sales["total_revenue"].median()

high_volume_low_revenue = product_sales[
    (product_sales["total_quantity"] > median_quantity)
    & (product_sales["total_revenue"] < median_revenue)
]

print(
    high_volume_low_revenue.sort_values(
        by="total_quantity", ascending=False
    ).head(10).to_string(index=False)
)

print("\n--- PRODUCT REVENUE SHARE ---")

print(
    product_sales.sort_values(
        by="revenue_share_percent", ascending=False
    )[
        [
            "product_detail",
            "total_quantity",
            "total_revenue",
            "revenue_share_percent",
            "revenue_per_unit"
        ]
    ].head(10).round(2).to_string(index=False)
)

# Save the updated product analysis
product_sales.to_csv("product_sales_analysis.csv", index=False)

print("\nProduct efficiency analysis completed!")


# --------------------------------
# 10. REVENUE CONCENTRATION & PARETO ANALYSIS
# --------------------------------

print("\n--- PARETO ANALYSIS ---")

# Sort products by revenue from highest to lowest
pareto = product_sales.sort_values(
    by="total_revenue",
    ascending=False
).copy()

# Calculate each product's share of total revenue
total_revenue = pareto["total_revenue"].sum()

pareto["revenue_share_percent"] = (
    pareto["total_revenue"] / total_revenue
) * 100

# Calculate cumulative revenue contribution
pareto["cumulative_revenue_percent"] = (
    pareto["revenue_share_percent"].cumsum()
)

# Display top 10 products and their cumulative contribution
print("\nTop 10 products - Revenue contribution:")

print(
    pareto[
        [
            "product_detail",
            "total_revenue",
            "revenue_share_percent",
            "cumulative_revenue_percent"
        ]
    ].head(10).round(2).to_string(index=False)
)

# Find how many products generate approximately 80% of revenue
products_for_80_percent = (
    pareto["cumulative_revenue_percent"] < 80
).sum() + 1

total_products = len(pareto)

print("\nTotal unique products:", total_products)
print(
    "Products needed to reach approximately 80% revenue:",
    products_for_80_percent
)

print(
    "Percentage of products contributing to approximately 80% revenue:",
    round(products_for_80_percent / total_products * 100, 2),
    "%"
)

# Save Pareto results
pareto.to_csv("pareto_analysis.csv", index=False)

print("\nPareto analysis completed!")
print("Saved: pareto_analysis.csv")
