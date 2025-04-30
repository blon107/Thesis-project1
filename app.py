try:
    import streamlit as st
    import pandas as pd
    import os
    from datetime import datetime
except ModuleNotFoundError as e:
    raise ImportError("This application requires 'streamlit'. Please ensure it is installed in your environment.") from e

st.title("Electrification Configuration Decision Matrix")

st.markdown("""
This app uses a Multi-Criteria Decision-Making (MCDM) approach to evaluate three alternatives:
- **A1: Battery-Electric**
- **A2: Hybrid-Electric**
- **A3: Hydrogen Fuel Cell**

Adjust the criteria weights and the scores for each alternative. The weighted sum model (WSM) will then calculate the overall score for each option.
""")

# 1. Input Criteria Weights
st.markdown("## 1. Input Criteria Weights")
st.markdown("The total weight should sum to 1.")
capex_w = st.number_input("CAPEX Weight", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
opex_w = st.number_input("OPEX Weight", min_value=0.0, max_value=1.0, value=0.20, step=0.01)
eff_w = st.number_input("Energy Efficiency Weight", min_value=0.0, max_value=1.0, value=0.30, step=0.01)
int_w = st.number_input("Integration Complexity Weight", min_value=0.0, max_value=1.0, value=0.10, step=0.01)
vess_w = st.number_input("Vessel Type Suitability Weight", min_value=0.0, max_value=1.0, value=0.10, step=0.01)
reg_w = st.number_input("Regulatory Impact Weight", min_value=0.0, max_value=1.0, value=0.05, step=0.01)

total_w = capex_w + opex_w + eff_w + int_w + vess_w + reg_w
st.write(f"**Total Weight:** {total_w:.2f}")
if abs(total_w - 1) > 0.01:
    st.warning("The total weight should sum to 1. Please adjust the values accordingly.")

# 2. Input Scores
st.markdown("## 2. Input Scores for Each Alternative (Scale 1-10)")
stakeholder = st.selectbox("Select Stakeholder Type:", ["Policy Maker", "Ship Owner/Operator", "Ship Designer/Shipyard", "Equipment Supplier", "Knowledge Center"])

with st.expander("Battery-Electric (A1)"):
    a1 = [
        st.number_input("A1 - CAPEX Score", 0.0, 10.0, 7.0, 0.1, key="a1_capex"),
        st.number_input("A1 - OPEX Score", 0.0, 10.0, 8.0, 0.1, key="a1_opex"),
        st.number_input("A1 - Efficiency Score", 0.0, 10.0, 9.0, 0.1, key="a1_eff"),
        st.number_input("A1 - Integration Score", 0.0, 10.0, 6.0, 0.1, key="a1_int"),
        st.number_input("A1 - Vessel Suitability Score", 0.0, 10.0, 6.0, 0.1, key="a1_vess"),
        st.number_input("A1 - Regulation Score", 0.0, 10.0, 8.0, 0.1, key="a1_reg")
    ]
with st.expander("Hybrid-Electric (A2)"):
    a2 = [
        st.number_input("A2 - CAPEX Score", 0.0, 10.0, 5.0, 0.1, key="a2_capex"),
        st.number_input("A2 - OPEX Score", 0.0, 10.0, 6.0, 0.1, key="a2_opex"),
        st.number_input("A2 - Efficiency Score", 0.0, 10.0, 7.0, 0.1, key="a2_eff"),
        st.number_input("A2 - Integration Score", 0.0, 10.0, 7.0, 0.1, key="a2_int"),
        st.number_input("A2 - Vessel Suitability Score", 0.0, 10.0, 8.0, 0.1, key="a2_vess"),
        st.number_input("A2 - Regulation Score", 0.0, 10.0, 7.0, 0.1, key="a2_reg")
    ]
with st.expander("Hydrogen Fuel Cell (A3)"):
    a3 = [
        st.number_input("A3 - CAPEX Score", 0.0, 10.0, 3.0, 0.1, key="a3_capex"),
        st.number_input("A3 - OPEX Score", 0.0, 10.0, 5.0, 0.1, key="a3_opex"),
        st.number_input("A3 - Efficiency Score", 0.0, 10.0, 6.0, 0.1, key="a3_eff"),
        st.number_input("A3 - Integration Score", 0.0, 10.0, 5.0, 0.1, key="a3_int"),
        st.number_input("A3 - Vessel Suitability Score", 0.0, 10.0, 7.0, 0.1, key="a3_vess"),
        st.number_input("A3 - Regulation Score", 0.0, 10.0, 9.0, 0.1, key="a3_reg")
    ]

if st.button("Calculate Results"):
    # Weighted sum
    scores = []
    for vals in (a1, a2, a3):
        scores.append(
            vals[0]*capex_w + vals[1]*opex_w + vals[2]*eff_w + vals[3]*int_w + vals[4]*vess_w + vals[5]*reg_w
        )
    df = pd.DataFrame({
        "Alternative": ["Battery-Electric (A1)", "Hybrid-Electric (A2)", "Hydrogen Fuel Cell (A3)"],
        "Score": scores
    }).sort_values("Score", ascending=False).reset_index(drop=True)

    st.markdown("## Decision Matrix Results")
    st.dataframe(df)
    st.success(f"The optimal configuration is **{df.loc[0,'Alternative']}** with score **{df.loc[0,'Score']:.2f}**.")

    # Save entries with count and timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"Stakeholder": stakeholder, "Timestamp": timestamp, "Score": df.loc[0,'Score']}
    count_file = "entry_counts.csv"
    if os.path.exists(count_file):
        counts = pd.read_csv(count_file)
    else:
        counts = pd.DataFrame(columns=["Stakeholder","Count"])
    if stakeholder in counts['Stakeholder'].values:
        counts.loc[counts['Stakeholder']==stakeholder,'Count'] += 1
    else:
        counts = pd.concat([counts, pd.DataFrame([[stakeholder,1]], columns=["Stakeholder","Count"])], ignore_index=True)
    entry_no = counts.loc[counts['Stakeholder']==stakeholder,'Count'].values[0]
    counts.to_csv(count_file, index=False)
    entry['Entry No'] = entry_no

    results_file = "wsm_results.csv"
    rec = pd.DataFrame([entry])
    if os.path.exists(results_file):
        all_rec = pd.read_csv(results_file)
        all_rec = pd.concat([all_rec, rec], ignore_index=True)
    else:
        all_rec = rec
    all_rec.to_csv(results_file, index=False)

if st.checkbox("Show All Entries"):
    if os.path.exists("wsm_results.csv"):
        history = pd.read_csv("wsm_results.csv")
        st.dataframe(history)
        # Plot scores by entry
        chart = history.pivot(index='Entry No', columns='Stakeholder', values='Score')
        st.bar_chart(chart)
    else:
        st.warning("No entries saved yet.")

 
