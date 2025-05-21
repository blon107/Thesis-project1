import sys
import pandas as pd
import os
from datetime import datetime

try:
    import streamlit as st
except ModuleNotFoundError:
    print("Error: Streamlit is not installed.")
    print("Please install it by running: pip install streamlit")
    sys.exit(1)

st.title("Electrification Configuration Decision Matrix")

st.markdown("""
This app uses a Multi-Criteria Decision-Making (MCDM) approach to evaluate three alternatives:
- **A1: Battery-Electric**
- **A2: Hybrid-Electric**
- **A3: Hydrogen Fuel Cell**

Adjust the criteria weights and the scores for each alternative. The weighted sum model (WSM) will then calculate the overall score for each option.
""")

# 1. Stakeholder
stakeholder = st.selectbox(
    "Select Stakeholder Type:",
    ["Policy Maker", "Ship Owner/Operator", "Ship Designer/Shipyard", "Equipment Supplier", "Knowledge Center"]
)

# 2. Criteria Weights
st.markdown("## Input Criteria Weights (sum to 1)")
capex_w = st.number_input("CAPEX Weight", 0.0, 1.0, 0.25, 0.01)
opex_w  = st.number_input("OPEX Weight", 0.0, 1.0, 0.20, 0.01)
eff_w   = st.number_input("Efficiency Weight", 0.0, 1.0, 0.30, 0.01)
int_w   = st.number_input("Integration Weight", 0.0, 1.0, 0.10, 0.01)
vess_w  = st.number_input("Vessel Suitability Weight", 0.0, 1.0, 0.10, 0.01)
reg_w   = st.number_input("Regulatory Weight", 0.0, 1.0, 0.05, 0.01)
total_w = sum([capex_w, opex_w, eff_w, int_w, vess_w, reg_w])
st.write(f"**Total Weight:** {total_w:.2f}")
if abs(total_w - 1) > 0.01:
    st.warning("Weights must sum to 1.")

# 3. Scores via Sliders (0.5 increments)
st.markdown("## Input Scores (1–10, step 0.5)")
st.markdown("**Note:** Scores represent impact on the project, where **1 is negative impact** and **10 is positive impact**.")

with st.expander("Battery-Electric (A1)"):
    a1 = [
        st.slider("A1 – CAPEX", 1.0, 10.0, 7.0, 0.5, key="a1_capex"),
        st.slider("A1 – OPEX",  1.0, 10.0, 8.0, 0.5, key="a1_opex"),
        st.slider("A1 – Efficiency", 1.0, 10.0, 9.0, 0.5, key="a1_eff"),
        st.slider("A1 – Integration", 1.0, 10.0, 6.0, 0.5, key="a1_int"),
        st.slider("A1 – Vessel Suitability", 1.0, 10.0, 6.0, 0.5, key="a1_vess"),
        st.slider("A1 – Regulation", 1.0, 10.0, 8.0, 0.5, key="a1_reg")
    ]
with st.expander("Hybrid-Electric (A2)"):
    a2 = [
        st.slider("A2 – CAPEX", 1.0, 10.0, 5.0, 0.5, key="a2_capex"),
        st.slider("A2 – OPEX",  1.0, 10.0, 6.0, 0.5, key="a2_opex"),
        st.slider("A2 – Efficiency", 1.0, 10.0, 7.0, 0.5, key="a2_eff"),
        st.slider("A2 – Integration", 1.0, 10.0, 7.0, 0.5, key="a2_int"),
        st.slider("A2 – Vessel Suitability", 1.0, 10.0, 8.0, 0.5, key="a2_vess"),
        st.slider("A2 – Regulation", 1.0, 10.0, 7.0, 0.5, key="a2_reg")
    ]
with st.expander("Hydrogen Fuel Cell (A3)"):
    a3 = [
        st.slider("A3 – CAPEX", 1.0, 10.0, 3.0, 0.5, key="a3_capex"),
        st.slider("A3 – OPEX",  1.0, 10.0, 5.0, 0.5, key="a3_opex"),
        st.slider("A3 – Efficiency", 1.0, 10.0, 6.0, 0.5, key="a3_eff"),
        st.slider("A3 – Integration", 1.0, 10.0, 5.0, 0.5, key="a3_int"),
        st.slider("A3 – Vessel Suitability", 1.0, 10.0, 7.0, 0.5, key="a3_vess"),
        st.slider("A3 – Regulation", 1.0, 10.0, 9.0, 0.5, key="a3_reg")
    ]

