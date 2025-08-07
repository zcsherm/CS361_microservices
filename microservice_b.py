import pickle
import os
import Player from player_record

PIPE = "player_pipe.txt"
ADD_REQUEST = "ADD"
REMOVE_REQUEST = "REMOVE"
CREATE_REQUEST = "CREATE"
QUIT_REQUEST = "QUIT"
REQUESTS = [ADD_REQUEST, REMOVE_REQUEST, REMOVE_REQUEST, QUIT_REQUEST]

PASSED_READ = "PLAYER"
WHICH_TEAM = "TEAM"
FAILED_READ = "INVALID"

NOT_FOUND = "404"
TIMED_OUT = "408"
FORBIDDEN = "403"
SUCCESS = "200"

PLAYER_DIRECTORY = "players"
MASTER_FILE = PLAYER_DIRECTORY + "/" + "master.pkl"
PLAYER_NAMES = "names.txt"

class Microservice:
    def __init__(self):
        self.make_pipe()
        self.make_player_directory()
        self.last_write = None
        self.main()
        

    def main(self):
        while self.last_write != QUIT_REQUEST:
            time.sleep(1)
            with open(PIPE, "r") as file:
                content = file.read().upper()

        
    def make_pipe(self):
        if not os.path.isfile(path):
            if not os.path.isfile(PIPE):
            with open(PIPE, 'w') as file:
                file.write('')
        
    def make_player_directory(self):
        if not os.path.isdir(PLAYER_DIRECTORY):
            os.mkdir(PLAYER_DIRECTORY)
            self.make_master_file()

    def make_master_file():
        player_names = []
        players = {}
        with open(PLAYER_NAMES,'r') as file:
            for line in file.read():
                player_names.append(line)
        count = 0
        for player in players:
            data = {"name": player,
                    "id": count,
                    "current_team": None
                   }
            players[player_names] = Player(data)
        with open(MASTER_FILE, 'wb') as f:
            pickle.dump(players, f)
            
    def validate_player_exists(self):
        pass

    def validate_player_available(self):
        pass
        
    def validate_player_on_team(self):
        pass
        
    def add_player(self):
        pass

    def remove_player(self):
        pass

    def add_new_player_to_database(self):
        pass

    def route_request(self):
        pass
