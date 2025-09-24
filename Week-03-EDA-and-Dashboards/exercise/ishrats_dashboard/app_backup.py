import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="MovieLens 200k – Week 3 Dashboard", layout="wide")

@st.cache_data(show_spinner=False)
def load_data():
    # Primary dataset
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
    df_expl = df.assign(genres=df["genres"].str.split("|")).explode("genres")
    df_expl["genres"] = df_expl["genres"].str.strip()
    df_expl = df_expl[df_expl["genres"] != ""]
    return df, df_expl

def filter_frame(df):
    with st.sidebar:
        st.header("Filters")
        genders = st.multiselect("Gender", sorted([g for g in df["gender"].dropna().unique()]))
        occupations = st.multiselect("Occupation", sorted([o for o in df["occupation"].dropna().unique()]))
        # Age
        age_min = int(np.nanmin(df["age"])) if "age" in df.columns else 0
        age_max = int(np.nanmax(df["age"])) if "age" in df.columns else 100
        age_range = st.slider("Age range", min_value=age_min, max_value=age_max, value=(age_min, age_max))
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
        # Minimum sample thresholds
        min_n = st.number_input("Min ratings per group (n ≥)", min_value=1, value=50, step=1)
        smooth = st.slider("Rolling window for trends (years)", 0, 11, 3)
    mask = pd.Series(True, index=df.index)
    if genders:
        mask &= df["gender"].isin(genders)
    if occupations:
        mask &= df["occupation"].isin(occupations)
    if "age" in df.columns:
        mask &= (df["age"] >= age_range[0]) & (df["age"] <= age_range[1])
    if rating_year:
        mask &= (df["rating_year"] >= rating_year[0]) & (df["rating_year"] <= rating_year[1])
    if rel_year:
        mask &= (df["year"] >= rel_year[0]) & (df["year"] <= rel_year[1])
    return df[mask].copy(), min_n, smooth

def top_movies(df, min_count, k=5):
    # Aggregate per movie title (fall back to id if title missing)
    key = "title" if "title" in df.columns else "movie_id"
    agg = (df.groupby(key)
             .agg(n=("rating", "count"), mean_rating=("rating", "mean"))
             .query("n >= @min_count")
             .sort_values(["mean_rating","n"], ascending=[False, False])
          )
    return agg.head(k).reset_index()

def ec_clean_genres():
    st.subheader("Extra Credit 7: Clean the original genres from `movie_ratings_EC.csv`")
    st.caption("Hint used: `.explode()` — this cell demonstrates a from-scratch clean.")
    path = "data/movie_ratings_EC.csv"
    try:
        raw = pd.read_csv(path)
        st.write("Raw sample:", raw.head())
        cleaned = raw.copy()
        cleaned["genres"] = cleaned["genres"].fillna("").astype(str)
        cleaned_expl = cleaned.assign(genres=cleaned["genres"].str.split("|")).explode("genres")
        cleaned_expl["genres"] = cleaned_expl["genres"].str.strip()
        cleaned_expl = cleaned_expl[cleaned_expl["genres"] != ""]
        st.write("Cleaned & exploded sample:", cleaned_expl.head())
        st.download_button("Download cleaned (exploded) CSV",
                           data=cleaned_expl.to_csv(index=False).encode("utf-8"),
                           file_name="movie_ratings_EC_clean_exploded.csv",
                           mime="text/csv")
    except FileNotFoundError:
        st.info("`data/movie_ratings_EC.csv` not found. Place it in the `data/` folder to run this step.")

