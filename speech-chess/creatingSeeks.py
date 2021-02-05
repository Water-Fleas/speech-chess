from itertools import zip_longest
import json
import requests
import ast
import chess


def main():
    headers = {"Authorization": "Bearer ytmQMWc5DGPbVuQe"}
    play_game(headers)


def play_game(headers):
    board = chess.Board()
    game_parameters = {
        "rated": "false",
        "time": "10",
        "increment": "0"
    }
    game_id = find_game(headers, game_parameters)
    r = requests.get(f'https://lichess.org/api/board/game/stream/{game_id}', headers=headers, stream=True)
    first_time = True
    side = 0
    for line in r.iter_lines():
        if first_time:
            if line:
                update = json.loads(line)
                if update['white']['name'] == 'Thunderfleas':
                    print("White")
                    board = play_move(board, game_id, headers)
                    side = 1
                else:
                    print("Black")
                first_time = False
        else:
            if line:
                update = json.loads(line)
                if 'status' in update:
                    if update['status'] != 'started':
                        break
                if 'moves' in update and update['status'] == 'started':
                    move_list = update['moves'].split()
                    print(move_list)
                    if len(move_list) % 2 != side:
                        board.push_uci(f'{move_list[-1]}')
                        play_move(board, game_id, headers)
    play_another = ""
    legal_answers = ['y', 'n']
    while play_another not in legal_answers:
        play_another = input("would you like to play another? y/n ")
    if play_another == 'y':
        play_game(headers=headers)


def play_move(x, game_id, headers):
    board = x
    while True:
        try:
            x = input('What is your next move? ')
            if x.lower() == "resign":
                requests.post(f'https://lichess.org/api/board/game/{game_id}/resign', headers=headers)
                return "0000"
            else:
                move = board.push_san(f"{x}")
                requests.post(f'https://lichess.org/api/board/game/{game_id}/move/{board.uci(move)}', headers=headers)
                return board
        except ValueError:
            print('you absolute clown. you complete fool. wrong.')


def find_game(headers, parameters):
    event = requests.get('https://lichess.org/api/stream/event', headers=headers, stream=True)
    seek = requests.post('https://lichess.org/api/board/seek', headers=headers, data=parameters, stream=True)
    for item, line in zip_longest(event, seek):
        if item or line:
            pass
        if item != b'\n':
            dict_str = item.decode("UTF-8")
            intermediate = ast.literal_eval(dict_str)
            return intermediate['game']['id']


if __name__ == '__main__':
    main()
