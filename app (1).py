import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import altair as alt
from streamlit_option_menu import option_menu
import base64
from reportlab.pdfgen import canvas
from io import BytesIO

# Define a style for Garamond-Bold font with color and font size
garamond_bold_style = "font-family: Garamond, sans-serif; font-weight: bold; color: red; font-size: 30px;"
garamond_bold_style2 = "font-family: Garamond, sans-serif; font-weight: bold; color: white; font-size: 25px;"

data = pd.read_csv("/content/cleaned_zomato_dataset.csv")

def generate_pdf_report(country_name, insights, chart_data=None):
    buffer = BytesIO()

    # Create a PDF document
    pdf = canvas.Canvas(buffer)

    # Add content to the PDF
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, 750, f"Report for {country_name}")  # Adjust x-coordinate to move title to the left

    pdf.setFont("Helvetica", 14)
    y_position = 720

    # Adjust spacing between title and insights
    y_position -= 20

    for insight in insights:
        pdf.drawString(50, y_position, f"- {insight}")  # Adjust x-coordinate to move insights to the left
        y_position -= 50  # Adjust the vertical spacing between insights



    # Save the PDF to the buffer
    pdf.save()

    # Set the buffer position to the beginning
    buffer.seek(0)

    return buffer

def get_download_link_pdf(file_buffer, file_name):
    base64_encoded = base64.b64encode(file_buffer.read()).decode()
    href = f'<a href="data:application/pdf;base64,{base64_encoded}" download="{file_name}.pdf">Download PDF Report</a>'
    return href

def generate_country_report(data):
    country_name = data['Country'].iloc[0]

    # Add your country-specific analysis or insights here
    top_restaurants = data.groupby(['Restaurant Name', 'Cuisines'])['Aggregate rating'].mean().reset_index().sort_values(by='Aggregate rating', ascending=False).head(5)

    # Simulate chart data for demonstration
    chart_data = {'data': [10, 20, 15], 'labels': ['Category A', 'Category B', 'Category C']}


    # Extract city-specific data for additional insights
    selected_city = st.selectbox(f'Select City in {country_name}:', ['All'] + sorted(data['City'].unique().tolist()))

    if selected_city != 'All':
        city_data = data[data['City'] == selected_city]

        # Top costliest restaurant in the selected city
        top_costliest_restaurant_city = city_data.groupby(['Restaurant Name'])['Average Cost for two'].mean().idxmax()

        insights = [
            f"Top 5 Restaurants: {', '.join(top_restaurants['Restaurant Name'])}",
            f"Top 5 Cuisines: {', '.join(top_Cuisines(data, criteria='Votes'))}",
            f"Costliest Restaurant in {country_name}: {costliest_restaurant_country(data)}.",
            f"Costliest Restaurant in {selected_city}: {top_costliest_restaurant_city}.",
            f"{city_spending_more_on_online_delivery(data)}",
            f"{city_spending_more_on_dine_in(data)}",
            f"Number of Restaurants providing Zomato Service in {country_name}: {num_restaurants_providing_zomato_service(data)}.",
            f"{city_high_cost_of_living(data)} is high in the cost of living in {country_name}.",
            f"{city_low_cost_of_living(data)} is low in the cost of living in {country_name}.",

        
        ]
        
        
        

        # Download Button for PDF
        st.markdown(f"""
        ## Download {country_name} Report
        - Click the button below to download the {country_name} report in PDF format.
        """)

        # Create a button to download the PDF report
        download_button_text = f"Download {country_name} Report (PDF)"
        if st.button(download_button_text):
            # Generate PDF report with a simulated bar chart
            pdf_buffer = generate_pdf_report(country_name, insights, chart_data)

            # Provide a download link for the user
            st.markdown(get_download_link_pdf(pdf_buffer, country_name), unsafe_allow_html=True)
            
def top_Cuisines(data, criteria='Votes', top_n=5):
    top_cuisines = data.sort_values(by=criteria, ascending=False).head(top_n)
    return top_cuisines['Cuisines'].tolist()

def city_spending_more_on_online_delivery(data):
    online_delivery_spending = data.groupby('City')['Has Online delivery'].value_counts().unstack().fillna(0)

    city = None  # Set a default value
    try:
        city = online_delivery_spending['Yes'].idxmax()
        return f"In {data['Country'].iloc[0]}, {city} spends more on online food delivery."
    except KeyError:
        return f"There is an equal amount of Cities spending currency on online deliver."

