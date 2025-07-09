
import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

st.set_page_config(page_title="SORM - SNAP Outreach Metrics", layout="wide")
st.title("📊 SORM - SNAP Outreach Replacement Metrics Dashboard")
st.markdown("This dashboard helps local agencies score and prioritize SNAP outreach after funding cuts.")

uploaded_file = st.file_uploader("Upload Household Data (CSV)", type="csv")

# Embedded sample data
default_csv = StringIO('Household_ID,County,Household_Size,Monthly_Income,Public_Assistance,Rent_Burden_Pct,LEP_Flag,Child_Present,Disability_Flag,Prior_Referral_Source,SNAP_Enrolled,Eligibility_Likelihood_Score,Outreach_Priority_Index,Food_Insecurity_Risk_Score,Enrollment_Support_Index\n101,Hennepin,3,1800,Yes,40,No,Yes,No,School,No,100,2,30,Medium\n102,Ramsey,1,900,No,55,Yes,No,Yes,Clinic,No,100,4,70,High\n103,St. Louis,4,2600,Yes,30,Yes,Yes,No,Food Shelf,Yes,100,3,30,High\n104,Winona,2,1400,Yes,50,No,Yes,Yes,Church,No,100,4,70,High\n105,Nobles,5,2900,No,35,Yes,Yes,No,Community Org,No,100,3,0,High\n')

@st.cache_data
def load_and_score_data(file):
    df = pd.read_csv(file)

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
    return df

# Load uploaded or embedded default data
if uploaded_file:
    df = load_and_score_data(uploaded_file)
    st.success("✅ File uploaded and scored successfully.")
else:
    df = load_and_score_data(default_csv)
    st.info("No file uploaded. Displaying embedded sample data.")

# Filter section
st.subheader("📋 Filter & Browse Data")
counties = st.multiselect("Select Counties", options=sorted(df['County'].unique()), default=df['County'].unique())
priority = st.slider("Minimum Outreach Priority Index", 1, 5, 1)
filtered_df = df[(df['County'].isin(counties)) & (df['Outreach_Priority_Index'] >= priority)]
st.dataframe(filtered_df)

# Visualizations
st.subheader("📈 Visualizations")
col1, col2 = st.columns(2)
with col1:
    bar1 = px.bar(filtered_df, x="County", y="Food_Insecurity_Risk_Score", color="County", title="Food Insecurity Risk by County")
    st.plotly_chart(bar1, use_container_width=True)
with col2:
    bar2 = px.histogram(filtered_df, x="Outreach_Priority_Index", nbins=5, title="Distribution of Outreach Priority")
    st.plotly_chart(bar2, use_container_width=True)

st.download_button("📥 Download Scored Data", data=filtered_df.to_csv(index=False), file_name="SORM_Scored_Data.csv")

st.sidebar.image("https://www.stratdesignsolutions.com/logo.png", use_column_width=True)
st.sidebar.markdown("**Powered by StratDesign Solutions**")

# Interpretation Section
st.markdown("### 📘 Output Interpretation and Feedback")
st.markdown("""
#### 🟢 **Eligibility Likelihood Score**
- 80–100: Very likely eligible → Recommend direct outreach or pre-filled SNAP application forms
- 60–79: Likely eligible → Include in ongoing outreach or reminders
- Below 60: Monitor but lower urgency

#### 🟠 **Outreach Priority Index**
- 4–5: Highest urgency. Recommend immediate contact via phone, text, or home visit.
- 3: Moderate urgency. Include in next mailer or newsletter.
- 1–2: Lower urgency. Passive support or info-only outreach.

#### 🔴 **Food Insecurity Risk Score**
- 60–100: Likely experiencing food hardship → Refer to food shelves, pantries, emergency meal programs
- 30–59: At risk → Recommend SNAP + local nutrition supports
- Below 30: Watch list for future

#### 🟣 **Enrollment Support Index**
- High: Needs 1:1 assistance — refer to bilingual navigator or trained SNAP advocate
- Medium: Some help — offer live chat or hotline
- Low: Self-service friendly — provide direct online application links
""")

st.markdown("These insights help you **target outreach efforts**, **deploy limited staff efficiently**, and **track household needs over time**.")
