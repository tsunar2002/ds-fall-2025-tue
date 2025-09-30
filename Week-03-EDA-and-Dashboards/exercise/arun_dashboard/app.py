from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

st.set_page_config(page_title="MovieLens Dashboard (Week 3)", layout="wide")

@st.cache_data(ttl=3600)
def load_movie_ratings() -> pd.DataFrame:
    df = pd.read_csv("../../data/movie_ratings.csv")
    return df


def render_header() -> None:
    st.title("🎬 MovieLens Analytics Dashboard")
    st.caption("Week 3 - EDA and Dashboards | Exploring 200k+ Movie Ratings")
    
    df = load_movie_ratings()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Ratings", f"{len(df):,}")
    with col2:
        st.metric("Unique Movies", f"{df['movie_id'].nunique():,}")
    with col3:
        st.metric("Users", f"{df['user_id'].nunique():,}")
    with col4:
        st.metric("Avg Rating", f"{df['rating'].mean():.2f}")


def render_sidebar(df: Optional[pd.DataFrame]) -> dict:
    with st.sidebar:
        st.header("📊 Dashboard Controls")
        show_raw = st.toggle("Show raw data preview", value=False)
        
        st.markdown("---")
        st.markdown("**Dataset Info:**")
        st.write(f"• {len(df):,} total ratings")
        st.write(f"• {df['genres'].nunique()} unique genres")
        st.write(f"• Years: {int(df['year'].min())} - {int(df['year'].max())}")

        controls = {"show_raw": show_raw}
        return controls


