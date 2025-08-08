import pickle
import os
import Player from player_record

PIPE = "player_pipe.txt"
ADD_REQUEST = "ADD"
REMOVE_REQUEST = "REMOVE"
CREATE_REQUEST = "CREATE"
QUIT_REQUEST = "QUIT"
USER_SELECT = "USER"
REQUESTS = [ADD_REQUEST, REMOVE_REQUEST, REMOVE_REQUEST, QUIT_REQUEST]

REQUESTS = {ADD_REQUEST: }
WHICH_PLAYER = "PLAYER"
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
        self.requests = {
                        ADD_REQUEST: self.add_player,
                        REMOVE_REQUEST: self.remove_player,
                        CREATE_REQUEST: self.add_new_player_to_database,
                        QUIT_REQUEST: self.quit
                        }
        self.make_pipe()
        self.make_player_directory()
        self.open_master()
        self.last_write = None
        self.main()
        

    def main(self):
        print(f"listening on {PIPE}...")
        while self.last_write != QUIT_REQUEST:
            time.sleep(1)
            with open(PIPE, "r") as file:
                content = file.read().upper()
            if content != '':
                self.route_request(content)
        
    def make_pipe(self):
        if not os.path.isfile(path):
            print(f"creating pipeline with name {PIPE}...")
            if not os.path.isfile(PIPE):
            with open(PIPE, 'w') as file:
                file.write('')
        
    def make_player_directory(self):
        if not os.path.isdir(PLAYER_DIRECTORY):
            print(f"creating a player directory with name {PLAYER_DIRECTORY}...")
            os.mkdir(PLAYER_DIRECTORY)
            self.make_master_file()

    def make_master_file(self):
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
            count += 1
        print(f"creating a masterfile with name {MASTER_FILE}...")
        with open(MASTER_FILE, 'wb') as file:
            pickle.dump(players, file)

    def open_master(self):
        print(f"opening masterfile...")
        with open(MASTER_FILE, 'rb') as file:
            self.players = pickle.load(file)

    def send_and_wait_for_message(self, sent_message):
        print(f"Sending request back to client: {sent_message}...")
        self.write_to_pipe(sent_message)
        count = 0
        while count < 20:
            time.sleep(.5)
            with open(PIPE, "r") as file:
                content = file.read()
            if content != '':
                print(f"Read response from client: {content}...")
                return content
            count += 1
        print(f"Connection timed out! Client did not respond within 10 seconds.")
        self.write_to_pipe(TIMED_OUT)
        
    def choose_user(self):
        return self.send_and_wait_for_message(USER_SELECT)
        
    def choose_team(self):
        return self.send_and_wait_for_message(WHICH_TEAM)
        
    def choose_player(self):
        return self.send_and_wait_for_message(WHICH_PLAYER)
        
    def add_player(self):
        # Change to get_query_params
        user = self.choose_user()
        if user is None:
            return
        team = self.choose_team()
        if team is None:
            return
        player = self.choose_player()
        if player is None:
            return
        print(f"Client sent the following request: Add {player} to {team} for user {user}")
        self.get_user_file(user)
        self.validate_player_exists(player)
        if self.last_write == NOT_FOUND:
            return
        self.validate_player_available(player, team)
        if self.last_write != FORBIDDEN:
            self.save_user_data(user)

    def get_user_file(username):
        user_file = f"{PLAYER_DIRECTORY}/{username}.pkl"
        if not os.path.isfile(user_file):
            print(f"Creating a save file for user {username}")
            self.open_master()
            with open(user_file, 'wb') as file:
                pickle.dump(self.players, file)
        print(f"Opening the users save file...")
        with open(user_file, 'rb') as file:
            self.players = pickle.load(file)
        
    def save_user_data(self, username):
        user_file = f"{PLAYER_DIRECTORY}/{username}.pkl"
        print(f"Saving user {username} data to {user_file}")
        with open(user_file, 'wb') as file:
            pickle.dump(self.players, file)
        
    def validate_player_exists(self, player):
        try:
            self.players[player]
            print(f"{Player successfully found!}")
        except KeyError:
            print(f"Unable to find player {player}!")
            self.write_to_pipe(NOT_FOUND)
        
    def validate_player_available(self, player, team):
        if team.upper() == 'NONE':
            team = None
        current_team = self.players[player]['current_team']
        if (current_team != None and team != None) or current_team == team:
            print(f"{Player} is unable to be added to {team}! Current team is {current_team}.")
            self.write_to_pipe(FORBIDDEN)
        else:
            print(f"{Player} is eligible for transfer! Updating player team...")
            self.write_to_pipe(SUCCESS)
            self.players[player]['current_team'] = team

    def remove_player(self):
        user, team, player = self.get_query_params()
        print("Client sent request: Remove {player} from their current team for user {user}")
        self.get_user_file()
        self.validate_player_exists
        if self.last_write == NOT_FOUND:
            return
        self.validate_player_available(player, team='none')
        if self.last_write != FORBIDDEN:
            self.save_user_data(user)
            
    def get_query_params(self):
        user = self.choose_user()
        if user is not None:
            team = self.choose_team()
            if team is not None:
                player = self.choose_player()
                if player is not None:
                    return user, team, player
        return None, None, None
        
    def add_new_player_to_database(self):
        user, team, player = self.get_query_params()
        print("Client sent request: Add {player} to the database for {user} and set their team to {team}")
        self.validate_player_exists(player)
        if self.last_write != NOT_FOUND:
            print("{player} already exists, unable to process request.")
            self.write_to_pipe(FORBIDDEN)
        if team.upper() == 'NONE':
            team = None
        else:
            data = {"name": player,
                    "id": len(self.players),
                    "current_team": team
                   }
            self.players[player] = Player(data)
            print(f"Added {player} to {user} with team {team}")
            self.save_user_data(user)

    def write_to_pipe(self, contents):
        """
        Writes a given message to the pipeline and saves what was written
        :param contents: The message to be written
        """
        with open(PIPE, "w") as file:
            file.write(contents)
        print("Wrote the following message to {PIPE}: {content}")
        self.last_write = contents
        
    def route_request(self, content):
        print(f"Attempting to handle request from client: {content}")
        try:
            self.requests[content]()
        except KeyError:
            self.invalid_request()

    def invalid_request(self):
        print(f"Unable to handle request!")
        self.write_to_pipe(FAILED_READ)

    def quit(self):
        self.write_to_pipe('')
        self.last_write = QUIT_REQUEST
        print("Microservice is shutting down.")
