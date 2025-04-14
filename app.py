import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="GMG Billing Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("billing_data_gpt.csv", parse_dates=["Date"])
    return df

df = load_data()

# Sidebar
st.sidebar.title("Filters")
designer = st.sidebar.selectbox("Select Designer", ["All"] + sorted(df["Designer"].unique().tolist()))
company = st.sidebar.selectbox("Select Company", ["All"] + sorted(df["Company"].unique().tolist()))
status = st.sidebar.selectbox("Select Status", ["All", "Completed", "Pending"])
date_range = st.sidebar.date_input("Select Date Range", [])

# Filter logic
filtered_df = df.copy()

if designer != "All":
    filtered_df = filtered_df[filtered_df["Designer"] == designer]
if company != "All":
    filtered_df = filtered_df[filtered_df["Company"] == company]
if status != "All":
    filtered_df = filtered_df[filtered_df["Status"] == status]
if len(date_range) == 2:
    filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(date_range[0])) & (filtered_df["Date"] <= pd.to_datetime(date_range[1]))]

# Monthly Summary
monthly_summary = filtered_df.groupby(filtered_df["Date"].dt.to_period("M")).agg({"Payment": "sum"}).reset_index()
monthly_summary["Date"] = monthly_summary["Date"].astype(str)
monthly_summary.rename(columns={"Date": "Month", "Payment": "Total Billing"}, inplace=True)

# Aggregated by Company
agg_by_company = filtered_df.groupby("Company")["Payment"].sum().reset_index()
agg_by_company.rename(columns={"Payment": "Total Amount"}, inplace=True)

# Pending
pending_df = filtered_df[filtered_df["Status"] == "Pending"]
total_pending_amount = pending_df["Payment"].sum()

# Main Title
st.markdown("<h1 style='text-align: center; color: white;'>GMG Billing Dashboard</h1>", unsafe_allow_html=True)

# Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(filtered_df))
col2.metric("Total Amount", f"₹{filtered_df['Payment'].sum()}")
col3.metric("Pending Amount", f"₹{total_pending_amount}")

# Work Records Table
st.subheader("Work Records")

def color_status(val):
    if val == "Completed":
        return f"<span style='color:lime;font-weight:bold;'>{val}</span>"
    elif val == "Pending":
        return f"<span style='color:orange;font-weight:bold;'>{val}</span>"
    else:
        return val

display_df = filtered_df.copy()
display_df["Status"] = display_df["Status"].apply(lambda x: color_status(x))
st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Monthly Billing Table
st.subheader("Monthly Billing Summary")
st.dataframe(monthly_summary, use_container_width=True)

# Company-wise Billing
st.subheader("Company-wise Billing Summary")
st.dataframe(agg_by_company, use_container_width=True)

# Pending Payments Table
if not pending_df.empty:
    st.subheader("Pending Payments")
    st.dataframe(pending_df, use_container_width=True)

# Add New Record
st.subheader("Add New Entry")
with st.form("new_entry_form"):
    c1, c2, c3 = st.columns(3)
    designer = c1.text_input("Designer")
    work_topic = c2.text_input("Work Topic")
    date = c3.date_input("Date")

    company = c1.selectbox("Company", sorted(df["Company"].unique()))
    payment = c2.number_input("Payment (₹)", step=50)
    status = c3.selectbox("Status", ["Completed", "Pending"])

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        new_row = pd.DataFrame([[designer, work_topic, pd.to_datetime(date), company, payment, status]], columns=df.columns)
        updated_df = pd.concat([df, new_row], ignore_index=True)
        updated_df.to_csv("billing_data.csv", index=False)
        st.success("New entry added! Please refresh to see changes.")

# Optional Password Lock (simple security)
# password = st.text_input("Enter Password", type="password")
# if password != "gmg123":
#     st.warning("Incorrect Password!")
#     st.stop()