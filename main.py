
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from fuzzywuzzy import fuzz
import webbrowser
import sqlite3


# SQL data base pentru a memora watchlistiurile
conn = sqlite3.connect('wishlist_watchlist.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (username TEXT PRIMARY KEY, password TEXT, games_wishlist TEXT, movies_watchlist TEXT)''')
conn.commit()

try:
    games_data = pd.read_csv("data/steam_top_100.csv")
    movies_data = pd.read_csv("data/top_100_movies.csv")
except FileNotFoundError:
    messagebox.showerror("File Not Found", "CSV files not found. Please check the file paths.")
    exit()

# Liste goale pentru wishlisturi
games_wishlist = []
movies_watchlist = []

def add_to_wishlist_or_watchlist(item, category):
    if category == "Games":
        games_wishlist.append(item)
        messagebox.showinfo("Added to Wishlist", f"Game '{item['Game']}' added to your wishlist.")
    elif category == "Movies":
        movies_watchlist.append(item)
        messagebox.showinfo("Added to Watchlist", f"Movie '{item['Title']}' added to your watchlist.")
# cod pentru a cauta pe google chrome jocul/filmul
def search_google(query):
    query = query.replace(" ", "+")
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
# pentru reviewuri
def add_review(item, category):
    def save_review():
        review = review_text.get("1.0", "end-1c")
        rating = rating_scale.get()
        messagebox.showinfo("Review Saved", f"Your review for {item['Title']} is saved.")
        review_window.destroy()

    review_window = tk.Toplevel()
    review_window.title(f"Add Review for {item['Title']}")
    review_window.geometry("1080x1080")

    review_label = tk.Label(review_window, text="Write your review:")
    review_label.pack(pady=5)

    review_text = tk.Text(review_window, height=5, width=30)
    review_text.pack(pady=5)

    rating_label = tk.Label(review_window, text="Rate this:")
    rating_label.pack(pady=5)

    rating_scale = ttk.Scale(review_window, from_=1, to=5)
    rating_scale.pack(pady=5)

    save_button = ttk.Button(review_window, text="Save Review", command=save_review)
    save_button.pack(pady=10)

def apply_filter(data, genre, year):
    filtered_data = data[(data["Genre"].str.contains(genre, case=False)) & (data["Year"] >= int(year))]
    display_list(filtered_data)

def display_list(data, category):
    def load_details(item):
        selected_item = tree.item(item, "values")
        messagebox.showinfo(
            f"{category} Details",
            "\n".join(f"{col}: {val}" for col, val in zip(data.columns, selected_item))
        )

    def add_item_to_list():
        if selected_item:
            if category == "Games":
                games_wishlist.append(selected_item)
                messagebox.showinfo("Added to Wishlist", f"Game '{selected_item['Game']}' added to your wishlist.")
            elif category == "Movies":
                movies_watchlist.append(selected_item)
                messagebox.showinfo("Added to Watchlist", f"Movie '{selected_item['Title']}' added to your watchlist.")
        else:
            messagebox.showwarning("No Selection", "Please select an item first.")

    selected_item = {}

    def on_tree_select(event):
        selected = tree.focus()
        if selected:
            values = tree.item(selected, "values")
            selected_item.clear()
            selected_item.update(dict(zip(data.columns, values)))

    list_window = tk.Toplevel()
    list_window.title(f"Top 100 {category}")
    list_window.geometry("1080x1080")
    list_window.config(bg="#f5f5f5")

    tree = ttk.Treeview(list_window, columns=list(data.columns), show="headings", height=20)
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    for col in data.columns:
        tree.heading(col, text=col, anchor="w")
        tree.column(col, width=200, anchor="w")

    for _, row in data.iterrows():
        tree.insert("", tk.END, values=row.tolist())

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    add_button = ttk.Button(
        list_window,
        text=f"Add to {'Wishlist' if category == 'Games' else 'Watchlist'}",
        command=add_item_to_list
    )
    add_button.pack(pady=5)

    # Search Google Button
    google_button = ttk.Button(
        list_window,
        text="Search on Google",
        command=lambda: search_google(selected_item['Game'] if category == 'Games' else selected_item['Title']) if selected_item else messagebox.showwarning("No Selection", "Please select an item first.")
    )
    google_button.pack(pady=5)

    # Add Review Button
    review_button = ttk.Button(
        list_window,
        text="Add Review",
        command=lambda: add_review(selected_item, category) if selected_item else messagebox.showwarning("No Selection", "Please select an item first.")
    )
    review_button.pack(pady=5)

def display_wishlist_or_watchlist(category):
    if category == "Games":
        display_list(pd.DataFrame(games_wishlist), "Games Wishlist")
    elif category == "Movies":
        display_list(pd.DataFrame(movies_watchlist), "Movies Watchlist")

def search_item(data, query, category):
    query = query.strip()
    if query:
        result = data[data.apply(lambda row: any(fuzz.partial_ratio(query.lower(), str(val).lower()) > 70 for val in row), axis=1)]
        if not result.empty:
            display_list(result, category)
        else:
            messagebox.showinfo("Search Result", f"'{query}' not found in the top 100 {category.lower()} list.")
    else:
        messagebox.showwarning("Search Error", "Please enter a search term.")

def show_statistics():
    game_count = len(games_wishlist)
    movie_count = len(movies_watchlist)
    messagebox.showinfo("Wishlist Statistics", f"You have {game_count} games in your wishlist and {movie_count} movies in your watchlist.")

root = tk.Tk()
root.title("FindersKeepers")
root.geometry("1080x1080")
root.config(bg="#eaeaea")

welcome_label = tk.Label(root, text="Welcome to FindersKeepers", font=("Arial", 18, "bold"), bg="#eaeaea", fg="#333")
welcome_label.pack(pady=20)

buttons_frame = tk.Frame(root, bg="#eaeaea")
buttons_frame.pack(pady=20)

games_button = ttk.Button(buttons_frame, text="Top 100 Games", command=lambda: display_list(games_data, "Games"))
games_button.grid(row=0, column=0, padx=10, pady=10)

movies_button = ttk.Button(buttons_frame, text="Top 100 Movies", command=lambda: display_list(movies_data, "Movies"))
movies_button.grid(row=0, column=1, padx=10, pady=10)

search_label = tk.Label(root, text="Search for a Game or Movie:", font=("Arial", 12), bg="#eaeaea", fg="#333")
search_label.pack(pady=5)

search_frame = tk.Frame(root, bg="#eaeaea")
search_frame.pack(pady=10)

search_entry = ttk.Entry(search_frame, width=30)
search_entry.grid(row=0, column=0, padx=5)

search_games_button = ttk.Button(search_frame, text="Search Games", command=lambda: search_item(games_data, search_entry.get(), "Games"))
search_games_button.grid(row=0, column=1, padx=5)

search_movies_button = ttk.Button(search_frame, text="Search Movies", command=lambda: search_item(movies_data, search_entry.get(), "Movies"))
search_movies_button.grid(row=0, column=2, padx=5)

wishlist_button = ttk.Button(root, text="View Wishlist (Games)", command=lambda: display_wishlist_or_watchlist("Games"))
wishlist_button.pack(pady=10)

watchlist_button = ttk.Button(root, text="View Watchlist (Movies)", command=lambda: display_wishlist_or_watchlist("Movies"))
watchlist_button.pack(pady=10)

statistics_button = ttk.Button(root, text="Wishlist Stats", command=show_statistics)
statistics_button.pack(pady=10)

root.mainloop()