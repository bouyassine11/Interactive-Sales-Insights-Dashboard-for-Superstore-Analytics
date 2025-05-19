import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set Streamlit page configuration
st.set_page_config(page_title="Superstore Sales Dashboard", page_icon="📊", layout="wide")

# Load and cache the dataset
@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")
    # Convert 'Order Date' to datetime
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d/%m/%Y')
    # Extract year and month
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.to_period('M')
    return df

# Load data
df = load_data()

# Sidebar for navigation and filters
st.sidebar.header("Sales Dashboard Filters")
page = st.sidebar.selectbox("Select Page", ["Home", "Revenue Trends", "Best-Selling Products", "Regional Analysis"])
year_filter = st.sidebar.multiselect("Select Year(s)", options=sorted(df['Year'].unique()), default=sorted(df['Year'].unique()))
region_filter = st.sidebar.multiselect("Select Region(s)", options=sorted(df['Region'].unique()), default=sorted(df['Region'].unique()))

# Filter data based on selections
filtered_df = df[(df['Year'].isin(year_filter)) & (df['Region'].isin(region_filter))]

# Home Page
if page == "Home":
    st.title("Superstore Sales Dashboard")
    st.write("Explore sales data with interactive visualizations. Use the sidebar to navigate and filter data.")
    
    # Key Metrics
    total_sales = filtered_df['Sales'].sum()
    total_orders = filtered_df['Order ID'].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Avg. Order Value", f"${avg_order_value:,.2f}")
    
    st.write("### Dataset Preview")
    st.dataframe(filtered_df.head())

# Revenue Trends Page
elif page == "Revenue Trends":
    st.title("Revenue Trends Over Time")
    
    # Aggregate sales by month
    monthly_sales = filtered_df.groupby('Month')['Sales'].sum().reset_index()
    monthly_sales['Month'] = monthly_sales['Month'].astype(str)
    
    # Plotly line chart
    fig = px.line(monthly_sales, x='Month', y='Sales', title="Monthly Sales Trend",
                  labels={'Sales': 'Total Sales ($)', 'Month': 'Month'},
                  markers=True)
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

# Best-Selling Products Page
elif page == "Best-Selling Products":
    st.title("Best-Selling Products")
    
    # Top products by sales
    top_products_sales = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(10)
    
    # Seaborn bar plot
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_products_sales, x='Sales', y='Sub-Category', palette='viridis')
    plt.title("Top 10 Products by Sales")
    plt.xlabel("Total Sales ($)")
    plt.ylabel("Product Sub-Category")
    st.pyplot(plt)
    
    # Top products by quantity
    top_products_quantity = filtered_df.groupby('Sub-Category')['Quantity'].sum().reset_index().sort_values('Quantity', ascending=False).head(10)
    
    # Plotly bar chart
    fig = px.bar(top_products_quantity, x='Quantity', y='Sub-Category', title="Top 10 Products by Quantity Sold",
                 labels={'Quantity': 'Total Quantity Sold', 'Sub-Category': 'Product Sub-Category'},
                 color='Quantity', color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

# Regional Analysis Page
elif page == "Regional Analysis":
    st.title("Regional Sales Analysis")
    
    # Sales by region
    region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index()
    
    # Seaborn heatmap for sales by region and state
    state_sales = filtered_df.groupby(['Region', 'State'])['Sales'].sum().unstack().fillna(0)
    plt.figure(figsize=(12, 8))
    sns.heatmap(state_sales, cmap='YlGnBu', annot=False)
    plt.title("Sales Heatmap by Region and State")
    plt.xlabel("State")
    plt.ylabel("Region")
    st.pyplot(plt)
    
    # Plotly choropleth map
    state_sales_total = filtered_df.groupby('State')['Sales'].sum().reset_index()
    fig = px.choropleth(state_sales_total, 
                        locations='State', 
                        locationmode='USA-states', 
                        color='Sales', 
                        scope='usa', 
                        title='Sales by State',
                        color_continuous_scale='Blues',
                        labels={'Sales': 'Total Sales ($)'})
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.sidebar.write("Built with Streamlit, Pandas, Matplotlib, Seaborn, and Plotly")