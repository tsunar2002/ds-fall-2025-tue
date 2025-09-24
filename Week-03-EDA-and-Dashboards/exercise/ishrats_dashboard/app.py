import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="🍿 MovieLens 200k - Week 3 Dashboard",
    layout="wide"
)

# --- CUSTOM THEME (CSS INJECTION) ---
st.markdown("""
<style>
/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #fbc2eb, #a6c1ee);
    font-family: "Trebuchet MS", sans-serif;
    color: #4b006e;
}

/* Sidebar */
.css-1d391kg {
    background: linear-gradient(180deg, #d8b4fe, #fbc2eb);
    color: #4b006e;
}

/* Headings */
h1, h2, h3 {
    color: #6a0dad !important;
    font-weight: bold;
}

/* Dataframe */
.stDataFrame {
    background: white;
    border-radius: 12px;
    padding: 10px;
}

/* Buttons */
.stDownloadButton button, .stButton button {
    background: linear-gradient(90deg, #ec4899, #8b5cf6);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.6em 1em;
    font-weight: bold;
}
.stDownloadButton button:hover, .stButton button:hover {
    background: linear-gradient(90deg, #8b5cf6, #ec4899);
}
</style>
""", unsafe_allow_html=True)

# --- PLOTLY DEFAULT TEMPLATE + DISTINCT PINK/PURPLE PALETTE ---
pio.templates.default = "plotly_white"
PINK_PURPLE_COLORS = [
    "#ec4899",  # bright pink
    "#d946ef",  # violet
    "#8b5cf6",  # purple
    "#a78bfa",  # lavender
    "#f472b6",  # light pink
    "#c026d3",  # deep purple
    "#f9a8d4",  # pastel pink
    "#9333ea",  # royal purple
    "#e879f9",  # magenta
    "#701a75",  # dark plum
]

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("data/movie_ratings.csv")
    # Parse/ensure fields
    if "timestamp" in df.columns:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        except Exception:
            pass
    # Derive rating_year if missing
    if "rating_year" not in df.columns:
        if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["rating_year"] = df["timestamp"].dt.year
        else:
            df["rating_year"] = np.nan
    # Derive decade if missing
    if "decade" not in df.columns and "year" in df.columns:
        df["decade"] = (df["year"] // 10) * 10
    # Clean genres for main analysis (explode-friendly)
    df["genres"] = df["genres"].fillna("").astype(str)
    return df

def filter_frame(df):
    with st.sidebar:
        st.header("Filters")
        genders = st.multiselect("Gender", sorted([g for g in df.get("gender", pd.Series(dtype=str)).dropna().unique()]))
        occupations = st.multiselect("Occupation", sorted([o for o in df.get("occupation", pd.Series(dtype=str)).dropna().unique()]))

        # Age range
        if "age" in df.columns and df["age"].notna().any():
            age_min = int(np.nanmin(df["age"]))
            age_max = int(np.nanmax(df["age"]))
            age_range = st.slider("Age range", min_value=age_min, max_value=age_max, value=(age_min, age_max))
        else:
            age_range = None

        # Rating year
        if "rating_year" in df.columns and df["rating_year"].notna().any():
            ry_min = int(np.nanmin(df["rating_year"]))
            ry_max = int(np.nanmax(df["rating_year"]))
            rating_year = st.slider("Rating year", min_value=ry_min, max_value=ry_max, value=(ry_min, ry_max))
        else:
            rating_year = None

        # Release year
        if "year" in df.columns and df["year"].notna().any():
            y_min = int(np.nanmin(df["year"]))
            y_max = int(np.nanmax(df["year"]))
            rel_year = st.slider("Release year", min_value=y_min, max_value=y_max, value=(y_min, y_max))
        else:
            rel_year = None

        # Minimum sample thresholds & smoothing
        min_n = st.number_input("Min ratings per group (n >=)", min_value=1, value=50, step=1)
        smooth = st.slider("Rolling window for trends (years)", 0, 11, 3)

    mask = pd.Series(True, index=df.index)
    if genders:
        mask &= df.get("gender", pd.Series(index=df.index)).isin(genders)
    if occupations:
        mask &= df.get("occupation", pd.Series(index=df.index)).isin(occupations)
    if ("age" in df.columns) and (age_range is not None):
        mask &= (df["age"] >= age_range[0]) & (df["age"] <= age_range[1])
    if rating_year:
        mask &= (df["rating_year"] >= rating_year[0]) & (df["rating_year"] <= rating_year[1])
    if rel_year:
        mask &= (df["year"] >= rel_year[0]) & (df["year"] <= rel_year[1])

    return df[mask].copy(), min_n, smooth

def explode_genres(df):
    """Explode genres safely for the provided frame."""
    df_expl = df.assign(genres=df["genres"].str.split("|")).explode("genres")
    df_expl["genres"] = df_expl["genres"].str.strip()
    df_expl = df_expl[df_expl["genres"] != ""]
    return df_expl

def top_movies(df, min_count, k=5):
    key = "title" if "title" in df.columns else "movie_id"
    agg = (
        df.groupby(key)
          .agg(n=("rating", "count"), mean_rating=("rating", "mean"))
          .query("n >= @min_count")
          .sort_values(["mean_rating", "n"], ascending=[False, False])
    )
    return agg.head(k).reset_index()

def ec_clean_genres():
    st.subheader("Extra Credit 7: Clean the original genres from movie_ratings_EC.csv")
    st.caption("Hint used: .explode() — this cell demonstrates a from-scratch clean.")
    path = "data/movie_ratings_EC.csv"
    try:
        raw = pd.read_csv(path)
        cleaned = raw.copy()
        cleaned["genres"] = cleaned["genres"].fillna("").astype(str)
        cleaned_expl = cleaned.assign(genres=cleaned["genres"].str.split("|")).explode("genres")
        cleaned_expl["genres"] = cleaned_expl["genres"].str.strip()
        cleaned_expl = cleaned_expl[cleaned_expl["genres"] != ""]
        st.write("Cleaned & exploded sample:", cleaned_expl.head())
        st.download_button(
            "⬇️ Download cleaned (exploded) CSV",
            data=cleaned_expl.to_csv(index=False).encode("utf-8"),
            file_name="movie_ratings_EC_clean_exploded.csv",
            mime="text/csv",
        )
    except FileNotFoundError:
        st.info("data/movie_ratings_EC.csv not found. Place it in the data/ folder to run this step.")

def main():
    st.title("💖💜 MovieLens 200k - Week 3 Dashboard")
    st.markdown("""
Use the filters in the sidebar to refine the analysis. Each section answers a prompt from the exercise.

Notes:
- Movies can belong to multiple genres. We **explode** genres for preference insights (not market share).
- We apply **minimum sample thresholds** to reduce small-sample noise.
- Decade/age-group distributions can be uneven — counts are shown to provide context.
""")

    # Load + filter
    df = load_data()
    st.write("Data preview", df.head())

    fdf, min_n, smooth = filter_frame(df)
    fdf_expl = explode_genres(fdf)  # explode AFTER filtering, to keep alignment

    # 1) Breakdown of genres
    st.header("1) Breakdown of genres for the movies that were rated")
    if not fdf_expl.empty:
        g_counts = (
            fdf_expl.groupby("genres")["rating"]
            .count()
            .rename("n_ratings")
            .sort_values(ascending=False)
            .reset_index()
        )
        fig1 = px.bar(
            g_counts, x="genres", y="n_ratings", color="genres",
            color_discrete_sequence=PINK_PURPLE_COLORS,
            title="Ratings per Genre"
        )
        fig1.update_layout(xaxis_title="Genre", yaxis_title="Number of ratings")
        st.plotly_chart(fig1, width="stretch")
    st.caption("Interpretation: counts reflect ratings tagged to each genre (a movie with multiple genres contributes to each of its genres).")

    # 2) Highest viewer satisfaction by genre (mean rating with min_n)
    st.header("2) Which genres have the highest viewer satisfaction?")
    if not fdf_expl.empty:
        g_mean = (
            fdf_expl.groupby("genres")
            .agg(mean_rating=("rating", "mean"), n=("rating", "count"))
            .query("n >= @min_n")
            .sort_values("mean_rating", ascending=False)
            .reset_index()
        )
        fig2 = px.bar(
            g_mean, x="genres", y="mean_rating", color="genres",
            hover_data=["n"],
            color_discrete_sequence=PINK_PURPLE_COLORS,
            title=f"Mean rating by Genre (n >= {min_n})"
        )
        fig2.update_layout(xaxis_title="Genre", yaxis_title="Mean rating (1-5)")
        st.plotly_chart(fig2, width="stretch")
        st.dataframe(g_mean, use_container_width=True, height=300)

    # 3) Mean rating across movie release years
    st.header("3) Mean rating across release years")
    if "year" in fdf.columns and not fdf.empty:
        yr = (
            fdf.groupby("year")
            .agg(mean_rating=("rating", "mean"), n=("rating", "count"))
            .sort_index()
            .reset_index()
        )
        fig3 = px.line(
            yr, x="year", y="mean_rating",
            title="Mean rating by Release Year",
            color_discrete_sequence=PINK_PURPLE_COLORS
        )
        if smooth and smooth > 0:
            yr["mean_rating_smoothed"] = yr["mean_rating"].rolling(window=smooth, min_periods=1, center=True).mean()
            fig3.add_scatter(x=yr["year"], y=yr["mean_rating_smoothed"], mode="lines", name=f"Smoothed ({smooth}y)")
        fig3.update_layout(xaxis_title="Release year", yaxis_title="Mean rating (1-5)")
        st.plotly_chart(fig3, width="stretch")
        st.dataframe(yr.tail(20), use_container_width=True, height=260)
    else:
        st.info("`year` column not available in the current selection.")

    # 4) Top movies with thresholds (tables keep the theme; no chart needed)
    st.header("4) Top movies by rating with minimum counts")
    colA, colB = st.columns(2)
    with colA:
        st.subheader("At least 50 ratings")
        top50 = top_movies(fdf, 50, k=5) if not fdf.empty else pd.DataFrame()
        st.dataframe(top50, use_container_width=True, height=260)
    with colB:
        st.subheader("At least 150 ratings")
        top150 = top_movies(fdf, 150, k=5) if not fdf.empty else pd.DataFrame()
        st.dataframe(top150, use_container_width=True, height=260)

    st.divider()
    st.header("Extra Credit")

    # 5) Genre vs age trend — avoid Interval dtype by labeling bins as strings
    st.subheader("5) For selected genres, how does rating change as age increases?")
    unique_genres = sorted(fdf_expl["genres"].dropna().unique()) if not fdf_expl.empty else []
    sel_genres = st.multiselect(
        "Pick genres",
        unique_genres[:10],
        default=unique_genres[:4] if len(unique_genres) >= 4 else unique_genres
    )

    if sel_genres and "age" in fdf_expl.columns:
        bins = st.slider("Age bin size", 5, 20, 10, step=5)
        ages = fdf_expl["age"].dropna()
        if ages.empty:
            st.info("No age data available in the current filter selection.")
        else:
            agemin, agemax = int(ages.min()), int(ages.max())
            # Build cut edges and readable labels (strings, not Intervals)
            cut_edges = list(range(agemin, agemax + bins, bins))
            if cut_edges[-1] < agemax + 1:
                cut_edges.append(agemax + 1)
            labels = [f"{b}-{b + bins - 1}" for b in cut_edges[:-1]]

            df_age = fdf_expl[fdf_expl["genres"].isin(sel_genres)].copy()
            df_age["age_bin"] = pd.cut(
                df_age["age"],
                bins=cut_edges,
                labels=labels,
                include_lowest=True,
                right=False
            ).astype(str)

            g_age = (
                df_age.groupby(["genres", "age_bin"], observed=True)
                      .agg(mean_rating=("rating", "mean"), n=("rating", "count"))
                      .reset_index()
            )
            g_age = g_age[g_age["n"] >= min_n]

            if not g_age.empty:
                # Sort age bins by numeric left edge for proper ordering
                g_age["age_bin_order"] = g_age["age_bin"].str.extract(r"^(\d+)").astype(int)
                g_age = g_age.sort_values(["genres", "age_bin_order"]).drop(columns="age_bin_order")

                fig5 = px.line(
                    g_age, x="age_bin", y="mean_rating", color="genres",
                    hover_data=["n"],
                    color_discrete_sequence=PINK_PURPLE_COLORS,
                    title=f"Mean rating vs Age (per genre, n >= {min_n} per bin)"
                )
                st.plotly_chart(fig5, width="stretch")
                st.dataframe(g_age, use_container_width=True, height=300)
            else:
                st.info("No genre/age bins met the minimum n. Lower the threshold or widen bins.")
    else:
        st.info("Select at least one genre and ensure `age` column exists.")

    # 6) Volume vs mean rating per genre
    st.subheader("6) Number of ratings vs mean rating per genre")
    if not fdf_expl.empty:
        vol = (
            fdf_expl.groupby("genres")
            .agg(n=("rating", "count"), mean_rating=("rating", "mean"))
            .reset_index()
        )
        fig6 = px.scatter(
            vol, x="n", y="mean_rating", text="genres",
            color="genres",
            color_discrete_sequence=PINK_PURPLE_COLORS,
            title="Ratings volume vs Mean rating per genre"
        )
        fig6.update_traces(textposition="top center")
        st.plotly_chart(fig6, width="stretch")

        if len(vol) >= 2:
            corr = vol[["n", "mean_rating"]].corr().iloc[0, 1]
            st.caption(f"Pearson correlation between count and mean rating: {corr:.3f}")
    else:
        st.info("No data available for the current filters to compute per-genre volume vs mean rating.")

    # 7) Cleaning original dataset
    ec_clean_genres()

    st.divider()
    st.markdown("""
**Notes & Caveats**
- Exploding genres double-counts multi-genre movies, which is fine for preference profiling but not market share.
- Use the "Min ratings per group (n >=)" control to avoid small-sample noise.
- Age and decade distributions may be uneven — counts are displayed alongside means for context.
""")

if __name__ == "__main__":
    main()
