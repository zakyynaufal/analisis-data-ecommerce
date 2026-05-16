import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# =========================
# Load Data
# =========================

all_df = pd.read_csv("all_data_submission.csv")

# =========================
# Data Preparation
# =========================

all_df["order_purchase_timestamp"] = pd.to_datetime(
    all_df["order_purchase_timestamp"]
)

# =========================
# Filter Dashboard
# =========================

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:

    st.header("Filter Data")

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[
    (all_df["order_purchase_timestamp"] >= str(start_date)) &
    (all_df["order_purchase_timestamp"] <= str(end_date))
]

# =========================
# Dashboard Header
# =========================

st.title("E-Commerce Sales Analysis Dashboard")

st.markdown(
    "Analisis performa penjualan e-commerce periode 2016–2018"
)

# st.write(main_df)

# =========================
# Monthly Revenue DataFrame
# =========================

def create_monthly_revenue_df(df):

    monthly_revenue_df = df.resample(
        rule='ME',
        on='order_purchase_timestamp'
    ).agg({
        "price": "sum"
    })

    monthly_revenue_df = monthly_revenue_df.reset_index()

    monthly_revenue_df.rename(columns={
        "price": "revenue"
    }, inplace=True)

    return monthly_revenue_df

monthly_revenue_df = create_monthly_revenue_df(main_df)
# st.write(monthly_revenue_df)

# =========================
# Visualisasi Monthly Revenue
# =========================

st.subheader("Monthly Revenue Trend")

fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(
    monthly_revenue_df["order_purchase_timestamp"],
    monthly_revenue_df["revenue"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)

ax.set_title(
    "Monthly Revenue 2016–2018",
    fontsize=20
)

ax.set_xlabel("Date", fontsize=14)
ax.set_ylabel("Revenue", fontsize=14)

st.pyplot(fig)

# =========================
# Category Revenue DataFrame
# =========================

def create_category_revenue_df(df):

    category_revenue_df = df.groupby(
        by="product_category_name_english"
    ).agg({
        "price": "sum"
    })

    category_revenue_df = category_revenue_df.reset_index()

    category_revenue_df.rename(columns={
        "price": "revenue"
    }, inplace=True)

    category_revenue_df = category_revenue_df.sort_values(
        by="revenue",
        ascending=False
    )

    return category_revenue_df
category_revenue_df = create_category_revenue_df(main_df)

# =========================
# Visualisasi Category Revenue
# =========================

st.subheader("Best & Worst Performing Product Categories")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))


# Top Categories
sns.barplot(
    x="revenue",
    y="product_category_name_english",
    data=category_revenue_df.head(10),
    ax=ax[0],
    palette="Blues_r"
)

ax[0].set_title(
    "Top 10 Product Categories",
    fontsize=20
)

ax[0].set_xlabel(
    "Revenue",
    fontsize=14
)

ax[0].set_ylabel(
    None
)

ax[0].tick_params(
    axis='y',
    labelsize=12
)

ax[0].tick_params(
    axis='x',
    labelsize=11
)


# Lowest Categories
sns.barplot(
    x="revenue",
    y="product_category_name_english",
    data=category_revenue_df.sort_values(
        by="revenue",
        ascending=True
    ).head(10),
    ax=ax[1],
    palette="Reds_r"
)

ax[1].set_title(
    "Lowest 10 Product Categories",
    fontsize=20
)

ax[1].set_xlabel(
    "Revenue",
    fontsize=14
)

ax[1].set_ylabel(
    None
)

ax[1].tick_params(
    axis='y',
    labelsize=12
)

ax[1].tick_params(
    axis='x',
    labelsize=11
)


plt.tight_layout()

st.pyplot(fig)

# =========================
# RFM DataFrame
# =========================

def create_rfm_df(df):

    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
    })

    rfm_df.columns = [
        "customer_id",
        "max_order_timestamp",
        "frequency",
        "monetary"
    ]

    recent_date = df["order_purchase_timestamp"].max().date()

    rfm_df["max_order_timestamp"] = (
        rfm_df["max_order_timestamp"].dt.date
    )

    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days
    )

    rfm_df.drop(
        "max_order_timestamp",
        axis=1,
        inplace=True
    )

    return rfm_df

rfm_df = create_rfm_df(main_df)

# =========================
# Visualisasi RFM Analysis
# =========================

st.subheader("RFM Analysis")


fig, ax = plt.subplots(
    nrows=1,
    ncols=3,
    figsize=(32, 10)
)


# Recency
sns.barplot(
    y="recency",
    x="customer_id",
    data=rfm_df.sort_values(
        by="recency"
    ).head(5),
    palette="Blues",
    ax=ax[0]
)

ax[0].set_title(
    "Best Customers by Recency",
    fontsize=18
)

ax[0].tick_params(
    axis='x',
    rotation=45
)

ax[0].tick_params(
    axis='y',
    labelsize=11
)


# Frequency
sns.barplot(
    y="frequency",
    x="customer_id",
    data=rfm_df.sort_values(
        by="frequency",
        ascending=False
    ).head(5),
    palette="Greens",
    ax=ax[1]
)

ax[1].set_title(
    "Best Customers by Frequency",
    fontsize=18
)

ax[1].tick_params(
    axis='x',
    rotation=45
)
ax[1].tick_params(
    axis='y',
    labelsize=11
)

# Monetary
sns.barplot(
    y="monetary",
    x="customer_id",
    data=rfm_df.sort_values(
        by="monetary",
        ascending=False
    ).head(5),
    palette="Reds",
    ax=ax[2]
)

ax[2].set_title(
    "Best Customers by Monetary",
    fontsize=18
)

ax[2].tick_params(
    axis='x',
    rotation=45
)
ax[2].tick_params(
    axis='y',
    labelsize=11
)

plt.tight_layout()

st.pyplot(fig)