import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random

# Page Configuration
st.set_page_config(
    page_title="E-commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data Generation
@st.cache_data
def generate_ecommerce_data(n_records=1000):
    np.random.seed(42)
    random.seed(42)
    
    # Product Categories & Names
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Beauty', 'Toys']
    product_names = [
        'Wireless Headphones', 'Smartphone', 'Laptop', 'T-Shirt', 'Jeans', 'Dress',
        'Garden Tools', 'Sofa', 'Lamp', 'Novel', 'Textbook', 'Running Shoes',
        'Bicycle', 'Makeup Kit', 'Skincare Set', 'Action Figure', 'Board Game'
    ]
    
    customer_segments = ['Premium', 'Regular', 'Budget']
    
    payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Cash on Delivery']
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    data = []
    
    for i in range(n_records):
        random_date = start_date + timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        category = random.choice(categories)
        product_name = random.choice(product_names)
        quantity = random.randint(1, 5)
        unit_price = round(random.uniform(10, 500), 2)
        total_amount = round(quantity * unit_price, 2)
        
        discount_percent = random.randint(0, 30)
        discount_amount = round(total_amount * discount_percent / 100, 2)
        final_amount = round(total_amount - discount_amount, 2)
        
        customer_id = f"CUST_{i+1:04d}"
        customer_segment = random.choice(customer_segments)
        
        order_id = f"ORD_{i+1:05d}"
        payment_method = random.choice(payment_methods)
        
        shipping_cost = round(random.uniform(5, 25), 2)
        
        rating = random.randint(1, 5)
        
        data.append({
            'order_id': order_id,
            'customer_id': customer_id,
            'order_date': random_date,
            'category': category,
            'product_name': product_name,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'final_amount': final_amount,
            'shipping_cost': shipping_cost,
            'customer_segment': customer_segment,
            'payment_method': payment_method,
            'rating': rating
        })
    
    df = pd.DataFrame(data)
    
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    df['month'] = df['order_date'].dt.to_period('M')
    df['year'] = df['order_date'].dt.year
    df['month_name'] = df['order_date'].dt.month_name()
    
    return df

df = generate_ecommerce_data(1000)

# Dashboard Title
st.title("🛒 E-commerce Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("📊 Filters")

# Date range slider
min_date = df['order_date'].min().date()
max_date = df['order_date'].max().date()

date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Category multiselect
selected_categories = st.sidebar.multiselect(
    "Select Categories",
    options=df['category'].unique(),
    default=df['category'].unique()
)

# Customer segment multiselect
selected_segments = st.sidebar.multiselect(
    "Select Customer Segments",
    options=df['customer_segment'].unique(),
    default=df['customer_segment'].unique()
)

# Payment method selectbox
selected_payment = st.sidebar.selectbox(
    "Select Payment Method",
    options=['All'] + list(df['payment_method'].unique())
)

# Rating filter
min_rating = st.sidebar.slider(
    "Minimum Rating",
    min_value=1,
    max_value=5,
    value=1
)

# Apply filters button
if st.sidebar.button("🔄 Apply Filters", type="primary"):
    st.sidebar.success("Filters applied!")

# Filter the data
filtered_df = df[
    (df['order_date'].dt.date >= date_range[0]) &
    (df['order_date'].dt.date <= date_range[1]) &
    (df['category'].isin(selected_categories)) &
    (df['customer_segment'].isin(selected_segments)) &
    (df['rating'] >= min_rating)
]

if selected_payment != 'All':
    filtered_df = filtered_df[filtered_df['payment_method'] == selected_payment]

# KPIs Section
st.header("📈 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_revenue = filtered_df['final_amount'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

with col2:
    total_orders = len(filtered_df)
    st.metric("Total Orders", f"{total_orders:,}")

with col3:
    avg_order_value = filtered_df['final_amount'].mean()
    st.metric("Avg Order Value", f"${avg_order_value:.2f}")

with col4:
    total_customers = filtered_df['customer_id'].nunique()
    st.metric("Total Customers", f"{total_customers:,}")

with col5:
    avg_rating = filtered_df['rating'].mean()
    st.metric("Avg Rating", f"{avg_rating:.2f}⭐")

st.markdown("---")

# Charts Section
st.header("📊 Analytics")

# Row 1: Revenue trends and Category performance
col1, col2 = st.columns(2)

with col1:
    # Revenue trend over time
    monthly_revenue = filtered_df.groupby('month')['final_amount'].sum().reset_index()
    monthly_revenue['month'] = monthly_revenue['month'].astype(str)
    
    fig_revenue = px.line(
        monthly_revenue, 
        x='month', 
        y='final_amount',
        title='Monthly Revenue Trend',
        labels={'final_amount': 'Revenue ($)', 'month': 'Month'}
    )
    fig_revenue.update_layout(height=400)
    st.plotly_chart(fig_revenue, use_container_width=True)

with col2:
    # Category performance
    category_revenue = filtered_df.groupby('category')['final_amount'].sum().reset_index()
    
    fig_category = px.bar(
        category_revenue,
        x='category',
        y='final_amount',
        title='Revenue by Category',
        labels={'final_amount': 'Revenue ($)', 'category': 'Category'}
    )
    fig_category.update_layout(height=400)
    st.plotly_chart(fig_category, use_container_width=True)

# Row 2: Customer segments and Payment methods
col1, col2 = st.columns(2)

with col1:
    # Customer segment distribution
    segment_data = filtered_df.groupby('customer_segment')['final_amount'].sum().reset_index()
    
    fig_segment = px.pie(
        segment_data,
        values='final_amount',
        names='customer_segment',
        title='Revenue by Customer Segment'
    )
    fig_segment.update_layout(height=400)
    st.plotly_chart(fig_segment, use_container_width=True)

with col2:
    # Payment method distribution
    payment_data = filtered_df.groupby('payment_method')['final_amount'].sum().reset_index()
    
    fig_payment = px.bar(
        payment_data,
        x='payment_method',
        y='final_amount',
        title='Revenue by Payment Method',
        labels={'final_amount': 'Revenue ($)', 'payment_method': 'Payment Method'}
    )
    fig_payment.update_layout(height=400)
    st.plotly_chart(fig_payment, use_container_width=True)

st.markdown("---")

# Data Summary Section
st.header("📋 Data Summary")

# Summary statistics
col1, col2 = st.columns(2)

with col1:
    st.subheader("Statistical Summary")
    summary_stats = filtered_df[['final_amount', 'quantity', 'rating', 'discount_percent']].describe()
    st.dataframe(summary_stats)

with col2:
    st.subheader("Top 10 Products by Revenue")
    top_products = filtered_df.groupby('product_name')['final_amount'].sum().sort_values(ascending=False).head(10)
    st.dataframe(top_products)

st.markdown("---")

# Raw Data Section
st.header("📊 Raw Data")

# Show/hide raw data toggle
if st.checkbox("Show Raw Data"):
    st.subheader(f"Filtered Dataset ({len(filtered_df)} records)")
    st.dataframe(filtered_df)

# Export functionality
st.header("💾 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    # Export filtered data as CSV
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"ecommerce_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col2:
    # Export summary statistics
    summary_csv = filtered_df.describe().to_csv()
    st.download_button(
        label="📈 Download Summary Stats",
        data=summary_csv,
        file_name=f"summary_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col3:
    # Export aggregated data
    agg_data = filtered_df.groupby(['category', 'customer_segment']).agg({
        'final_amount': ['sum', 'mean', 'count'],
        'rating': 'mean'
    }).round(2)
    
    agg_csv = agg_data.to_csv()
    st.download_button(
        label="📊 Download Aggregated Data",
        data=agg_csv,
        file_name=f"aggregated_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("**Dashboard created with Streamlit**")