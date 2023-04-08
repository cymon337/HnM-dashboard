import streamlit as st
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.colors as mcolors

API_BASE_URL = "https://fit-territory-377423.oa.r.appspot.com/api/"
API_URL_REGISTER = 'https://fit-territory-377423.oa.r.appspot.com/api/register'
API_URL_AUTHENTICATE = 'https://fit-territory-377423.oa.r.appspot.com/api/authenticate'

# ------------------------------------------------------------------------------------------------------------------------
#                                                       LOGIN
# ------------------------------------------------------------------------------------------------------------------------

def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log in"):
        response = requests.post(API_BASE_URL + "authenticate", json={"username": username, "password": password})
        print("Response status code:", response.status_code)
        print("Response text:", response.text)
        if response.status_code == 200:
            return True
        elif response.status_code == 401:
            st.error("Invalid login details. Please try again.")
            return False
        else:
            st.error("An unexpected error occurred during authentication")
            return False

    st.caption("Note: You may need to click 'Log in' twice to load the dashboard.")

# ------------------------------------------------------------------------------------------------------------------------
#                                                       REGISTER
# ------------------------------------------------------------------------------------------------------------------------

def register():
    st.write("Please enter your registration details below.")
    st.markdown("**Note:** Fields marked with an asterisk (*) are mandatory.")
    username = st.text_input("Username*")
    email = st.text_input("Email")
    password = st.text_input("Password*", type="password")
    password_confirmation = st.text_input("Confirm Password*", type="password")

    if st.button("Register"):
        if password == password_confirmation:
            data = {
                "username": username,
                "email": email,
                "password": password
            }
            response = requests.post(API_URL_REGISTER, json=data)
            if response.content:
                response_json = response.json()
                if 'message' in response_json and response_json['message'] == 'User registered successfully':
                    st.success('User registered successfully')
                else:
                    st.error(response_json.get('message', 'An unexpected error occurred during registration'))
            else:
                st.error("An error occurred during registration.")
        else:
            st.error("Passwords do not match.")

# ------------------------------------------------------------------------------------------------------------------------
#                                                       MAIN PART
# ------------------------------------------------------------------------------------------------------------------------

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.sidebar.title('User Authentication')
    auth_options = ['Login', 'Register']
    selected_option = st.sidebar.radio('Select an option', auth_options)

    if selected_option == 'Login':
        st.session_state.logged_in = login()
    elif selected_option == 'Register':
        register()
