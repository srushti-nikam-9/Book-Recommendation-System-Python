from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd

# Load data
popular_df = pickle.load(open('popular.pkl', 'rb'))
new_popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)


@app.route('/')
def index():
    image_urls = new_popular_df['Image-URL-M'].values
    if all(pd.isnull(image) for image in image_urls):
        image_urls = new_popular_df['Image-URL-L'].values

    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(image_urls),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['post'])
def recommend():
    user_input = request.form.get('user_input', '').strip().lower()  # Convert input to lowercase
    message = 'Book not found'

    # Convert all pt.index to lowercase for case-insensitive comparison
    pt_index_lower = [title.lower() for title in pt.index]

    if user_input not in pt_index_lower:
        return render_template('recommend.html', message=message)

    # Find the index of the book in the lowercase list
    index = pt_index_lower.index(user_input)
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html', data=data)


# if __name__ == '__main__':
#     app.run(debug=True)
