import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt
import base64
from streamlit_extras.no_default_selectbox import selectbox
from pathlib import Path

st.set_page_config(page_title="Used Car Analysis and Price Prediction", 
                    page_icon=":bar_chart:",
                    layout="wide")

# -----PROCESSING BACKGROUND IMAGE-----
@st.experimental_memo
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("images/17580.jpg")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] >.main {{
background-image: url("data:old-cars/jpg:;base64,{img}");
background-size: cover;
background-attachment: local;
}}

[data-testid="stHeader] {{
background: rgba(0,0,0,0.1);
}}
</style>
"""

font_css = """
<style>
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
  font-size: 22px;
  font-weight: 600;
}
</style>
"""

st.write(page_bg_img, unsafe_allow_html=True)

st.write(font_css, unsafe_allow_html=True)
# -----END OF PROCESSING BACKGROUND IMAGE -----

# ----- LOAD DATA -----
df = pd.read_csv('cars.csv')

# -----MAIN APP-----
st.header(":bar_chart: Used Cars Analysis and Prediction")

listTabs = [
    "Visualization Dashboard",
    "Price Prediction",
    "PandasAI"
]

whitespace=9
tab1, tab2, tab3 = st.tabs([s.center(whitespace) for s in listTabs])
# tab1, tab2, tab3 = st.tabs([s.center(whitespace,"\u2001") for s in listTabs])

# ----- 
with tab1:
    # FILTER 
    ##Top 10 Manufacturers by count
    top_10_makes = (
        df['Make'].value_counts().head(10).rename_axis('Make').reset_index(name='count').sort_values(by='count')
    )
    # Create list of 10 makes by frequency
    list_top_makes = top_10_makes['Make'].to_list()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        make = st.selectbox(
        "Manufacturer:",
        list_top_makes
    )

    with col2:
        body = st.selectbox(
        "Body:",
        df['Body'].unique()
    )
        
    with col3:
        year_range = st.slider("Year range:", 
        value = (int(df['Year'].min()), int(df['Year'].max())),
        min_value=int(df['Year'].min()), max_value=int(df['Year'].max()),
        step=1
        )

    with col4:
        price_range = st.slider("Price range:", 
        value = (int(df['Price'].min()), int(df['Price'].max())),
        min_value=int(df['Price'].min()), max_value=int(df['Price'].max()),
        step=1
        )

    df_selection = df.query("(Make == @make) and (Body == @body)")

    # st.divider()

    ##-----TOP KPIs-----##
    average_driven = int(df_selection['Mileage (km)'].mean())

    average_price = int(df_selection['Price'].mean())

    min_price = int(df_selection['Price'].min())
    max_price = int(df_selection['Price'].max())

    count_of_cars = int(len(df_selection))

    g_df = df_selection.groupby(['Make', 'Model']).size().sort_values(ascending=False).reset_index(name="count")

    top_make = g_df.iloc[0]['Make']
    top_model = g_df.iloc[0]['Model']

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with st.container():
        with col1:
            st.write("##### Average Mileage:")
            st.write(f"##### {average_driven:,} km")

        with col2:
            st.write("##### Number of Cars:")
            st.write(f"##### {count_of_cars}")

        with col3:
            st.write("##### Average Price:")
            st.write(f"##### GHC {average_price:,}")

        with col4:
            st.write("##### Lowest Price:")
            st.write(f"##### GHC {min_price:,}")

        with col5:
            st.write("##### Highest Price:")
            st.write(f"##### GHC {max_price:,}")

        with col6:
            st.write("##### Popular Make and Model:")
            st.write(f"##### {top_make} {top_model}")

    st.markdown("---")

    ##-----CHARTS-----##

    ##Top 10 Manufacturers by count
    top_10_makes = (
        df['Make'].value_counts().head(10).rename_axis('Make').reset_index(name='count').sort_values(by='count')
    )
    # Create list of 10 makes by frequency
    list_top_makes = top_10_makes['Make'].to_list()

    # create dataframe on only top 10 makes
    top_df = df[df['Make'].isin(list_top_makes)]

    avg_make_price = top_df['Price'].groupby(top_df['Make']).mean()

    # Plot the average price per year as a line chart
    fig = px.bar(avg_make_price, 
                 title = "<b> Average Price per top 10 manufacurers </b>", 
                 color_discrete_sequence=["#003399"],
                 template='plotly_white')

    fig_makes = px.bar(
        top_10_makes,
        x="count",
        y="Make",
        orientation="h",
        title="<b> Top 10 Car Manufacturers by Frequency</b>",
        color_discrete_sequence=["#003399"] * len(top_10_makes),
        template="plotly_white",
    )

    ## Line Chart - Average car price per year
    year = df_selection['Year']
    price = df_selection['Price']

    avg_price = price.groupby(year).mean()
    avg_price.index.name = 'Year'

    # Plot the average price per year as a line chart
    price_per_year = px.line(
        avg_price, 
        title = "<b> Average Price of Cars manufactured in each year </b>", 
        color_discrete_sequence=["#003399"],
        template='plotly_white')

    ## Scatter plot - Price vs Mileage
    scat_miles = px.scatter(df_selection, 
                            x='Price', 
                            y='Mileage (km)', 
                            title = "<b> Mileage(km) vs Price (GHC) </b>",
                            color_discrete_sequence=["#003399"],
                            template="plotly_white"
                            )

    # Scatter plot - Price vs Horse Power
    scat_hp = px.scatter(df_selection, 
                            x='Price', 
                            y='Horse Power', 
                            title = "<b> Horse Power vs Price (GHC) </b>",
                            color_discrete_sequence=["#003399"],
                            template="plotly_white"
                        )

    # ## Scatter plot - Price vs Engine Size
    # scat_engine = px.scatter(df_selection, 
    #                         x='Price', 
    #                         y='Engine Size (l)', 
    #                         title = "<b> Horse Power vs Price (GHC) </b>",
    #                         template="plotly_white"
    #                         )


    # grouped = df_selection.groupby(['Make', 'Model', 'Year'])
    # # Calculate the average price and mileage for each make, model, and year
    # avg_price = grouped['Price'].mean()
    # avg_mileage = grouped['Mileage (km)'].mean()

    # avg_price_list = list(avg_price)
    # avg_mileage_list = list(avg_mileage)

    # Create a Plotly figure
    # fig_idk = px.line(
    #             avg_mileage_list, 
    #             x='Price', 
    #             y='Mileage', 
    #             title='Average Price and Mileage of Used Cars Over Time')

    # # Plot the figure
    # st.plotly_chart(fig_idk)

    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig_makes, use_container_width=True)
    right_column.plotly_chart(fig, use_container_width=True)

    left2, right2, mid2 = st.columns(3)
    left2.plotly_chart(price_per_year, use_container_width=True, )
    right2.plotly_chart(scat_miles, use_container_width=True)
    mid2.plotly_chart(scat_hp, use_container_width=True)

with tab2:
    st.write("##### Coming Soon...")

with tab3:
    st.write("##### Coming Soon...")