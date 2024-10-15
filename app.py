from flask import Flask,render_template,request
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import requests

with open('word_index','rb') as handle:
  word2index = pickle.load(handle)

with open('movie_vectors','rb') as handle:
  vectors = pickle.load(handle)

movies = pd.read_csv('Movies.csv')


def recommender(movie_name):
  index = word2index[movie_name]

  movie_tfidf = vectors[index]

  similar = cosine_similarity(movie_tfidf,vectors)

  score = similar.flatten()

  top_5_index = score.argsort()[::-1][:6]

  top_5_movies = movies['title'].iloc[top_5_index]

  return top_5_movies.to_list()


def filter_movies(search,num_results=10):
  # num_results = int(num_results)
  genres = movies[movies['genres'].apply(lambda x: search in x and 'Adventure' not in x and 'Fantasy' not in x)]
  if not genres.empty:
    if len(genres['genres']) < num_results:
      return genres['title'][:len(genres['genres'])]
    return genres['title'][:num_results]

  cast = movies[movies['cast'].apply(lambda x: search in x)]
  if not cast.empty:
    if len(cast['cast']) < num_results:
      return cast['title'][:len(cast['cast'])]
    return cast['title'][:num_results]

  director = movies[movies['director'] == 'search']
  if not director.empty:
    return director['title']

  return ['No Results!']

# def recommended_movie_poster(recommend_movies):



OMDB_API_KEY = '95227554'

app = Flask(__name__)

@app.route("/")
def index():
  return render_template('index.html')


@app.route("/recommend",methods=['GET','POST'])
def recommend():
  movie = request.form.get('movie')
  genre_actor_director = request.form.get('genre_actor_director')
  number_of_results = int(request.form.get('number_of_results',10) or 10)
  search_method = request.form.get('search_method')

  recommend_movie_posters = []
  filter_movie = []

  # if search_method == 'recommend':
  recommend_movies = recommender(movie)
  for movie in recommend_movies:
    url = f'http://www.omdbapi.com/?t={movie}&apikey={OMDB_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if data.get('Response') == 'True' and data.get('Poster') != 'NA':
        recommend_movie_posters.append({
                            'title':data.get('Title'),
                            'year':data.get('Year'),
                            'poster':data.get('Poster'),
                            'collection':data.get('BoxOffice')
                            })

  # if search_method == 'filter':
  filtered_movies = filter_movies(genre_actor_director,number_of_results)
  for movie in filtered_movies:
    url = f'http://www.omdbapi.com/?t={movie}&apikey={OMDB_API_KEY}'
    response = requests.get(url=url)
    dat = response.json()

    if dat.get('Response') == True and dat.get('Poster') != 'NA':
      filter_movie.append({'title':dat.get('Title'),
                          'year':dat.get('Year'),
                          'poster':dat.get('Poster'),
                          'collection':dat.get('BoxOffice')
      })

  return render_template('index.html',recommend_movie_posters=recommend_movie_posters,filter_movie=filter_movie)


if __name__ == '__main__':
  app.run(host='0.0.0.0',debug=True)

