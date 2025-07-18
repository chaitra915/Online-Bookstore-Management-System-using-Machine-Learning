import streamlit as st
import numpy as np
import sqlite3
import zipfile

DATABASE = "./database.db"

# Path to the zip file and the target file inside the zip
zip_path = "./similarity.zip"
file_to_extract = "similarity.npy"
output_dir = "./"

try:
    # Open the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract the specific file
        zip_ref.extract(file_to_extract, output_dir)
except KeyError:
    print(f"{file_to_extract} not found in {zip_path}")
except zipfile.BadZipFile:
    print("Error: The file is not a valid zip archive.")

# Load the similarity array
similarity = np.load("./similarity.npy")

# Open a new database connection.
def get_connection():
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    return db

# Title of the app
st.title("Book Recommender System :book:")

# Create a database connection
conn = get_connection()
cursor = conn.cursor()

# Retrieve and display book titles
cursor.execute("SELECT title FROM books")

title_rows = cursor.fetchall()

form = st.form("my_form")
option = form.selectbox(
    "Select a book from the dropdown below",
    [row[0] for row in title_rows],
    index=None,
    placeholder="Select a book...",
)
submit_btn = form.form_submit_button('Get Recommendations',
                        use_container_width=True,
                         )
# Main function
def get_similar_books(name: str, cur: sqlite3.Cursor, similarity_data: np.ndarray):
    # Fetch the book index(id)
    query = """SELECT id FROM books
                WHERE title = ?
    """
    cur.execute(query, (name,))
    rows = cur.fetchall()
    
    # Get the id
    book_index = rows[0][0]
    
    # Get the distances and sort them
    distances = similarity_data[book_index]
    
    books_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:9]
    
    # Retrieve the book ids
    book_ids = [item[0] for item in books_list]
    
    # Fetch and display recommended books
    # Create a query with placeholders
    query = "SELECT * FROM books WHERE id IN ({})".format(
        ",".join("?" for _ in book_ids)
    )

    # Execute the query with the values
    cur.execute(query, book_ids)

    # Fetch all matching rows
    rows = cur.fetchall()
    
    # Extract titles and image urls
    titles = []
    image_urls = []
    for row in rows:
        titles.append(row[1])
        image_urls.append(row[-2])

    # Show the results
    row1 = st.columns(4)
    row2 = st.columns(4)
    
    for col, title, image_url in zip(row1 + row2, titles, image_urls):
        tile = col.container(height=300)
        tile.text(title)
        tile.image(image_url)

# display the result when submit button is clicked
if submit_btn:
    get_similar_books(option, cursor, similarity)

# close the database connection
conn.close()