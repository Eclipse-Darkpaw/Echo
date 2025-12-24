import datetime
import json
import os
from .repository import JsonRepository
from config import Paths
from util import (
    FileWatcher,
    modify_json_file
)

class ArtfightRepo(JsonRepository):
    _watched_artfight_json = None

    def __init__(self):
        os.makedirs(Paths.data_dir, exist_ok=True)

        if self.__class__._watched_artfight_json is None:
            self.__class__._watched_artfight_json = FileWatcher(Paths.artfight)
        
        self.forbidden_team_names = ['teams']
    
    def _get(self, *keys: str) -> any:
        return super()._get(self.__class__._watched_artfight_json, *keys)
    
    def _set(self, *keys: str, value: any) -> None:
        modify_json_file(
            Paths.artfight,
            lambda data: super(ArtfightRepo, self)._set(data, *keys, value=value)
        )

    def _remove(self, *keys) -> None:
        modify_json_file(
            Paths.artfight,
            lambda data: super(ArtfightRepo, self)._remove(data, *keys)
        )

    def _ensure_allowed_team_name(self, team_name: str) -> None:
        if team_name in self.forbidden_team_names:
            raise ValueError(f'Team name cannot be in: {self.forbidden_team_names}')
        
    def ensure_guild_entry(self, guild_id: int | str) -> bool:
        guild_id = str(guild_id)
        if self._get(guild_id) is None:
            self._set(guild_id, value={'teams': {}, 'prompts': {}})
            return False
        return True
        

    # general artfight settings

    def get_artfight_role(self, guild_id: int | str) -> int | None:
        return self._get(str(guild_id), 'artfight_role')
    
    def set_artfight_role(self, guild_id: int | str, role_id: int | str):
        self._set(str(guild_id), 'artfight_role', value=int(role_id))

    def get_points_name(self, guild_id: int | str) -> str:
        return self._get(str(guild_id), 'points_name') or 'points'
    
    def set_points_name(self, guild_id: int | str, name: str):
        self._set(str(guild_id), 'points_name', value=name)

    # join message persistence

    def get_join_message(self, guild_id: int | str) -> tuple[int, int] | None:
        """Returns (channel_id, message_id) or None if not set."""
        channel_id = self._get(str(guild_id), 'join_message_channel_id')
        message_id = self._get(str(guild_id), 'join_message_id')
        if channel_id is not None and message_id is not None:
            return (channel_id, message_id)
        return None
    
    def set_join_message(self, guild_id: int | str, channel_id: int | str, message_id: int | str):
        self._set(str(guild_id), 'join_message_channel_id', value=int(channel_id))
        self._set(str(guild_id), 'join_message_id', value=int(message_id))

    def clear_join_message(self, guild_id: int | str):
        self._set(str(guild_id), 'join_message_channel_id', value=None)
        self._set(str(guild_id), 'join_message_id', value=None)

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

    # yap messages

    def get_yap_messages(self, guild_id: int | str) -> dict[str, str] | None:
        return self._get(str(guild_id), 'yap_messages')

    def get_yap_message(self, guild_id: int | str, day_of_artfight: int) -> str | None:
        return self._get(str(guild_id), 'yap_messages', str(day_of_artfight))

    def add_yap_message(self, guild_id: int | str, day_of_artfight: int | str, yap_message: str):
        artfight_days = self.get_duration_in_days(guild_id)

        if artfight_days is None:
            raise ValueError('Artfight start_date & end_date must be set before being able to add yap messages, others the duration cannot be validated')
        elif day_of_artfight <= 0:
            raise ValueError('The "day of artfight" for which the yap message is, cannot be lower than 1')
        elif day_of_artfight > artfight_days:
            raise ValueError(f'The "day of artfight", for which the yap message is, cannot be more than the amount of days in the artfight; {artfight_days}')
        
        self._set(str(guild_id), 'yap_messages', str(day_of_artfight), value=yap_message)

    def remove_yap_message(self, guild_id: int | str, day_of_artfight: int | str):
        self._remove(str(guild_id), 'yap_messages', str(day_of_artfight))

    # sent messages tracking (to prevent duplicate sends on bot restart)

    def has_sent_message(self, guild_id: int | str, day: int, message_type: str) -> bool:
        """
        Check if a specific message type has been sent for a given day.
        
        :param guild_id: The guild ID
        :param day: The day of artfight (1-indexed)
        :param message_type: One of 'warning', 'status', 'yap', 'prompt', 'hall_of_fame'
        :return: True if message was already sent, False otherwise
        """
        return self._get(str(guild_id), 'sent_messages', str(day), message_type) is True

    def mark_message_sent(self, guild_id: int | str, day: int, message_type: str):
        """
        Mark a specific message type as sent for a given day.
        
        :param guild_id: The guild ID
        :param day: The day of artfight (1-indexed)
        :param message_type: One of 'warning', 'status', 'yap', 'prompt', 'hall_of_fame'
        """
        self._set(str(guild_id), 'sent_messages', str(day), message_type, value=True)

    def clear_sent_messages(self, guild_id: int | str):
        """
        Clear all sent message tracking for a guild.
        Typically called when archiving/resetting artfight.
        """
        self._remove(str(guild_id), 'sent_messages')

    # teams

    def get_teams(self, guild_id: int | str) -> dict[str, int]:
        teams = self._get(str(guild_id), 'teams')

        if teams is None:
            return {}
        
        return {
            team_name: teams[team_name].get('role')
            for team_name in teams.keys()
            if team_name not in self.forbidden_team_names
        }
    
    def add_team(self, guild_id: int | str, name: str, role_id: int | str):
        self._ensure_allowed_team_name(name)
        self.set_team_role(guild_id, name, role_id=role_id)
        self.set_team_score(guild_id, name, 0)

    def remove_team(self, guild_id: int | str, name: str):
        self._ensure_allowed_team_name(name)
        self._remove(str(guild_id), 'teams', name)

    # team roles

    def get_team_role(self, guild_id: int | str, team_name: str) -> int | None:
        return self._get(str(guild_id), 'teams', team_name, 'role')

    def get_team_of_role_id(self, guild_id: int | str, role_id: int | str) -> str | None:
        teams = self._get(str(guild_id), 'teams')

        if not isinstance(teams, dict):
            return None
        
        for team_name, data in teams.items():
            if isinstance(data, dict) and data.get('role') == int(role_id):
                return team_name
        return None
    
    def set_team_role(self, guild_id: int | str, team_name: str, role_id: int | str):
        self._ensure_allowed_team_name(team_name)
        self._set(str(guild_id),'teams', team_name, 'role', value=int(role_id))

    # team score
    
    def get_team_score(self, guild_id: int | str, team_name: str) -> int | None:
        return self._get(str(guild_id), 'teams', team_name, 'score')
    
    def set_team_score(self, guild_id: int | str, team_name: str, score: int):
        self._ensure_allowed_team_name(team_name)
        self._set(str(guild_id), 'teams', team_name, 'score', value=score)

    def add_to_team_score(self, guild_id: int | str, team_name: str, score: int):
        current = self.get_team_score(guild_id, team_name) or 0
        self.set_team_score(str(guild_id), team_name, score=max(0, current + score))

    def subtract_from_team_score(self, guild_id: int | str, team_name: str, score: int):
        current = self.get_team_score(guild_id, team_name) or 0
        self.set_team_score(str(guild_id), team_name, score=max(0, current - score))

    # team members
    
    def get_team_members(self, guild_id: int | str, team_name: str) -> dict[str, dict[str, int | dict[str, dict[str, int | str | list]]]] | None:
        return self._get(str(guild_id), 'teams', team_name, 'members')
    
    def get_team_member(self, guild_id: int | str, team_name: str, user_id: int | str) -> dict[str, int | dict[str, dict[str, int | str]]] | None:
        return self._get(str(guild_id), 'teams', team_name, 'members', str(user_id))
    
    def add_team_member(self, guild_id: int | str, team_name: str, user_id: int | str):
        self._ensure_allowed_team_name(team_name)
        self._set(str(guild_id), 'teams', team_name, 'members', str(user_id), value={'points': 0, 'submissions': {}})

    def remove_team_member(self, guild_id: int | str, team_name: str, user_id: int | str):
        self._ensure_allowed_team_name(team_name)
        self._remove(str(guild_id), 'teams', team_name, 'members', str(user_id))

    # team member data
    
    def get_team_member_points(self, guild_id: int | str, team_name: str, user_id: int | str) -> int | None:
        return self._get(str(guild_id), 'teams', team_name, 'members', str(user_id), 'points')
    
    def get_team_member_submissions(self, guild_id: int | str, team_name: str, user_id: int | str) -> dict[str, dict[str, int | str]] | None:
        return self._get(str(guild_id), 'teams', team_name, 'members', str(user_id), 'submissions')
    
    def get_team_member_submission(self, guild_id: int | str, team_name: str, user_id: int | str, submission_url: str) -> dict | None:
        return self._get(str(guild_id), 'teams', team_name, 'members', str(user_id), 'submissions', submission_url)
    
    def set_team_member_points(self, guild_id: int | str, team_name: str, user_id: int | str, points: int):
        self._ensure_allowed_team_name(team_name)
        self._set(str(guild_id), 'teams', team_name, 'members', str(user_id), 'points', value=points)

    def add_to_team_member_points(self, guild_id: int | str, team_name: str, user_id: int | str, points: int):
        current = self.get_team_member_points(guild_id, team_name, user_id) or 0
        self.set_team_member_points(
            guild_id, team_name, user_id,
            points=max(0, current + points)
        )
        self.add_to_team_score(guild_id, team_name, points)

    def subtract_from_team_member_points(self, guild_id: int | str, team_name: str, user_id: int | str, points: int):
        current = self.get_team_member_points(guild_id, team_name, user_id) or 0
        self.set_team_member_points(
            guild_id, team_name, user_id,
            points=max(0, current - points)
        )
        self.subtract_from_team_score(guild_id, team_name, points)
    
    def add_team_member_submission(
        self,
        guild_id: int | str,
        team_name: str,
        user_id: int | str,
        submission_url: str,
        points: int,
        title: str,
        prompt_day: int,
        victims: list[int | str],
        collaborators: list[int | str] | None = None
    ):
        """
        Add a submission for a team member.
        
        :param guild_id: The guild ID
        :param team_name: The team name
        :param user_id: The submitting user's ID
        :param submission_url: The URL of the submitted image
        :param points: The points earned for this submission
        :param title: The title of the piece
        :param prompt_day: Which day's prompt this submission is for
        :param victims: List of user IDs whose characters were attacked
        :param collaborators: List of user IDs who collaborated (None if solo)
        """
        self._ensure_allowed_team_name(team_name)
        self._set(
            str(guild_id), 'teams', team_name, 'members', str(user_id), 'submissions', submission_url,
            value={
                'points': points,
                'datetime': datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
                'title': title,
                'prompt_day': prompt_day,
                'victims': [str(v) for v in victims],
                'collaborators': [str(c) for c in collaborators] if collaborators else []
            }
        )
        self.add_to_team_member_points(guild_id, team_name, user_id, points)

    def modify_submission_points(
        self,
        guild_id: int | str,
        team_name: str,
        user_id: int | str,
        submission_url: str,
        point_delta: int
    ) -> int | None:
        """
        Modify the points for a specific submission by adding/subtracting a delta.
        Also updates the member's total points and team score.
        
        :param guild_id: The guild ID
        :param team_name: The team name
        :param user_id: The user ID
        :param submission_url: The submission URL (unique identifier)
        :param point_delta: The amount to add (positive) or subtract (negative)
        :return: The new submission points value, or None if submission not found
        """
        self._ensure_allowed_team_name(team_name)
        submission = self.get_team_member_submission(guild_id, team_name, user_id, submission_url)
        if submission is None:
            return None
        
        old_points = submission.get('points', 0)
        new_points = max(0, old_points + point_delta)  # Don't allow negative submission points
        
        # Update submission points
        self._set(
            str(guild_id), 'teams', team_name, 'members', str(user_id), 
            'submissions', submission_url, 'points',
            value=new_points
        )
        
        # Update member points and team score
        actual_delta = new_points - old_points
        if actual_delta > 0:
            self.add_to_team_member_points(guild_id, team_name, user_id, actual_delta)
        elif actual_delta < 0:
            self.subtract_from_team_member_points(guild_id, team_name, user_id, abs(actual_delta))
        
        return new_points

    def remove_team_member_submission(self, guild_id: int | str, team_name: str, user_id: int | str, submission_url: str):
        self._ensure_allowed_team_name(team_name)
        submission = self.get_team_member_submission(guild_id, team_name, user_id, submission_url)
        if submission:
            self.subtract_from_team_member_points(
                guild_id, team_name, user_id,
                submission.get('points', 0)
            )
        self._remove(str(guild_id), 'teams', team_name, 'members', str(user_id), 'submissions', submission_url)

    # Archiving

    def archive_artfight(self, guild_id: int | str):
        artfight_start_date = self.get_start_date(guild_id)
        artfight_end_date = self.get_end_date(guild_id)

        if artfight_start_date is None or artfight_end_date is None:
            archive_name = datetime.datetime.now(datetime.timezone.utc).isoformat().replace(':', "-")
        else:
            archive_name = f'{artfight_start_date.isoformat()}_{artfight_end_date.isoformat()}'

        archive_file_path = f'{Paths.artfight_archive_dir}/{str(guild_id)}/{archive_name}.json'
        os.makedirs(os.path.dirname(archive_file_path), exist_ok=True)

        with open(archive_file_path, 'w', encoding="utf-8") as archive_file:
            json.dump(self.__class__._watched_artfight_json.get(str(guild_id), {}), archive_file, indent=4)
        
        self._remove(str(guild_id))