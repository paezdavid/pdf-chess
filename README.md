Generate a PDF file with some chess puzzles.

<img width="1429" height="1004" alt="Screenshot from 2025-11-01 23-58-30" src="https://github.com/user-attachments/assets/10b3b921-3e60-40da-9dad-99017371da9b" />

As this is a work in progress, the PDF generation is only working locally.
If you want to test it you will need to setup the Lichess puzzle database on your machine.

- Download the CSV file with all puzzle data from the Lichess website.
- Copy that data to a local PostgreSQL database. If you are using `psql` and Ubuntu you may try the following:
  - Create the table on your psql session:
    - `CREATE TABLE chess_puzzles (
    puzzleid TEXT,
    fen TEXT,
    moves TEXT,
    rating INTEGER,
    ratingdeviation INTEGER,
    popularity TEXT,
    nbplays INTEGER,
    themes TEXT,
    gameurl TEXT,
    openingtags TEXT);`
  - Import the data to the database
    - `psql -U your_user -d your_database -c "\copy chess_puzzles FROM '/path/to/your/file.csv' WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');"`

Then, to run the project:
- Activate a virtual environment
- Add a `.env` file with your database credentials
- `pip install -r requirements.txt `
- `python3 app.py`

To-do:
- Limit amount of puzzles 
- Add more parameters and customization
- Add UI
