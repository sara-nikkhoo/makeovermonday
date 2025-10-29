import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

import kagglehub

# Download latest version
path = kagglehub.dataset_download("sahilislam007/ai-impact-on-job-market-20242030")

# Load data
data = pd.read_csv(path + "/ai_job_trends_dataset.csv")


# Set Streamlit background color
st.markdown(
    """
    <style>
    .stApp {
        background-color: #151a40;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.set_page_config(layout="wide")
# Display title
st.title("AI Impact on Job Market (2024-2030)")
st.markdown(
    "<span style='color:white'>This is a synthetic dataset generated using realistic modeling, public job data patterns (U.S. BLS, OECD, McKinsey, WEF reports).</span>",
    unsafe_allow_html=True
)


# Apply white color to the title
st.markdown(
    """
    <style>
    .stApp h1 {
        color: #efa500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

## Calculate job difference
data['job_diff'] = data['Projected Openings (2030)'] - data['Job Openings (2024)'] 

industry_ = data['Industry'].unique()

## high AI impact difference

# Transform data for multi-line chart

highimpact_data = data[data['AI Impact Level'] == 'High']
highlight_data_col = highimpact_data[['Job Title', 'Job Openings (2024)', 'Projected Openings (2030)','Job Status', 'job_diff']]


it_data_melted = highlight_data_col.melt(
    id_vars=['Job Title', 'Job Status'],   # ✅ keep Job Status     
    value_vars=['Job Openings (2024)', 'Projected Openings (2030)'],
    var_name='Year',
    value_name='Number of Jobs'
)

it_mean_jobs_by_year = it_data_melted.groupby('Year')['Number of Jobs'].mean().reset_index().round(0)
it_mean_jobs_by_year['Year'] = it_mean_jobs_by_year['Year'].map({
    'Job Openings (2024)': 2024,
    'Projected Openings (2030)': 2030
})
# Display the results


# Select jobs with the most positive growth
top_positive_growth = highlight_data_col.nlargest(4, 'job_diff')
max_growth = top_positive_growth.head(1)['Job Title'].values[0]

# Select jobs with the most negative growth
top_negative_growth = highlight_data_col.nsmallest(4, 'job_diff')
min_growth = top_negative_growth.head(1)['Job Title'].values[0]
# Select 100 random data points from it_data_col
random_sample = highlight_data_col.sample(n=70, random_state=42)



# Combine the two into a single DataFrame
growth_data = pd.concat([top_positive_growth.reset_index(drop=True), top_negative_growth.reset_index(drop=True)], keys=['Positive Growth', 'Negative Growth'])
growth_data = pd.concat([growth_data.reset_index(drop=True), random_sample.reset_index(drop=True)], keys=['Growth Data', 'Random Sample'])
#growth_data = growth_data.reset_index(drop=True)

# Melt the DataFrame for Altair
growth_data_melted = growth_data.melt(
    id_vars=['Job Title', 'Job Status'],   # ✅ keep Job Status
    value_vars=['Job Openings (2024)', 'Projected Openings (2030)'],
    var_name='Year',
    value_name='Number of Jobs'
)


# Map year names to actual years
growth_data_melted['Year'] = growth_data_melted['Year'].map({
    'Job Openings (2024)': 2024,
    'Projected Openings (2030)': 2030
})


growth_data_melted["Highlight"] = growth_data_melted["Job Title"].apply(
    lambda x: "Most Positive Growth" if x == max_growth else 
              ("Most Negative Growth" if x == min_growth else "Other")
)


# Display altair line chart for high AI impact jobs
base = alt.Chart(growth_data_melted).encode(
    x=alt.X('Year:O', title=None),
    y='Number of Jobs:Q',
    detail='Job Title:N',
    tooltip=['Job Title', 'Year', 'Number of Jobs']
).transform_filter(
    alt.datum.Highlight == "Other"
)  # Filter to exclude highlighted jobs when creating the base chart and most positive/negative growth lines (not used currently)

base_lines = base.mark_line(color="lightgray", strokeWidth=1)
#base_points = base.mark_point(color="white", size=60, filled=True)


# Additional highlight for increasing jobs in green (not used currently)
increasing_highlight = alt.Chart(growth_data_melted).mark_line(size=1).encode(
    x="Year:O",
    y="Number of Jobs:Q",
    detail="Job Title:N",
     color=alt.Color(
        "Job Status:N",
        scale=alt.Scale(
            domain=["Increasing", "Decreasing"],
            range=["#41b853", 'lightgray']  # Green for increasing, None for decreasing"]
        ),
        legend=None
    ),

    tooltip=['Job Title', 'Year', 'Number of Jobs', 'Job Status']
)

high_ai_mean_job_chart = alt.Chart(it_mean_jobs_by_year).mark_line(color='#41b853', size=5).encode(
    x='Year:O',
    y='Number of Jobs:Q',
    tooltip=['Year', 'Number of Jobs']
)

# Add vertical dashed line at 2030(not used currently)
vertical_line = alt.Chart(pd.DataFrame({'Year': [2030]})).mark_rule(
    #strokeDash=[5, 5],
    color='gray'
).encode(
    x='Year:O',
    size=alt.value(2),
    y=alt.value(-150),
    y2=alt.value(100)
) 

# mean text
mean_text_2030 = high_ai_mean_job_chart.mark_text(
    align='left',
    baseline='middle',
    dx=5,
    dy=0,
    color='#41b853',
    fontSize=16,
    fontWeight='bold'
).encode(
    x=alt.X('Year:O', title=None),
    y=alt.Y('Number of Jobs:Q', title=None),
    text=alt.Text('Number of Jobs:Q', format=',.0f')
).transform_filter(
    alt.datum.Year == 2030
)

mean_text_2024 = high_ai_mean_job_chart.mark_text(
    align='left',
    baseline='middle',
    dx=-45,
    dy=0,
    color='#41b853',
    fontSize=16,
    fontWeight='bold'
).encode(
    x=alt.X('Year:O', title=None),
    y=alt.Y('Number of Jobs:Q', title=None),
    text=alt.Text('Number of Jobs:Q', format=',.0f')
).transform_filter(
    alt.datum.Year == 2024
)
# Combine both
line_chart = (base_lines + high_ai_mean_job_chart + mean_text_2024 + mean_text_2030).properties(
    #width=400,
    height=450,
    background='transparent'
).configure_view(
    strokeWidth=0,
    fill='transparent'
).configure_axis(
    grid=False
)



st.markdown('<br></br>', unsafe_allow_html=True)
#st.markdown('<br></br>', unsafe_allow_html=True)

col1, col2, col3,col4,col5 = st.columns([1, 0.05, 1, 0.05, 1])
with col1:
    st.markdown(
    "<span style='color:white; font-size: 15px'>Jobs with</span> <span style='color:#f40058; font-size: 18px, font-weight: bolder'>High AI Impact</span> <span style='color:white; font-size: 15px'>(2024-2030),</span> <span style='color:#41b853; font-size: 15px'>average trend line</span> <span style='color:white; font-size: 15px'>vs individual job trends.</span>",
    unsafe_allow_html=True
)
    st.markdown('<br></br>', unsafe_allow_html=True)

    st.altair_chart(line_chart, use_container_width=True)
    
with col2:
    st.markdown(
    """
    <div style="
        border-left: 2px solid #43bee5;
        height: 570px;
        margin-left: -50px;  
        margin-top: -20px;    
        position: relative;  /* allows positioning control */
    ">
    </div>
    """,
    unsafe_allow_html=True
)
    
##---------------------------------------- moderate AI impact jobs -------------------------------------------------

moderate_impact_data = data[data['AI Impact Level'] == 'Moderate']
moderate_data_col = moderate_impact_data[['Job Title', 'Job Openings (2024)', 'Projected Openings (2030)','Job Status', 'job_diff']]


moderate_data_melted = moderate_data_col.melt(
    id_vars=['Job Title', 'Job Status'],   # ✅ keep Job Status     
    value_vars=['Job Openings (2024)', 'Projected Openings (2030)'],
    var_name='Year',
    value_name='Number of Jobs'
)

moderate_mean_jobs_by_year = moderate_data_melted.groupby('Year')['Number of Jobs'].mean().reset_index().round(0)
moderate_mean_jobs_by_year['Year'] = moderate_mean_jobs_by_year['Year'].map({
    'Job Openings (2024)': 2024,
    'Projected Openings (2030)': 2030
})
# Display the results

# Select  random data points from it_data_col
random_sample_moderate = moderate_data_col.sample(n=70, random_state=42)

# Melt the DataFrame for Altair
random_sample_moderate = random_sample_moderate.melt(
    id_vars=['Job Title', 'Job Status'],   # ✅ keep Job Status
    value_vars=['Job Openings (2024)', 'Projected Openings (2030)'],
    var_name='Year',
    value_name='Number of Jobs'
)


# Map year names to actual years
random_sample_moderate['Year'] = random_sample_moderate['Year'].map({
    'Job Openings (2024)': 2024,
    'Projected Openings (2030)': 2030
})



# Display altair line chart for high AI impact jobs
base_moderate = alt.Chart(random_sample_moderate).encode(
    x=alt.X('Year:O', title=None),
    y='Number of Jobs:Q',
    detail='Job Title:N',
    tooltip=['Job Title', 'Year', 'Number of Jobs']
)
base_lines_moderate = base_moderate.mark_line(color="lightgray", strokeWidth=1)
#base_points = base.mark_point(color="white", size=60, filled=True)




moderate_ai_mean_job_chart = alt.Chart(moderate_mean_jobs_by_year).mark_line(color='#41b853', size=5).encode(
    x='Year:O',
    y='Number of Jobs:Q',
    tooltip=['Year', 'Number of Jobs']
)


# mean text
mean_text_2030_moderate = moderate_ai_mean_job_chart.mark_text(
    align='left',
    baseline='middle',
    dx=5,
    dy=0,
    color='#41b853',
    fontSize=16,
    fontWeight='bold'
).encode(
    x=alt.X('Year:O', title=None),
    y=alt.Y('Number of Jobs:Q', title=None, axis=None),
    text=alt.Text('Number of Jobs:Q', format=',.0f')
).transform_filter(
    alt.datum.Year == 2030
)

mean_text_2024_moderate = moderate_ai_mean_job_chart.mark_text(
    align='left',
    baseline='middle',
    dx=-45,
    dy=0,
    color='#41b853',
    fontSize=16,
    fontWeight='bold'
).encode(
    x=alt.X('Year:O', title=None),
    y=alt.Y('Number of Jobs:Q', title=None),
    text=alt.Text('Number of Jobs:Q', format=',.0f')
).transform_filter(
    alt.datum.Year == 2024
)
# Combine both
line_chart_moderate = (base_lines_moderate + moderate_ai_mean_job_chart + mean_text_2024_moderate + mean_text_2030_moderate).properties(
    #width=400,
    height=450,
    background='transparent'
).configure_view(
    strokeWidth=0,
    fill='transparent'
).configure_axis(
    grid=False
)



st.markdown('<br></br>', unsafe_allow_html=True)

with col3:
    st.markdown(
    "<span style='color:#f40058; font-size: 18px, font-weight: bolder; display: flex; justify-content: center'>Moderate AI Impact</span>",
    unsafe_allow_html=True
)
    st.markdown('<br></br>', unsafe_allow_html=True)

    st.altair_chart(line_chart_moderate, use_container_width=True)

##---------------------------------------- low AI impact jobs -------------------------------------------------

low_impact_data = data[data['AI Impact Level'] == 'Low']
low_data_col = low_impact_data[['Job Title', 'Job Openings (2024)', 'Projected Openings (2030)','Job Status', 'job_diff']]


low_data_melted = low_data_col.melt(
    id_vars=['Job Title', 'Job Status'],   # ✅ keep Job Status     
    value_vars=['Job Openings (2024)', 'Projected Openings (2030)'],
    var_name='Year',
    value_name='Number of Jobs'
)

low_mean_jobs_by_year = low_data_melted.groupby('Year')['Number of Jobs'].mean().reset_index().round(0)
low_mean_jobs_by_year['Year'] = low_mean_jobs_by_year['Year'].map({
    'Job Openings (2024)': 2024,
    'Projected Openings (2030)': 2030
})
# Display the results

# Select  random data points from it_data_col
random_sample_low = low_data_col.sample(n=70, random_state=42)

# Melt the DataFrame for Altair
random_sample_low = random_sample_low.melt(
    id_vars=['Job Title', 'Job Status'],   # ✅ keep Job Status
    value_vars=['Job Openings (2024)', 'Projected Openings (2030)'],
    var_name='Year',
    value_name='Number of Jobs'
)


# Map year names to actual years
random_sample_low['Year'] = random_sample_low['Year'].map({
    'Job Openings (2024)': 2024,
    'Projected Openings (2030)': 2030
})



# Display altair line chart for high AI impact jobs
base_low = alt.Chart(random_sample_low).encode(
    x=alt.X('Year:O', title=None),
    y='Number of Jobs:Q',
    detail='Job Title:N',
    tooltip=['Job Title', 'Year', 'Number of Jobs']
)
base_lines_low = base_low.mark_line(color="lightgray", strokeWidth=1)
#base_points = base.mark_point(color="white", size=60, filled=True)




low_ai_mean_job_chart = alt.Chart(low_mean_jobs_by_year).mark_line(color='#41b853', size=5).encode(
    x='Year:O',
    y='Number of Jobs:Q',
    tooltip=['Year', 'Number of Jobs']
)


# mean text
mean_text_2030_low = low_ai_mean_job_chart.mark_text(
    align='left',
    baseline='middle',
    dx=5,
    dy=0,
    color='#41b853',
    fontSize=16,
    fontWeight='bold'
).encode(
    x=alt.X('Year:O', title=None),
    y=alt.Y('Number of Jobs:Q', title=None, axis=None),
    text=alt.Text('Number of Jobs:Q', format=',.0f')
).transform_filter(
    alt.datum.Year == 2030
)

mean_text_2024_low = low_ai_mean_job_chart.mark_text(
    align='left',
    baseline='middle',
    dx=-45,
    dy=0,
    color='#41b853',
    fontSize=16,
    fontWeight='bold'
).encode(
    x=alt.X('Year:O', title=None),
    y=alt.Y('Number of Jobs:Q', title=None),
    text=alt.Text('Number of Jobs:Q', format=',.0f')
).transform_filter(
    alt.datum.Year == 2024
)
# Combine both
line_chart_low = (base_lines_low + low_ai_mean_job_chart + mean_text_2024_low + mean_text_2030_low).properties(
    #width=400,
    height=450,
    background='transparent'
).configure_view(
    strokeWidth=0,
    fill='transparent'
).configure_axis(
    grid=False
)



st.markdown('<br></br>', unsafe_allow_html=True)

with col4:
    st.markdown(
    """
    <div style="
        border-left: 2px solid #43bee5;
        height: 570px;
        margin-left: -10px;  
        margin-top: -20px;    
        position: relative;  /* allows positioning control */
    ">
    </div>
    """,
    unsafe_allow_html=True
)

with col5:
    st.markdown(
    "<span style='color:#f40058; font-size: 20px, font-weight: bolder; display: flex; justify-content: center'>Low AI Impact</span>",
    unsafe_allow_html=True
)
    st.markdown('<br></br>', unsafe_allow_html=True)

    st.altair_chart(line_chart_low, use_container_width=True)


##---------------------------------------- Average job openings by industry -------------------------------------------------
#st.markdown('<br></br>', unsafe_allow_html=True)
average_job_industry = data.groupby('Industry').agg({
    'Job Openings (2024)': 'sum',
    'Projected Openings (2030)': 'sum'
}).reset_index().round(0).sort_values(by='Job Openings (2024)', ascending=True)
average_job_industry['dif_percent'] = (((average_job_industry['Projected Openings (2030)'] - average_job_industry['Job Openings (2024)']) / average_job_industry['Job Openings (2024)']) * 100).round(1)

# Bar chart for job for trends by industry

dif_sort = average_job_industry.sort_values('dif_percent', ascending=False)
dif_order = dif_sort['Industry'].tolist()

bar_chart = alt.Chart(average_job_industry).mark_bar(size=20, tooltip=None, color='white').encode(
    x=alt.X('dif_percent:Q', axis=None),
    y=alt.Y('Industry:N', sort=dif_order, title=None),
    color=alt.condition(
        alt.datum.dif_percent > 0,
        alt.value('#41b853'),  # Green for positive growth
        alt.value('#f40058')   # Red for negative growth
    ),
)
average_job_industry['dif_percent_label'] = average_job_industry['dif_percent'].apply(lambda x: f"{x:.1f}%")


dif_percent_text_negative = alt.Chart(average_job_industry).mark_text(
    align='right',
    baseline='middle',
    dx=5,
    dy=0,
    color='white',
    fontSize=14,
    #fontWeight='bold'
).encode(
    x=alt.value(150),
    y=alt.Y('Industry:N', sort=dif_order, title=None),
    text=alt.Text('dif_percent_label:N')
).transform_filter(
    alt.datum.dif_percent <= 0
)

dif_percent_text_positive = alt.Chart(average_job_industry).mark_text(
    align='left',   
    baseline='middle',
    dx=5,
    dy=0,
    color='white',
    fontSize=14,
    #fontWeight='bold'
).encode(
    x=alt.X('dif_percent:Q', axis=None),
    y=alt.Y('Industry:N', sort=dif_order, title=None),
    text=alt.Text('dif_percent_label:N')
).transform_filter(
    alt.datum.dif_percent > 0
)
#----add explanatory text
explain_text_inc = alt.Chart(average_job_industry).mark_text(
    align='left',   
    baseline='middle',
    dx=40,
    dy=7,
    color='#efa500',
    fontSize=16,
    #fontWeight='bold'
).encode(
    x=alt.X('dif_percent:Q', axis=None),
    y=alt.Y('Industry:N', sort=dif_order, title=None),
    text=alt.value("Increase in job openings from 2024 to 2030" +  "  _ ")
).transform_filter(
    alt.datum.dif_percent == 2.8
)

explain_text_dec = alt.Chart(average_job_industry).mark_text(
    align='right',   
    baseline='middle',
    dx=12,
    dy=7,
    color='#efa500',
    fontSize=16,
    #fontWeight='bold'
).encode(
    x=alt.value(438),
    y=alt.Y('Industry:N', sort=dif_order, title=None),
    text=alt.value("Decrease in job openings from 2024 to 2030")
).transform_filter(
    alt.datum.dif_percent == -0.5
)
#---- Combine bar chart and text
bar_chart = (bar_chart + dif_percent_text_positive + dif_percent_text_negative + explain_text_inc + explain_text_dec).properties(
    width=550,
    height=300,
    background='transparent'
).configure_view(
    strokeWidth=0,
    fill='transparent'
).configure_axis(
    grid=False
)
col10, col11,col12 = st.columns([2, .25, 1.5])
with col10:
    st.markdown('<br></br>', unsafe_allow_html=True)
    st.altair_chart(bar_chart, use_container_width=True)
#st.write(average_job_industry)


with col12:
    st.markdown('<br></br>', unsafe_allow_html=True)
    st.markdown('<br></br>', unsafe_allow_html=True)
    
    st.markdown(
    """
    <span style='color:white; font-size: 15px'>
    The bar chart illustrates the percentage change in job openings across various industries from 2024 to 2030. 
    Positive values (green bars) indicate industries with projected growth, while negative values (red bars) highlight industries expected to decline.
    </span>
    """,
    unsafe_allow_html=True
)
#---------------------------------------- most decrease in projected -------------------------------------------------
data['job_diff_%'] = ((data['Projected Openings (2030)'] - data['Job Openings (2024)']) / data['Job Openings (2024)']).round(1) * 100


jobtitle_agg = data.groupby('Job Title').agg({
    'Job Openings (2024)': 'sum',
    'Projected Openings (2030)': 'sum'
}).reset_index().round(0).sort_values(by='Job Openings (2024)', ascending=True)
jobtitle_agg['dif_percent_job'] = (((jobtitle_agg['Projected Openings (2030)'] - jobtitle_agg['Job Openings (2024)']) / jobtitle_agg['Job Openings (2024)']) * 100).round(1)

most_decrease = jobtitle_agg.nsmallest(6, 'dif_percent_job')
most_decrease['dif_percent_job_%'] = most_decrease['dif_percent_job'].apply(lambda x: f"{x:.1f}%")

# Bar chart for job for trends by industry
bar_chart_decrease = alt.Chart(most_decrease).mark_bar(size=40, tooltip=None, color='white').encode(
    x=alt.X('dif_percent_job:Q', axis=None),
    y=alt.Y('Job Title:N', sort='-x', axis=None),
    color=alt.condition(
        alt.datum.dif_percent_job > 0,
        alt.value('#41b853'),  # Green for positive growth
        alt.value('#43bee5')   # Blue for negative growth
    ),
)

bar_jobs_percent = alt.Chart(most_decrease).mark_text(
    align='left',
    baseline='middle',
    dx=10,
    dy=0,
    color='white',
    fontSize=14,
).encode(
    x=alt.X('dif_percent_job:Q'),
    y=alt.Y('Job Title:N', sort='-x'),
    text=alt.Text('dif_percent_job_%:N')
)

# Create a DataFrame with job names and x value 0
jobname_x_zero = pd.DataFrame({
    'Job Title': most_decrease['Job Title'],
    'y': most_decrease['dif_percent_job'],
    'x': 0
})

most_decrease['zero'] = 0
bar_jobs_name = alt.Chart(most_decrease).mark_text(
    align='left',
    baseline='middle',
    dx=10,
    dy=0,
    color='white',
    fontSize=14,
).encode(
    x=alt.X('zero:Q'),
    y=alt.Y('Job Title:N', sort='-x'),
    text=alt.Text('Job Title:N')
)


bar_chart_decrease = (bar_chart_decrease +  bar_jobs_percent + bar_jobs_name).properties(
    width=550,
    height=300,
    background='transparent'
).configure_view(
    strokeWidth=0,
    fill='transparent'
).configure_axis(
    grid=False,
    title=None
)
st.markdown('<br></br>', unsafe_allow_html=True)
st.markdown(
    "<span style='color:#f40058; font-size: 16px; display: flex; justify-content: center'>Most Decrease in Projected Job Openings (2024-2030)</span>",
    unsafe_allow_html=True
)
st.altair_chart(bar_chart_decrease, use_container_width=True)


