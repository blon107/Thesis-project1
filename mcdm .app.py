requirements.txt
stramlit
pandas
import streamlit as st
import pandas as pd

st.title("Electrification Configuration Decision Matrix")

st.markdown("""
This app uses a Multi-Criteria Decision-Making (MCDM) approach to evaluate three alternatives:
- **A1: Battery-Electric**
- **A2: Hybrid-Electric**
- **A3: Hydrogen Fuel Cell**

Adjust the criteria weights and the scores for each alternative. The weighted sum model (WSM) will then calculate the overall score for each option.
""")

st.markdown("## 1. Input Criteria Weights")
st.markdown("The total weight should sum to 1. (For example: CAPEX = 0.25, OPEX = 0.20, Efficiency = 0.30, Integration Complexity = 0.10, Vessel Type = 0.10, Regulatory Impact = 0.05)")

capex_weight = st.number_input("CAPEX Weight", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
opex_weight = st.number_input("OPEX Weight", min_value=0.0, max_value=1.0, value=0.20, step=0.01)
efficiency_weight = st.number_input("Energy Efficiency Weight", min_value=0.0, max_value=1.0, value=0.30, step=0.01)
integration_weight = st.number_input("Integration Complexity Weight", min_value=0.0, max_value=1.0, value=0.10, step=0.01)
vessel_type_weight = st.number_input("Vessel Type Suitability Weight", min_value=0.0, max_value=1.0, value=0.10, step=0.01)
regulation_weight = st.number_input("Regulatory Impact Weight", min_value=0.0, max_value=1.0, value=0.05, step=0.01)

total_weight = capex_weight + opex_weight + efficiency_weight + integration_weight + vessel_type_weight + regulation_weight
st.write(f"**Total Weight:** {total_weight:.2f}")

if abs(total_weight - 1) > 0.01:
    st.warning("The total weight should sum to 1. Please adjust the values accordingly.")

st.markdown("## 2. Input Scores for Each Alternative (Scale 1-10)")
st.markdown("### Battery-Electric (A1)")
a1_capex = st.number_input("A1 - CAPEX Score", min_value=0.0, max_value=10.0, value=7.0, step=0.1, key="a1_capex")
a1_opex = st.number_input("A1 - OPEX Score", min_value=0.0, max_value=10.0, value=8.0, step=0.1, key="a1_opex")
a1_efficiency = st.number_input("A1 - Energy Efficiency Score", min_value=0.0, max_value=10.0, value=9.0, step=0.1, key="a1_efficiency")
a1_integration = st.number_input("A1 - Integration Complexity Score", min_value=0.0, max_value=10.0, value=6.0, step=0.1, key="a1_integration")
a1_vessel = st.number_input("A1 - Vessel Type Suitability Score", min_value=0.0, max_value=10.0, value=6.0, step=0.1, key="a1_vessel")
a1_regulation = st.number_input("A1 - Regulatory Impact Score", min_value=0.0, max_value=10.0, value=8.0, step=0.1, key="a1_regulation")

st.markdown("### Hybrid-Electric (A2)")
a2_capex = st.number_input("A2 - CAPEX Score", min_value=0.0, max_value=10.0, value=5.0, step=0.1, key="a2_capex")
a2_opex = st.number_input("A2 - OPEX Score", min_value=0.0, max_value=10.0, value=6.0, step=0.1, key="a2_opex")
a2_efficiency = st.number_input("A2 - Energy Efficiency Score", min_value=0.0, max_value=10.0, value=7.0, step=0.1, key="a2_efficiency")
a2_integration = st.number_input("A2 - Integration Complexity Score", min_value=0.0, max_value=10.0, value=7.0, step=0.1, key="a2_integration")
a2_vessel = st.number_input("A2 - Vessel Type Suitability Score", min_value=0.0, max_value=10.0, value=8.0, step=0.1, key="a2_vessel")
a2_regulation = st.number_input("A2 - Regulatory Impact Score", min_value=0.0, max_value=10.0, value=7.0, step=0.1, key="a2_regulation")

st.markdown("### Hydrogen Fuel Cell (A3)")
a3_capex = st.number_input("A3 - CAPEX Score", min_value=0.0, max_value=10.0, value=3.0, step=0.1, key="a3_capex")
a3_opex = st.number_input("A3 - OPEX Score", min_value=0.0, max_value=10.0, value=5.0, step=0.1, key="a3_opex")
a3_efficiency = st.number_input("A3 - Energy Efficiency Score", min_value=0.0, max_value=10.0, value=6.0, step=0.1, key="a3_efficiency")
a3_integration = st.number_input("A3 - Integration Complexity Score", min_value=0.0, max_value=10.0, value=5.0, step=0.1, key="a3_integration")
a3_vessel = st.number_input("A3 - Vessel Type Suitability Score", min_value=0.0, max_value=10.0, value=7.0, step=0.1, key="a3_vessel")
a3_regulation = st.number_input("A3 - Regulatory Impact Score", min_value=0.0, max_value=10.0, value=9.0, step=0.1, key="a3_regulation")

if st.button("Calculate Results"):
    # Calculate weighted scores for each alternative
    a1_score = (a1_capex * capex_weight +
                a1_opex * opex_weight +
                a1_efficiency * efficiency_weight +
                a1_integration * integration_weight +
                a1_vessel * vessel_type_weight +
                a1_regulation * regulation_weight)
    
    a2_score = (a2_capex * capex_weight +
                a2_opex * opex_weight +
                a2_efficiency * efficiency_weight +
                a2_integration * integration_weight +
                a2_vessel * vessel_type_weight +
                a2_regulation * regulation_weight)
    
    a3_score = (a3_capex * capex_weight +
                a3_opex * opex_weight +
                a3_efficiency * efficiency_weight +
                a3_integration * integration_weight +
                a3_vessel * vessel_type_weight +
                a3_regulation * regulation_weight)
    
    # Create a DataFrame to display the results
    results_df = pd.DataFrame({
        "Alternative": ["Battery-Electric (A1)", "Hybrid-Electric (A2)", "Hydrogen Fuel Cell (A3)"],
        "Score": [a1_score, a2_score, a3_score]
    })
    results_df = results_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
    
    st.markdown("## Decision Matrix Results")
    st.dataframe(results_df)
    
    best_option = results_df.loc[0, "Alternative"]
    best_score = results_df.loc[0, "Score"]
    st.success(f"The optimal electrification configuration is **{best_option}** with a score of **{best_score:.2f}**.")
 