else:
    API_URL_CUSTOMERS = 'https://fit-territory-377423.oa.r.appspot.com/api/customers'
    API_URL_ARTICLES = 'https://fit-territory-377423.oa.r.appspot.com/api/articles'
    API_URL_TRANSACTIONS = 'https://fit-territory-377423.oa.r.appspot.com/api/transactions'
    
    def load_data(api_url):
        api_key = "cool-key"  
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.get(api_url, headers=headers)
        data = response.json()
        return pd.DataFrame(data)

    # Sidebar logo
    logo = "img/logo.svg.png" 
    st.sidebar.image(logo, use_column_width=True)

    # Tab selector for customers, articles, transactions
    tabs = ["Home", "Customers", "Articles", "Transactions"]
    selected_tab = st.sidebar.radio("Select a Page", tabs)

    # ------------------------------------------------------------------------------------------------------------------------
    #                                                       HOME
    # ------------------------------------------------------------------------------------------------------------------------

    if selected_tab == "Home":
        # H&M store image
        image_path = "img/home.jpg" 
        st.image(image_path, use_column_width=True)

        st.title("Welcome to my Capstone Project!")
        # Project description
        st.markdown("""
        This dashboard provides insights into customer, transaction and article data for an H&M retail store.

        **Customers Tab:**
        - Explore and filter customer data.
        - Visualize customer age distribution.
        - Analyze revenue KPIs based on selected filters.

        **Transactions Tab:**
        - Explore and filter transaction data.
        - Visualize transaction data through various charts, such as the number of transactions per day and revenue per day.

        **Articles Tab:**
        - Explore and filter article data.
        - Analyze article KPIs based on selected filters, such as the number of unique products, average perceived color value and top 3 index group names.
        - Visualize article data through various charts, such as the number of articles per garment group and revenue per article category.

        Use the sidebar to navigate through the tabs and apply filters to explore the data further.
        """)

    # ------------------------------------------------------------------------------------------------------------------------
    #                                                       CUSTOMERS
    # ------------------------------------------------------------------------------------------------------------------------

    elif selected_tab == "Customers":

        st.title('Customers')
        st.markdown('*Data may take up to 30 seconds to load*')

        # Load data
        customer_df = load_data(API_URL_CUSTOMERS)

        column_order = ['customer_id', 'club_member_status', 'fashion_news_frequency', 'age']
        customer_df = customer_df[column_order]

        # ----------------------------- Filters -----------------------------
        st.sidebar.header("Filters")

        # Filter out rows with missing values
        df = customer_df.dropna(subset=['club_member_status', 'fashion_news_frequency', 'age'])

        # Age filter
        min_age, max_age = st.sidebar.slider("Age Range", 0, 100, (0, 100), 1)
        st.sidebar.markdown(f"Age range selected: ({min_age}, {max_age})")

        # Club member status filter
        club_member_status_options = ["All", "ACTIVE", "PRE-CREATE", "LEFT CLUB"]
        club_member_status = st.sidebar.selectbox("Club Member Status", club_member_status_options)

        # Fashion news frequency filter
        fashion_news_frequency_options = ["All", "NONE", "Regularly"]
        fashion_news_frequency = st.sidebar.selectbox("Fashion News Frequency", fashion_news_frequency_options)

        filtered_df = df.copy()

        if club_member_status != "All":
            filtered_df = filtered_df[filtered_df['club_member_status'] == club_member_status]

        if fashion_news_frequency != "All":
            filtered_df = filtered_df[filtered_df['fashion_news_frequency'] == fashion_news_frequency]

        filtered_df = filtered_df[(filtered_df['age'] >= min_age) & (filtered_df['age'] <= max_age)]

        st.write(filtered_df)

        # ----------------------------- KPIs -----------------------------

        # Load transactions data
        transactions_df = load_data(API_URL_TRANSACTIONS)

        # Merge filtered_df (filtered customers) and transactions DataFrames
        merged_customers_transactions = pd.merge(filtered_df, transactions_df, on="customer_id")

        # Calculate total revenue for all customers
        total_revenue_all_customers = transactions_df["price"].sum()

        # Calculate total revenue for the filtered customers
        total_revenue_filtered_customers = merged_customers_transactions["price"].sum()

        # Calculate the percentage of revenue from the filtered customers
        if total_revenue_all_customers != 0:
            percentage_revenue_filtered_customers = (total_revenue_filtered_customers / total_revenue_all_customers) * 100
        else:
            percentage_revenue_filtered_customers = 0
        
        # Calculate min and max ages in the filtered DataFrame
        min_age_filtered = filtered_df['age'].min()
        max_age_filtered = filtered_df['age'].max()

        # Calculate min and max ages in the original DataFrame (df)
        min_age_original = df['age'].min()
        max_age_original = df['age'].max()

        # Calculate the differences (deltas) between the filtered and original DataFrames
        min_age_delta = min_age_filtered - min_age_original
        max_age_delta = max_age_filtered - max_age_original
        
        # KPIs
        num_customers = len(filtered_df)
        avg_age = np.mean(filtered_df["age"])

        total_customers = len(df)
        average_age = np.mean(df["age"])

        st.subheader("KPIs")
        kpi1, kpi2 = st.columns(2)

        kpi1.metric(
            label="Different Customers",
            value=num_customers,
            delta=num_customers - total_customers
        )

        kpi2.metric(
            label="Revenue from Customers",
            value=f"{percentage_revenue_filtered_customers:.2f}%",
            delta="updated automatically"
        )

        # KPIs continued
        kpi1, kpi2, kpi3 = st.columns(3)

        kpi1.metric(
            label="Minimum Age",
            value=min_age_filtered,
            delta=min_age_delta,
            delta_color=("normal" if min_age_delta >= 0 else "inverse")
        )

        kpi2.metric(
            label="Average Age",
            value=round(avg_age, 2),
            delta=round(avg_age - average_age, 2)
        )

        kpi3.metric(
            label="Maximum Age",
            value=max_age_filtered,
            delta=max_age_delta,
            delta_color=("normal" if max_age_delta >= 0 else "inverse")
        )

        # ----------------------------- Charts -----------------------------
        st.subheader("Charts")

        # Create age bins for the age distribution chart
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-100']
        filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=bins, labels=labels, include_lowest=True)

        # Create the age distribution chart
        age_distribution = filtered_df['age_group'].value_counts().sort_index()
        fig = px.bar(age_distribution, x=age_distribution.index, y=age_distribution.values, labels={'x': 'Age Group', 'y': 'Number of Customers'}, color_discrete_sequence=['red'])

        # Update the x-axis title
        fig.update_xaxes(title_text='Age Group')

        st.plotly_chart(fig)

        # Load articles data
        articles_df = load_data(API_URL_ARTICLES)

        # Merge the merged_customers_transactions DataFrame with the articles DataFrame
        merged_all = pd.merge(merged_customers_transactions, articles_df, on='article_id')

        # Create the scatter plot using Plotly
        fig = px.scatter(merged_all,
                        x='age',
                        y='price',
                        color='index_group_name', 
                        labels={'x': 'Age', 'y': 'Price', 'color': 'Article Category'},
                        title='Customer Age vs Price by Article Category')

        st.plotly_chart(fig)

    # ------------------------------------------------------------------------------------------------------------------------
    #                                                       ARTICLES
    # ------------------------------------------------------------------------------------------------------------------------

    elif selected_tab == "Articles":
        st.title('Articles')

        # Load articles data
        articles_df = load_data(API_URL_ARTICLES)

        # Reorder columns
        column_order = [
            'article_id', 'product_code', 'prod_name', 'product_type_no', 'product_type_name',
            'product_group_name', 'graphical_appearance_no', 'graphical_appearance_name',
            'colour_group_code', 'colour_group_name', 'perceived_colour_value_id',
            'perceived_colour_value_name', 'perceived_colour_master_id', 'perceived_colour_master_name',
            'department_no', 'department_name', 'index_code', 'index_name', 'index_group_no',
            'index_group_name', 'section_no', 'section_name', 'garment_group_no', 'garment_group_name',
            'detail_desc'
        ]

        articles_df = articles_df[column_order]

        # ----------------------------- Filters -----------------------------
        st.sidebar.header("Filters")

        # Garment group name filter
        garment_group_names = ['All', 'Jersey Basic', 'Under-, Nightwear', 'Socks and Tights', 'Jersey Fancy', 'Accessories', 'Trousers Denim', 'Outdoor', 'Shoes', 'Swimwear', 'Knitwear', 'Shirts', 'Trousers', 'Dressed', 'Shorts', 'Dresses Ladies', 'Skirts', 'Special Offers', 'Blouses', 'Unknown', 'Woven/Jersey/Knitted mix Baby', 'Dresses/Skirts girls']
        selected_garment_group = st.sidebar.selectbox("Garment Group", garment_group_names)

        # Perceived color master name filter (multiselect)
        color_master_names = ['All', 'Black', 'White', 'Beige', 'Grey', 'Blue', 'Pink', 'Lilac Purple', 'Red', 'Mole', 'Orange', 'Metal', 'Brown', 'Turquoise', 'Yellow', 'Khaki green', 'Green', 'undefined', 'Unknown', 'Yellowish Green', 'Bluish Green']
        selected_color_master_names = st.sidebar.multiselect("Colors", color_master_names, default='All')

        # Filter articles DataFrame based on the selected options
        if selected_garment_group != "All":
            articles_df = articles_df[articles_df["garment_group_name"] == selected_garment_group]
        if 'All' not in selected_color_master_names:
            articles_df = articles_df[articles_df["perceived_colour_master_name"].isin(selected_color_master_names)]

        # Display filtered articles data without the index column
        st.write(articles_df)

        # ----------------------------- KPIs -----------------------------

        # Calculate and display article KPIs
        total_products = articles_df['product_code'].nunique()
        avg_perceived_colour_value = articles_df['perceived_colour_value_id'].mean()

        # Group the filtered DataFrame by index_group_name and count the occurrences
        top_index_group_names = articles_df['index_group_name'].value_counts()

        # Sort the counts in descending order and get the top 3 index_group_name
        top_3_index_group_names = top_index_group_names.head(3)

        # Create a list of strings with the top 3 index_group_name
        top_3_index_group_names_list = [f"{cat}" for cat in top_3_index_group_names.index]

        # Calculate the total number of products with the top 3 index_group_name
        total_top_3_products = top_3_index_group_names.sum()

        # Calculate the percentage change compared to the total number of products
        percentage_change = (total_top_3_products / total_products - 1) * 100

        # KPIs
        st.subheader("KPIs")
        kpi1, kpi2 = st.columns(2)
        kpi1.metric(
            label="Unique Products",
            value=total_products,
            delta="updated automatically"
        )

        kpi2.metric(
            label="Average Perceived Colour Value",
            value=avg_perceived_colour_value,
            delta="updated automatically"
        )

        # Calculate the most common product type in the filtered DataFrame
        most_common_product_type = articles_df['product_type_name'].mode()[0]

        # Calculate the occurrences of the most common product type in the filtered DataFrame
        occurrences = len(articles_df[articles_df['product_type_name'] == most_common_product_type])

        # KPIs continued
        kpi3, kpi4 = st.columns(2)

        kpi3.metric(
            label="Top 3 Index Groups",
            value="",
            delta=f"{percentage_change:.2f}%"
        )

        kpi4.metric(
            label="Most Common Product Type",
            value=most_common_product_type,
            delta=f"Occurrences: {occurrences}"
        )

        # Display the index group names one below the other
        for name in top_3_index_group_names_list:
            kpi3.write(name)

        # ----------------------------- Charts -----------------------------
            
        # Load transactions data
        transactions_df = load_data(API_URL_TRANSACTIONS)

        # Merge transactions and articles data
        merged_transactions_articles = pd.merge(transactions_df, articles_df, on='article_id')

        # Group articles by garment group name and count the number of articles in each group
        articles_by_garment_group = articles_df["garment_group_name"].value_counts().reset_index()
        articles_by_garment_group.columns = ["garment_group_name", "count"]

        st.subheader("Charts")

        # Create a bar chart
        fig = go.Figure(go.Bar(
            x=articles_by_garment_group["garment_group_name"],
            y=articles_by_garment_group["count"],
            marker_color='red'
        ))

        # Customize the chart
        fig.update_layout(
            title="Number of Articles per Garment Group",
            xaxis_title="Garment Group",
            yaxis_title="Number of Articles",
            plot_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(
                family="Arial, sans-serif",
                size=14,
                color="black"
            )
        )

        # Display the chart
        st.plotly_chart(fig)

        # Calculate the revenue per article category
        revenue_per_category = merged_transactions_articles.groupby('index_group_name')['price'].sum()

        # Add a new subheader for the bar chart
        st.subheader("Revenue per Article Category")

        # Create a bar chart of revenue per article category
        fig, ax = plt.subplots()
        ax.bar(revenue_per_category.index, revenue_per_category.values, color='red')
        ax.set_xlabel('Article Category')
        ax.set_ylabel('Revenue')
        st.pyplot(fig)

        # Make sure to have the filtered DataFrame: articles_df
        product_counts_by_group = articles_df['product_group_name'].value_counts()

        # Create a treemap chart using Plotly
        fig = px.treemap(
            names=product_counts_by_group.index,
            parents=[""] * len(product_counts_by_group),
            values=product_counts_by_group.values,
            title="Number of Products in Each Product Group",
            labels={"names": "Product Group", "values": "Count"},
        )

        # Display the treemap chart
        st.plotly_chart(fig)

    # ------------------------------------------------------------------------------------------------------------------------
    #                                                       TRANSACTIONS
    # ------------------------------------------------------------------------------------------------------------------------

    elif selected_tab == "Transactions":
        st.title('Transactions')

        # Load transactions data
        transactions_df = load_data(API_URL_TRANSACTIONS)

        # Reorder columns
        column_order = [
            't_dat', 'customer_id', 'article_id', 'price', 'sales_channel_id'
        ]
        transactions_df = transactions_df[column_order]

        # Convert t_dat to datetime
        transactions_df['t_dat'] = pd.to_datetime(transactions_df['t_dat'])

        # ----------------------------- Filters -----------------------------
        st.sidebar.title("Filters")

        # Date filter
        min_date = pd.to_datetime("2018-09-20")
        max_date = pd.to_datetime("2018-10-01")
        date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

        # Price range filter
        min_price, max_price = transactions_df['price'].min(), transactions_df['price'].max()
        price_range = st.sidebar.slider("Price Range", float(min_price), float(max_price), [float(min_price), float(max_price)])

        # Create a dictionary to map sales_channel_id to the corresponding label
        sales_channel_labels = {
            1: "online",
            2: "offline"
        }

        # Replace the sales_channel_id with the corresponding labels
        transactions_df['sales_channel_label'] = transactions_df['sales_channel_id'].map(sales_channel_labels)

        # Sales channel filter
        sales_channels = transactions_df['sales_channel_label'].unique()
        selected_sales_channels = st.sidebar.multiselect("Sales Channels", options=sales_channels, default=sales_channels)

        # Apply filters
        filtered_transactions = transactions_df[
            (transactions_df['t_dat'] >= pd.to_datetime(date_range[0])) &
            (transactions_df['t_dat'] <= pd.to_datetime(date_range[1])) &
            (transactions_df['price'] >= price_range[0]) &
            (transactions_df['price'] <= price_range[1]) &
            (transactions_df['sales_channel_label'].isin(selected_sales_channels))
        ]

        # Display filtered transactions data without the index column
        st.write(filtered_transactions)

        # ----------------------------- KPIs -----------------------------
        total_revenue = filtered_transactions['price'].sum()
        average_price = filtered_transactions['price'].mean()
        repeat_customers = filtered_transactions['customer_id'].value_counts()
        repeat_customers = repeat_customers[repeat_customers > 1].sum()

        st.subheader("KPIs")
        kpi1, kpi2, kpi3 = st.columns(3)

        kpi1.metric(
            label="Total Revenue",
            value=f"${total_revenue:,.2f}"
        )
        kpi2.metric(
            label="Average Price",
            value=f"${average_price:.2f}"
        )
        kpi3.metric(
            label="Repeat Customers",
            value=repeat_customers
        )

        # Load customers data
        customers_df = load_data(API_URL_CUSTOMERS)

        # Merge transactions and customers data
        merged_data = pd.merge(filtered_transactions, customers_df, on='customer_id')

        # ----------------------------- Charts -----------------------------
        st.subheader("Charts")
        st.write("Sales Channel-wise Sum of Prices")

        sales_channel_sums = filtered_transactions.groupby('sales_channel_id')['price'].sum()
        sales_channel_sums.index = sales_channel_sums.index.map(sales_channel_labels)

        fig, ax = plt.subplots()
        ax.bar(sales_channel_sums.index, sales_channel_sums.values, color='red')
        ax.set_xlabel('Sales Channel')
        ax.set_ylabel('Sum of Prices')
        st.pyplot(fig)

        st.write("Trend of Prices over Time")
        transactions_by_date = filtered_transactions.groupby('t_dat')['price'].sum()

        fig, ax = plt.subplots()
        ax.plot(transactions_by_date.index, transactions_by_date.values, color='red')
        ax.set_xlabel('Transaction Date')
        ax.set_ylabel('Sum of Prices')
        st.pyplot(fig)

        # Sales Channel-wise Percentage
        sales_channel_count = filtered_transactions['sales_channel_id'].value_counts()

        # Create the colormap
        red_shades = mcolors.LinearSegmentedColormap.from_list("red_shades", ["lightcoral", "red", "darkred"], N=len(sales_channel_count))

        # Generate the list of colors from the colormap
        colors = [red_shades(i) for i in range(len(sales_channel_count))]

        # Create the pie chart with the list of colors
        fig, ax = plt.subplots()
        ax.pie(sales_channel_count, labels=sales_channel_count.index.map(sales_channel_labels), autopct='%1.1f%%', colors=colors)
        ax.set_title('Sales Channel-wise Percentage')
        st.pyplot(fig)

        fig, ax = plt.subplots()
        ax.scatter(merged_data['age'], merged_data['price'], c='red')
        ax.set_title('Relationship between Price and Customer Age')
        ax.set_xlabel('Customer Age')
        ax.set_ylabel('Price')
        st.pyplot(fig)

    # Thank you for reading until the end!