import requests



headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNzRjMzE3NWJjMGExNzNiMDkwZjkyZTljMjQ3NzRmNyIsIm5iZiI6MTY4NTExOTk1MS42MzM5OTk4LCJzdWIiOiI2NDcwZTNjZjc3MDcwMDAwZGYxNDAxY2IiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.NMt1OBO3u48WnAvkNhJPNfElncshpahxxq2xpOgp9Ag",
}

def get_popular_movies(page=1):
    global headers
    url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={page}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    else:
        return[]
    

def get_toprated_movies():
    global headers
    url = "https://api.themoviedb.org/3/movie/top_rated?language=en-US&page=1"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        print("Failed get top rated: ", response.status_code)
        return []
    
def get_movie_details(movie_id):
    global headers
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed get top rated: ", response.status_code)
        return []
    

def get_images_detail(movie_id):
    global headers
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?include_image_language=en"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed get images: ", response.status_code)
        return {}


def get_movie_videos(movie_id):
    global headers
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?language=en-US"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        print("Failed get videos: ", response.status_code)
        return []
    

def get_recomendation(movie_id):
    global headers
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?language=en-US&page=1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        print("Failed get  recomendation: ", response.status_code)
        return []
    

def search_movies(query, page=1):
    global headers
    url = f"https://api.themoviedb.org/3/search/movie?query={query}&include_adult=true&language=en-US&page={page}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        print("Failed search movies: ", response.status_code)
        return []