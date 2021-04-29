import discord


class Badge:
    def __init__(self, icon, name, explanation):
        self.__icon = icon
        self.__name = name
        self.__explanation = explanation

    def get_icon(self):
        return self.__icon

    def get_name(self):
        return self.__icon + ' - ' + self.__name

    def get_explanation(self):
        return self.__explanation

    def save_string(self):



class Profile:
    all_badges = []

    def __init__(self):
        self.bio = 'This user has not set a bio yet'
        self.badges = []

    def award(self, badge):
        self.badges = self.badges.append(badge)
