import pickle
import os
import time

from tensorflow.compiler.xla.xla_data_pb2 import INVALID

from player_record import Player

PIPE = "player_pipe.txt"
ADD_REQUEST = "ADD"
REMOVE_REQUEST = "REMOVE"
CREATE_REQUEST = "CREATE"
QUIT_REQUEST = "QUIT"
USER_SELECT = "USER"
GET_PLAYERS = "LIST"
REQUESTS = [ADD_REQUEST, REMOVE_REQUEST, REMOVE_REQUEST, GET_PLAYERS, QUIT_REQUEST]

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
    """
    Manages the players available to a user, allows the user to change player info and add players
    """
    def __init__(self):
        """
        Set up the microservice
        """
        # Map client requests to the appropriate functions
        self.requests = {
                        ADD_REQUEST: self.add_player,
                        REMOVE_REQUEST: self.remove_player,
                        CREATE_REQUEST: self.add_new_player_to_database,
                        GET_PLAYERS: self.get_player_list,
                        QUIT_REQUEST: self.quit
                        }
        
        # Create the pipe and directories on first time setup
        self.make_pipe()
        self.make_player_directory()
        self.open_master()
        # Launch into the main loop
        self.last_write = None
        self.main()
        

    def main(self):
        """
        Checks the pipe every second for a new client request
        """
        print(f"listening on {PIPE}...")
        while self.last_write != QUIT_REQUEST:
            time.sleep(1)
            with open(PIPE, "r") as file:
                content = file.read().upper()

            # If there is a client request, route that request to the appropriate function
            if content != '':
                self.route_request(content)
        
    def make_pipe(self):
        """
        Creates the communication pipe if it does not exist
        """
        if not os.path.isfile(PIPE):
            print(f"creating pipeline with name {PIPE}...")
            if not os.path.isfile(PIPE):
                with open(PIPE, 'w') as file:
                    file.write('')
        
    def make_player_directory(self):
        """
        Creates the player directory if it does not exist
        """
        if not os.path.isdir(PLAYER_DIRECTORY):
            print(f"creating a player directory with name {PLAYER_DIRECTORY}...")
            os.mkdir(PLAYER_DIRECTORY)
            self.make_master_file()

    def make_master_file(self):
        """
        Creates/overwrites the master list of players
        """
        # Get every player name
        player_names = []
        players = {}
        with open(PLAYER_NAMES,'r') as file:
            for line in file:
                player_names.append(line.rstrip())
        print(player_names)
        # Construct a new player from each name and add it to the master file
        count = 0
        for player in player_names:
            data = {"name": player,
                    "id": count,
                    "current team": None,
                    "seasons": []
                   }
            players[player] = Player(data)
            count += 1
        print(f"creating a masterfile with name {MASTER_FILE}...")
        print(players)
        with open(MASTER_FILE, 'wb') as file:
            pickle.dump(players, file)

    def open_master(self):
        """
        Opens the master file and loads the data from it
        """
        print(f"opening masterfile...")
        with open(MASTER_FILE, 'rb') as file:
            self.players = pickle.load(file)

    def send_and_wait_for_message(self, sent_message):
        """
        Sends a message to the pipe line and waits for a response from the client
        :param sent_message: The message to send to the client
        :return: The response from client, or None if timed out
        """
        print(f"Sending request back to client: {sent_message}...")
        self.write_to_pipe(sent_message)

        # Read the pipe for 10 seconds, wait for a response
        count = 0
        while count < 20:
            time.sleep(.5)
            with open(PIPE, "r") as file:
                content = file.read()
            if content != '':
                print(f"Read response from client: {content}...")
                return content
            count += 1

        # After 10 seconds, time out
        print(f"Connection timed out! Client did not respond within 10 seconds.")
        self.write_to_pipe(TIMED_OUT)
        
    def choose_user(self):
        """
        Gets the user from the client
        """
        return self.send_and_wait_for_message(USER_SELECT)
        
    def choose_team(self):
        """
        Gets the target team from the client
        """
        return self.send_and_wait_for_message(WHICH_TEAM)
        
    def choose_player(self):
        """
        Gets the target player from the client
        """
        return self.send_and_wait_for_message(WHICH_PLAYER)
        
    def add_player(self):
        """
        Checks if a user is able to add a given player to a team and communicates that back to the client
        """
        # Get parameters for addition from client
        user, team, player = self.get_query_params()

        # Stop execution if the client failed to respond
        if user is None:
            return

        # Get the users file, validate the parameters, and attempt addition
        print(f"Client sent the following request: Add {player} to {team} for user {user}")
        self.get_user_file(user)
        self.validate_player_exists(player)
        if self.last_write == NOT_FOUND:
            return
        self.validate_player_available(player, team)

        # If the addition was successful then save the users new data
        if self.last_write != FORBIDDEN:
            self.save_user_data(user)
        time.sleep(1)

    def get_user_file(self, username):
        """
        Loads the requested users save file
        """
        user_file = f"{PLAYER_DIRECTORY}/{username}.pkl"

        # If the users save file does not exist, create a new one from the master
        if not os.path.isfile(user_file):
            print(f"Creating a save file for user {username}")
            self.open_master()
            with open(user_file, 'wb') as file:
                pickle.dump(self.players, file)

        # Load the users data into self.players
        print(f"Opening the users save file...")
        with open(user_file, 'rb') as file:
            self.players = pickle.load(file)
        print(self.players['jasper'].get_current_team())
    def save_user_data(self, username):
        """
        Saves the current changes to the users data to their save file
        """
        user_file = f"{PLAYER_DIRECTORY}/{username}.pkl"
        print(f"Saving user {username} data to {user_file}")
        with open(user_file, 'wb') as file:
            pickle.dump(self.players, file)
        
    def validate_player_exists(self, player, new_player = False):
        """
        Check if the requested user currently exists in the dataset
        """
        try:
            a = self.players[player]
            print(f"{player} successfully found!")
        except KeyError:
            print(f"Unable to find player {player}!")
            if new_player:
                return True
            self.write_to_pipe(NOT_FOUND)
        
    def validate_player_available(self, player, team):
        """
        Check if a player is available to be added to a given team
        """
        # Set team to None object if appropriate
        if team.upper() == 'NONE':
            team = None
        current_team = self.players[player].get_current_team()
        print(current_team , team)
        # If the current team is the passed team, or the player is currently reserved, then send back 
        if (current_team != None and team != None) or current_team == team:
            print(f"{Player} is unable to be added to {team}! Current team is {current_team}.")
            self.write_to_pipe(FORBIDDEN)

        # If the request is valid then update the players team
        else:
            print(f"{Player} is eligible for transfer! Updating player team...")
            self.write_to_pipe(SUCCESS)
            self.players[player].update_current_team(team)
            print(self.players[player].get_current_team())

    def remove_player(self):
        """
        Remove a player from a given team
        """
        # Get the parameters for the request and exit if the request timed out
        user, team, player = self.get_query_params()
        print("Client sent request: Remove {player} from their current team for user {user}")
        if user is None:
            return

        # Load in the players save file, validate the player
        self.get_user_file(user)
        self.validate_player_exists(player)
        if self.last_write == NOT_FOUND:
            return

        # Set the players team to None if the player exists
        self.validate_player_available(player, team='none')
        if self.last_write != FORBIDDEN:
            self.save_user_data(user)
        time.sleep(1)

    def get_query_params(self):
        """
        Gets request parametes from client
        :return: user, team, and player parameters
        """
        user = self.choose_user()
        if user is not None:
            team = self.choose_team()
            if team is not None:
                player = self.choose_player()
                if player is not None:
                    return user, team, player
        return None, None, None
        
    def add_new_player_to_database(self):
        """
        Add a new player intoo the users data base
        """
        # Get the parameters from the request and exit if the request timed out
        user, team, player = self.get_query_params()
        print(f"Client sent request: Add {player} to the database for {user} and set their team to {team}")
        if user is None:
            return
        if team.upper() == 'NONE':
            team = None
            
        # Confirm that the player does not currently exist
        self.get_user_file(user)
        new_player = self.validate_player_exists(player, new_player=True)
        if not new_player:
            print("{player} already exists, unable to process request.")
            self.write_to_pipe(FORBIDDEN)
        # Create a new player object and add it to the users dataset.
        else:
            data = {"name": player,
                    "id": len(self.players),
                    "current team": team,
                    "seasons" : []
                   }
            self.players[player] = Player(data)
            print(f"Added {player} to {user} with team {team}")
            self.write_to_pipe(SUCCESS)
            self.save_user_data(user)
        time.sleep(1)

    def write_to_pipe(self, contents):
        """
        Writes a given message to the pipeline and saves what was written
        :param contents: The message to be written
        """
        with open(PIPE, "w") as file:
            file.write(contents)
        print(f"Wrote the following message to {PIPE}: {contents}")
        self.last_write = contents
        
    def route_request(self, content):
        """
        Redirects a client request to the appropriate function
        """
        if content == FAILED_READ:
            return
        print(f"Attempting to handle request from client: {content}")
        try:
            self.requests[content]()
        except KeyError:
            self.invalid_request()

    def invalid_request(self):
        """
        Tell the client that an invalid request type was sent
        """
        if self.last_write == FAILED_READ:
            return
        print(f"Unable to handle request!")
        self.write_to_pipe(FAILED_READ)

    def get_player_list(self):
        user, team, player = self.get_query_params()
        print(f"Client sent request: get all players for user {user}")
        if user is None:
            return
        self.get_user_file(user)
        print(list(self.players.keys()))
        message = ""
        for key in list(self.players.keys()):
            message += (key + '\n')
        self.write_to_pipe(message)
        time.sleep(1)

    def quit(self):
        """
        Terminate program execution and clear the pipeline.
        """
        self.write_to_pipe('')
        self.last_write = QUIT_REQUEST
        print("Microservice is shutting down.")

if __name__ == '__main__':
    Microservice()
