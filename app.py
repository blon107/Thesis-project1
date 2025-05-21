import pandas as pd

try:
    import streamlit as st
except ModuleNotFoundError:
    st.error("Streamlit is not installed. Run `pip install streamlit` and try again.")
    sys.exit(1)

# File paths
CNT_FILE = "entry_counts.csv"
RESULTS_FILE = "wsm_results.csv"

st.title("Electrification Configuration Decision Matrix")

st.markdown("""
This app uses a Multi-Criteria Decision-Making (MCDM) approach to evaluate three alternatives:
- **A1: Battery-Electric**
- **A2: Hybrid-Electric**
- **A3: Hydrogen Fuel Cell**

Adjust the criteria weights and the scores for each alternative.
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
if abs(total_w - 1) > 1e-6:
    st.warning("Weights must sum to 1.")
    calculate_enabled = False
else:
    calculate_enabled = True

# 3. Scores via Sliders
st.markdown("## Input Scores (1–10, step 0.5)")
st.markdown("**Note:** 1 = worst, 10 = best impact")

def make_sliders(prefix, defaults):
    return [
        st.slider(f"{prefix} – CAPEX", 1.0, 10.0, defaults[0], 0.5, key=f"{prefix}_capex"),
        st.slider(f"{prefix} – OPEX",  1.0, 10.0, defaults[1], 0.5, key=f"{prefix}_opex"),
        st.slider(f"{prefix} – Efficiency", 1.0, 10.0, defaults[2], 0.5, key=f"{prefix}_eff"),
        st.slider(f"{prefix} – Integration", 1.0, 10.0, defaults[3], 0.5, key=f"{prefix}_int"),
        st.slider(f"{prefix} – Vessel Suitability", 1.0, 10.0, defaults[4], 0.5, key=f"{prefix}_vess"),
        st.slider(f"{prefix} – Regulation", 1.0, 10.0, defaults[5], 0.5, key=f"{prefix}_reg")
    ]

with st.expander("Battery-Electric (A1)"):
    a1 = make_sliders("A1", [7.0, 8.0, 9.0, 6.0, 6.0, 8.0])
with st.expander("Hybrid-Electric (A2)"):
    a2 = make_sliders("A2", [5.0, 6.0, 7.0, 7.0, 8.0, 7.0])
with st.expander("Hydrogen Fuel Cell (A3)"):
    a3 = make_sliders("A3", [3.0, 5.0, 6.0, 5.0, 7.0, 9.0])

if st.button("Calculate Results", disabled=not calculate_enabled):
    weights = [capex_w, opex_w, eff_w, int_w, vess_w, reg_w]
    A1_score = sum(v * w for v, w in zip(a1, weights))
    A2_score = sum(v * w for v, w in zip(a2, weights))
    A3_score = sum(v * w for v, w in zip(a3, weights))

    df = pd.DataFrame({
        "Alternative": ["A1 Battery-Electric", "A2 Hybrid-Electric", "A3 Fuel Cell-Electric"],
        "Score": [A1_score, A2_score, A3_score]
    }).sort_values("Score", ascending=False).reset_index(drop=True)

    st.markdown("## Results")
    st.dataframe(df)
    best = df.iloc[0]
    st.success(f"Optimal: **{best['Alternative']}** ({best['Score']:.2f})")

    # Timestamp & record
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    criteria = ["CAPEX", "OPEX", "Efficiency", "Integration", "Vessel_Suitability", "Regulation"]

    entry = {
        "Stakeholder": stakeholder,
        "Timestamp": timestamp,
        "Best_Alternative": best["Alternative"],
        "Best_Score": best["Score"],
        "A1_Overall_Score": A1_score,
        "A2_Overall_Score": A2_score,
        "A3_Overall_Score": A3_score
    }
    for idx, score in enumerate(a1):
        entry[f"A1_{criteria[idx]}_Score"] = score
    for idx, score in enumerate(a2):
        entry[f"A2_{criteria[idx]}_Score"] = score
    for idx, score in enumerate(a3):
        entry[f"A3_{criteria[idx]}_Score"] = score

    # Update entry count
    if os.path.exists(CNT_FILE):
        counts = pd.read_csv(CNT_FILE)
    else:
        counts = pd.DataFrame(columns=["Stakeholder", "Count"])

    if stakeholder in counts.Stakeholder.values:
        counts.loc[counts.Stakeholder == stakeholder, "Count"] += 1
    else:
        # FIX: Replace deprecated .append() with pd.concat()
        new_row = pd.DataFrame([{"Stakeholder": stakeholder, "Count": 1}])
        counts = pd.concat([counts, new_row], ignore_index=True)

    counts.to_csv(CNT_FILE, index=False)
    entry_no = int(counts.loc[counts.Stakeholder == stakeholder, "Count"].iloc[0])
    entry["Entry No"] = entry_no

    # Save full history
    rec = pd.DataFrame([entry])
    if os.path.exists(RESULTS_FILE):
        all_rec = pd.read_csv(RESULTS_FILE)
        all_rec = pd.concat([all_rec, rec], ignore_index=True)
    else:
        all_rec = rec
    all_rec.to_csv(RESULTS_FILE, index=False)

    st.info(f"Saved at {timestamp} (Entry #{entry_no})")

# Detailed breakdown
if st.checkbox("Show All Entries (Detailed Breakdown & Charts)"):
    if os.path.exists(RESULTS_FILE):
        history = pd.read_csv(RESULTS_FILE)

        st.markdown("### Full Entry History with Detailed Scoring")
        st.dataframe(history)

        st.markdown("---")
        st.markdown("### Best Scores by Stakeholder (Overall Score)")
        chart = history.pivot(index="Entry No", columns="Stakeholder", values="Best_Score")
        st.bar_chart(chart)

        st.markdown("---")
        st.markdown("### Analytical Breakdown of Individual Criteria Scores")
        st.markdown("Select a specific score to see its trend across entries.")

        detailed = [c for c in history.columns
                    if "_Score" in c and "Overall_Score" not in c and "Best_Score" not in c]
        if detailed:
            choice = st.selectbox("Select score to chart:", detailed)
            st.line_chart(history.set_index("Entry No")[choice])
            st.write(f"Trend of **{choice}** over entries.")
        else:
            st.info("No individual criteria scores found yet.")
    else:
        st.warning("No entries saved yet.")
