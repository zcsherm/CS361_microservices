class Player:
    def __init__(self, data):
        self._name = data["name"]
        self._id = data["id"]
        self._seasons = {}
        self._current_team = data["current team"]
        for season in data["seasons"]:
            # Maybe construct it by attribute? runs, rbi, singles, doubles, triples, hrs, saves, team
            self._seasons[season] = data["seasons"][season]

    def add_season(self, season):
        self._seasons[season] = {"runs": 0,
                                 "rbi": 0,
                                 "singles": 0,
                                 "doubles": 0,
                                 "triples": 0,
                                 "home runs": 0,
                                 "saves": 0,
                                 "team": None

                                 }

    def increment_runs(self, season):
        self._seasons[season]["runs"] += 1

    def increment_rbi(self, season):
        self._seasons[season]["rbi"] += 1

    def increment_singles(self, season):
        self._seasons[season]["singles"] += 1

    def increment_doubles(self, season):
        self._seasons[season]["doubles"] += 1

    def increment_triples(self, season):
        self._seasons[season]["triples"] += 1

    def increment_home_runs(self, season):
        self._seasons[season]["home runs"] += 1

    def increment_saves(self, season):
        self._seasons[season]["saves"] += 1

    def update_team(self, season, new_team):
        self._seasons[season]["team"] = new_team

    def update_current_team(self, new_team):
        self._current_team = new_team

    def get_season(self, season):
        return self._seasons[season]

    def get_current_team(self):
        return self._current_team

    def get_name(self):
        return self._name