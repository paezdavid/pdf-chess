import psycopg2
import chess
import chess.svg
from weasyprint import HTML, CSS
from jinja2 import Template
from dotenv import dotenv_values

config = dotenv_values(".env")

# Connect to the database
connection = psycopg2.connect(
    dbname=config["DB_NAME"],
    user=config["USER"],
    password=config["PASSWORD"],
    host=config["HOST"],
    port=config["PORT"]
)

def get_puzzles_data(rating_min, rating_max, amount):
    """Returns dictionary with all the relevant puzzle data."""
    try:
        cursor = connection.cursor()
        cursor.execute(f"""SELECT puzzleid, fen, moves, rating, themes, gameurl 
                           FROM puzzles
                           WHERE rating >= {rating_min} AND rating <= {rating_max} 
                           ORDER BY RANDOM() 
                           LIMIT {amount};
                        """)
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        data = {}
        puzzle_counter = 1

        # Display the results
        for row in rows:

            # As the solution is a string, we convert it to a list so we can extract the first move
            solution_list = row[2].split()

            # Insert FEN. The FEN provided by Lichess is one move behind the actual puzzle.
            board = chess.Board(row[1])

            # Add the first move of the puzzle to update the FEN
            board.push(chess.Move.from_uci(solution_list[0]))

            # The FEN is updated now:
            board.fen()

            # The solution to the puzzle after converting UCI to SAN.
            solution = board.variation_san([chess.Move.from_uci(m) for m in solution_list[1:]])
            
            # Add all the data to a dict to make it more manageable and readable
            data[row[0]] = {
                'puzzleid': row[0],
                'fen': row[1],
                'moves': solution,
                'rating': row[3],
                'themes': row[4],
                'svg': chess.svg.board(board, orientation=chess.BLACK if row[1].split()[1] == 'w' else chess.WHITE, size=330),
                'color': 'Black to play' if row[1].split()[1] == 'w' else 'White to play',
                'theme': row[4].split(' ')[0].capitalize(),
                'gameurl': row[5],
                'puzzlecounter': puzzle_counter
            }

            puzzle_counter += 1

        return data

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
    finally:
        # Close cursor and connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def generate_puzzles_pdf(paper_size):
    data = get_puzzles_data(2000, 2500, amount=13)

    html_string_template_grid = '''
    <style>
            .puzzle-grid {
                display: grid;
                grid-template-columns: repeat({{ user_columns | default(3) }}, 1fr);
                gap: 1.5rem;
                width: 100%;
                box-sizing: border-box;
            }
            .puzzle-item {
                min-width: 0; 
                display: flex;
                flex-direction: column;
            }
            .puzzle-header {
                display: flex; 
                justify-content: space-between;
                margin-bottom: 5px;
            }
            .puzzle-header p {
                margin: 0;
                font-size: 12px;
            }
            .puzzle-svg-container {
                width: 100%;
                aspect-ratio: 1 / 1; 
            } 
            .puzzle-svg-container svg {
                width: 100%;
                height: 100%;
                display: block;
            }
            .puzzle-footer {
                text-align: right; 
                font-size: 10px;
                margin-top: 4px;
                word-break: break-all; 
            }
        </style>
        
        <div class="puzzle-grid">
            {% for puzzle in puzzles %}
                <div class="puzzle-item">
                    <div class="puzzle-header">
                        <p>#{{puzzles[puzzle]['puzzlecounter']}}</p>
                        <p>{{puzzles[puzzle]['color']}}</p>
                        <p>{{puzzles[puzzle]['rating']}}</p>
                    </div>    
                    <div class="puzzle-svg-container">
                        {{ puzzles[puzzle]['svg'] }}
                    </div>
                    <div class="puzzle-footer">
                        https://lichess.org/training/{{puzzles[puzzle]['puzzleid']}}
                    </div>
                </div>
            {% endfor %}
        </div>
        <div style="page-break-before: always; height: 100%;"></div>        
        <h2>Solutions</h2>
        {% for puzzle in puzzles %}
            <li style="list-style-type: none;">#{{puzzles[puzzle]['puzzlecounter']}} - {{puzzles[puzzle]['moves']}}</li>
        {% endfor %}
    '''

    # Tell the script that my HTML string is an HTML template
    template = Template(html_string_template_grid)
    css = CSS(string=f"@page {{ size: {paper_size}; margin: 1.5cm; }}")

    # Grab the HTML template string and create a PDF file from it
    HTML(string=template.render({'puzzles': data, 'user_columns': 3})).write_pdf('./lichess.pdf', stylesheets=[css])


generate_puzzles_pdf("A4")
