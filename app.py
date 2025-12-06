import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="UP Crop Recommendation System",
    page_icon="🌾",
    layout="wide"
)

CUSTOM_CSS = """
<style>
:root {
    --accent: #22c55e;
    --bg-main: #1a1a1a;
    --bg-card: #262626;
    --bg-elevated: #2a2a2a;
    --border: #404040;
    --text: #ffffff;
    --text-muted: #a3a3a3;
}
.stApp {
    background: #1a1a1a;
    color: var(--text);
}
[data-testid="stSidebar"] {
    background: #0f0f0f;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown, 
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] span {
    color: var(--text-muted) !important;
}
.metric-card {
    padding: 1.5rem;
    border-radius: 4px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    color: var(--text);
}
.rec-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 2px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #000;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-green { background: #22c55e; }
.badge-amber { background: #eab308; }
.badge-orange { background: #f97316; }
.hero {
    padding: 2.5rem;
    border-radius: 4px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    color: var(--text);
}
.hero h1 {
    font-size: 3rem;
    font-weight: 900;
    margin-bottom: 0.5rem;
    letter-spacing: -1px;
}
.hero p {
    font-size: 1rem;
    color: var(--text-muted);
    font-weight: 400;
}
.stButton button {
    width: 100%;
    border-radius: 2px;
    padding: 0.875rem 1.5rem;
    font-weight: 700;
    background: var(--accent);
    color: #000;
    border: none;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.875rem;
}
.stButton button:hover {
    background: #16a34a;
    transform: translateY(-1px);
}
.npk-card {
    padding: 1.25rem;
    border-radius: 4px;
    border: 1px solid var(--border);
    background: var(--bg-card);
    color: var(--text);
}
.npk-card h4 {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}
.npk-card h2 {
    font-size: 2rem;
    font-weight: 900;
    color: var(--text);
}
.stMetric {
    color: var(--text);
}
.stProgress > div > div {
    background: var(--accent);
}
h1, h2, h3, h4 {
    font-weight: 900 !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

@st.cache_data
def load_crop_data():
    try:
        return pd.read_csv('crops_data.csv')
    except FileNotFoundError:
        st.error("❌ Error: crops_data.csv file not found! Please make sure the file is in the same directory as app.py")
        st.stop()

@st.cache_data
def load_districts_data():
    try:
        return pd.read_csv('districts_data.csv')
    except FileNotFoundError:
        st.error("❌ Error: districts_data.csv file not found! Please make sure the file is in the same directory as app.py")
        st.stop()

def get_region_from_district(district, districts_df):
    result = districts_df[districts_df['district_name'] == district]
    if not result.empty:
        return result.iloc[0]['region']
    return 'Central UP'

def calculate_suitability_score(crop_row, user_inputs):
    score = 0
    ph = user_inputs['ph']
    ph_min, ph_max = crop_row['ph_min'], crop_row['ph_max']
    if ph_min <= ph <= ph_max:
        score += 20
    elif abs(ph - ph_min) <= 0.5 or abs(ph - ph_max) <= 0.5:
        score += 10
    n = user_inputs['nitrogen']
    n_min, n_max = crop_row['nitrogen_min'], crop_row['nitrogen_max']
    if n_min <= n <= n_max:
        score += 20
    elif n_min - 20 <= n <= n_max + 20:
        score += 10
    p = user_inputs['phosphorus']
    p_min, p_max = crop_row['phosphorus_min'], crop_row['phosphorus_max']
    if p_min <= p <= p_max:
        score += 20
    elif p_min - 15 <= p <= p_max + 15:
        score += 10
    k = user_inputs['potassium']
    k_min, k_max = crop_row['potassium_min'], crop_row['potassium_max']
    if k_min <= k <= k_max:
        score += 20
    elif k_min - 15 <= k <= k_max + 15:
        score += 10
    soil_types = crop_row['soil_types'].split(',')
    if user_inputs['soil_type'] in soil_types:
        score += 10
    if crop_row['season'] == user_inputs['season'] or crop_row['season'] == 'Year-round':
        score += 10
    return score

def recommend_crops(user_inputs, crops_df, districts_df, min_score):
    recommendations = []
    user_region = get_region_from_district(user_inputs['district'], districts_df)
    for _, crop_row in crops_df.iterrows():
        suitable_regions = crop_row['suitable_regions'].split(',')
        if user_region not in suitable_regions:
            continue
        score = calculate_suitability_score(crop_row, user_inputs)
        if score >= min_score:
            recommendations.append({
                'crop': crop_row['crop_name'],
                'crop_hindi': crop_row['crop_name_hindi'],
                'score': score,
                'data': crop_row
            })
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations

def main():
    crops_df = load_crop_data()
    districts_df = load_districts_data()
    st.markdown(
        """
        <div class="hero">
            <h1>Uttar Pradesh Crop Intelligence</h1>
            <p>Balanced recommendations tailored to your soil profile, district climate, and seasonal ambitions. Built with growers, for growers.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.header("Field Profile")
    st.sidebar.caption("Precision grows profits. Keep your soil test handy.")
    st.sidebar.subheader("Location")
    all_districts = sorted(districts_df['district_name'].tolist())
    district = st.sidebar.selectbox("Select District", all_districts)
    st.sidebar.subheader("Soil Character")
    soil_type = st.sidebar.selectbox(
        "Soil Type",
        ['Loamy', 'Clay', 'Sandy', 'Alluvial', 'Black', 'Red']
    )
    ph = st.sidebar.slider("Soil pH", 4.0, 9.0, 6.5, 0.1)
    st.sidebar.markdown("**NPK (kg/hectare)**")
    nitrogen = st.sidebar.number_input("Nitrogen (N)", 0, 200, 50, key="n")
    phosphorus = st.sidebar.number_input("Phosphorus (P)", 0, 150, 40, key="p")
    potassium = st.sidebar.number_input("Potassium (K)", 0, 150, 40, key="k")
    st.sidebar.subheader("Season")
    season = st.sidebar.selectbox(
        "Select Season",
        ['Kharif', 'Rabi', 'Zayad']
    )
    st.sidebar.subheader("Context")
    water_availability = st.sidebar.select_slider(
        "Water Availability",
        options=['Low', 'Medium', 'High']
    )
    land_size = st.sidebar.number_input("Land Size (hectares)", 0.1, 1000.0, 1.0, 0.1)
    min_score = st.sidebar.slider("Minimum Suitability %", 40, 100, 55, 5)
    user_inputs = {
        'district': district,
        'soil_type': soil_type,
        'ph': ph,
        'nitrogen': nitrogen,
        'phosphorus': phosphorus,
        'potassium': potassium,
        'season': season,
        'water_availability': water_availability,
        'land_size': land_size
    }
    st.sidebar.markdown("—")
    if st.sidebar.button("🔍 Get Recommendations", type="primary"):
        region = get_region_from_district(district, districts_df)
        st.subheader("Field Snapshot")
        info_cols = st.columns(4)
        info_cols[0].metric("District", district)
        info_cols[1].metric("Region", region)
        info_cols[2].metric("Season", season)
        info_cols[3].metric("Land Size (ha)", f"{land_size:.1f}")
        soil_cols = st.columns(3)
        soil_cols[0].metric("Soil Type", soil_type)
        soil_cols[1].metric("pH Level", f"{ph:.1f}")
        soil_cols[2].metric("Water", water_availability)
        st.markdown("**Nutrient Balance**")
        npk_cols = st.columns(3)
        npk_cols[0].markdown(f"<div class='npk-card'><h4>Nitrogen</h4><h2>{nitrogen}</h2></div>", unsafe_allow_html=True)
        npk_cols[1].markdown(f"<div class='npk-card'><h4>Phosphorus</h4><h2>{phosphorus}</h2></div>", unsafe_allow_html=True)
        npk_cols[2].markdown(f"<div class='npk-card'><h4>Potassium</h4><h2>{potassium}</h2></div>", unsafe_allow_html=True)
        recommendations = recommend_crops(user_inputs, crops_df, districts_df, min_score)
        st.markdown("---")
        st.subheader("Tailored Crop Lineup")
        if not recommendations:
            st.warning("⚠️ No suitable crops found for your soil conditions. Consider soil treatment or consult an agricultural expert.")
        else:
            for i, rec in enumerate(recommendations[:8], 1):
                crop_name = rec['crop']
                crop_hindi = rec['crop_hindi']
                score = rec['score']
                crop_data = rec['data']
                if score >= 80:
                    badge = "<span class='rec-badge badge-green'>Highly Suitable</span>"
                elif score >= 65:
                    badge = "<span class='rec-badge badge-amber'>Suitable</span>"
                else:
                    badge = "<span class='rec-badge badge-orange'>Moderate Fit</span>"
                expander_label = f"**{i}. {crop_name} ({crop_hindi})** — {score}% match"
                with st.expander(expander_label):
                    st.markdown(badge, unsafe_allow_html=True)
                    st.progress(min(score, 100) / 100)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"• Season: {crop_data['season']}")
                        st.write(f"• Duration: {crop_data['duration']}")
                        st.write(f"• Water Needs: {crop_data['water_needs']}")
                        st.write(f"• Expected Yield: {crop_data['yield_min']}-{crop_data['yield_max']} quintals/hectare")
                    with col2:
                        st.write(f"• pH Range: {crop_data['ph_min']} - {crop_data['ph_max']}")
                        st.write(f"• Nitrogen: {crop_data['nitrogen_min']}-{crop_data['nitrogen_max']} kg/ha")
                        st.write(f"• Phosphorus: {crop_data['phosphorus_min']}-{crop_data['phosphorus_max']} kg/ha")
                        st.write(f"• Potassium: {crop_data['potassium_min']}-{crop_data['potassium_max']} kg/ha")
                        st.write(f"• Suitable Soils: {crop_data['soil_types']}")
                    avg_yield = (crop_data['yield_min'] + crop_data['yield_max']) / 2
                    estimated_production = avg_yield * land_size
                    st.info(f"📊 **Estimated Production for {land_size} hectare(s):** ~{estimated_production:.1f} quintals")
    else:
        st.info("👈 Please fill in your soil and location details in the sidebar and click 'Get Recommendations'")
        st.markdown("### How to get precise recommendations")
        colA, colB = st.columns(2)
        colA.markdown(
            """
            1. Choose district and soil profile.
            2. Feed in recent soil-test NPK results.
            3. Lock the season you are planning for.
            4. Share irrigation comfort and land area.
            5. Hit the scan button to view curated crops.
            """
        )
        colB.markdown(
            """
            **Pro tips**
            - Run soil tests every 6 months.
            - Stack allied crops for risk balancing.
            - Track mandi prices before sowing.
            - Explore state schemes for subsidies.
            """
        )
        st.markdown("### Database Pulse")
        stat_cols = st.columns(2)
        stat_cols[0].markdown(f"<div class='metric-card'><h3>{len(crops_df)}</h3><p>Crops tracked</p></div>", unsafe_allow_html=True)
        stat_cols[1].markdown(f"<div class='metric-card'><h3>{len(districts_df)}</h3><p>Districts mapped</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
