import datetime
import json
import os
from .repository import JsonRepository
from util import (
    FileWatcher,
    FilePaths,
    modify_json_file
)

class ArtfightRepo(JsonRepository):
    _watched_artfight_json = None

    def __init__(self):
        if self.__class__._watched_artfight_json is None:
            self.__class__._watched_artfight_json = FileWatcher(FilePaths.artfight)
        
        self.reserved_keys = ['submissions_channel', 'prompts_channel', 'start_date', 'end_date', 'next_prompt_hour', 'prompts']
    
    def _get(self, *keys: str) -> any:
        return super()._get(self.__class__._watched_artfight_json, *keys)
    
    def _set(self, *keys: str, value: any) -> None:
        modify_json_file(
            FilePaths.artfight,
            lambda data: super(ArtfightRepo, self)._set(data, *keys, value=value)
        )

    def _remove(self, *keys) -> None:
        modify_json_file(
            FilePaths.artfight,
            lambda data: super(ArtfightRepo, self)._remove(data, *keys)
        )

    def _ensure_allowed_team_name(self, team_name: str) -> None:
        if team_name in self.reserved_keys:
            raise ValueError(f'Team name cannot be in: {self.reserved_keys}')

    # channels

    def get_submissions_channel(self, guild_id: int | str) -> int | None:
        return self._get(str(guild_id), 'submissions_channel')
    
    def get_prompts_channel(self, guild_id: int | str) -> int | None:
        return self._get(str(guild_id), 'prompts_channel')
    
    def set_submissions_channel(self, guild_id: int | str, channel_id: str | int):
        return self._set(str(guild_id), 'submissions_channel', value=int(channel_id))
    
    def set_prompts_channel(self, guild_id: int | str, channel_id: str | int):
        return self._set(str(guild_id), 'prompts_channel', value=int(channel_id))

    # dates

    def get_start_date(self, guild_id: int | str) -> datetime.date | None:
        try:
            date_string = self._get(str(guild_id), 'start_date')
            return datetime.date.fromisoformat(date_string) if date_string is not None else None
        except ValueError:
            return None

    def get_end_date(self, guild_id: int | str) -> datetime.date | None:
        try:
            date_string = self._get(str(guild_id), 'end_date')
            return datetime.date.fromisoformat(date_string) if date_string is not None else None
        except ValueError:
            return None

    def get_next_prompt_hour(self, guild_id: int | str) -> datetime.time | None:
        try:
            time_string = self._get(str(guild_id), 'next_prompt_hour')
            return datetime.time.fromisoformat(time_string) if time_string is not None else None
        except ValueError:
            return None

    def get_duration_in_days(self, guild_id: int | str) -> int | None:
        start_date = self.get_start_date(guild_id)
        end_date = self.get_end_date(guild_id)

        if start_date is None or end_date is None:
            return None
        
        return (end_date - start_date).days + 1

    def set_start_date(self, guild_id: int | str, date: datetime.date):
        self._set(str(guild_id), 'start_date', value=date.isoformat())

    def set_end_date(self, guild_id: int | str, date: datetime.date):
        self._set(str(guild_id), 'end_date', value=date.isoformat())

    def set_next_prompt_hour(self, guild_id: int | str, time: datetime.time):
        self._set(str(guild_id), 'next_prompt_hour', value=time.isoformat())

    # prompts

    def get_prompts(self, guild_id: int | str) -> dict[str, str] | None:
        return self._get(str(guild_id), 'prompts')

    def get_prompt(self, guild_id: int | str, day_of_artfight: int) -> str | None:
        return self._get(str(guild_id), 'prompts', str(day_of_artfight))

    def add_prompt(self, guild_id: int | str, day_of_artfight: int | str, prompt):
        artfight_days = self.get_duration_in_days(guild_id)

        if artfight_days is None:
            raise ValueError('Artfight start_date & end_date must be set before being able to add prompts, others the duration cannot be validated')
        elif day_of_artfight <= 0:
            raise ValueError('The "day of artfight" for which the prompt is, cannot be lower than 1')
        elif day_of_artfight > artfight_days:
            raise ValueError(f'The "day of artfight", for which the prompt is, cannot be more than the amount of days in the artfight; {artfight_days}')
        
        self._set(str(guild_id), 'prompts', str(day_of_artfight), value=prompt)


    def remove_prompt(self, guild_id: int | str, day_of_artfight: int | str):
        self._remove(str(guild_id), 'prompts', str(day_of_artfight))

    # teams

    def get_teams(self, guild_id: int | str) -> dict[str, int]:
        guild_data = self._get(str(guild_id))

        if guild_data is None:
            return {}
        
        return {
            team_name: guild_data[team_name].get('role_id')
            for team_name in guild_data.keys()
            if team_name not in self.reserved_keys
        }
    
    def add_team(self, guild_id: int | str, name: str, role_id: int | str):
        self._ensure_allowed_team_name(name)
        self.set_team_role(guild_id, name, role_id=role_id)
        self.set_team_score(guild_id, name, 0)

    # team roles

    def get_team_role(self, guild_id: int | str, team_name: str) -> int | None:
        return self._get(str(guild_id), team_name, 'role')

    def get_team_of_role_id(self, guild_id: int | str, role_id: int | str) -> str | None:
        guild_data = self._get(str(guild_id))

        if not isinstance(guild_data, dict):
            return None
        
        for team_name, data in guild_data.items():
            if isinstance(data, dict) and data.get('role') == int(role_id):
                return team_name
        return None
    
    def set_team_role(self, guild_id: int | str, team_name: str, role_id: int | str):
        self._ensure_allowed_team_name(team_name)
        self._set(str(guild_id), team_name, 'role', value=int(role_id))

    # team score
    
    def get_team_score(self, guild_id: int | str, team_name: str) -> int | None:
        return self._get(str(guild_id), team_name, 'score')
    
    def set_team_score(self, guild_id: int | str, team_name: str, score: int):
        self._ensure_allowed_team_name(team_name)
        self._set(str(guild_id), team_name, 'score', value=score)

    def add_to_team_score(self, guild_id: int | str, team_name: str, score: int):
        self.set_team_score(
            str(guild_id), team_name,
            value=max(0, ((current := self.get_team_score(guild_id, team_name)) if current is not None else 0) + score)
        )

    def subtract_from_team_score(self, guild_id: int | str, team_name: str, score: int):
        self.set_team_score(
            str(guild_id), team_name,
            value=max(0, ((current := self.get_team_score(guild_id, team_name)) if current is not None else 0) - score)
        )

    # team members
    
    def get_team_members(self, guild_id: int | str, team_name: str) -> dict[str, dict[str, int | dict[str, dict[str, int | str]]]] | None:
        return self._get(str(guild_id), team_name, 'members')
    
    def get_team_member(self, guild_id: int | str, team_name: str, user_id: int | str) -> dict[str, int | dict[str, dict[str, int | str]]] | None:
        return self._get(str(guild_id), team_name, 'members', str(user_id))
    
    def add_team_member(self, guild_id: int | str, team_name: str, user_id: int | str):
        self._ensure_allowed_team_name(team_name)
        self._set(str(guild_id), team_name, 'members', str(user_id), value={'points': 0, 'submissions': {}})

    def remove_team_member(self, guild_id: int | str, team_name: str, user_id: int | str):
        self._ensure_allowed_team_name(team_name)
        self._remove(str(guild_id), team_name, 'members', str(user_id))

    # team member data
    
    def get_team_member_points(self, guild_id: int | str, team_name: str, user_id: int | str) -> int | None:
        return self._get(str(guild_id), team_name, 'members', str(user_id), 'points')
    
    def get_team_member_submissions(self, guild_id: int | str, team_name: str, user_id: int | str) -> dict[str, dict[str, int | str]] | None:
        return self._get(str(guild_id), team_name, 'members', str(user_id), 'submissions')
    
    def get_team_member_submission(self, guild_id: int | str, team_name: str, user_id: int | str, submission_url: str) -> dict[str, int | str]:
        return self._get(str(guild_id), team_name, 'members', str(user_id), 'submissions', submission_url)
    
    def set_team_member_points(self, guild_id: int | str, team_name: str, user_id: int | str, points: int):
        self._ensure_allowed_team_name(team_name)
        self._set(str(guild_id), team_name, 'members', str(user_id), 'points', value=points)

    def add_to_team_member_points(self, guild_id: int | str, team_name: str, user_id: int | str, points: int):
        self.set_team_member_points(
            guild_id, team_name, user_id,
            value=max(0, ((current := self.get_team_member_points(guild_id, team_name, user_id)) if current is not None else 0) + points)
        )
        self.add_to_team_score(guild_id, team_name, points)

    def subtract_from_team_member_points(self, guild_id: int | str, team_name: str, user_id: int | str, points: int):
        self.set_team_member_points(
            guild_id, team_name, user_id,
            value=max(0, ((current := self.get_team_member_points(guild_id, team_name, user_id)) if current is not None else 0) - points)
        )
        self.subtract_from_team_score(guild_id, team_name, points)
    
    def add_team_member_submission(self, guild_id: int | str, team_name: str, user_id: int | str, submission_url: str, points: int):
        self._ensure_allowed_team_name(team_name)
        self._set(
            str(guild_id), team_name, 'members', str(user_id), 'submissions', submission_url,
            value={'points': points, 'datetime': datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()}
        )
        self.add_to_team_member_points(guild_id, team_name, user_id, points)

    def remove_team_member_submission(self, guild_id: int |str, team_name: str, user_id: int | str, submission_url: str):
        self._ensure_allowed_team_name(team_name)
        self.subtract_from_team_member_points(
            guild_id, team_name, user_id,
            self.get_team_member_submission(guild_id, team_name, user_id).get('points', 0)
        )
        self._remove(str(guild_id), team_name, 'members', str(user_id), 'submissions', submission_url)

    # Archiving

    def archive_artfight(self, guild_id: int | str):
        artfight_start_date = self.get_start_date(guild_id)
        artfight_end_date = self.get_end_date(guild_id)

        if artfight_start_date is None or artfight_end_date is None:
            archive_name = datetime.datetime.now(datetime.timezone.utc).isoformat().replace(':', "-")
        else:
            archive_name = f'{artfight_start_date.isoformat()}_{artfight_end_date.isoformat()}'

        archive_file_path = f'{FilePaths.artfight_archive_dir}/{str(guild_id)}/{archive_name}.json'
        os.makedirs(os.path.dirname(archive_file_path), exist_ok=True)

        with open(archive_file_path, 'w', encoding="utf-8") as archive_file:
            json.dump(self.__class__._watched_artfight_json.get(str(guild_id), {}), archive_file, indent=4)
        
        self._remove(str(guild_id))