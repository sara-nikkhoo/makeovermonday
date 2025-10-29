import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
#import plotly.express as px


data = pd.read_excel('data.xlsx', engine='openpyxl')

data.fillna(0, inplace=True)
#st.write(data.columns)

# Rename columns based on the specified pattern
new_columns = {}
for col in data.columns:
    if ',' in col and '|' in col:
        new_columns[col] = col.split(',')[1].split('|')[0].strip()

data.rename(columns=new_columns, inplace=True)

###

st.set_page_config(layout="wide")
# Add a colored background for the title
st.markdown("""
    <style>
    .title-container {
        background-color: #f0f8ff;
        padding: 10px;
        border-radius: 5px;
    }
    .title-container h1 {
        color: navy;
        text-align: center;
    }
    </style>
    <div class="title-container">
        <h1>More Meat, More Impact: Environmental Awareness and Sustainable Diets in Germany</h1>
    </div>
""", unsafe_allow_html=True)


data_germany = data[data['Entity'] == 'Germany']

# Separate 'beef and buffalo' and 'Poultry' columns into individual series
data_germany_be_pou = data_germany[['Year','beef and buffalo' , 'poultry']]
data_germany_be_pou.rename(columns={'beef and buffalo': 'Beef'}, inplace=True)


# Create an Altair line chart

chart = alt.Chart(data_germany_be_pou).transform_fold(
    ['Beef', 'poultry'],
    as_=['Type', 'Production']
).mark_line().encode(
    x=alt.X('Year:Q',
            axis=alt.Axis(title=None,
                            labelAngle=0, tickCount=10, format='d'
            ),
    ),
    y=alt.Y('Production:Q',
            axis=None
            )
    ,
    color=alt.Color('Type:N',scale=alt.Scale(range=['#b92028','#f1ddb6']),legend=None)
).properties(
    #title='Beef and Poultry Production in Germany',
    width=6500,
    height=400
)

## maximum vale between 1960-2023 and circle it
max_beef = data_germany_be_pou['Beef'].max()    
max_pou = data_germany_be_pou['poultry'].max()
st_year_beef = data_germany_be_pou.loc[data_germany_be_pou['Beef'] == max_beef, 'Year'].values[0]
st_year_pou = data_germany_be_pou.loc[data_germany_be_pou['poultry'] == max_pou, 'Year'].values[0]



# Create a DataFrame for maximum points
chart_max_beff_pou = alt.Chart(pd.DataFrame({
    'Type': ['Beef', 'poultry'],    
    'Max Production': [max_beef, max_pou],
    'Year': [st_year_beef, st_year_pou]})).mark_circle(size=250, color='navy').encode(
    y=alt.Y('Max Production:Q'),
    x=alt.X('Year:Q', axis=alt.Axis(format="d", tickCount=10, labelAngle=0)),
    #color=alt.Color('Type:N',scale=alt.Scale(range=['gray','gray']),legend=None)
    )



# Create a DataFrame for reasons why beef production has decreased

df_context = pd.DataFrame({'text' : [' Why has beef production decreased in recent years?',
                            '1. Environmental concerns?', 
                            '2. Diet shifts?', 
                            '3. Economic factors?'],
                           'y': [0,1,2,3]})
 

context = alt.Chart(df_context).mark_text(fontSize=15, align='left', dy=10, dx=-0).encode(
    x = alt.value(0),
    y = alt.Y('y:O', axis=alt.Axis(title=None, ticks=False, domain=False, labels=False)),
    text = 'text',
    stroke = alt.condition(alt.datum.y == 0, alt.value('#b92028'), alt.value('grey')),
    strokeWidth = alt.condition(alt.datum.y == 0, alt.value(1), alt.value(0)
 )
)

### Highlight lines and area between them


stroke_line = chart.mark_line(
    strokeWidth=6
).transform_filter(
    ((alt.datum.Type == 'Beef')) & 
    (alt.datum.Year <= 2008) 
)

stroke_line_pou = chart.mark_line(
    strokeWidth=7
).transform_filter(
    ((alt.datum.Type == 'poultry')) & 
    (alt.datum.Year >= 2008) 
)



# Area between Beef and Poultry

data_2008 = data_germany_be_pou[data_germany_be_pou['Year'] <= 2008]
data_after_2008 = data_germany_be_pou[data_germany_be_pou['Year'] >= 2008]  

# Create a new DataFrame with Year, Poultry production, and Beef production
df_production_2008 = pd.DataFrame({
    'Year': data_2008['Year'],
    'y1': data_2008['poultry'],
    'y2': data_2008['Beef']
})

