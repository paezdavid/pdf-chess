import psycopg2
import chess
import chess.svg
from weasyprint import HTML, CSS
from jinja2 import Template


def query_database():
    try:
        # Connect to the database
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="admin",
            host="localhost",
            port="5432"
        )
        
        # Create a cursor object
        cursor = connection.cursor()
        
        # Execute SQL query
        cursor.execute(f"SELECT puzzleid, fen, moves, rating, themes FROM lichesspuzzle WHERE rating > 2000 ORDER BY RANDOM() LIMIT 2;")
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        data = {}

        # Display the results
        for row in rows:

            # As the solution is a string, we convert it to a list so we can extract the first move
            solution_list = row[2].split()

            # Insert FEN. The FEN provided by Lichess is one move behind the actual puzzle.
            board = chess.Board(row[1])

            # Add the first move of the puzzle to update the FEN
            board.push(chess.Move.from_uci(solution_list[0]))

            # The FEN that we have after the puzzle has started:
            board.fen()

            # The solution of the puzzle after converting UCI to SAN.
            board.variation_san([chess.Move.from_uci(m) for m in solution_list[1:]])
           
           # Add all the data to a dict to make it more manageable and readable
            data[row[0]] = {
                'fen': row[1],
                'moves': row[2],
                'rating': row[3],
                'themes': row[4],
                'svg': chess.svg.board(board, orientation=chess.WHITE if row[1].split()[1] == 'w' else chess.BLACK, size=330),
                'color': 'White to play' if row[1].split()[1] == 'w' else 'Black to play',
                'theme': row[4].split(' ')[0].capitalize()
            }

        # Insert the variables into a HTML string (jinja!)
        html_string_template = '''
        
            {% for puzzle in puzzles %}
                <div style="display:flex;">
                    <div style="width: 100%; height: 100%;"> {{ puzzles[puzzle]['svg'] }} </div>

                    <div style="width: 100%;">
                        <div style="">
                            <h1 style="text-align:center; text-decoration:underline;">{{puzzles[puzzle]['theme']}}</h1>
                            <h2 style="text-align:center;">{{puzzles[puzzle]['color']}}</h2>
                            <h2 style="text-align:center;">{{puzzles[puzzle]['rating']}}</h2>
                            
                        </div>
                    </div>
                </div>
                <hr style="margin: 2rem 0">
            {% endfor %}
       
        '''

        # Tell the script that my HTML string is a real HTML template
        template = Template(html_string_template)

        css = CSS(string='@page { size: A4; margin: 1.5cm; }')

        # Grab the HTML template string and create a PDF file from it
        HTML(string=template.render(puzzles=data)).write_pdf('./lichess.pdf', stylesheets=[css])


    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
   
    finally:
        # Close cursor and connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

# Call the function to execute the query
query_database()
