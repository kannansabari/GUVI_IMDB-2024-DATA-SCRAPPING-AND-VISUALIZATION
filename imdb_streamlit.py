import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import mysql.connector


r = st.sidebar.radio('Navigation',['Analysis & Visualization','Filtering'])

if r == 'Analysis & Visualization':

    # Connect to MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="012345678",
        database="movies"
    )
    cursor = connection.cursor()

    st.title("🎬 1.Top 10 Movies by Rating") #! Number 1

    # Run query
    query = "SELECT movie_name, ratings FROM combined_movies ORDER BY ratings DESC LIMIT 10"
    cursor.execute(query)

    # Fetch results and convert to DataFrame
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=["movie_name", "ratings"])

    # Close cursor and connection
    # cursor.close()
    # connection.close()
    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # df.rename_axis("Rank", inplace=True)  # Rename index column for clarity

    # Show the table
    st.dataframe(df)


    st.title("🎬 2.Count of movies for each Genre") #! Number 2

    # Query to count movies per genre
    query = """
        SELECT genre, COUNT(*) AS movie_count
        FROM combined_movies
        GROUP BY genre
        ORDER BY movie_count DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()

    # Convert to DataFrame
    df = pd.DataFrame(results, columns=["Genre", "Movie Count"])

    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # Show data table
    st.dataframe(df)

    # Plot bar chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Genre:N', sort='-y'),
        y=alt.Y('Movie Count:Q'),
        tooltip=['Genre', 'Movie Count']
    ).properties(
        width=700,
        height=400,
        title='🎬 Number of Movies per Genre'
    )

    st.altair_chart(chart, use_container_width=True)

    st.title("🎬 3.Average Duration by Genre") #! Number 3

    # Query to get average duration per genre
    query = """
            SELECT 
        genre,
        AVG(COALESCE(SUBSTRING_INDEX(duration, 'h', 1), 0) * 60 + 
            COALESCE(REGEXP_SUBSTR(duration, '[0-9]+(?=min)'), 0)
        ) AS avg_duration_mins,
        CONCAT(
            FLOOR(AVG(
                COALESCE(SUBSTRING_INDEX(duration, 'h', 1), 0) * 60 +
                COALESCE(REGEXP_SUBSTR(duration, '[0-9]+(?=min)'), 0)
            ) / 60), 'h ',
            LPAD(FLOOR(
                AVG(
                    COALESCE(SUBSTRING_INDEX(duration, 'h', 1), 0) * 60 +
                    COALESCE(REGEXP_SUBSTR(duration, '[0-9]+(?=min)'), 0)
                ) % 60), 2, '0'), 'm'
        ) AS avg_duration_hm
    FROM movies.combined_movies
    WHERE duration IS NOT NULL
    GROUP BY genre
    ORDER BY avg_duration_mins DESC;
    """
    cursor.execute(query)
    results = cursor.fetchall()

    # Convert to DataFrame
    df = pd.DataFrame(results, columns=["Genre", "Average Duration (mins)", "Formatted Duration"])
    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # Show formatted durations
    st.dataframe(df[["Genre", "Formatted Duration"]])

    # Plot numeric durations
    chart = alt.Chart(df).mark_bar().encode(
        y=alt.Y('Genre:N', sort='-x'),
        x=alt.X('Average Duration (mins):Q'),
        tooltip=['Genre', 'Formatted Duration']
    ).properties(
        width=700,
        height=400,
        title='🎬 Average Movie Duration per Genre'
    )

    st.altair_chart(chart, use_container_width=True)

    st.title("🎬 4.	Voting Trends by Genre") #! Number 4
    
    # Execute query
    query = """
        SELECT 
            genre,
            AVG(voting_counts) AS avg_votes
        FROM combined_movies
        WHERE voting_counts IS NOT NULL
        GROUP BY genre
        ORDER BY avg_votes DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()

    # Load into DataFrame
    df = pd.DataFrame(results, columns=["Genre", "Average Votes"])
    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # Show table
    st.dataframe(df)

    # Plot bar chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Average Votes:Q'),
        y=alt.Y('Genre:N', sort='-x'),
        tooltip=['Genre', 'Average Votes']
    ).properties(
        width=700,
        height=400,
        title='📊 Average Voting Counts per Genre'
    )

    st.altair_chart(chart, use_container_width=True)

    st.title("🎬 5.	Rating Distribution") #! Number 5

    # Execute Query
    query = "SELECT ratings FROM combined_movies WHERE ratings IS NOT NULL"
    cursor.execute(query)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=['ratings'])
    df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce")
    df = df.dropna(subset=["ratings"])  # Drop rows that couldn't convert

    # st.dataframe(df)

    # Plot histogram
    hist = alt.Chart(df).mark_bar().encode(
    x=alt.X("ratings:Q", bin=alt.Bin(maxbins=20), title="ratings"),
    y=alt.Y("count():Q", title="Frequency"),
    tooltip=["count()"]
    ).properties(
    width=600,
    height=400,
    title="Distribution of Movie Ratings (Histogram)"
    )

    st.altair_chart(hist, use_container_width=True)

    # box = alt.Chart(df).mark_boxplot(extent='min-max').encode(
    # y=alt.Y("ratings:Q", title="Ratings")
    # ).properties(
    #     width=100,
    #     height=400,
    #     title="Distribution of Movie Ratings (Box Plot)"
    # )

    # st.altair_chart(box, use_container_width=True)

    st.title("🎬 6.	Genre-Based Rating Leaders") #! Number 6

    # Execute Query
    query = """SELECT genre, movie_name, ratings
    FROM movies.combined_movies AS m
    WHERE ratings = (
        SELECT MAX(ratings)
        FROM movies.combined_movies
        WHERE genre = m.genre AND ratings IS NOT NULL
    )
    ORDER BY ratings DESC;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    # Load into DataFrame
    df = pd.DataFrame(results, columns=["Genre", "movie_name", "ratings"])
    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # Show table
    st.dataframe(df)

    st.title("🎬 7.	Most Popular Genres by Voting") #! Number 7

    # Execute query
    query = """
        SELECT genre, SUM(voting_counts) AS total_votes
        FROM combined_movies
        WHERE voting_counts IS NOT NULL
        GROUP BY genre
        ORDER BY total_votes DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=["Genre", "Total Votes"])
    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # Show data table
    st.dataframe(df)

    # Create pie chart using Altair
    pie = alt.Chart(df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Total Votes", type="quantitative"),
        color=alt.Color(field="Genre", type="nominal"),
        tooltip=["Genre", "Total Votes"]
    ).properties(
        title="🗳️ Total Voting Counts by Genre"
    )

    st.altair_chart(pie, use_container_width=True)

    st.title("🎬 8.	Duration Extremes") #! Number 8

    query = """(
    SELECT movie_name, genre, duration,
           COALESCE(SUBSTRING_INDEX(duration, 'h', 1), 0) * 60 +
           COALESCE(REGEXP_SUBSTR(duration, '[0-9]+(?=min)'), 0) AS total_minutes
    FROM movies.combined_movies
    WHERE duration IS NOT NULL
    ORDER BY total_minutes ASC
    LIMIT 1
    )
    UNION ALL
    (
    SELECT movie_name, genre, duration,
        COALESCE(SUBSTRING_INDEX(duration, 'h', 1), 0) * 60 +
        COALESCE(REGEXP_SUBSTR(duration, '[0-9]+(?=min)'), 0) AS total_minutes
    FROM movies.combined_movies
    WHERE duration IS NOT NULL
    ORDER BY total_minutes DESC
    LIMIT 1
    );
    """
    cursor.execute(query)
    results = cursor.fetchall()
    # Load into dataframe
    df = pd.DataFrame(results, columns=["Movie Name", "Genre", "Duration", "Total Minutes"])

    # Card-style display
    st.markdown("## 🎬 Shortest and Longest Movies")

    for i, row in df.iterrows():
        label = "📏 Shortest Movie" if i == 0 else "📐 Longest Movie"
        st.markdown(f"""
        <div style="
            border: 2px solid #4f4f4f;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #f9f9f9;
        ">
            <h4>{label}</h4>
            <p><strong>Title:</strong> {row['Movie Name']}</p>
            <p><strong>Genre:</strong> {row['Genre']}</p>
            <p><strong>Duration:</strong> {row['Duration']}</p>
            <p><strong>Total Minutes:</strong> {row['Total Minutes']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.title("🎬 9.	Ratings by Genre") #! Number 9

    query = """
    # SELECT genre, ROUND(AVG(ratings), 2) AS avg_rating
    SELECT genre, ratings
    FROM movies.combined_movies
    WHERE ratings IS NOT NULL
    # GROUP BY genre
    # ORDER BY avg_rating DESC;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    df = pd.DataFrame(results, columns=["Genre", "Rating"])
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df = df.dropna()

    # Group by genre and compute average
    df_avg = df.groupby("Genre", as_index=False)["Rating"].mean().round(2)
    df_avg.rename(columns={"Rating": "Average Rating"}, inplace=True)
    df_avg["Metric"] = "Average Rating"  # Add a constant column

    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # Show data table
    st.dataframe(df_avg)

    heatmap = alt.Chart(df_avg).mark_rect().encode(
        x=alt.X('Genre:N'),
        y=alt.Y('Metric:N'),
        color=alt.Color('Average Rating:Q', scale=alt.Scale(scheme='blues')),
        tooltip=['Genre', 'Average Rating']
    ).properties(
        width=400,
        height=300,
        title='🔥 Average Ratings by Genre (Heatmap)'
    )

    st.altair_chart(heatmap, use_container_width=True)

    st.title("🎬 10.	Correlation Analysis") #! Number 10

    # Execute query
    query = """
        SELECT ratings, voting_counts
        FROM combined_movies
        WHERE ratings IS NOT NULL AND voting_counts IS NOT NULL
    """
    cursor.execute(query)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=["Rating", "Voting Count"])

    # Ensure numeric types
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Voting Count"] = pd.to_numeric(df["Voting Count"], errors="coerce")
    df = df.dropna()

    # Scatter plot
    scatter = alt.Chart(df).mark_circle(size=60, opacity=0.5).encode(
        x=alt.X("Rating:Q", scale=alt.Scale(domain=[0, 10])),
        y=alt.Y("Voting Count:Q"),
        tooltip=["Rating", "Voting Count"]
    ).properties(
        width=700,
        height=400,
        title="🎯 Relationship Between Ratings and Voting Counts"
    )

    st.altair_chart(scatter, use_container_width=True)

    # Clean up
    cursor.close()
    connection.close()





