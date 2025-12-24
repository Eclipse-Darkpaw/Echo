import discord
import datetime

from repositories import ArtfightRepo


def build_warning_message(
    artfight_role_id: int | None,
    prompt_datetime: datetime.datetime | None = None,
    is_last_day: bool = False
) -> str:
    """
    Builds the warning message sent 30 minutes before prompt time.
    Simple text message, no embed.
    
    :param artfight_role_id: The artfight role ID to ping (or None)
    :param prompt_datetime: The datetime when the prompt drops (for Discord timestamp)
    :param is_last_day: Whether this is the last day of artfight
    :return: The warning message string
    """
    role_ping = f"<@&{artfight_role_id}>" if artfight_role_id else ""
    
    # Build Discord timestamp
    if prompt_datetime:
        timestamp = int(prompt_datetime.timestamp())
        time_str = f"<t:{timestamp}:R>"  # Relative format like "in 30 minutes"
    else:
        time_str = "in 30 minutes"
    
    if is_last_day:
        return f"{role_ping} **TIME IS ALMOST UP!** Submissions close {time_str}!\nThis is your last chance, you **CANNOT** submit after the score is announced today. "
    else:
        return f"{role_ping} **Just 30 more minutes!!**\nNext prompt {time_str}\n-# There is a 15min grace period with 75% points"


def build_scores_message(
    artfight_repo: ArtfightRepo,
    guild_id: int,
    artfight_role_id: int | None
) -> str:
    """
    Builds the scores overview message sent 5 minutes before prompt time.
    Shows teams sorted by score (highest first).
    
    :param artfight_repo: The artfight repository
    :param guild_id: The guild ID
    :param artfight_role_id: The artfight role ID to ping (or None)
    :return: The scores message string
    """
    role_ping = f"<@&{artfight_role_id}>" if artfight_role_id else "**Artfight**"
    points_name = artfight_repo.get_points_name(guild_id)
    
    teams = artfight_repo.get_teams(guild_id)
    if not teams:
        return f"{role_ping} No teams configured!"

    # Build team scores list
    team_scores = []
    for team_name, role_id in teams.items():
        score = artfight_repo.get_team_score(guild_id, team_name) or 0
        team_scores.append({
            'name': team_name,
            'role_id': role_id,
            'score': score
        })

    # Sort by score descending
    team_scores.sort(key=lambda t: t['score'], reverse=True)

    lines = [f"**Team Scores:**\n"]
    
    for i, team in enumerate(team_scores):
        lines.append(f"{i + 1}. <@&{team['role_id']}> — **{team['score']:,}** {points_name}")

    return '\n'.join(lines)


def build_yap_with_ping(
    yap_message: str | None,
    artfight_role_id: int | None,
    artfight_day: int
) -> str:
    """
    Builds the yap message with the artfight role ping.
    
    :param yap_message: The custom yap message (or None)
    :param artfight_role_id: The artfight role ID to ping (or None)
    :param artfight_day: The current day of artfight
    :return: The yap message with ping
    """
    role_ping = f"<@&{artfight_role_id}>" if artfight_role_id else ""
    
    if yap_message:
        return f"{role_ping}\n{yap_message}"
    else:
        return f"{role_ping}\nIt's day {artfight_day} of Artfight!\nSome skibidi cheese car didn't write a message, or something...\nMaybe he fell in the hole-"


def build_prompt_embed(
    prompt: str | None,
    artfight_day: int,
    artfight_role: 'discord.Role | None' = None
) -> discord.Embed:
    """
    Builds a clean embed showing just the daily prompt.
    No ping - this is for easy reference.
    
    :param prompt: The prompt for the day (or None)
    :param artfight_day: The current day of artfight
    :param artfight_role: The artfight role (for embed color)
    :return: The prompt embed
    """
    embed_color = artfight_role.color if artfight_role else discord.Color.purple()
    
    embed = discord.Embed(
        title=f"Prompt {artfight_day}",
        color=embed_color
    )
    
    if prompt:
        embed.description = prompt
    else:
        embed.description = "*No prompt set for today*"
    
    return embed


