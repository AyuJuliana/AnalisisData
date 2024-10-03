import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_option_menu import option_menu

# Load the dataset
df = pd.read_csv("main_data.csv")

# Ensure datetime columns are in correct format
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])

def show_customer_count_by_state(data):
    customer_state = data.groupby("customer_state").size().sort_values(ascending=False).reset_index(name='customer_count')
    return customer_state

def show_order_status_distribution(data):
    # Mendapatkan semua status order yang unik
    unique_statuses = ['delivered', 'canceled', 'shipped', 'pending', 'invoiced']  # tambahkan status lain yang mungkin ada

    # Hitung distribusi status order
    order_status_counts = data['order_status'].value_counts().reindex(unique_statuses, fill_value=0)

    # Reset index untuk format DataFrame yang tepat
    return order_status_counts.reset_index(name='count').rename(columns={'index': 'order_status'})


def show_shipping_time_mean(data):
    data['shipping_time'] = (data['order_delivered_customer_date'] - data['order_purchase_timestamp']).dt.days
    return data['shipping_time'].mean()

def show_monthly_revenue(data):
    data['purchase_month'] = data['order_purchase_timestamp'].dt.to_period('M')
    monthly_revenue = data.groupby('purchase_month')['price'].sum()
    return monthly_revenue

def rfm_analysis(data):
    # Calculating RFM values for each unique customer
    rfm_df = data.groupby('customer_unique_id', as_index=False).agg({
        "order_delivered_customer_date": "max",  # Taking the most recent order date
        "order_id": "nunique",                   # Counting unique orders (Frequency)
        "price": "sum"                           # Summing revenue from the customer (Monetary)
    })

    # Renaming columns for clarity
    rfm_df.columns = ["customer_unique_id", "max_order_date", "frequency", "monetary"]

    # Calculating the last transaction date for customers
    rfm_df["max_order_date"] = pd.to_datetime(rfm_df["max_order_date"])
    recent_date = data["order_purchase_timestamp"].max()
    rfm_df["recency"] = (recent_date - rfm_df["max_order_date"]).dt.days

    # Dropping the max_order_date column as it's no longer needed
    rfm_df.drop("max_order_date", axis=1, inplace=True)

    return rfm_df

def display_rfm_visualizations(rfm_df):
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
    colors = ["#72BCD4", "#72BCD4", "#72BCD4"]

    sns.barplot(y="recency", x="customer_unique_id", data=rfm_df.sort_values(by="recency", ascending=False).head(5), hue="customer_unique_id", legend=False, palette=colors, ax=ax[0])
    ax[0].set_title("By Recency", fontsize=18)
    ax[0].tick_params(axis='x', labelsize=15, rotation=90)

    sns.barplot(y="frequency", x="customer_unique_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), hue="customer_unique_id", legend=False, palette=colors, ax=ax[1])
    ax[1].set_title("By Frequency", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=15, rotation=90)

    sns.barplot(y="monetary", x="customer_unique_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), hue="customer_unique_id", legend=False, palette=colors, ax=ax[2])
    ax[2].set_title("By Monetary", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=15, rotation=90)

    plt.suptitle("Top Customers Based on RFM Parameters (customer_unique_id)", fontsize=20)
    st.pyplot(fig)

def payment_distribution_analysis(data):
    # Calculate the customer distribution based on payment types
    payment_distribution = data['payment_type'].value_counts().reset_index()
    payment_distribution.columns = ['payment_type', 'customer_count']
    return payment_distribution

def display_payment_distribution(payment_distribution):
    plt.figure(figsize=(12, 6))
    sns.barplot(data=payment_distribution, x='payment_type', y='customer_count', color='steelblue')  # Consistent bar color
    plt.title('Sebaran Pelanggan Berdasarkan Tipe Pembayaran', fontsize=16)
    plt.xlabel('Tipe Pembayaran', fontsize=14)
    plt.ylabel('Jumlah Pelanggan', fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

def home(df):
    st.header("E-commerce Data Dashboard 📊")

    # Display customer count by state
    customer_count = show_customer_count_by_state(df)
    st.subheader("Customer Count by State")
    st.write("This section shows the total number of customers grouped by their respective states. "
             "It helps to identify which states have the highest number of customers.")
    st.write(customer_count)
    
    # Display order status distribution
    order_status_dist = show_order_status_distribution(df)
    st.subheader("Order Status Distribution")
    st.write("This chart displays the distribution of different order statuses, showing how many orders "
             "are completed, shipped, canceled, etc. It provides insight into the overall performance "
             "of order fulfillment.")
    st.bar_chart(order_status_dist.set_index('order_status'))
    
    # Display mean shipping time
    mean_shipping_time = show_shipping_time_mean(df)
    st.subheader("Mean Shipping Time")
    st.write("The mean shipping time indicates the average number of days taken for orders to be delivered "
             "to customers. This metric is essential for assessing the efficiency of the shipping process.")
    st.write(f"The average shipping time is {mean_shipping_time:.2f} days.")

    # Display monthly revenue
    monthly_revenue = show_monthly_revenue(df)
    st.subheader("Monthly Revenue")
    st.write("This graph shows the total revenue generated each month, allowing us to track trends "
             "in sales over time. It can help identify peak sales periods and potential downturns.")
    fig, ax = plt.subplots()
    ax.plot(monthly_revenue.index.astype(str), monthly_revenue.values, marker='o', linestyle='-', color='skyblue')
    plt.title('Monthly E-commerce Revenue')
    plt.xlabel('Month')
    plt.ylabel('Total Revenue')
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # RFM Analysis
    st.subheader("RFM Analysis")
    st.write("RFM (Recency, Frequency, Monetary) analysis is used to segment customers based on their purchasing behavior. "
             "This analysis helps to identify valuable customers and tailor marketing strategies accordingly.")
    rfm_df = rfm_analysis(df)
    st.write(rfm_df.head())
    display_rfm_visualizations(rfm_df)

    # Payment Distribution Analysis
    st.subheader("Payment Distribution Analysis")
    st.write("This section shows the distribution of customers based on the payment methods they used. "
             "Understanding payment preferences can inform decisions regarding payment options offered to customers.")
    payment_distribution = payment_distribution_analysis(df)
    display_payment_distribution(payment_distribution)

def main():
    with st.sidebar:
        selected = option_menu(menu_title="Dashboard Menu",
                               options=["Main Dashboard"],
                               default_index=0)

    if selected == "Main Dashboard":
        home(df)

if __name__ == "__main__":
    main()
