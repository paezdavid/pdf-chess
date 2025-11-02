import psycopg2
import chess
import chess.svg
from weasyprint import HTML, CSS
from jinja2 import Template
from dotenv import dotenv_values

config = dotenv_values(".env")

def query_database():
    try:
        # Connect to the database
        connection = psycopg2.connect(
            dbname=config["DB_NAME"],
            user=config["USER"],
            password=config["PASSWORD"],
            host=config["HOST"],
            port=config["PORT"]
        )
        
        # Create a cursor object
        cursor = connection.cursor()
        
        # Execute SQL query
        cursor.execute(f"SELECT puzzleid, fen, moves, rating, themes, gameurl FROM puzzles ORDER BY RANDOM() LIMIT 11;")
        
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

        # Insert the variables into a HTML string (jinja!)
        html_string_template_2_per_page = '''
        
            {% for puzzle in puzzles %}
                <div style="display:flex;">
                    <div style="width: 100%; height: 100%;"> {{ puzzles[puzzle]['svg'] }} </div>

                    <div style="width: 100%;">
                        <div style="">
                            <h1 style="text-align:center; text-decoration:underline;">#{{puzzles[puzzle]['puzzlecounter']}} {{puzzles[puzzle]['theme']}}</h1>
                            <h2 style="text-align:center;">{{puzzles[puzzle]['color']}}</h2>
                            <h2 style="text-align:center;">{{puzzles[puzzle]['rating']}}</h2>
                            
                        </div>
                    </div>
                </div>
                
                <div style="text-align: right;">https://lichess.org/training/{{puzzles[puzzle]['puzzleid']}}</div>
                
                <hr style="margin: 2rem 0">
            {% endfor %}
            <h2>Solutions</h2>
            {% for puzzle in puzzles %}
                <li style="list-style-type: none;">#{{puzzles[puzzle]['puzzlecounter']}} - {{puzzles[puzzle]['moves']}}</li>
            {% endfor %}
       
        '''

        html_string_template_grid = '''
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                {% for puzzle in puzzles %}
                    <div>
                        <div style="display: flex; justify-content: space-between;">
                            <p>#{{puzzles[puzzle]['puzzlecounter']}}</p>
                            <p>{{puzzles[puzzle]['color']}}</p>
                            <p>{{puzzles[puzzle]['rating']}}</p>
                        </div>    
                        <div style="width: 100%; height: 100%;">
                            {{ puzzles[puzzle]['svg'] }}
                            <div style="text-align: right; font-size: 10px;">https://lichess.org/training/{{puzzles[puzzle]['puzzleid']}}</div>
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
        # template = Template(html_string_template_2_per_page)
        template = Template(html_string_template_grid)

        css = CSS(string='@page { size: A4; margin: 1.5cm; }')

        # Grab the HTML template string and create a PDF file from it
        HTML(string=template.render(puzzles=data)).write_pdf('./lichess.pdf', stylesheets=[css])


    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
   
    finally:
        # Close cursor and connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

# Call the function to execute the query
query_database()