if r == "Filtering":
    import streamlit as st
    import pandas as pd
    import mysql.connector

    # Connect to MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="012345678",
        database="movies"
    )
    cursor = connection.cursor()

    # Execute query
    query = """
        SELECT 
            movie_name,
            genre,
            ratings,
            voting_counts,
            duration,
            COALESCE(SUBSTRING_INDEX(duration, 'h', 1), 0) * 60 +
            COALESCE(REGEXP_SUBSTR(duration, '[0-9]+(?=min)'), 0) AS total_minutes
        FROM combined_movies
        WHERE ratings IS NOT NULL AND voting_counts IS NOT NULL AND duration IS NOT NULL
    """
    cursor.execute(query)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=["Movie Name", "Genre", "Rating", "Voting Count", "Duration", "Total Minutes"])

    # Sidebar filters
    st.sidebar.header("🎛️ Filter Movies")

    # Duration filter
    duration_option = st.sidebar.selectbox("Duration (Hours)", ["All", "< 2 hrs", "2–3 hrs", "> 3 hrs"])
    if duration_option == "< 2 hrs":
        df = df[df["Total Minutes"] < 120]
    elif duration_option == "2–3 hrs":
        df = df[(df["Total Minutes"] >= 120) & (df["Total Minutes"] <= 180)]
    elif duration_option == "> 3 hrs":
        df = df[df["Total Minutes"] > 180]
    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # Rating filter
    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 7.0, 0.1)
    df = df[df["Rating"] >= min_rating]
    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # Voting count filter
    min_votes = st.sidebar.number_input("Minimum Voting Count", min_value=0, value=10000)
    df = df[df["Voting Count"] >= min_votes]
    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # Genre filter
    genres = df["Genre"].dropna().unique().tolist()
    selected_genres = st.sidebar.multiselect("Select Genres", genres, default=genres)
    df = df[df["Genre"].isin(selected_genres)]
    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    # Display filtered results
    st.title("🎬 Filtered Movie Results")
    df.index = range(1, len(df) + 1)  # Reset index to start from 1
    st.dataframe(df.reset_index(drop=True))

    # Clean up
    cursor.close()
    connection.close()


# st.title("Home")
# col1,col2 = st.columns(2,gap = "small")
# col1.image(r"I:\My Drive\Pictures\Our pics\IMG_5348.JPG")
# col2.image(r"I:\My Drive\Pictures\Our pics\IMG_5348.JPG")

# tab1,tab2 = st.tabs(['image','Video'])
# tab1.image(r"I:\My Drive\Pictures\Our pics\IMG_5348.JPG")
# tab2.video(r"https://www.youtube.com/watch?v=tYslGmi48oM")
