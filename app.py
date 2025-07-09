import streamlit as st
import pandas as pd
from io import StringIO
import plotly.express as px

st.set_page_config(page_title="SORM - SNAP Outreach Metrics", layout="wide")
st.title("📊 SORM - SNAP Outreach Replacement Metrics Dashboard")

csv_data = '''Household_ID,County,Household_Size,Monthly_Income,Public_Assistance,Rent_Burden_Pct,LEP_Flag,Child_Present,Disability_Flag,Prior_Referral_Source,SNAP_Enrolled
101,Hennepin,3,1800,Yes,40,No,Yes,No,School,No
102,Ramsey,1,900,No,55,Yes,No,Yes,Clinic,No
103,St. Louis,4,2600,Yes,30,Yes,Yes,No,Food Shelf,Yes
104,Winona,2,1400,Yes,50,No,Yes,Yes,Church,No
105,Nobles,5,2900,No,35,Yes,Yes,No,Community Org,No'''

df = pd.read_csv(StringIO(csv_data))

def calculate_scores(row):
    income_score = 100 if row['Monthly_Income'] <= 1500 else (80 if row['Monthly_Income'] <= 2000 else 60)
    size_score = 10 * row['Household_Size']
    pa_score = 20 if row['Public_Assistance'] == 'Yes' else 0
    eligibility_likelihood = min(income_score + size_score + pa_score, 100)

    priority_score = 1
    if row['LEP_Flag'] == 'Yes':
        priority_score += 1
    if row['Child_Present'] == 'Yes':
        priority_score += 1
    if row['Disability_Flag'] == 'Yes':
        priority_score += 1
    if row['Rent_Burden_Pct'] > 40:
        priority_score += 1
    outreach_priority = min(priority_score, 5)

    risk_score = 0
    if row['Rent_Burden_Pct'] >= 50:
        risk_score += 40
    if row['Monthly_Income'] < 1000:
        risk_score += 30
    if row['Public_Assistance'] == 'Yes':
        risk_score += 30
    food_insecurity_risk = min(risk_score, 100)

    support_index = 'Low'
    if row['LEP_Flag'] == 'Yes' or row['Disability_Flag'] == 'Yes':
        support_index = 'High'
    elif row['Child_Present'] == 'Yes':
        support_index = 'Medium'

    return pd.Series([eligibility_likelihood, outreach_priority, food_insecurity_risk, support_index])

df[['Eligibility_Likelihood_Score', 'Outreach_Priority_Index', 'Food_Insecurity_Risk_Score', 'Enrollment_Support_Index']] = df.apply(calculate_scores, axis=1)

st.dataframe(df)

fig = px.bar(df, x='County', y='Food_Insecurity_Risk_Score', title='Food Insecurity Risk by County')
st.plotly_chart(fig, use_container_width=True)

