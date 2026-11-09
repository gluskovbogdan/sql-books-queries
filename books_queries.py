"""SQL practice: querying a books library with SQLite and pandas.

The script creates the database on first run, fills it with 15 books
and then runs 21 queries: sorting, filtering, LIKE, aggregation,
GROUP BY and a few more advanced queries (subquery, LIMIT).
"""
import sqlite3

import pandas as pd

DB_FILE = "books_library.sqlite"

BOOKS = [
    # title, author, genre, price, pages, release_year, language, country
    ("O‘tgan kunlar", "Abdulla Qodiriy", "Drama", 45000.0, 400, 1926, "Uzbek", "Uzbekistan"),
    ("Mehrobdan chayon", "Abdulla Qodiriy", "Drama", 50000.0, 350, 1929, "Uzbek", "Uzbekistan"),
    ("The Master and Margarita", "Mikhail Bulgakov", "Fantasy", 85000.0, 480, 1967, "Russian", "Russia"),
    ("Atomic Habits", "James Clear", "Self-Help", 95000.0, 320, 2018, "English", "USA"),
    ("1984", "George Orwell", "Fantasy", 60000.0, 328, 1949, "English", "UK"),
    ("Shaytanat", "Tohir Malik", "Detective", 120000.0, 600, 2001, "Uzbek", "Uzbekistan"),
    ("Sariq devni minib", "Xudoyberdi To‘xtaboyev", "Children", 40000.0, 280, 1968, "Uzbek", "Uzbekistan"),
    ("Clean Code", "Robert Martin", "Programming", 150000.0, 464, 2008, "English", "USA"),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Classic", 55000.0, 180, 1925, "English", "USA"),
    ("To Kill a Mockingbird", "Harper Lee", "Classic", 65000.0, 281, 1960, "English", "USA"),
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy", 75000.0, 310, 1937, "English", "UK"),
    ("Python Crash Course", "Eric Matthes", "Programming", 140000.0, 544, 2019, "English", "USA"),
    ("Ikki eshik orasi", "O‘tkir Hoshimov", "Drama", 70000.0, 450, 1986, "Uzbek", "Uzbekistan"),
    ("Dunyoning ishlari", "O‘tkir Hoshimov", "Drama", 48000.0, 230, 1982, "Uzbek", "Uzbekistan"),
    ("Dune", "Frank Herbert", "Fantasy", 90000.0, 412, 1965, "English", "USA"),
]

database = sqlite3.connect(DB_FILE)
cursor = database.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT,
    price REAL,
    pages INTEGER,
    release_year INTEGER,
    language TEXT,
    country TEXT
);
""")

# Fill the table only if it is empty, so re-running does not create duplicates
if cursor.execute("SELECT COUNT(*) FROM books;").fetchone()[0] == 0:
    cursor.executemany(
        "INSERT INTO books (title, author, genre, price, pages, release_year, "
        "language, country) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        BOOKS,
    )
    database.commit()


def run(title, sql):
    """Run a query and print the result as a table."""
    print(f"\n{title}")
    print(pd.read_sql_query(sql, database).to_string(index=False))


print("=== 1. SORTING ===")
run("[1] Books by price (highest first):",
    "SELECT title, author, price FROM books ORDER BY price DESC;")
run("[2] Books by release year (oldest first):",
    "SELECT title, release_year FROM books ORDER BY release_year ASC;")
run("[3] Sorted by genre, then by pages (descending):",
    "SELECT title, genre, pages FROM books ORDER BY genre ASC, pages DESC;")

print("\n=== 2. FILTERING (WHERE) ===")
run("[4] Fantasy books:",
    "SELECT * FROM books WHERE genre = 'Fantasy';")
run("[5] Books more expensive than 70,000:",
    "SELECT title, price FROM books WHERE price > 70000;")
run("[6] Books with 300 to 500 pages:",
    "SELECT title, pages FROM books WHERE pages BETWEEN 300 AND 500;")
run("[7] Books released in 1937, 1965 or 2019:",
    "SELECT title, release_year FROM books WHERE release_year IN (1937, 1965, 2019);")

print("\n=== 3. PATTERN SEARCH (LIKE) ===")
run("[8] Titles containing 'The' (LIKE is case-insensitive in SQLite):",
    "SELECT title FROM books WHERE title LIKE '%The%';")
run("[9] Authors whose name starts with 'J':",
    "SELECT title, author FROM books WHERE author LIKE 'J%';")

print("\n=== 4. MULTIPLE CONDITIONS ===")
run("[10] Uzbek books priced above 50,000:",
    "SELECT title, language, price FROM books WHERE language = 'Uzbek' AND price > 50000;")
run("[11] English books released after 2010:",
    "SELECT title, language, release_year FROM books WHERE language = 'English' AND release_year > 2010;")
run("[12] Fantasy books with more than 400 pages:",
    "SELECT title, genre, pages FROM books WHERE genre = 'Fantasy' AND pages > 400;")

print("\n=== 5. AGGREGATION AND GROUPING ===")
run("[13] Total number of books:",
    "SELECT COUNT(*) AS total_books FROM books;")
run("[14] Average price (rounded to 2 decimals):",
    "SELECT ROUND(AVG(price), 2) AS avg_price FROM books;")
run("[15] Most expensive and cheapest book price:",
    "SELECT MAX(price) AS max_price, MIN(price) AS min_price FROM books;")
run("[16] Number of books per genre:",
    "SELECT genre, COUNT(*) AS book_count FROM books GROUP BY genre;")
run("[17] Average price per language (highest first):",
    "SELECT language, ROUND(AVG(price), 2) AS avg_price FROM books "
    "GROUP BY language ORDER BY avg_price DESC;")
run("[18] Highest price per author:",
    "SELECT author, MAX(price) AS max_author_price FROM books GROUP BY author;")

print("\n=== 6. ADVANCED QUERIES ===")
run("[19] Top 3 most expensive books:",
    "SELECT title, author, price FROM books ORDER BY price DESC LIMIT 3;")
run("[20] Longest book for each language (subquery):", """
    SELECT b1.language, b1.title, b1.author, b1.pages
    FROM books b1
    WHERE b1.pages = (
        SELECT MAX(b2.pages) FROM books b2 WHERE b2.language = b1.language
    );
""")
run("[21] Books released 2018-2022 priced above 60,000:",
    "SELECT title, release_year, price FROM books "
    "WHERE release_year BETWEEN 2018 AND 2022 AND price > 60000;")

database.close()
