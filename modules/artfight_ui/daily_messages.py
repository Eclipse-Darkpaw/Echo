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
) -> str:
    """
    Builds the Hall of Fame message with fun stats for the end of artfight.
    Returns a plain text message with markdown formatting (not an embed).
    
    :param artfight_repo: The artfight repository
    :param guild: The Discord guild (for member lookups)
    :param guild_id: The guild ID
    :param artfight_role: The artfight role (unused, kept for compatibility)
    :return: The Hall of Fame message string
    """
    import datetime
    from collections import Counter
    
    end_date = artfight_repo.get_end_date(guild_id)
    year = end_date.year if end_date else datetime.datetime.now().year
    
    teams = artfight_repo.get_teams(guild_id)
    if not teams:
        return f"# 🏆 Artfight {year} - Hall of Fame 🏆\n\nNo team data available."
    
    # Collect comprehensive stats
    team_stats = {}  # team_name -> {role_id, submissions, members_data}
    all_submissions = []
    victim_stats = {}  # user_id -> {by_count, by_score, team}
    prompt_counts = Counter()
    biggest_collab = {'size': 0, 'members': [], 'title': ''}
    
    for team_name, role_id in teams.items():
        members = artfight_repo.get_team_members(guild_id, team_name) or {}
        team_submission_count = 0
        members_data = {}
        
        for user_id, user_data in members.items():
            submissions = user_data.get('submissions', {})
            submission_count = len(submissions)
            user_points = user_data.get('points', 0)
            team_submission_count += submission_count
            
            members_data[user_id] = {
                'submissions': submission_count,
                'points': user_points,
                'team': team_name
            }
            
            for sub_url, sub_data in submissions.items():
                victims = sub_data.get('victims', [])
                collaborators = sub_data.get('collaborators', [])
                prompt_day = sub_data.get('prompt_day')
                title = sub_data.get('title', 'Untitled')
                points = sub_data.get('points', 0)
                
                all_submissions.append({
                    'user_id': user_id,
                    'team_name': team_name,
                    'points': points,
                    'victims': victims,
                    'collaborators': collaborators,
                    'prompt_day': prompt_day,
                    'title': title
                })
                
                for victim_id in victims:
                    if victim_id not in victim_stats:
                        victim_stats[victim_id] = {'by_count': 0, 'by_score': 0, 'team': None}
                    victim_stats[victim_id]['by_count'] += 1
                    victim_stats[victim_id]['by_score'] += points
                
                if prompt_day:
                    prompt_counts[prompt_day] += 1
                
                collab_size = 1 + len(collaborators)
                if collab_size > biggest_collab['size']:
                    biggest_collab = {
                        'size': collab_size,
                        'members': [user_id] + collaborators,
                        'title': title
                    }
        
        team_stats[team_name] = {
            'role_id': role_id,
            'submissions': team_submission_count,
            'members_data': members_data
        }
    
    # Determine team for each victim
    for victim_id in victim_stats:
        for team_name in teams.keys():
            if artfight_repo.get_team_member(guild_id, team_name, victim_id):
                victim_stats[victim_id]['team'] = team_name
                break
    
    # Helper to format winners with tie support
    def format_winners(entries: list[tuple], value_suffix: str = "") -> str:
        """Format top entries, showing all ties for first place."""
        if not entries:
            return "None"
        entries = sorted(entries, key=lambda x: x[1], reverse=True)
        top_val = entries[0][1]
        winners = [e for e in entries if e[1] == top_val]
        if len(winners) == 1:
            return f"<@{winners[0][0]}> ({winners[0][1]}{value_suffix})"
        else:
            return " / ".join(f"<@{uid}>" for uid, _ in winners) + f" ({top_val}{value_suffix})"
    
    def format_team_winners(entries: list[tuple], value_suffix: str = "") -> str:
        """Format top team entries with tie support."""
        if not entries:
            return "None"
        entries = sorted(entries, key=lambda x: x[1], reverse=True)
        top_val = entries[0][1]
        winners = [e for e in entries if e[1] == top_val]
        if len(winners) == 1:
            return f"<@&{winners[0][2]}> ({winners[0][1]}{value_suffix})"
        else:
            return " / ".join(f"<@&{rid}>" for _, _, rid in winners) + f" ({top_val}{value_suffix})"
    
    team_names = list(teams.keys())
    lines = [f"# 🏆 Artfight {year} - Hall of Fame 🏆", ""]
    
    # === 👑 The Hard-Working 👑 ===
    lines.append("## 👑 The Hard-Working 👑")
    
    all_members_subs = [(uid, data['submissions']) 
                        for stats in team_stats.values() 
                        for uid, data in stats['members_data'].items() 
                        if data['submissions'] > 0]
    all_members_score = [(uid, data['points']) 
                         for stats in team_stats.values() 
                         for uid, data in stats['members_data'].items() 
                         if data['points'] > 0]
    
    if all_members_subs:
        lines.append(f"By submissions: {format_winners(all_members_subs)}")
    if all_members_score:
        lines.append(f"By score: {format_winners(all_members_score, ' pts')}")
    lines.append("")
    
    # Per team
    for team_name in team_names:
        stats = team_stats.get(team_name, {})
        members_data = stats.get('members_data', {})
        role_id = stats.get('role_id')
        
        team_subs = [(uid, d['submissions']) for uid, d in members_data.items() if d['submissions'] > 0]
        team_score = [(uid, d['points']) for uid, d in members_data.items() if d['points'] > 0]
        
        if team_subs or team_score:
            lines.append(f"On <@&{role_id}>:")
            if team_subs:
                lines.append(f"By submissions: {format_winners(team_subs)}")
            if team_score:
                lines.append(f"By score: {format_winners(team_score, ' pts')}")
            lines.append("")
    
    # === ☠️ The Victim ☠️ ===
    lines.append("## ☠️ The Victims ☠️")
    
    victims_by_count = [(vid, data['by_count']) for vid, data in victim_stats.items()]
    victims_by_score = [(vid, data['by_score']) for vid, data in victim_stats.items()]
    
    if victims_by_count:
        lines.append(f"By attacks: {format_winners(victims_by_count)}")
    if victims_by_score:
        lines.append(f"By score: {format_winners(victims_by_score, ' pts')}")
    lines.append("")
    
    # Per team
    for team_name in team_names:
        role_id = teams.get(team_name)
        team_victims_count = [(vid, d['by_count']) for vid, d in victim_stats.items() if d['team'] == team_name]
        team_victims_score = [(vid, d['by_score']) for vid, d in victim_stats.items() if d['team'] == team_name]
        
        if team_victims_count or team_victims_score:
            lines.append(f"On <@&{role_id}>:")
            if team_victims_count:
                lines.append(f"By attacks: {format_winners(team_victims_count)}")
            if team_victims_score:
                lines.append(f"By score: {format_winners(team_victims_score, ' pts')}")
            lines.append("")
    
    # === 📝 Highest Scoring Solo Attack 📝 ===
    solo_submissions = [s for s in all_submissions if not s.get('collaborators')]
    if solo_submissions:
        top_solo = max(solo_submissions, key=lambda s: s['points'])
        title_part = f'*"{top_solo["title"]}"*' if top_solo.get('title') else ''
        lines.append("### 📝 Highest Scoring Solo Attack 📝")
        lines.append(f"<@{top_solo['user_id']}> with {title_part} ({top_solo['points']} pts)")
        lines.append("")
    
    # === 🤝 Biggest Collab 🤝 ===
    if biggest_collab['size'] > 1:
        title_part = f'*"{biggest_collab["title"]}"*' if biggest_collab.get('title') else 'Untitled'
        lines.append("### 🤝 Biggest Collab 🤝")
        lines.append(f"{title_part} with {biggest_collab['size']} people")
        lines.append("")
    
    # === 💥 Most Active Team 💥 ===
    if team_stats:
        teams_by_subs = [(name, stats['submissions'], stats['role_id']) for name, stats in team_stats.items()]
        teams_by_subs.sort(key=lambda x: x[1], reverse=True)
        if teams_by_subs and teams_by_subs[0][1] > 0:
            lines.append("### 💥 Most Active Team 💥")
            lines.append(f"{format_team_winners(teams_by_subs, ' submissions')}")
            lines.append("")
    
    # === 🌸 Most Popular Prompt 🌸 ===
    prompts = artfight_repo.get_prompts(guild_id) or {}
    if prompt_counts and prompts:
        most_popular_day, most_count = prompt_counts.most_common(1)[0]
        most_prompt_text = prompts.get(str(most_popular_day), "Unknown")
        lines.append("### 🌸 Most Popular Prompt 🌸")
        lines.append(f"Day {most_popular_day}: *\"{most_prompt_text}\"* ({most_count} submissions)")
        lines.append("")
    
    # === 😎 The Skibidiest 😎 ===
    lines.append("### 😎 The Skibidiest 😎")
    lines.append("<@465057997190856714>")
    lines.append("")
    
    lines.append("-# sigma sigma on the wall, who's the skibidiest of them all?")
    
    return '\n'.join(lines)