def build_final_scores_message(
    artfight_repo: ArtfightRepo,
    guild_id: int,
    artfight_role_id: int | None,
    artfight_role_color: 'discord.Color | None' = None
) -> tuple[str, discord.Embed]:
    """
    Builds the final scores message sent at the end of artfight.
    Announces submissions are closed and shows final team standings.
    
    :param artfight_repo: The artfight repository
    :param guild_id: The guild ID
    :param artfight_role_id: The artfight role ID to ping (or None)
    :param artfight_role_color: The artfight role color (or None for gold)
    :return: A tuple of (role ping content, final scores embed)
    """
    role_ping = f"<@&{artfight_role_id}>" if artfight_role_id else ""
    points_name = artfight_repo.get_points_name(guild_id)
    embed_color = artfight_role_color or discord.Color.gold()
    
    teams = artfight_repo.get_teams(guild_id)
    if not teams:
        embed = discord.Embed(
            title="🏁 ARTFIGHT HAS ENDED!",
            description="Submissions are now closed!",
            color=embed_color
        )
        return role_ping, embed

    # Build team scores list
    team_scores = []
    for team_name, role_id in teams.items():
        score = artfight_repo.get_team_score(guild_id, team_name) or 0
        team_scores.append({
            'name': team_name,
            'role_id': role_id,
            'score': score
        })

    # Sort by score descending
    team_scores.sort(key=lambda t: t['score'], reverse=True)

    # Build standings
    standings_lines = []
    medals = ["🥇", "🥈", "🥉"]
    for i, team in enumerate(team_scores):
        prefix = medals[i] if i < len(medals) else f"{i + 1}."
        standings_lines.append(f"{prefix} <@&{team['role_id']}> — **{team['score']:,}** {points_name}")

    # Determine winner text
    winner_text = ""
    if len(team_scores) >= 2:
        if team_scores[0]['score'] > team_scores[1]['score']:
            winner_text = f"\n\n**Congratulations to <@&{team_scores[0]['role_id']}>!** 🎉\n-# skill issue <@&{team_scores[1]['role_id']}>"
        elif team_scores[0]['score'] == team_scores[1]['score']:
            winner_text = f"\n\n**It's a tie! smh**\n-# no sigma today"

    embed = discord.Embed(
        title="🏁 ARTFIGHT HAS ENDED!",
        description=(
            "Submissions are now closed. Thank you all for participating!\n\n"
            "**FINAL SCORES:**\n\n" +
            '\n'.join(standings_lines) +
            winner_text
        ),
        color=embed_color
    )

    return role_ping, embed