def city_spending_more_on_dine_in(data):
    dine_in_spending = data.groupby('City')['Has Table booking'].value_counts().unstack().fillna(0)

    city = None  # Set a default value
    try:
        city = dine_in_spending['Yes'].idxmax()
        return f"In {data['Country'].iloc[0]}, {city} spends more on dine-in."
    except KeyError:
        return f"There is an equal amount of Cities spending currency on online dine booking."

    
def costliest_restaurant_country(data):
    costliest_restaurant_country = data.loc[data['Average Cost for two'].idxmax()]
    return costliest_restaurant_country['Restaurant Name']

def num_restaurants_providing_zomato_service(data):
    return data['Restaurant Name'].nunique()

def city_high_cost_of_living(data):
    living_cost_comparison = data.groupby('City')['Average Cost for two'].mean().sort_values(ascending=False)
    city = living_cost_comparison.index[0]
    return f"{city}"

def city_low_cost_of_living(data):
    living_cost_comparison = data.groupby('City')['Average Cost for two'].mean().sort_values(ascending=True)
    city = living_cost_comparison.index[0]
    return f"{city}"


# Main Streamlit function
def main():
    st.set_page_config(
        page_title="Zomato Data Analysis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "About": "<h1 style='" + garamond_bold_style + "'>About:</h1> Enjoy this  interactive dashboard is created for user-friendly data visualization."
        }
    )

    st.markdown(f"<h1 style='{garamond_bold_style}'>Zomato Analysis Dashboard</h1>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<h2 style='{garamond_bold_style2}'>Hello, Welcome !!!</h2>", unsafe_allow_html=True)

    # Load the image with PIL
    image_path = "/content/zomato.jpg"
    pil_image = Image.open(image_path)

    # Specify the image width
    image_width = 800

    # Display the PIL image with the specified width
    st.image(pil_image, width=image_width)

    with st.sidebar:
        selected = option_menu("Menu", ["Home","Charts","Report"],
                    icons=["house","graph-up-arrow","file"],
                    menu_icon= "menu-button-wide",
                    default_index=0,
                    styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "#6F36AD"},
                            "nav-link-selected": {"background-color": "#eb1328"}})

    if selected == 'Home':
        st.markdown("<h1 style='" + garamond_bold_style + "'>Certainly! Zomato is a popular online food delivery and restaurant discovery platform that operates in numerous countries around the world. It provides users with a comprehensive database of restaurants, cafes, and eateries, along with menus, reviews, and ratings. Users can explore a wide range of cuisines, place orders for food delivery, and make reservations at restaurants through the platform.</h1>", unsafe_allow_html=True)

        st.markdown("<h1 style='" + garamond_bold_style + "'>Restaurant Discovery:</h1>", unsafe_allow_html=True)
        st.markdown("<p style='" + garamond_bold_style2 + "'>Zomato helps users discover new dining options based on location, cuisine preferences, and user reviews.</p>", unsafe_allow_html=True)

        st.markdown("<h1 style='" + garamond_bold_style + "'>Menu Information:</h1>", unsafe_allow_html=True)
        st.markdown("<p style='" + garamond_bold_style2 + "'> The platform provides detailed menus for listed restaurants, helping users make informed decisions about their food choices.</p>", unsafe_allow_html=True)

        st.markdown("<h1 style='" + garamond_bold_style + "'>User Reviews and Ratings:</h1>", unsafe_allow_html=True)
        st.markdown("<p style='" + garamond_bold_style2 + "'>Zomato allows users to rate and review restaurants, contributing to a dynamic and transparent feedback system.</p>", unsafe_allow_html=True)

        st.markdown("<h1 style='" + garamond_bold_style + "'>Online Food Delivery:</h1>", unsafe_allow_html=True)
        st.markdown("<p style='" + garamond_bold_style2 + "'>Users can order food online for home delivery from a wide array of restaurants partnered with Zomato.</p>", unsafe_allow_html=True)

        st.markdown("<h1 style='" + garamond_bold_style + "'>Table Reservations: </h1>", unsafe_allow_html=True)
        st.markdown("<p style='" + garamond_bold_style2 + "'>Zomato offers a reservation service, allowing users to book tables at their favorite restaurants in advance.</p>", unsafe_allow_html=True)

        st.markdown("<h1 style='" + garamond_bold_style + "'>Location-Based Services:</h1>", unsafe_allow_html=True)
        st.markdown("<p style='" + garamond_bold_style2 + "'>The platform utilizes location services to provide personalized restaurant recommendations and delivery options based on the user's geographical location.</p>", unsafe_allow_html=True)

        st.markdown("<h1 style='" + garamond_bold_style + "'>For further details click on Charts 👈.</h1>", unsafe_allow_html=True)


    if selected == 'Charts':
        selected_country = st.selectbox('Select Country:', ['All'] + sorted(data['Country'].unique().tolist()))

        # Filter the data based on the selected country
        if selected_country != 'All':
            filtered_data = data[data['Country'] == selected_country]
        else:
            filtered_data = data  # Show all data if 'All' is selected
            
        fig = px.scatter_mapbox(filtered_data, 
                        lat='Latitude', 
                        lon='Longitude', 
                        #color='Average Cost for two', 
                        hover_data=['Country', 'Restaurant Name', 'Address'],
                        zoom=2,  # Adjust the zoom level
                        mapbox_style="white-bg",
                        color_discrete_map={'Average Cost for two': '#0AFB02'} 
                        )

        fig.update_layout(
            title='Scatter Plot on Map', 
            mapbox=dict(
                style="white-bg",
                layers=[
                    {
                        "below": 'traces',
                        "sourcetype": "raster",
                        "sourceattribution": "United States Geological Survey",
                        "source": [
                            "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                        ]
                    }
                ],
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            autosize=True,
            height=500,
            width=800  # Set the width parameter here
        )

        st.plotly_chart(fig)
    

        # Display the filtered data
        #st.write(filtered_data)

        if selected_country == 'India':
            # Display costliest cuisines in India
            costliest_cuisines = filtered_data.groupby('Cuisines')['Cost in INR'].mean().sort_values(ascending=False)
            st.markdown("<h1 style='" + garamond_bold_style + "'>Top 10 Costliest Cuisines in India</h1>", unsafe_allow_html=True)
            st.write(costliest_cuisines)

            # Create a bar chart for costliest cuisines with different colors
            chart = px.bar(
                    costliest_cuisines, 
                    x=costliest_cuisines.index, 
                    y='Cost in INR', 
                    labels={'x': 'Cuisine', 'y': 'Cost in INR'},
                    title='Top 10 Costliest Cuisines in India in bar chart',
                    color='Cost in INR',  # Use 'Average Cost for two' for coloring
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    width=1600,  # Adjust the width
                    height=800   # Adjust the height
                )

            st.plotly_chart(chart, use_container_width=True)

            # Display count of cities in India
            city_count = filtered_data['City'].nunique()
            st.markdown(f"<h1 style='{garamond_bold_style2}'>Number of Cities in India: {city_count}</h1>", unsafe_allow_html=True)

            # Comparison between cities in India
            if st.checkbox('Comparison between Cities in India'):
                st.subheader('Comparison between Cities in India')

                # Filter data for cities in India
                india_data = filtered_data[filtered_data['Country'] == 'India']

                # Online delivery spending
                st.markdown("<h1 style='" + garamond_bold_style + "'>Online Delivery Spending</h1>", unsafe_allow_html=True)
                online_delivery_spending = india_data.groupby('City')['Has Online delivery'].value_counts().unstack().fillna(0)
                st.bar_chart(online_delivery_spending['Yes'])
                st.markdown("<p style='" + garamond_bold_style2 + "'>In India, New Delhi spends more on online food delivery.</h1>", unsafe_allow_html=True)

                # Dine-in spending
                st.markdown("<h1 style='" + garamond_bold_style + "'>Dine-in Spending</h1>", unsafe_allow_html=True)
                dine_in_spending = india_data.groupby('City')['Has Table booking'].value_counts().unstack().fillna(0)
                st.bar_chart(dine_in_spending['Yes'])
                st.markdown("<p style='" + garamond_bold_style2 + "'>In India, New Delhi spends more on dine-in.</h1>", unsafe_allow_html=True)

                # Living cost comparison
                st.markdown("<h1 style='" + garamond_bold_style + "'>Living Cost Comparison</h1>", unsafe_allow_html=True)
                living_cost_comparison = india_data.groupby('City')['Cost in INR'].mean().sort_values(ascending=False)
                st.bar_chart(living_cost_comparison)
                st.markdown("<p style='" + garamond_bold_style2 + "'>Panchkula is high in the cost of living. Faridabad is low in the cost of living.</h1>", unsafe_allow_html=True)
        
            
        # Display count of cities in the selected country
        Restaurant_Name_count = filtered_data['Restaurant Name'].nunique()
        st.markdown(f"<h1 style='{garamond_bold_style}'>Number of Restaurants providing Zomato Service in  {selected_country}: {Restaurant_Name_count}</h1>", unsafe_allow_html=True)

        # Display restaurants with the top aggregate rating, cuisines, and rating
        top_restaurants = filtered_data.groupby(['Restaurant Name', 'Cuisines'])['Aggregate rating'].mean().reset_index().sort_values(by='Aggregate rating', ascending=False).head(15)
        # Create a bar chart using Altair
        chart = alt.Chart(top_restaurants).mark_bar().encode(
            x='Aggregate rating:Q',
            y=alt.Y('Restaurant Name:N', sort='-x'),
            color='Cuisines:N',
            tooltip=['Restaurant Name', 'Cuisines', 'Aggregate rating']
            ).properties(
                width=600
            )

        # Display the chart
        st.altair_chart(chart, use_container_width=True)


        if selected_country != 'All':
            selected_city = st.selectbox('Select City:', ['All'] + sorted(filtered_data['City'].unique().tolist()))

            if selected_city != 'All':
                # Filter data based on the selected city
                city_data = filtered_data[filtered_data['City'] == selected_city]

                # Display famous cuisines with the help of votes
                famous_cuisines = city_data.groupby(['Restaurant Name', 'Cuisines'])['Votes'].sum().sort_values(ascending=False)
                st.markdown(f"<h1 style='{garamond_bold_style}'>Famous Cuisines in {selected_city} based on Votes</h1>", unsafe_allow_html=True)
                st.write(famous_cuisines)

                # Display costlier cuisine in that city
                costlier_cuisine_city = city_data.groupby(['Restaurant Name', 'Cuisines', 'Cost in INR', 'Currency'])['Average Cost for two'].mean().sort_values(
                    ascending=False)
                st.markdown(f"<h1 style='{garamond_bold_style}'>Costliest Cuisine in {selected_city}</h1>", unsafe_allow_html=True)
                st.write(costlier_cuisine_city)

                # Display rating count in that city with restaurant name
                rating_count_city = city_data.groupby(['Rating text', 'Restaurant Name']).size().reset_index(name='Count')
                st.markdown(f"<h1 style='{garamond_bold_style}'>Rating Count in {selected_city} with Restaurant Name</h1>", unsafe_allow_html=True)
                st.write(rating_count_city)

                # Display pie chart for Has Table booking vs Has Online delivery
                booking_delivery_counts = city_data['Has Table booking'].value_counts()
                online_delivery_counts = city_data['Has Online delivery'].value_counts()

                # Create a DataFrame for the pie chart
                pie_chart_df = pd.DataFrame({
                    'Category': ['Table Booking - Yes', 'Table Booking - No', 'Online Delivery - Yes', 'Online Delivery - No'],
                    'Count': [
                        booking_delivery_counts.get('Yes', 0),
                        booking_delivery_counts.get('No', 0),
                        online_delivery_counts.get('Yes', 0),
                        online_delivery_counts.get('No', 0)
                    ]
                })

                # Display the counts
                st.markdown(f"<h1 style='{garamond_bold_style}'>Online Table Booking vs Online Delivery in {selected_city}</h1>", unsafe_allow_html=True)
                st.write(pie_chart_df)

                # Display the pie chart
                st.plotly_chart(px.pie(pie_chart_df, names='Category', values='Count', title=f"Online Table Booking vs Online Delivery in {selected_city}"), use_container_width=True)


    # Country-wise Reports
    if selected == 'Report':
        st.header("Country-wise Reports")

        # Get the selected country for the report
        selected_country_for_report = st.selectbox('Select Country for Report:', ['All'] + sorted(data['Country'].unique().tolist()))

        if selected_country_for_report != 'All':
            # Filter data based on the selected country
            country_data_for_report = data[data['Country'] == selected_country_for_report]

            # Generate report for the selected country
            generate_country_report(country_data_for_report)


if __name__ == "__main__":
    main()
        
        