def main() -> None:
    render_header()
    df = load_movie_ratings()
    controls = render_sidebar(df)

    if controls.get("show_raw"):
        with st.expander("📋 Raw data preview (first 50 rows)", expanded=False):
            st.dataframe(df.head(50), use_container_width=True)

    tabs = st.tabs([
        "📊 Q1: Genre Distribution",
        "⭐ Q2: Genre Satisfaction", 
        "📈 Q3: Rating Trends Over Time",
        "🏆 Q4: Top-Rated Movies",
    ])

    with tabs[0]:
        st.subheader("📊 Q1: What's the breakdown of genres for movies that were rated?")

        genre_counts = (
            df.groupby("genres", dropna=False)
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

        total = genre_counts["count"].sum()
        genre_counts["pct"] = 100 * genre_counts["count"] / max(total, 1)

        fig = px.treemap(
            genre_counts,
            path=['genres'],
            values='count',
            title="Genre Distribution (Treemap)",
            color='count',
            color_continuous_scale='viridis'
        )
        
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📈 Genre Insights")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Most Popular", genre_counts.iloc[0]['genres'], 
                     f"{genre_counts.iloc[0]['count']:,} ratings")
        with col2:
            st.metric("Total Genres", len(genre_counts))
        with col3:
            st.metric("Market Share", f"{genre_counts.iloc[0]['pct']:.1f}%")


    with tabs[1]:
        st.subheader("⭐ Q2: Which genres deliver the highest viewer satisfaction?")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            min_count = st.number_input(
                "Min ratings per genre",
                min_value=10,
                max_value=5000,
                value=100,
                step=50,
                help="Filter out genres with few ratings",
            )
            
            show_error_bars = st.checkbox(
                "Show confidence intervals",
                value=True,
                help="Display 95% confidence intervals"
            )

        genre_stats = (
            df.groupby("genres", dropna=False)
            .agg({
                'rating': ['mean', 'std', 'count'],
                'user_id': 'nunique'
            })
            .reset_index()
        )
        genre_stats.columns = ['genres', 'mean_rating', 'std_rating', 'n_ratings', 'n_users']
        
        genre_stats['se'] = genre_stats['std_rating'] / np.sqrt(genre_stats['n_ratings'])
        genre_stats['ci_lower'] = genre_stats['mean_rating'] - 1.96 * genre_stats['se']
        genre_stats['ci_upper'] = genre_stats['mean_rating'] + 1.96 * genre_stats['se']
        
        filtered = genre_stats[genre_stats["n_ratings"] >= min_count].copy()
        filtered = filtered.sort_values("mean_rating", ascending=True)

        with col1:
            if show_error_bars:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=filtered['genres'],
                    x=filtered['mean_rating'],
                    orientation='h',
                    error_x=dict(
                        type='data',
                        symmetric=False,
                        array=filtered['ci_upper'] - filtered['mean_rating'],
                        arrayminus=filtered['mean_rating'] - filtered['ci_lower'],
                        thickness=2
                    ),
                    marker=dict(
                        color=filtered['mean_rating'],
                        colorscale='RdYlGn',
                        showscale=True,
                        colorbar=dict(title="Avg Rating")
                    ),
                    hovertemplate='<b>%{y}</b><br>' +
                                'Rating: %{x:.2f}<br>' +
                                'Count: %{customdata:,}<extra></extra>',
                    customdata=filtered['n_ratings']
                ))
                fig.update_layout(
                    title="Average Rating by Genre (with 95% CI)",
                    xaxis_title="Average Rating",
                    yaxis_title="Genre"
                )
            else:
                fig = px.bar(
                    filtered,
                    y="genres",
                    x="mean_rating",
                    orientation="h",
                    hover_data={"n_ratings": ":,", "n_users": ":,", "mean_rating": ":.2f"},
                    title="Average Rating by Genre",
                    color="mean_rating",
                    color_continuous_scale="RdYlGn",
                    text="mean_rating"
                )
                fig.update_traces(texttemplate='%{text:.2f}', textposition='inside')
                
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("🎯 Genre Performance Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**🏆 Top 5 Highest Rated:**")
            top_5 = filtered.tail(5)
            for _, row in top_5[::-1].iterrows():
                st.write(f"**{row['genres']}**: {row['mean_rating']:.2f} ⭐ ({row['n_ratings']:,} ratings)")
        with col2:
            st.write("**📉 Bottom 5 Genres:**")
            bottom_5 = filtered.head(5)
            for _, row in bottom_5.iterrows():
                st.write(f"**{row['genres']}**: {row['mean_rating']:.2f} ⭐ ({row['n_ratings']:,} ratings)")

    with tabs[2]:
        st.subheader("📈 Q3: How do movie ratings evolve over time?")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            time_grouping = st.radio(
                "Time Grouping:",
                ["By Year", "By Decade"],
                key="time_group"
            )
            
            min_count_year = st.number_input(
                "Min ratings per period",
                min_value=10,
                max_value=10000,
                value=100,
                step=50,
            )
            
            show_trend = st.checkbox(
                "Show trend line",
                value=True
            )

        time_col = 'year' if time_grouping == "By Year" else 'decade'
        
        time_stats = (
            df.groupby(time_col, dropna=False)
            .agg({
                'rating': ['mean', 'count', 'std'],
                'movie_id': 'nunique'
            })
            .reset_index()
        )
        time_stats.columns = [time_col, 'mean_rating', 'n_ratings', 'std_rating', 'n_movies']
        
        time_filtered = time_stats[time_stats["n_ratings"] >= min_count_year].copy()
        time_filtered = time_filtered.sort_values(time_col)

        with col1:
            if time_grouping == "By Year":
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=time_filtered[time_col],
                    y=time_filtered['mean_rating'],
                    mode='lines+markers',
                    name='Average Rating',
                    line=dict(color='#ff6b6b', width=3),
                    marker=dict(size=8),
                    fill='tonexty' if not show_trend else None,
                    hovertemplate='<b>Year %{x}</b><br>' +
                                'Rating: %{y:.2f}<br>' +
                                'Total Ratings: %{customdata:,}<extra></extra>',
                    customdata=time_filtered['n_ratings']
                ))
                
                if show_trend:
                    z = np.polyfit(time_filtered[time_col], time_filtered['mean_rating'], 2)
                    p = np.poly1d(z)
                    trend_line = p(time_filtered[time_col])
                    
                    fig.add_trace(go.Scatter(
                        x=time_filtered[time_col],
                        y=trend_line,
                        mode='lines',
                        name='Trend Line',
                        line=dict(color='orange', width=2, dash='dash')
                    ))
                
                fig.update_layout(
                    title="Movie Rating Evolution Over Years",
                    xaxis_title="Release Year",
                    yaxis_title="Average Rating",
                    hovermode='x unified'
                )
            else:
                fig = px.bar(
                    time_filtered,
                    x=time_col,
                    y='mean_rating',
                    hover_data={'n_ratings': ':,', 'n_movies': ':,'},
                    title="Average Rating by Decade",
                    color='mean_rating',
                    color_continuous_scale='viridis',
                    text='mean_rating'
                )
                fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig.update_layout(xaxis_title="Decade", yaxis_title="Average Rating")
            
            st.plotly_chart(fig, use_container_width=True)

        if not time_filtered.empty:
            st.subheader("📊 Temporal Insights")
            col1, col2, col3 = st.columns(3)
            with col1:
                best_period = time_filtered.loc[time_filtered["mean_rating"].idxmax()]
                period_name = "Year" if time_grouping == "By Year" else "Decade"
                st.metric(f"Best {period_name}", int(best_period[time_col]), 
                         f"{best_period['mean_rating']:.2f} ⭐")
            with col2:
                worst_period = time_filtered.loc[time_filtered["mean_rating"].idxmin()]
                st.metric(f"Worst {period_name}", int(worst_period[time_col]), 
                         f"{worst_period['mean_rating']:.2f} ⭐")
            with col3:
                correlation = np.corrcoef(time_filtered[time_col], time_filtered['mean_rating'])[0,1]
                trend_emoji = "📈" if correlation > 0.1 else "📉" if correlation < -0.1 else "➡️"
                st.metric("Overall Trend", f"{trend_emoji}", f"r = {correlation:.3f}")

    with tabs[3]:
        st.subheader("🏆 Q4: What are the best-rated movies with sufficient ratings?")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_thresholds = st.multiselect(
                "Rating thresholds to compare:",
                [25, 50, 100, 150, 250, 500],
                default=[50, 150],
                max_selections=3
            )

        if not selected_thresholds:
            st.warning("Please select at least one threshold.")
            return

        movie_stats = (
            df.groupby(["movie_id", "title"], dropna=False)
            .agg(mean_rating=("rating", "mean"), n_ratings=("rating", "size"))
            .reset_index()
        )

        cols = st.columns(len(selected_thresholds))
        
        for i, threshold in enumerate(selected_thresholds):
            with cols[i]:
                st.write(f"**Top 5 Movies ({threshold}+ ratings)**")
                
                movie_filtered = movie_stats[movie_stats["n_ratings"] >= threshold].copy()
                top_movies = movie_filtered.sort_values(
                    ["mean_rating", "n_ratings"], ascending=[False, False]
                ).head(5)

                if not top_movies.empty:
                    fig = px.bar(
                        top_movies,
                        y="title",
                        x="mean_rating",
                        orientation="h",
                        hover_data={"n_ratings": True, "mean_rating": ":.2f"},
                        color="n_ratings",
                        color_continuous_scale="viridis",
                        height=400
                    )
                    fig.update_layout(
                        xaxis_title="Rating",
                        yaxis_title="",
                        showlegend=False,
                        margin=dict(l=10, r=10, t=30, b=10)
                    )
                    fig.update_traces(texttemplate='%{x:.2f}', textposition='inside')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No movies meet {threshold}+ threshold")

if __name__ == "__main__":
    main()