df_production_after_2008 = pd.DataFrame({
    'Year': data_after_2008['Year'],
    'y1': data_after_2008['poultry'],
    'y2': data_after_2008['Beef']
})




fill_between = alt.Chart(df_production_2008).mark_area(opacity=0.1, color="#b92028").encode(
    x=alt.X("Year:Q", axis=alt.Axis(format="d", tickCount=10, labelAngle=0)),
    y="y1:Q",
    y2="y2:Q"
)

fill_between_after_2008 = alt.Chart(df_production_after_2008).mark_area(opacity=0.5, color="#f1ddb6").encode(
    x=alt.X("Year:Q", axis=alt.Axis(format="d", tickCount=10, labelAngle=0)),
    y="y2:Q",
    y2="y1:Q"
)

vertical_line = alt.Chart(pd.DataFrame({'Year': [2008]})).mark_rule(
    strokeDash=[5, 5],
    color='gray'
).encode(
    x='Year:Q'
)

text_2008 = alt.Chart(pd.DataFrame({'Year': [2008], 'label': ['2008']})).mark_text(
    align='left',
    baseline='bottom',
    dx=-32,
    dy=-160,
    color='gray',
    fontSize=13,
    fontWeight='bold'
).encode(
    x='Year:Q',
    text='label:N'
)

text_beef = alt.Chart(pd.DataFrame({'Year': [1960], 'label': ['Beef']})).mark_text(
    align='left',  
    baseline='bottom',
    dx=-30,
    dy=-15,
    color='#b92028',
    fontSize=17,
    fontWeight='bold'
).encode(
    x='Year:Q',
    text='label:N'
)

text_pou = alt.Chart(pd.DataFrame({'Year': [1960], 'label': ['poultry']})).mark_text(
    align='left',
    baseline='bottom',
    dx=-50,   
    dy=178,
    color='#f1ddb6',
    fontSize=17,
    fontWeight='bold'
).encode(
    x='Year:Q', 
    text='label:N'
)


# Melt the data_germany_be_pou 
data_melted = data_germany_be_pou.melt(id_vars=['Year'], 
                                       value_vars=['Beef', 'poultry'], 
                                       var_name='Type', 
                                       value_name='Production')

                                    # Add million production columns to data_melted
data_melted['Million_Production'] = data_melted['Production'] / 1e6
data_melted['text'] = data_melted['Million_Production'].apply(lambda x: f"{x:.1f}M")

# Add text labels for the year 2023
text_production = alt.Chart(data_melted).mark_text(
    align='left',   
    baseline='bottom',
    dx=3,   
    dy=5,
    color='gray',
    fontSize=16,
    #fontWeight='bold'
).encode(
    x='Year:Q',
    y=alt.Y('Production:Q'),
    text='text:N',
).transform_filter(
     (alt.datum.Year == 2023
) 
)  
# Add text labels for the maximum production points
# Get max rows for each meat type
max_rows = data_melted.loc[data_melted.groupby("Type")["Production"].idxmax()]

# Now create the text chart just from these rows
text_max_beef_pou = alt.Chart(max_rows).mark_text(
    align='left',
    baseline='bottom',
    dx=2,
    dy=-8,
    color='navy',
    fontSize=15,
    fontWeight='bold'
).encode(
    x='Year:Q',
    y='Production:Q',
    text='text:N',
    #color=alt.Color('Type:N', legend=None) 
)

# Create a DataFrame for water usage per kilogram of meat
water_usage_data = pd.DataFrame({
    'Meat Type': ['Beef', 'Pork', 'Poultry'],
    'Water Usage (liters/kg)': [15415, 6000, 4300]
})
# Add x and y coordinates to water usage data for positioning circles
water_usage_data['x'] = [1, 1.4, 1.4]
water_usage_data['y'] = [1, 0.35, 1.4]
# Create a circle mark chart for water usage data
water_usage_chart = alt.Chart(water_usage_data).mark_circle(color='#3ea4f0').encode(
    x=alt.X('x:Q', axis=None),
    y=alt.Y('y:Q', axis=None),
    size=alt.Size('Water Usage (liters/kg):Q', scale=alt.Scale(range=[1000, 70000]), legend=None),
    #color=alt.value('#add8e6'),
    stroke=alt.value('#5d97e7'),
    tooltip=['Meat Type', 'Water Usage (liters/kg)']
).properties(
    #title='Water Usage per Kilogram of Meat',
    width=600,
    height=400
)

water_usage_text = alt.Chart(water_usage_data).mark_text(
    align='left',
    baseline='middle',
    dx=-20,
    fontSize=17,
    color='white',
).encode(
    x='x:Q',
    y='y:Q',
    text='Meat Type:N'
)

