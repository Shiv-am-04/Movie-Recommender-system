import streamlit as st
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

omdb_api_key = os.getenv('OMDB_API_KEY')


st.set_page_config(page_title='Movie Recommender')

st.title(":blue[_Movie Recommender_] :movie_camera:")


with open('word_index','rb') as handle:
  word2index = pickle.load(handle)

with open('movie_vectors','rb') as handle:
  vectors = pickle.load(handle)

movies = pd.read_csv('Movies.csv')


def recommender(movie_name):
  if movie_name in word2index:
    index = word2index[movie_name]

    movie_tfidf = vectors[index]

    similar = cosine_similarity(movie_tfidf,vectors)

    score = similar.flatten()

    top_5_index = score.argsort()[::-1][:6]

    top_5_movies = movies['title'].iloc[top_5_index]

    return top_5_movies.to_list()

  return 0


def filter_movies(cast=None,director=None,num_results=10):
  if cast is not None:
    casting = movies[movies['cast'].apply(lambda x: cast in x)]
    if not casting.empty:
      if len(casting['cast']) < num_results:
        return casting['title'][:len(casting['cast'])].to_list()
      return casting['title'][:num_results].to_list()
    else:
      return 0

  if director is not None:
    directors = movies[movies['director'] == director] 
    if not directors.empty:
      return directors['title'].to_list()
    else:
      return 0


def movie_poster(movies_list):
  for movie in movies_list:
    url = f'http://www.omdbapi.com/?t={movie}&apikey={omdb_api_key}'
    response = requests.get(url)
    data = response.json()

    if data.get('Response') == 'True' and data.get('Poster') != 'NA':
      movie_title = data.get('Title')
      movie_poster_ = data.get('Poster')
      movie_year = data.get('Year')
      movie_box_office = data.get('BoxOffice')

      # Display the movie details
      st.write(f"### {movie_title} ({movie_year})")
      st.image(movie_poster_,use_column_width=True)
      st.write(f":orange[**Box Office Collection**] {movie_box_office}")
    
    elif data.get('Response') == 'True' and data.get('Poster') == 'NA':
      movie_title = data.get('Title')
      movie_year = data.get('Year')
      movie_box_office = data.get('BoxOffice')

      st.write(f"### {movie_title} ({movie_year})")
      st.write(f":orange[**Box Office Collection**] {movie_box_office}")
      st.error('sorry movie poster not found')
    
    elif data.get('Poster') == 'NA':
      st.error("Movie not found or no poster available.")





sidebox = st.sidebar.selectbox(
            ':green[**Choose Option**]',
            ("Recommened Movies", "Filter Movies")
        )


if sidebox == "Recommened Movies":
  user_input = st.text_input(label=':blue[***Enter Movie Name***]',placeholder='The Batman Begins')

  if user_input:
    movies = recommender(user_input.lower())
    if movies == 0:
      st.warning('movie not found')
    else:
      movie_poster(movies)

elif sidebox == 'Filter Movies':
  radio_option = ['Cast','Director']

  select_option = st.sidebar.radio(":blue[***Select Any One***]",options=radio_option)
  
  if radio_option.index(select_option) == 0:
    starcast = st.sidebar.text_input(":red[***Actor/Actress***]",placeholder='Tom Cruise')
    if starcast:
      filtered_movies = filter_movies(cast=starcast.lower())
      if filtered_movies == 0:
        st.error('No result found')
      else:
        movie_poster(filtered_movies)
  
  elif radio_option.index(select_option) == 1:
    director = st.sidebar.text_input(":red[***Director***]",placeholder='Cristopher Nolan')
    if director:
      filtered_movies = filter_movies(director=director.lower())
      if filtered_movies == 0:
        st.error('No result found')
      else:
        movie_poster(filtered_movies)