if st.button("Calculate Results"):
    # Calculate each alternative
    A1_score = sum(val * w for val, w in zip(a1, [capex_w, opex_w, eff_w, int_w, vess_w, reg_w]))
    A2_score = sum(val * w for val, w in zip(a2, [capex_w, opex_w, eff_w, int_w, vess_w, reg_w]))
    A3_score = sum(val * w for val, w in zip(a3, [capex_w, opex_w, eff_w, int_w, vess_w, reg_w]))

    df = pd.DataFrame({
        "Alternative": ["A1 Battery-Electric", "A2 Hybrid-Electric", "A3 Fuel Cell-Electric"],
        "Score": [A1_score, A2_score, A3_score]
    }).sort_values("Score", ascending=False).reset_index(drop=True)

    st.markdown("## Results")
    st.dataframe(df)
    best = df.loc[0]
    st.success(f"Optimal: **{best['Alternative']}** ({best['Score']:.2f})")

    # Timestamp & full entry record
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "Stakeholder": stakeholder,
        "Timestamp": timestamp,
        "Entry No": None,
        "Best_Alternative": best["Alternative"],
        "Best_Score": best["Score"],
        "A1_Score": A1_score,
        "A2_Score": A2_score,
        "A3_Score": A3_score,
        "A1_CAPEX_Score": a1[0], # Storing individual scores
        "A1_OPEX_Score": a1[1],
        "A1_Efficiency_Score": a1[2],
        "A1_Integration_Score": a1[3],
        "A1_Vessel_Suitability_Score": a1[4],
        "A1_Regulation_Score": a1[5],
        "A2_CAPEX_Score": a2[0],
        "A2_OPEX_Score": a2[1],
        "A2_Efficiency_Score": a2[2],
        "A2_Integration_Score": a2[3],
        "A2_Vessel_Suitability_Score": a2[4],
        "A2_Regulation_Score": a2[5],
        "A3_CAPEX_Score": a3[0],
        "A3_OPEX_Score": a3[1],
        "A3_Efficiency_Score": a3[2],
        "A3_Integration_Score": a3[3],
        "A3_Vessel_Suitability_Score": a3[4],
        "A3_Regulation_Score": a3[5],
    }

    # Update counts
    cnt_file = "entry_counts.csv"
    if os.path.exists(cnt_file):
        counts = pd.read_csv(cnt_file)
    else:
        counts = pd.DataFrame(columns=["Stakeholder", "Count"])
    if stakeholder in counts.Stakeholder.values:
        counts.loc[counts.Stakeholder == stakeholder, "Count"] += 1
    else:
        counts = pd.concat([counts, pd.DataFrame([{"Stakeholder": stakeholder, "Count": 1}])], ignore_index=True)
    counts.to_csv(cnt_file, index=False)
    entry["Entry No"] = int(counts[counts.Stakeholder == stakeholder]["Count"].iloc[0])

    # Save to history
    results_file = "wsm_results.csv"
    rec = pd.DataFrame([entry])
    if os.path.exists(results_file):
        all_rec = pd.read_csv(results_file)
        all_rec = pd.concat([all_rec, rec], ignore_index=True)
    else:
        all_rec = rec
    all_rec.to_csv(results_file, index=False)

    st.info(f"Saved at {timestamp} (Entry #{entry['Entry No']})")

# Show full breakdown
if st.checkbox("Show All Entries"):
    if os.path.exists("wsm_results.csv"):
        history = pd.read_csv("wsm_results.csv")
        st.markdown("### Full Entry History (Detailed Scoring)")
        # Display the history with all columns, including detailed scores
        st.dataframe(history)

        # Chart best scores by stakeholder (can keep this as it is or modify)
        st.markdown("### Best Scores by Stakeholder (Bar Chart)")
        chart = history.pivot(index="Entry No", columns="Stakeholder", values="Best_Score")
        st.bar_chart(chart)
    else:
        st.warning("No entries saved yet.")
