import psycopg2
import chess
import chess.svg

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
        cursor.execute(f"SELECT fen, moves, rating, puzzleid, themes FROM lichesspuzzle LIMIT 2;")
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Display the results
        for row in rows:

            # As the solution is a string, we convert it to a list so we can extract the first move
            solution_list = row[1].split()

            # Insert FEN. The FEN provided by Lichess is one move behind the actual puzzle.
            board = chess.Board(row[0])
            # Add the first move of the puzzle to update the FEN
            board.push(chess.Move.from_uci(solution_list[0]))
            # The FEN that we have after the puzzle has started:
            updated_fen = board.fen()
            # The solution of the puzzle after converting UCI to SAN.
            converted_solution = board.variation_san([chess.Move.from_uci(m) for m in solution_list[1:]])

            # print(f"Rating: {row[2]}")
            # print(f"ID: {row[3]}")
            # print(f"Themes: {row[4]}")
            print(f"FEN: {row[0].split()[1]}")
            print(f"Solution: {converted_solution}")
            print(chess.svg.board(board, orientation=chess.WHITE if row[0].split()[1] == 'w' else chess.BLACK, size=400))
            print(" ")
            print(" ")
        


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
