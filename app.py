import sqlite3
import os
import argparse
from datetime import datetime
import matplotlib.pyplot as plt

def get_db_connection(db_path='mood_journal.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            rating INTEGER,
            note TEXT,
            tags TEXT
        )
    ''')
    conn.commit()
    return conn


def add_entry():
    conn = get_db_connection()
    c = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')
    # Check if entry for today exists
    c.execute('SELECT * FROM entries WHERE date = ?', (today,))
    existing = c.fetchone()
    if existing:
        print(f"You already have an entry for {today}. It will be updated.")

    # Prompt user
    while True:
        try:
            rating = int(input('Rate your mood today (1-10): '))
            if 1 <= rating <= 10:
                break
            else:
                print('Please enter a number between 1 and 10.')
        except ValueError:
            print('Invalid input. Please enter an integer.')

    note = input('Write a note about your day: ').strip()
    tags = input('Enter activities or tags (comma-separated): ').strip()

    # Insert or replace entry
    c.execute('''
        INSERT INTO entries (date, rating, note, tags) VALUES (?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            rating = excluded.rating,
            note = excluded.note,
            tags = excluded.tags
    ''', (today, rating, note, tags))
    conn.commit()
    conn.close()
    print(f"Entry for {today} saved successfully.")


def visualize():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT date, rating, tags FROM entries ORDER BY date')
    rows = c.fetchall()
    conn.close()

    if not rows:
        print('No entries found. Add some entries first!')
        return

    # Parse data
    dates = [datetime.strptime(r[0], '%Y-%m-%d') for r in rows]
    ratings = [r[1] for r in rows]
    all_tags = [tag.strip().lower() for r in rows for tag in (r[2].split(',') if r[2] else [])]

    # Plot mood over time
    plt.figure()
    plt.plot(dates, ratings, marker='o')
    plt.title('Mood Rating Over Time')
    plt.xlabel('Date')
    plt.ylabel('Mood Rating (1-10)')
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.show()

    # Plot tag frequency
    if all_tags:
        from collections import Counter
        counts = Counter(all_tags)
        tags = list(counts.keys())
        freqs = list(counts.values())

        plt.figure()
        plt.bar(tags, freqs)
        plt.title('Activity/Tag Frequency')
        plt.xlabel('Tag')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    else:
        print('No tags to display.')


def main():
    parser = argparse.ArgumentParser(description='Daily Mood Journal')
    parser.add_argument('action', nargs='?', choices=['add', 'visualize'], default='add',
                        help='"add" to add or update today\'s entry (default), "visualize" to view trends')
    args = parser.parse_args()

    if args.action == 'add':
        add_entry()
    elif args.action == 'visualize':
        visualize()


if __name__ == '__main__':
    main()