def main():
    st.title("🎬 MovieLens 200k – Week 3 Dashboard")
    st.markdown(\"\"\"
    Use the filters in the sidebar to refine the analysis. Each section answers a prompt from the exercise.
    Notes:
    - Movies can belong to multiple genres. We **explode** genres for preference insights (not market share).
    - We apply **minimum sample thresholds** to reduce small-sample noise.
    - Decade/age-group distributions can be uneven — counts are shown to provide context.
    \"\"\")
    df, df_expl = load_data()
    st.write("Data preview", df.head())

    # Filters
    fdf, min_n, smooth = filter_frame(df)
    fdf_expl = df_expl.loc[df.index.isin(fdf.index)]

    # 1. Breakdown of genres
    st.header("1) Breakdown of genres for the movies that were rated")
    g_counts = (fdf_expl.groupby("genres")["rating"]
                .count()
                .rename("n_ratings")
                .sort_values(ascending=False)
                .reset_index())
    fig1 = px.bar(g_counts, x="genres", y="n_ratings", title="Ratings per Genre")
    fig1.update_layout(xaxis_title="Genre", yaxis_title="Number of ratings")
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("Interpretation: counts reflect **ratings tagged to each genre** (a movie with multiple genres contributes to each of its genres).")

    # 2. Highest viewer satisfaction by genre (mean rating with min_n)
    st.header("2) Which genres have the highest viewer satisfaction?")
    g_mean = (fdf_expl.groupby("genres")
              .agg(mean_rating=("rating","mean"), n=("rating","count"))
              .query("n >= @min_n")
              .sort_values("mean_rating", ascending=False)
              .reset_index())
    fig2 = px.bar(g_mean, x="genres", y="mean_rating",
                  hover_data=["n"], title=f"Mean rating by Genre (n ≥ {min_n})")
    fig2.update_layout(xaxis_title="Genre", yaxis_title="Mean rating (1–5)")
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(g_mean, use_container_width=True, height=300)

    # 3. Mean rating across movie release years
    st.header("3) Mean rating across release years")
    if "year" in fdf.columns:
        yr = (fdf.groupby("year")
                .agg(mean_rating=("rating","mean"), n=("rating","count"))
                .sort_index()
                .reset_index())
        if smooth and smooth > 0:
            yr["mean_rating_smoothed"] = yr["mean_rating"].rolling(window=smooth, min_periods=1, center=True).mean()
        fig3 = px.line(yr, x="year", y="mean_rating", title="Mean rating by Release Year")
        if "mean_rating_smoothed" in yr.columns:
            fig3.add_scatter(x=yr["year"], y=yr["mean_rating_smoothed"], mode="lines", name=f"Smoothed ({smooth}y)")
        fig3.update_layout(xaxis_title="Release year", yaxis_title="Mean rating (1–5)")
        st.plotly_chart(fig3, use_container_width=True)
        st.dataframe(yr.tail(20), use_container_width=True, height=260)
    else:
        st.info("`year` column not available.")

    # 4. Best-rated movies with thresholds
    st.header("4) Top movies by rating with minimum counts")
    colA, colB = st.columns(2)
    with colA:
        st.subheader("At least 50 ratings")
        top50 = top_movies(fdf, 50, k=5)
        st.dataframe(top50, use_container_width=True, height=260)
    with colB:
        st.subheader("At least 150 ratings")
        top150 = top_movies(fdf, 150, k=5)
        st.dataframe(top150, use_container_width=True, height=260)

    st.divider()
    st.header("Extra Credit")

    # 5. Genre vs age trend
    st.subheader("5) For selected genres, how does rating change as age increases?")
    unique_genres = sorted(fdf_expl["genres"].dropna().unique())
    sel_genres = st.multiselect("Pick genres", unique_genres[:10], default=unique_genres[:4] if len(unique_genres)>=4 else unique_genres)
    if sel_genres and "age" in fdf_expl.columns:
        bins = st.slider("Age bin size", 5, 20, 10, step=5)
        # Create age bins
        ages = fdf_expl["age"].dropna()
        agemin, agemax = (int(ages.min()), int(ages.max())) if not ages.empty else (0,100)
        labels = list(range(agemin, agemax+1, bins))
        fdf_expl["age_bin"] = pd.cut(fdf_expl["age"], bins=list(range(agemin, agemax+bins, bins)), include_lowest=True, right=False)
        g_age = (fdf_expl[fdf_expl["genres"].isin(sel_genres)]
                 .groupby(["genres","age_bin"])
                 .agg(mean_rating=("rating","mean"), n=("rating","count"))
                 .reset_index())
        # Filter by min_n per (genre, age_bin)
        g_age = g_age[g_age["n"] >= min_n]
        if not g_age.empty:
            fig5 = px.line(g_age, x="age_bin", y="mean_rating", color="genres",
                           hover_data=["n"], title=f"Mean rating vs Age (per genre, n ≥ {min_n} per bin)")
            st.plotly_chart(fig5, use_container_width=True)
            st.dataframe(g_age, use_container_width=True, height=300)
        else:
            st.info("No genre/age bins met the minimum n. Lower the threshold or widen bins.")
    else:
        st.info("Select at least one genre and ensure `age` column exists.")

    # 6. Volume vs mean rating per genre
    st.subheader("6) Number of ratings vs mean rating per genre")
    vol = (fdf_expl.groupby("genres")
           .agg(n=("rating","count"), mean_rating=("rating","mean"))
           .reset_index())
    fig6 = px.scatter(vol, x="n", y="mean_rating", text="genres",
                      title="Ratings volume vs Mean rating per genre")
    fig6.update_traces(textposition="top center")
    st.plotly_chart(fig6, use_container_width=True)
    if len(vol) >= 2:
        corr = vol[["n","mean_rating"]].corr().iloc[0,1]
        st.caption(f"Pearson correlation between count and mean rating: **{corr:.3f}**")

    # 7. Cleaning original dataset
    ec_clean_genres()

    st.divider()
    st.markdown(\"\"\"
    **Notes & Caveats**
    - Exploding genres double-counts multi-genre movies, which is fine for preference profiling but not market share.
    - Use the `Min ratings per group (n ≥)` control to avoid small-sample noise.
    - Age and decade distributions may be uneven; counts are displayed alongside means for context.
    \"\"\")

if __name__ == "__main__":
    main()