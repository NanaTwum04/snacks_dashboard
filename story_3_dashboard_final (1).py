import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Blue Ocean Snack Analysis",
    page_icon="🍿",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv('snacks_with_categories.csv')
    df = df[
        (df['sugars_100g'] >= 0) & (df['sugars_100g'] <= 100) &
        (df['proteins_100g'] >= 0) & (df['proteins_100g'] <= 100)
    ]
    return df

try:
    df = load_data()
except:
    st.error("⚠️ Please make sure 'snacks_with_categories.csv' is in the same directory")
    st.stop()

st.title("🍿 Finding the Healthy Snacking Blue Ocean")
st.markdown("**Goal:** Identify the gap between High Protein + Low Sugar demand vs. current market supply")
st.markdown("---")

st.sidebar.header("Filter Categories")
all_categories = sorted(df['Primary_Category'].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Select Categories to Display",
    all_categories,
    default=all_categories
)

if selected_categories:
    df_filtered = df[df['Primary_Category'].isin(selected_categories)]
else:
    df_filtered = df.copy()

st.sidebar.markdown(f"**Showing {len(df_filtered):,} products**")

HIGH_PROTEIN = 15
LOW_SUGAR = 5

st.sidebar.markdown("---")
st.sidebar.markdown("### Opportunity Zone")
st.sidebar.markdown(f"**High Protein:** ≥ {HIGH_PROTEIN}g")
st.sidebar.markdown(f"**Low Sugar:** ≤ {LOW_SUGAR}g")

st.subheader("The Nutrient Matrix")

fig = go.Figure()

categories = df_filtered['Primary_Category'].unique()
colors = px.colors.qualitative.Plotly + px.colors.qualitative.Set2

for i, category in enumerate(categories):
    cat_data = df_filtered[df_filtered['Primary_Category'] == category]
    
    fig.add_trace(go.Scatter(
        x=cat_data['sugars_100g'],
        y=cat_data['proteins_100g'],
        mode='markers',
        name=category,
        marker=dict(
            size=8,
            color=colors[i % len(colors)],
            opacity=0.6,
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>%{hovertext}</b><br>Sugar: %{x:.1f}g<br>Protein: %{y:.1f}g<br><extra></extra>',
        hovertext=cat_data['product_name']
    ))

fig.add_hline(y=HIGH_PROTEIN, line_dash="dash", line_color="green", line_width=2, opacity=0.6)
fig.add_vline(x=LOW_SUGAR, line_dash="dash", line_color="red", line_width=2, opacity=0.6)

fig.add_annotation(
    x=LOW_SUGAR / 2,
    y=HIGH_PROTEIN + 8,
    text="<b>OPPORTUNITY ZONE</b><br>(High Protein, Low Sugar)",
    showarrow=False,
    font=dict(size=12, color="green", family="Arial Black"),
    bgcolor="white",
    bordercolor="green",
    borderwidth=2,
    borderpad=10
)

fig.update_layout(
    height=650,
    plot_bgcolor='white',
    xaxis=dict(
        title="Sugar (g per 100g)",
        showgrid=True,
        gridcolor='lightgray',
        range=[0, df_filtered['sugars_100g'].max() * 1.05]
    ),
    yaxis=dict(
        title="Protein (g per 100g)",
        showgrid=True,
        gridcolor='lightgray',
        range=[0, df_filtered['proteins_100g'].max() * 1.05]
    ),
    legend=dict(
        title="Category",
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="lightgray",
        borderwidth=1
    ),
    hovermode='closest'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# STORY 4: THE RECOMMENDATION - Make it prominent
st.subheader("💡 Key Insight & Recommendation")

opportunity_products = df_filtered[
    (df_filtered['proteins_100g'] >= HIGH_PROTEIN) &
    (df_filtered['sugars_100g'] <= LOW_SUGAR)
]

category_gaps = []
for cat in df_filtered['Primary_Category'].unique():
    cat_total = len(df_filtered[df_filtered['Primary_Category'] == cat])
    cat_opp = len(opportunity_products[opportunity_products['Primary_Category'] == cat])
    gap_pct = (cat_opp / cat_total * 100) if cat_total > 0 else 0
    category_gaps.append({
        'Category': cat,
        'Total': cat_total,
        'In Opportunity Zone': cat_opp,
        '% Coverage': gap_pct
    })

gap_df = pd.DataFrame(category_gaps).sort_values('% Coverage')

if len(gap_df) > 0:
    biggest_gap = gap_df.iloc[0]
    
    st.success(f"""
    ### 🎯 Client Recommendation
    
    **"Based on the data, the biggest market opportunity is in {biggest_gap['Category']}, 
    specifically targeting products with {HIGH_PROTEIN}g of protein and less than {LOW_SUGAR}g of sugar."**
    
    ---
    
    **Why this category?**
    - Market size: {biggest_gap['Total']} existing products
    - Current healthy options: Only {biggest_gap['In Opportunity Zone']} products ({biggest_gap['% Coverage']:.1f}%)
    - **Gap:** {biggest_gap['Total'] - biggest_gap['In Opportunity Zone']} products missing from the opportunity zone
    
    **Action for R&D Team:**
    - Develop a {biggest_gap['Category'].lower()} product line with ≥{HIGH_PROTEIN}g protein per 100g
    - Keep sugar content ≤{LOW_SUGAR}g per 100g
    - This addresses unmet consumer demand for healthier snacking options
    """)
else:
    st.info("Select categories to see the recommendation")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Blue Ocean Gap Analysis")
    
    st.metric("Products in Opportunity Zone", len(opportunity_products))
    st.metric("Total Products Analyzed", len(df_filtered))
    
    opportunity_pct = (len(opportunity_products) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
    st.metric("% in Opportunity Zone", f"{opportunity_pct:.1f}%")
    
    if len(opportunity_products) > 0:
        st.markdown("**Opportunity Products by Category:**")
        opp_by_cat = opportunity_products['Primary_Category'].value_counts()
        st.dataframe(opp_by_cat.to_frame('Count'), height=250)

with col2:
    st.subheader("📋 All Categories Ranked by Gap")
    
    if len(gap_df) > 0:
        st.markdown("**Categories sorted by opportunity (lowest coverage = biggest gap):**")
        st.dataframe(gap_df.sort_values('% Coverage'), hide_index=True, height=400)

st.markdown("---")
st.subheader("📈 Nutrition Profiles by Category")

avg_nutrition = df_filtered.groupby('Primary_Category')[['proteins_100g', 'sugars_100g', 'fat_100g']].mean().round(1)
avg_nutrition = avg_nutrition.sort_values('proteins_100g', ascending=False)
st.dataframe(avg_nutrition, use_container_width=True)

if len(opportunity_products) > 0:
    st.markdown("---")
    st.subheader("🌟 Example Products in Opportunity Zone")
    
    display_cols = ['product_name', 'Primary_Category', 'proteins_100g', 'sugars_100g', 'fat_100g']
    sample = opportunity_products[display_cols].head(10)
    st.dataframe(sample, hide_index=True, use_container_width=True)

st.markdown("---")
st.caption("Story 3: Nutrient Matrix Visualization ✓ | Story 4: The Recommendation ✓")
