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
        return f"{role_ping} **FINAL DAY!** Submissions close {time_str}!\nThis is your last chance!"
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
) -> discord.Embed:
    """
    Builds the fancy leaderboard embed with fun stats for the end of artfight.
    
    :param artfight_repo: The artfight repository
    :param guild: The Discord guild (for member lookups)
    :param guild_id: The guild ID
    :param artfight_role: The artfight role (for embed color)
    :return: The fancy leaderboard embed
    """
    import datetime
    from collections import Counter
    
    start_date = artfight_repo.get_start_date(guild_id)
    end_date = artfight_repo.get_end_date(guild_id)
    year = end_date.year if end_date else datetime.datetime.now().year
    
    # Use artfight role color if available
    embed_color = artfight_role.color if artfight_role else discord.Color.gold()
    
    embed = discord.Embed(
        title=f"🏆 Artfight {year} - Hall of Fame 🏆",
        color=embed_color
    )
    
    teams = artfight_repo.get_teams(guild_id)
    if not teams:
        embed.description = "No team data available."
        return embed
    
    # Collect comprehensive stats
    team_stats = {}  # team_name -> {role_id, submissions, top_attacker: (user_id, count)}
    all_submissions = []  # List of submission dicts with full data
    victim_counts = Counter()  # user_id -> times attacked
    prompt_counts = Counter()  # prompt_day -> submission count
    biggest_collab = {'size': 0, 'members': [], 'title': ''}
    
    for team_name, role_id in teams.items():
        members = artfight_repo.get_team_members(guild_id, team_name) or {}
        team_submission_count = 0
        top_attacker_id = None
        top_attacker_count = 0
        
        for user_id, user_data in members.items():
            submissions = user_data.get('submissions', {})
            submission_count = len(submissions)
            team_submission_count += submission_count
            
            if submission_count > top_attacker_count:
                top_attacker_count = submission_count
                top_attacker_id = user_id
            
            for sub_url, sub_data in submissions.items():
                # Extract new fields
                victims = sub_data.get('victims', [])
                collaborators = sub_data.get('collaborators', [])
                prompt_day = sub_data.get('prompt_day')
                title = sub_data.get('title', 'Untitled')
                
                all_submissions.append({
                    'user_id': user_id,
                    'team_name': team_name,
                    'points': sub_data.get('points', 0),
                    'url': sub_url,
                    'victims': victims,
                    'collaborators': collaborators,
                    'prompt_day': prompt_day,
                    'title': title
                })
                
                # Count victims
                for victim_id in victims:
                    victim_counts[victim_id] += 1
                
                # Count prompts
                if prompt_day:
                    prompt_counts[prompt_day] += 1
                
                # Track biggest collab
                collab_size = 1 + len(collaborators)  # Submitter + collaborators
                if collab_size > biggest_collab['size']:
                    biggest_collab = {
                        'size': collab_size,
                        'members': [user_id] + collaborators,
                        'title': title
                    }
        
        team_stats[team_name] = {
            'role_id': role_id,
            'submissions': team_submission_count,
            'top_attacker': (top_attacker_id, top_attacker_count) if top_attacker_id else None
        }
    
    # The Hardworking of {year} - Most attacks per team
    hardworking_lines = []
    for team_name, stats in team_stats.items():
        if stats['top_attacker']:
            user_id, count = stats['top_attacker']
            hardworking_lines.append(f"<@&{stats['role_id']}>: <@{user_id}> ({count} attacks)")
    
    if hardworking_lines:
        embed.add_field(
            name=f"The Hardworking of {year}",
            value="\n".join(hardworking_lines),
            inline=False
        )
    
    # The Victim of {year} - Most attacks received per team
    if victim_counts:
        # Group victims by team
        team_victims = {}
        for victim_id, count in victim_counts.most_common():
            victim_team = None
            for team_name in teams.keys():
                if artfight_repo.get_team_member(guild_id, team_name, victim_id):
                    victim_team = team_name
                    break
            
            if victim_team and victim_team not in team_victims:
                team_victims[victim_team] = (victim_id, count)
        
        if team_victims:
            victim_lines = []
            for team_name, (victim_id, count) in team_victims.items():
                role_id = teams.get(team_name)
                victim_lines.append(f"<@&{role_id}>: <@{victim_id}> ({count} times)")
            
            embed.add_field(
                name=f"The Victim of {year}",
                value="\n".join(victim_lines),
                inline=False
            )
    
    # Individual Attack with the highest score
    if all_submissions:
        top_submission = max(all_submissions, key=lambda s: s['points'])
        embed.add_field(
            name="Highest Scoring Attack",
            value=f"<@{top_submission['user_id']}> with **{top_submission['points']}** points\n*\"{top_submission['title']}\"*",
            inline=True
        )
    
    # Biggest collab
    if biggest_collab['size'] > 1:
        collab_mentions = [f"<@{m}>" for m in biggest_collab['members']]
        embed.add_field(
            name="Biggest Collab",
            value=f"{', '.join(collab_mentions)}\n*\"{biggest_collab['title']}\"*",
            inline=True
        )
    
    # Team with the most submissions
    if team_stats:
        top_team = max(team_stats.items(), key=lambda t: t[1]['submissions'])
        if top_team[1]['submissions'] > 0:
            embed.add_field(
                name="Most ~~Active~~ Sigma Team",
                value=f"<@&{top_team[1]['role_id']}> with **{top_team[1]['submissions']}** submissions",
                inline=True
            )
    
    # Most and least popular prompts
    prompts = artfight_repo.get_prompts(guild_id) or {}
    if prompt_counts and prompts:
        most_popular_day, most_count = prompt_counts.most_common(1)[0]
        least_popular_day, least_count = prompt_counts.most_common()[-1]
        
        most_prompt_text = prompts.get(str(most_popular_day), "Unknown")[:30]
        least_prompt_text = prompts.get(str(least_popular_day), "Unknown")[:30]
        
        embed.add_field(
            name="Most Popular Prompt",
            value=f"Day {most_popular_day}: *\"{most_prompt_text}...\"* ({most_count} submissions)",
            inline=True
        )
        
        if most_popular_day != least_popular_day:
            embed.add_field(
                name="Least Popular Prompt",
                value=f"Day {least_popular_day}: *\"{least_prompt_text}...\"* ({least_count} submissions)",
                inline=True
            )
    
    # The skibidest of the event - always Riko (as per OVERVIEW)
    embed.add_field(
        name="The Skibidest of the Event",
        value="<@465057997190856714>",
        inline=True
    )
    
    embed.set_footer(text="sigma sigma on the wall, who's the skibidiest of them all?")
    
    return embed