# spacer between title and first chart
st.markdown("<br>", unsafe_allow_html=True)  # Add a space 
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)



#----------------------------------------------------- Display -----------------------------------------------------#

col1, col2, col3 = st.columns([1,3,1])
with col2:
    total_chart = (context & (chart + stroke_line + stroke_line_pou + fill_between + fill_between_after_2008 + vertical_line +
                text_2008 + text_pou + text_beef + text_production + chart_max_beff_pou + text_max_beef_pou)
                ).configure_view(
                    strokeWidth=0
                ).configure_axis(
                    grid=False
                ).configure_title(
                    fontSize=20,
                    anchor='start',
                    color='navy'
                )
    st.altair_chart(total_chart, use_container_width=True)



st.markdown("<br>", unsafe_allow_html=True)  # Add a space 
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


col4, col5, col6 = st.columns([2,2,1])
with col4:
    st.markdown("<br>", unsafe_allow_html=True)  # Add a space 
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Water Usage per Kilogram of Meat")
    st.markdown("""
The chart shows large differences in <b style='color:blue;font-weight: 700; font-size: 22px'>water</b> use for meat production. 
Beef requires about <b style='color:red; font-weight: 700; font-size: 19px'>15,415</b> liters of water per kilogram, 
while pork and poultry need around <b style='color:orange; font-weight: 700; font-size: 19px'>6,000</b> and <b style='color:green;font-weight: 700; font-size: 19px'>4,300</b> liters. 
This highlights the impact of meat choices and the importance of sustainable diets for saving water.
""", unsafe_allow_html=True)
with col5:
    water_usage = water_usage_chart + water_usage_text
    st.altair_chart(water_usage, use_container_width=True)

##----------------------------------------------------- Greenhous Emission -----------------------------------------------------#
    # Create a DataFrame for greenhouse gas emissions per kilogram of meat
    ghg_emissions_data = pd.DataFrame({
        'Meat Type': ['Beef', 'Pork', 'Poultry'],
        'GHG Emissions (kg CO2e/kg)': [30, 12.1, 6.9]
    })
    # Add x and y coordinates to greenhouse gas data for positioning circles
    #ghg_emissions_data['x'] = [0, 1.1, 1.1]
    #ghg_emissions_data['y'] = [.8, 0.35, 1.2]

    ghg_emissions_data['x'] = [0, -4, 4]
    ghg_emissions_data['y'] = [.8, 0.7, .7]

    # Create a circle mark chart for greenhouse gas emissions data
    ghg_emissions_chart = alt.Chart(ghg_emissions_data).mark_circle(color="#fc7f68").encode(
        x=alt.X('x:Q', axis=None),
        y=alt.Y('y:Q', axis=None),
        size=alt.Size('GHG Emissions (kg CO2e/kg):Q', scale=alt.Scale(range=[1000, 70000]), legend=None),
        stroke=alt.value('#e55347'),
        tooltip=['Meat Type', 'GHG Emissions (kg CO2e/kg)']
    ).properties(
        width=500,
        height=350
    )

    ghg_emissions_text = alt.Chart(ghg_emissions_data).mark_text(
        align='left',
        baseline='middle',
        dx=-20,
        fontSize=17,
        color='white',
    ).encode(
        x='x:Q',
        y='y:Q',
        text='Meat Type:N'
    )


st.markdown("<br>", unsafe_allow_html=True)  # Add a space 
st.markdown("<br>", unsafe_allow_html=True)


col7, col8, col9, col10 = st.columns([1.7,.3, 2, .4])
with col9:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Greenhouse Gas Emissions per Kilogram of Meat")
        st.markdown("""
    The chart illustrates the <b style='color:#b5b3b3;font-weight: 700; font-size: 22px'>greenhouse gas emissions</b> associated with meat production. 
    Beef generates approximately <b style='color:red; font-weight: 700; font-size: 19px'>30</b> kg CO2e per kilogram, 
    while pork and poultry produce around <b style='color:orange; font-weight: 700; font-size: 19px'>12.1</b> and <b style='color:green;font-weight: 700; font-size: 19px'>6.9</b> kg CO2e, respectively. 
    This highlights the environmental impact of meat production and the need for sustainable dietary choices.
    """, unsafe_allow_html=True)
with col7:
        ghg_emissions = ghg_emissions_chart + ghg_emissions_text
        st.altair_chart(ghg_emissions, use_container_width=True)





st.markdown("<br>", unsafe_allow_html=True)  # Add a space between title and first chart
