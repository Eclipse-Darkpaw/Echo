from fileManagement import guild_badges_path

class Badge:
    def __init__(self, icon, name, explanation, message):
        self.__icon = icon
        self.__name = name
        self.__explanation = explanation
        filename = guild_badges_path(message.guild.id)
        with open(filename,'a') as file:
            file.write(self.save_string())

    def get_icon(self):
        return self.__icon

    def get_name(self):
        return self.__icon + ' - ' + self.__name

    def get_explanation(self):
        return self.__explanation

    def save_string(self):
        return self.__icon + ',' + self.__name + ',' + self.__explanation + '\n'

    def award(self, target):