def build_fancy_leaderboard_embed(
    artfight_repo: ArtfightRepo,
    guild: 'discord.Guild',
    guild_id: int,
    artfight_role: 'discord.Role | None' = None
) -> list[str]:
    """
    Builds the Hall of Fame messages with fun stats for the end of artfight.
    Returns a list of plain text messages with markdown formatting (not embeds).
    Split to respect Discord's 2000 character limit.
    
    :param artfight_repo: The artfight repository
    :param guild: The Discord guild (for member lookups)
    :param guild_id: The guild ID
    :param artfight_role: The artfight role (unused, kept for compatibility)
    :return: List of Hall of Fame message strings
    """
    import datetime
    from collections import Counter
    
    end_date = artfight_repo.get_end_date(guild_id)
    year = end_date.year if end_date else datetime.datetime.now().year

    def get_display_name(member_id: int) -> str:
        """Get member's display name or fallback to 'Unknown (id)'"""
        member = guild.get_member(member_id)
        return member.display_name if member else f"Unknown ({member_id})"
    
    teams: dict[str, int] = artfight_repo.get_teams(guild_id)
    """team_name: role_id"""
    if not teams:
        return [f"# 🏆 Artfight {year} - Hall of Fame 🏆\nI got hungry and ate the data, sorry guys"]
    
    player_most_submissions: tuple[list[int], int] = ([], 0) # member_ids, submission_count
    player_most_points: tuple[list[int], int] = ([], 0) # member_ids, points
    player_most_attacked_by_submissions: tuple[list[int], int] = ([], 0) # member_ids, submission_count
    player_most_attacked_by_points: tuple[list[int], int] = ([], 0) # member_ids, points

    team_rankings: dict[str, dict[str, tuple[list[int], int]]] = {}
    # team_name, [stat_name, [member_ids, stat_value]] 

    most_active_team: tuple[list[int], int] = ([], 0) # team_role_ids, submission_count
    biggest_solo_attack: tuple[list[dict], int] = ([], 0) # [{member_id, attack_name, image_url}, ...], points
    biggest_collab: dict[str: int | str] = {} # attack_name, image_url, member_count

    prompt_day_submission_count: dict[int, int] = {} # artfight_day: count
    seen_collab_urls: set[str] = set() # track already counted collabs
    
    # victim_id -> {attack_count, points_received, team_name}
    victim_stats: dict[int, dict[str, int | str]] = {}

    for team_name, team_role_id in teams.items():
        members = artfight_repo.get_team_members(guild_id=guild_id, team_name=team_name)

        if team_name not in team_rankings:
            team_rankings[team_name] = {
                'most_points_1': ([], 0),
                'most_points_2': ([], 0),
                'most_points_3': ([], 0),
                'most_submissions_1': ([], 0),
                'most_submissions_2': ([], 0),
                'most_submissions_3': ([], 0),
            }

        team_submission_count = 0

        for member_id_str, member_data in filter(lambda kv: kv[0].isdigit(), members.items()):
            member_id = int(member_id_str)

            points = member_data['points']
            if points > player_most_points[1]:
                player_most_points = ([member_id], points)
            elif points == player_most_points[1] and points > 0:
                player_most_points[0].append(member_id)

            # Team rankings - most points (with shift down)
            if points > team_rankings[team_name]['most_points_1'][1]:
                team_rankings[team_name]['most_points_3'] = team_rankings[team_name]['most_points_2']
                team_rankings[team_name]['most_points_2'] = team_rankings[team_name]['most_points_1']
                team_rankings[team_name]['most_points_1'] = ([member_id], points)
            elif points == team_rankings[team_name]['most_points_1'][1] and points > 0:
                team_rankings[team_name]['most_points_1'][0].append(member_id)
            elif points > team_rankings[team_name]['most_points_2'][1]:
                team_rankings[team_name]['most_points_3'] = team_rankings[team_name]['most_points_2']
                team_rankings[team_name]['most_points_2'] = ([member_id], points)
            elif points == team_rankings[team_name]['most_points_2'][1] and points > 0:
                team_rankings[team_name]['most_points_2'][0].append(member_id)
            elif points > team_rankings[team_name]['most_points_3'][1]:
                team_rankings[team_name]['most_points_3'] = ([member_id], points)
            elif points == team_rankings[team_name]['most_points_3'][1] and points > 0:
                team_rankings[team_name]['most_points_3'][0].append(member_id)
            
            submission_count = len(member_data['submissions'])
            team_submission_count += submission_count

            if submission_count > player_most_submissions[1]:
                player_most_submissions = ([member_id], submission_count)
            elif submission_count == player_most_submissions[1] and submission_count > 0:
                player_most_submissions[0].append(member_id)

            # Team rankings - most submissions (with shift down)
            if submission_count > team_rankings[team_name]['most_submissions_1'][1]:
                team_rankings[team_name]['most_submissions_3'] = team_rankings[team_name]['most_submissions_2']
                team_rankings[team_name]['most_submissions_2'] = team_rankings[team_name]['most_submissions_1']
                team_rankings[team_name]['most_submissions_1'] = ([member_id], submission_count)
            elif submission_count == team_rankings[team_name]['most_submissions_1'][1] and submission_count > 0:
                team_rankings[team_name]['most_submissions_1'][0].append(member_id)
            elif submission_count > team_rankings[team_name]['most_submissions_2'][1]:
                team_rankings[team_name]['most_submissions_3'] = team_rankings[team_name]['most_submissions_2']
                team_rankings[team_name]['most_submissions_2'] = ([member_id], submission_count)
            elif submission_count == team_rankings[team_name]['most_submissions_2'][1] and submission_count > 0:
                team_rankings[team_name]['most_submissions_2'][0].append(member_id)
            elif submission_count > team_rankings[team_name]['most_submissions_3'][1]:
                team_rankings[team_name]['most_submissions_3'] = ([member_id], submission_count)
            elif submission_count == team_rankings[team_name]['most_submissions_3'][1] and submission_count > 0:
                team_rankings[team_name]['most_submissions_3'][0].append(member_id)
            
            for submission_url, submission_data in member_data['submissions'].items():
                sub_points = submission_data.get('points', 0)
                sub_title = submission_data.get('title', '')
                collaborators = submission_data.get('collaborators', [])
                prompt_day = submission_data.get('prompt_day')

                # Track prompt day counts
                if prompt_day:
                    if prompt_day not in prompt_day_submission_count:
                        prompt_day_submission_count[prompt_day] = 0
                    prompt_day_submission_count[prompt_day] += 1

                # Track biggest solo attack (no collaborators)
                if not collaborators:
                    if sub_points > biggest_solo_attack[1]:
                        biggest_solo_attack = ([{
                            'member_id': member_id,
                            'attack_name': sub_title,
                            'image_url': submission_url
                        }], sub_points)
                    elif sub_points == biggest_solo_attack[1] and sub_points > 0:
                        biggest_solo_attack[0].append({
                            'member_id': member_id,
                            'attack_name': sub_title,
                            'image_url': submission_url
                        })

                # Track biggest collab (check if image_url not already seen)
                if collaborators and submission_url not in seen_collab_urls:
                    seen_collab_urls.add(submission_url)
                    member_count = 1 + len(collaborators)  # submitter + collaborators
                    if not biggest_collab or member_count > biggest_collab['member_count']:
                        biggest_collab = {
                            'attack_name': sub_title,
                            'image_url': submission_url,
                            'member_count': member_count
                        }

                # Track victim stats
                victims = submission_data.get('victims', [])
                for victim_id in victims:
                    if isinstance(victim_id, str) and victim_id.isdigit():
                        victim_id = int(victim_id)
                    if isinstance(victim_id, int):
                        if victim_id not in victim_stats:
                            victim_stats[victim_id] = {'attack_count': 0, 'points_received': 0, 'team_name': None}
                        victim_stats[victim_id]['attack_count'] += 1
                        victim_stats[victim_id]['points_received'] += sub_points

        # Track most active team
        if team_submission_count > most_active_team[1]:
            most_active_team = ([team_role_id], team_submission_count)
        elif team_submission_count == most_active_team[1] and team_submission_count > 0:
            most_active_team[0].append(team_role_id)

    # Calculate most popular prompt from counts
    most_popular_prompt: dict[str: int | str] = {}  # prompt_day, prompt_name, submission_count
    if prompt_day_submission_count:
        prompts = artfight_repo.get_prompts(guild_id) or {}
        max_day = max(prompt_day_submission_count, key=prompt_day_submission_count.get)
        most_popular_prompt = {
            'prompt_day': max_day,
            'prompt_name': prompts.get(str(max_day), 'Unknown'),
            'submission_count': prompt_day_submission_count[max_day]
        }

    # Determine team for each victim and calculate global most attacked
    for victim_id in victim_stats:
        for team_name in teams.keys():
            if artfight_repo.get_team_member(guild_id, team_name, victim_id):
                victim_stats[victim_id]['team_name'] = team_name
                break
        
        attack_count = victim_stats[victim_id]['attack_count']
        points_received = victim_stats[victim_id]['points_received']
        
        if attack_count > player_most_attacked_by_submissions[1]:
            player_most_attacked_by_submissions = ([victim_id], attack_count)
        elif attack_count == player_most_attacked_by_submissions[1] and attack_count > 0:
            player_most_attacked_by_submissions[0].append(victim_id)
        
        if points_received > player_most_attacked_by_points[1]:
            player_most_attacked_by_points = ([victim_id], points_received)
        elif points_received == player_most_attacked_by_points[1] and points_received > 0:
            player_most_attacked_by_points[0].append(victim_id)

    # Initialize victim rankings in team_rankings for each team
    for team_name in teams.keys():
        team_rankings[team_name]['most_attacked_1'] = ([], 0)
        team_rankings[team_name]['most_attacked_2'] = ([], 0)
        team_rankings[team_name]['most_attacked_3'] = ([], 0)
        team_rankings[team_name]['most_points_received_1'] = ([], 0)
        team_rankings[team_name]['most_points_received_2'] = ([], 0)
        team_rankings[team_name]['most_points_received_3'] = ([], 0)

    # Calculate per-team victim rankings
    for victim_id, stats in victim_stats.items():
        team_name = stats['team_name']
        if not team_name:
            continue
        
        attack_count = stats['attack_count']
        points_received = stats['points_received']
        
        # By attack count
        if attack_count > team_rankings[team_name]['most_attacked_1'][1]:
            # Shift down
            team_rankings[team_name]['most_attacked_3'] = team_rankings[team_name]['most_attacked_2']
            team_rankings[team_name]['most_attacked_2'] = team_rankings[team_name]['most_attacked_1']
            team_rankings[team_name]['most_attacked_1'] = ([victim_id], attack_count)
        elif attack_count == team_rankings[team_name]['most_attacked_1'][1] and attack_count > 0:
            team_rankings[team_name]['most_attacked_1'][0].append(victim_id)
        elif attack_count > team_rankings[team_name]['most_attacked_2'][1]:
            team_rankings[team_name]['most_attacked_3'] = team_rankings[team_name]['most_attacked_2']
            team_rankings[team_name]['most_attacked_2'] = ([victim_id], attack_count)
        elif attack_count == team_rankings[team_name]['most_attacked_2'][1] and attack_count > 0:
            team_rankings[team_name]['most_attacked_2'][0].append(victim_id)
        elif attack_count > team_rankings[team_name]['most_attacked_3'][1]:
            team_rankings[team_name]['most_attacked_3'] = ([victim_id], attack_count)
        elif attack_count == team_rankings[team_name]['most_attacked_3'][1] and attack_count > 0:
            team_rankings[team_name]['most_attacked_3'][0].append(victim_id)
        
        # By points received
        if points_received > team_rankings[team_name]['most_points_received_1'][1]:
            team_rankings[team_name]['most_points_received_3'] = team_rankings[team_name]['most_points_received_2']
            team_rankings[team_name]['most_points_received_2'] = team_rankings[team_name]['most_points_received_1']
            team_rankings[team_name]['most_points_received_1'] = ([victim_id], points_received)
        elif points_received == team_rankings[team_name]['most_points_received_1'][1] and points_received > 0:
            team_rankings[team_name]['most_points_received_1'][0].append(victim_id)
        elif points_received > team_rankings[team_name]['most_points_received_2'][1]:
            team_rankings[team_name]['most_points_received_3'] = team_rankings[team_name]['most_points_received_2']
            team_rankings[team_name]['most_points_received_2'] = ([victim_id], points_received)
        elif points_received == team_rankings[team_name]['most_points_received_2'][1] and points_received > 0:
            team_rankings[team_name]['most_points_received_2'][0].append(victim_id)
        elif points_received > team_rankings[team_name]['most_points_received_3'][1]:
            team_rankings[team_name]['most_points_received_3'] = ([victim_id], points_received)
        elif points_received == team_rankings[team_name]['most_points_received_3'][1] and points_received > 0:
            team_rankings[team_name]['most_points_received_3'][0].append(victim_id)
    
    hardworking_team_parts = []
    victems_team_parts = []

    for team_name, team_role_id in teams.items():
        team_ranking = team_rankings[team_name]

        hardworking_team_parts.append(
            f'On team <@&{team_role_id}> ({team_name})\n'
            'By submissions:\n'
            f'🥇 {', '.join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking['most_submissions_1'][0])} - {team_ranking['most_submissions_1'][1]}\n'
            f'🥈 {', '.join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking['most_submissions_2'][0])} - {team_ranking['most_submissions_2'][1]}\n'
            f'🥉 {', '.join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking['most_submissions_3'][0])} - {team_ranking['most_submissions_3'][1]}\n'
            '\n'
            'By score:\n'
            f'🥇 {', '.join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking['most_points_1'][0])} - {team_ranking['most_points_1'][1]}\n'
            f'🥈 {', '.join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking['most_points_2'][0])} - {team_ranking['most_points_2'][1]}\n'
            f'🥉 {', '.join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking['most_points_3'][0])} - {team_ranking['most_points_3'][1]}\n'
        )

        victems_team_parts.append(
            f'On team <@&{team_role_id}> ({team_name})\n'
            'By attacks:\n'
            f'🥀 {", ".join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking["most_attacked_1"][0])} - {team_ranking["most_attacked_1"][1]}\n'
            f'🥀 {", ".join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking["most_attacked_2"][0])} - {team_ranking["most_attacked_2"][1]}\n'
            f'🥀 {", ".join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking["most_attacked_3"][0])} - {team_ranking["most_attacked_3"][1]}\n'
            '\n'
            'By points received:\n'
            f'🥀 {", ".join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking["most_points_received_1"][0])} - {team_ranking["most_points_received_1"][1]}\n'
            f'🥀 {", ".join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking["most_points_received_2"][0])} - {team_ranking["most_points_received_2"][1]}\n'
            f'🥀 {", ".join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in team_ranking["most_points_received_3"][0])} - {team_ranking["most_points_received_3"][1]}\n'
        )
    
    # Build sections as a list, then combine with smart splitting
    sections = [
        f'# 🏆 Artfight {year} - Hall of Fame 🏆\n',
        
        '## 👑 The Hard-Working 👑\n'
        f'🏅 By submission: {', '.join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in player_most_submissions[0])} - {player_most_submissions[1]}\n'
        f'🏅 By score: {', '.join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in player_most_points[0])} - {player_most_points[1]}\n',
    ]
    
    for team_part in hardworking_team_parts:
        sections.append(team_part)
    
    sections.append(
        '## ☠️ The Victims ☠️\n'
        f'⚰️ By attacks: {', '.join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in player_most_attacked_by_submissions[0])} - {player_most_attacked_by_submissions[1]}\n'
        f'⚰️ By score: {', '.join(f"<@{member_id}> ({get_display_name(member_id)})" for member_id in player_most_attacked_by_points[0])} - {player_most_attacked_by_points[1]}\n'
    )
    
    for team_part in victems_team_parts:
        sections.append(team_part)
    
    sections.extend([
        '## 💥 Most Active Team 💥\n'
        f'{", ".join(f"<@&{team_id}>" for team_id in most_active_team[0])} - {most_active_team[1]} submissions\n',
        
        '## ✍️ Highest Scoring Solo Attack ✍️\n'
        f'{'\n'.join(f"[{attack['attack_name']}]({attack['image_url']}) by <@{attack['member_id']}> ({get_display_name(attack['member_id'])}) - {biggest_solo_attack[1]}" for attack in biggest_solo_attack[0])}\n',
        
        '## 🤝 Biggest Collab 🤝\n'
        f'[{biggest_collab.get("attack_name", "N/A")}]({biggest_collab.get("image_url", "")}) - {biggest_collab.get("member_count", 0)} members\n',
        
        '## 🌸 Most Popular Prompt 🌸\n'
        f'Day {most_popular_prompt.get("prompt_day", "N/A")}: {most_popular_prompt.get("prompt_name", "N/A")} - {most_popular_prompt.get("submission_count", 0)} submissions\n',
        
        '## 😎 The Skibidiest 😎\n'
        'Riko Sakari\n'
        '\n'
        '-# sigma sigma on the wall, who\'s the skibidiest of them all? - me heh'
    ])

    # Split into messages respecting Discord's 2000 char limit
    messages = []
    current_message = ""
    
    for section in sections:
        # If adding this section would exceed the limit, start a new message
        if len(current_message) + len(section) + 1 > 2000:
            if current_message:
                messages.append(current_message.strip())
            current_message = section
        else:
            current_message += '\n' + section if current_message else section
    
    # Don't forget the last message
    if current_message:
        messages.append(current_message.strip())

    return messages
