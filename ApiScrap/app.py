from flask import Flask, render_template
import requests
import pandas as pd 

app = Flask(__name__)

# Initialize an empty DataFrame
df = pd.DataFrame()

for i in range(1, 462):
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/top_rated?api_key=d6d6db9828ca83b2e849b84cf888f842&language=en-US&page={i}")
        response_json = response.json()
        
        # Check if 'results' key exists in the response JSON
        if 'results' in response_json:
            tempdf = pd.DataFrame(response_json['results'])[['id', 'original_title', 'overview', 'popularity', 'release_date', 'vote_average', 'vote_count']]
            df = df.append(tempdf, ignore_index=True)
        else:
            print(f"No results found in response for page {i}")
    except KeyError:
        print(f"KeyError occurred while processing page {i}")

# After the loop, df will contain the concatenated DataFrame


@app.route('/')
def index():
    # Render the template with DataFrame passed to it
    return render_template('home.html', tables=[df.to_html(classes='data', header="true")])


