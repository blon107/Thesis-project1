try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os
    from datetime import datetime
except ModuleNotFoundError as e:
    raise ImportError("This application requires 'streamlit'. Please ensure it is installed in your environment.") from e

st.title("MCDM Tool for Inland Vessel Electrification")
st.subheader("Multi-Criteria Decision Making Tool")

criteria = [
    "CAPEX (Upfront Cost)",
    "OPEX (Operational Cost)",
    "Integration Complexity",
    "Technical Performance",
    "Environmental Impact",
    "Safety & Regulatory Compliance"
]

alternatives = ["Battery-Electric", "Hybrid-Electric", "Fuel Cell-Electric", "Diesel (Baseline)"]

st.markdown("### Instructions:")
st.markdown("- Rate each configuration from 1 (worst) to 5 (best) on each criterion.")
st.markdown("- Adjust weights to indicate importance of each criterion.")
st.markdown("- View overall scores and rankings below.")

stakeholder_type = st.selectbox("Select Stakeholder Type:", ["Policy Maker", "Ship Owner/Operator", "Ship Designer/Shipyard", "Equipment Supplier", "Knowledge Center"])

scores = {}
st.markdown("### Scoring Matrix")
for alt in alternatives:
    scores[alt] = []
    st.markdown(f"**{alt}**")
    for crit in criteria:
        score = st.slider(f"{crit} score for {alt}", 1, 5, 3, key=f"{alt}_{crit}")
        scores[alt].append(score)

st.markdown("### Criteria Weights (1 = least important, 5 = most important)")
weights = []
for crit in criteria:
    weight = st.slider(f"Weight for {crit}", 1, 5, 3, key=f"weight_{crit}")
    weights.append(weight)

score_df = pd.DataFrame(scores, index=criteria).T
weights_array = np.array(weights)
weighted_scores = score_df.multiply(weights_array, axis=1)
score_df['Total Score'] = weighted_scores.sum(axis=1)
score_df['Average Score'] = score_df['Total Score'] / sum(weights)

st.markdown("### Results")
st.dataframe(score_df.style.format("{:.2f}"))
st.bar_chart(score_df['Total Score'])

ranked = score_df.sort_values("Total Score", ascending=False)
st.markdown("### Rankings")
st.table(ranked[['Total Score']])

if st.button("Save My Inputs"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = score_df.copy()
    result['Stakeholder'] = stakeholder_type
    result['Normalized'] = result['Total Score'] / result['Total Score'].max()
    result['Timestamp'] = timestamp
    result.reset_index(inplace=True)

    counter_file = "stakeholder_entry_counts.csv"
    if os.path.exists(counter_file):
        counter_df = pd.read_csv(counter_file)
    else:
        counter_df = pd.DataFrame(columns=["Stakeholder", "Count"])

    if stakeholder_type in counter_df['Stakeholder'].values:
        counter_df.loc[counter_df['Stakeholder'] == stakeholder_type, 'Count'] += 1
    else:
        new_row = pd.DataFrame([[stakeholder_type, 1]], columns=["Stakeholder", "Count"])
        counter_df = pd.concat([counter_df, new_row], ignore_index=True)

    current_count = counter_df[counter_df['Stakeholder'] == stakeholder_type]['Count'].values[0]
    result['Entry No'] = current_count
    counter_df.to_csv(counter_file, index=False)

    if os.path.exists("user_mcdm_results.csv"):
        saved_data = pd.read_csv("user_mcdm_results.csv")
        saved_data = pd.concat([saved_data, result], ignore_index=True)
    else:
        saved_data = result
    saved_data.to_csv("user_mcdm_results.csv", index=False)
    st.success("Inputs saved successfully!")

if st.checkbox("View All Saved Inputs"):
    if os.path.exists("user_mcdm_results.csv"):
        all_data = pd.read_csv("user_mcdm_results.csv")
        st.dataframe(all_data)
        st.markdown("### Analysis of Saved Inputs")
        stakeholder_grouped = all_data.groupby(['Stakeholder', 'index'])['Total Score'].mean().unstack()
        st.bar_chart(stakeholder_grouped)
    else:
        st.warning("No data found yet. Please save at least one entry.")
