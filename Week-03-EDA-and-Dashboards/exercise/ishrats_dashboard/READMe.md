# MovieLens 200k – Week 3 Dashboard: 
visit here: https://ishratsmoviedashboard.streamlit.app/

This repo contains a Streamlit dashboard and optional notebook to analyze ratings from the MovieLens 200k dataset.

## Files
- `app.py` — Streamlit app answering all required questions + extra credit.
- `requirements.txt` — Python dependencies.
- *(Optional)* `MovieLens_Week3.ipynb` — Starter notebook (if you add one).

## Data
Place the datasets in a `data/` folder relative to your run location:
- `data/movie_ratings.csv` (required)
- `data/movie_ratings_EC.csv` (optional for Extra Credit 7)

## How to run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## What’s included
- Filters: gender, occupation, age range, rating year, release year, min sample, smoothing
- Q1: Genre breakdown (bar)
- Q2: Viewer satisfaction by genre with min-n (bar + table)
- Q3: Mean rating across release years with optional smoothing (line + table)
- Q4: Top 5 movies with ≥50 and ≥150 ratings (tables)
- EC5: Age vs rating by selected genres with binning & min-n (line + table)
- EC6: Ratings count vs mean rating per genre + correlation (scatter)
- EC7: Cleaning `movie_ratings_EC.csv` with `.explode()` + download button
