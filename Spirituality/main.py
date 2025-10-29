
import numpy as np  
import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import os
import altair as alt    
import base64
import plotly.express as px

##style
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, white 50%,  black 50%) !important;
.chart-container {
    display: flex;
    justify-content: flex-end; 
    align-items: center;

</style>
""", unsafe_allow_html=True)



def load_data():
    # Load the dataset
    data_path = 'data.csv'
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        return df
    else:
        st.error("Data file not found.")
        return None


df = load_data()    


## Continent
# mapping dictionary
continent_map = {
    "Argentina": "South America",
    "Brazil": "South America",
    "Chile": "South America",
    "Colombia": "South America",
    "Peru": "South America",
    "Canada": "North America",
    "Mexico": "North America",
    "U.S.": "North America",
    "Australia": "Asia-Pacific",
    "Bangladesh": "Asia-Pacific",
    "India": "Asia-Pacific",
    "Indonesia": "Asia-Pacific",
    "Israel": "Asia-Pacific",
    "Japan": "Asia-Pacific",
    "Malaysia": "Asia-Pacific",
    "Philippines": "Asia-Pacific",
    "Singapore": "Asia-Pacific",
    "South Korea": "Asia-Pacific",
    "Sri Lanka": "Asia-Pacific",
    "Thailand": "Asia-Pacific",
    "Turkey": "Asia-Pacific",
    "France": "Europe",
    "Germany": "Europe",
    "Greece": "Europe",
    "Hungary": "Europe",
    "Italy": "Europe",
    "Netherlands": "Europe",
    "Poland": "Europe",
    "Spain": "Europe",
    "Sweden": "Europe",
    "UK": "Europe",
    "Ghana": "Africa",
    "Kenya": "Africa",
    "Nigeria": "Africa",
    "South Africa": "Africa",
    "Tunisia": "Africa"
}

# add continent column
df["Continent"] = df["Country"].map(continent_map)

##  Rename columns with new names
if df is not None:
    new_column_names = {
        "Are religiously affiliated": "religious",
        "Say there is definitely/probably life after death": "life_after_death",
        "Say that parts of nature can have spirits or spiritual energies": "spirits_nature",
        "Say they pray at least daily": "pray_daily",
        "Say they consult a fortune teller, horoscope or other way to see the future": "fortune_teller"
        # Add more mappings as needed
    }
    df.rename(columns=new_column_names, inplace=True)

## Data preparation
 
df_continent = df.groupby('Continent')[["life_after_death",'religious', "spirits_nature", "pray_daily", "fortune_teller"]].mean().reset_index()
df_continent['rel_percentage'] = (df_continent['religious']).round(0).astype(int).astype(str) + '%'
df_continent['rel_explaination'] = 'Identify with a religion'

df_continent['afterlife_percentage'] = (df_continent['life_after_death']).round(0).astype(int).astype(str) + '%'
df_continent['afterlife_explaination'] = 'Believe in life after death'

df_continent['spirits_percentage'] = (df_continent['spirits_nature']).round(0).astype(int).astype(str) + '%'
df_continent['spirits_explaination'] = 'Believe in spirits in nature'

df_continent['pray_percentage'] = (df_continent['pray_daily']).round(0).astype(int).astype(str) + '%'
df_continent['pray_explaination'] = 'Pray at least daily'

df_continent['fortune_percentage'] = (df_continent['fortune_teller']).round(0).astype(int).astype(str) + '%'
df_continent['fortune_explaination'] = 'Consult a fortune teller'

# Data for the radial chart 

min_radius = 60    
max_radius = 90   
outer_dash = 100 

values = df['religious']
n_points = len(values)  # Number of data points


radius = min_radius + (values - (values.min()-3)) * \
         (max_radius - min_radius) / (values.max() - (values.min()-3))

# Generate angles 
angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)

# DataFrame for solid lines
df_solid = pd.DataFrame({
    'Country': df['Country'],
    'x1': min_radius * np.cos(angles),
    'y1': min_radius * np.sin(angles),
    'x2': radius * np.cos(angles),
    'y2': radius * np.sin(angles)
})

# data for country label 

df_sorted = df.sort_values(by='religious', ascending=False)
top3 = df_sorted.head(3)
bottom3 = df_sorted.tail(3)
df_labels = pd.concat([top3, bottom3])


df_dash = pd.DataFrame({
    'Country': df_labels['Country'],
    'x1': radius * np.cos(angles),
    'y1': radius * np.sin(angles),
    'x2': outer_dash * np.cos(angles),
    'y2': outer_dash * np.sin(angles)
})

solid_lines = alt.Chart(df_solid).mark_line(stroke='#D3AF37', strokeWidth=2).encode(
    x=alt.X('x1', scale=alt.Scale(domain=[-outer_dash, outer_dash]), axis=None),
    y=alt.Y('y1', scale=alt.Scale(domain=[-outer_dash, outer_dash]), axis=None),
    x2='x2',
    y2='y2',
    tooltip=alt.Tooltip('Country', title='Country')
)

dash_lines = alt.Chart(df_dash).mark_line(stroke='gray', strokeWidth=1, strokeDash=[4, 4]).encode(
    x=alt.X('x1', scale=alt.Scale(domain=[-outer_dash, outer_dash])),
    y=alt.Y('y1', scale=alt.Scale(domain=[-outer_dash, outer_dash])),
    x2='x2',
    y2='y2',
  
)


## image
def get_image_base64(path):
    with open(path, "rb") as f:
        data_pic = f.read()
    return base64.b64encode(data_pic).decode()

image_base64 = get_image_base64("pic1.png")

# Create a dummy chart with image as background
image_chart = alt.Chart(pd.DataFrame({'x': [0], 'y': [0]})).mark_image(
    url=f"data:image/png;base64,{image_base64}",
    width=3.5*min_radius,   
    height=3.5*min_radius,
    
).encode(
    x=alt.X('x', scale=alt.Scale(domain=[-outer_dash, outer_dash]), axis=None),
    y=alt.Y('y', scale=alt.Scale(domain=[-outer_dash, outer_dash]), axis=None)
)




chart = (( image_chart + solid_lines )).properties(background='transparent', width=450, height=450
                                                   ).configure_axis(
    grid=False, domain=False, labels=False, ticks=False
).configure_mark(tooltip=None
).configure_view(
    stroke=None,  # Remove border
    #fill='#f0f0f0'  # Set background color
)

##style 
with st.container(key='title'):
    st.header("Religion and Spirituality Around the World", divider="gray")
    st.markdown("""
Data comes from a <span style='color:#debd68'>Pew Research Center</span> survey conducted in 
2023 and 2024.
""", unsafe_allow_html=True)
    

st.markdown(
    """
     <span style="color:white; font-size: 12px; margin-top:-60px; float:right; margin-right: -390px; ">
        Hover over the lines to see the country names </span>
        <hr style="height:1px;border:none;background-color:#d36428 ;width:230px; margin-top:-42px; margin-right:-390px; float:right;">
    
    """,
    unsafe_allow_html=True
)




col1, col2 = st.columns(2)
with col2:
    box_sun = st.container(key="chart1")
    with box_sun:
        st.altair_chart(chart, use_container_width=False)


# radio buttons
with st.container(key="explain"):
        st.markdown('<span style="color:black; font-size: 28px; margin-left:-380px; margin-top:300px;">Belief in God isn’t the same everywhere.</span>', unsafe_allow_html=True)
        st.markdown(
            '<span style="color:black; font-size: 24px; margin-left:-380px; margin-top:10px;">It is </span>'
            '<span style="color:navy; font-size: 24px;">lower in wealthier nations</span>'
            '<span style="color:black; font-size: 24px;">, but remains </span>'
            '<span style="color:#c5a34f; font-size: 24px;">strong in developing regions.</span>',
            unsafe_allow_html=True
        )
options = ['Belief in God','Life after death', 'Spirits in nature', 'Daily prayer', 'Fortune telling/Horoscope'] 
with col1:
    box_title = st.container(key="title2")
    with box_title:
        selected_option = st.radio('Highlight', options, key='radio', horizontal=False, index=0, label_visibility="visible")



st.markdown("""
<style>
.st-key-explain {
    margin-top: -400px;
    font-weight: 600
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
.st-key-hover {
    text-align:right;
    margin-top: -80px;
    width:100%;   
    
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
.st-key-chart1 {
    margin-left: 100px;
    margin-top: -50px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.st-key-title {
    margin-left: -380px;
    margin-top: 0px;
   
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.st-key-title2 {
    display: inline-block;
    margin-left: -370px;
    margin-top: 320px;
   
}
</style>
""", unsafe_allow_html=True)
  


option_map = {
    'Belief in God': {
        'value': 'religious',
        'percentage': 'rel_percentage',
        'explaination': 'rel_explaination'
    },
    'Life after death': {
        'value': 'life_after_death',
        'percentage': 'afterlife_percentage',
        'explaination': 'afterlife_explaination'
    },
    'Spirits in nature': {
        'value': 'spirits_nature',
        'percentage': 'spirits_percentage',
        'explaination': 'spirits_explaination'
    },
    'Daily prayer': {
        'value': 'pray_daily',
        'percentage': 'pray_percentage',
        'explaination': 'pray_explaination'
    },
    'Fortune telling/Horoscope': {
        'value': 'fortune_teller',
        'percentage': 'fortune_percentage',
        'explaination': 'fortune_explaination'
    }
}

col_map = option_map[selected_option]
temp_df = df_continent.copy()
## second part


sorting_grouped = df_continent.sort_values('religious', ascending=False)
continent_order = sorting_grouped['Continent'].tolist()

bars = alt.Chart(df_continent).mark_bar(size=50, tooltip=None).encode(
    x=alt.X('religious:Q', 
            axis=alt.Axis(tickMinStep = 1,
                          grid=False, 
                          title=None, 
                          #orient='bottom',
                           tickCount=6,
                         
                        )),
    y=alt.Y('Continent:N',sort=continent_order, axis=None, ),

    color=alt.Color(
    'Continent:N',
    scale=alt.Scale(
        domain=["Africa","Asia-Pacific","South America","North America","Europe"],  
        range=['#af9146', '#c5a34f', '#dbb658', '#debd68', '#e2c479']  ),  
    legend=None
    
    #color=alt.Color('type:N', scale=color_scale, legend=None),
    
)
).properties(
    width=580,
    height=370,
   
)


# Add text labels to the bars
text = alt.Chart(df_continent).mark_text(
    align='left',
    baseline='middle',
    dy=0,
    dx=0,
    fontSize=25,
    color='white'
).encode(
    x=alt.value(20),
    y=alt.Y('Continent:N', axis=None, sort=continent_order),
    text='Continent:N'
)




text_percentage = alt.Chart(temp_df).mark_text(
    align='left', baseline='middle', dx=6, fontSize=23, color='navy', font='Josefin Sans'
).encode(
    x=alt.X("religious:Q", axis=None),
    y=alt.Y('Continent:N', axis=None, sort=continent_order),
    text=f"{col_map['percentage']}:N"
)

text_explaination = alt.Chart(temp_df).mark_text(
    align='left', baseline='middle', dx=50, dy=5, fontSize=11, color='black', font='Arial'
).encode(
    x=alt.X("religious:Q", axis=None),
    y=alt.Y('Continent:N', axis=None, sort=continent_order),
    text=f"{col_map['explaination']}:N"
)

# --- Add circles if other option selected ---
line_ = None
if selected_option != 'Belief in God':
    metric = option_map[selected_option]
    line_ = alt.Chart(temp_df).mark_bar(size=40, color='white').encode(
        x=f"{col_map['value']}:Q",
        y=alt.Y('Continent:N', sort=continent_order),
        color=alt.value('rgba(0, 0, 0, 0.25)')
    )
    

bar_chrt = bars + text + text_percentage + text_explaination
if line_:
    bar_chrt = bar_chrt + line_

bar_chrt = bar_chrt.configure_mark(
    tooltip=None  
).configure_view(
    stroke=None,  # Remove border
    #fill='transparent'  # Set background color to transparent
).configure(background="transparent") 




# Tree map chart



col_map = option_map[selected_option]

value_col = col_map['value']
percentage_col = col_map['percentage']
explain_col = col_map['explaination']


# --- Tree Map ---
tree_map = px.treemap(
    df,
    path=['Continent', 'Country'],
    values=value_col,
    color=value_col,
    color_continuous_scale=["navy", "#76b9ee", "#c5a34f"]
)

tree_map.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=0, t=0, b=0),
    height=430, width=450
)

tree_map.update_traces(
    marker=dict(colorscale=["navy", "#76b9ee", "#c5a34f"], line=dict(width=0)),
    tiling=dict(pad=4),
    branchvalues='total',
    root_color="rgba(0,0,0,0)"
)
tree_map.data[0].marker.pad = dict(t=0, l=0, r=0, b=0)

# Remove treemap background rectangles
tree_map.update_traces(root_color="rgba(0,0,0,0)")
tree_map.data[0].marker.pad = dict(t=0, l=0, r=0, b=0)

##chart with style
col4, col5 = st.columns([1, 2.2])
with col4:
    box_left = st.container(key="barchart")
    with box_left:
        st.altair_chart(bar_chrt, use_container_width=False)

with col5:
    box_right = st.container(key="treemap")
    with box_right:
        st.plotly_chart(tree_map, use_container_width=True)

st.markdown("""
<style>
.st-key-barchart {
    margin-left: -370px;
    margin-top: -100px;
    
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.st-key-treemap {
    margin-left: 270px;
    fill: None !important;
    margin-top: -140px;
    
}
</style>
""", unsafe_allow_html=True)

##
#st.write(continent_order)  # Display the first 10 rows of the DataFrame
