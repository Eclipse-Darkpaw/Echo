import discord
import datetime

from repositories import ArtfightRepo


def build_daily_status_embed(
    artfight_repo: ArtfightRepo,
    guild: discord.Guild,
    artfight_day: int,
    start_date: datetime.date,
    end_date: datetime.date,
    artfight_role: discord.Role | None = None
) -> discord.Embed:
    """
    Builds the daily status embed with team scores and the day's prompt.
    
    Last docstring edit: -FoxyHunter V4.5.0
    Last method edit: -FoxyHunter V4.5.0
    
    :param artfight_repo: The artfight repository instance
    :param guild: The Discord guild
    :param artfight_day: The current day of artfight (1-indexed)
    :param start_date: The artfight start date
    :param end_date: The artfight end date
    :param artfight_role: The artfight role (for embed color)
    :return: The constructed embed
    """
    total_days = (end_date - start_date).days + 1
    embed_color = artfight_role.color if artfight_role else discord.Color.gold()

    embed = discord.Embed(
        title=f"🎨 Artfight Day {artfight_day} of {total_days}",
        color=embed_color,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    # Add team scores
    teams = artfight_repo.get_teams(guild.id)
    if teams:
        # Collect team data with scores
        team_data = []
        for team_name, role_id in teams.items():
            score = artfight_repo.get_team_score(guild.id, team_name) or 0
            role = guild.get_role(role_id)
            team_data.append({
                'name': team_name,
                'role': role,
                'role_id': role_id,
                'score': score
            })

        # Sort by score descending
        team_data.sort(key=lambda x: x['score'], reverse=True)

        # Build scoreboard
        scoreboard_lines = []
        for i, team in enumerate(team_data):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "▪️"
            role_mention = f"<@&{team['role_id']}>" if team['role'] else team['name']
            scoreboard_lines.append(f"{medal} {role_mention}: **{team['score']}** points")

        embed.add_field(
            name="📊 Team Standings",
            value="\n".join(scoreboard_lines) if scoreboard_lines else "No teams configured",
            inline=False
        )

        # If there are exactly 2 teams, show the point difference
        if len(team_data) == 2:
            diff = abs(team_data[0]['score'] - team_data[1]['score'])
            if diff == 0:
                embed.set_footer(text="🔥 It's a tie! The battle is intense!")
            else:
                leader_name = team_data[0]['name']
                embed.set_footer(text=f"🔥 {leader_name} leads by {diff} points!")
    else:
        embed.add_field(
            name="📊 Team Standings",
            value="No teams configured",
            inline=False
        )

    # Add today's prompt
    prompt = artfight_repo.get_prompt(guild.id, artfight_day)
    if prompt:
        embed.add_field(
            name=f"✨ Today's Prompt (Day {artfight_day})",
            value=prompt,
            inline=False
        )
    else:
        embed.add_field(
            name=f"✨ Today's Prompt (Day {artfight_day})",
            value="*No prompt set for today*",
            inline=False
        )

    # Add day multiplier info if applicable
    if artfight_day % 4 == 0:
        embed.add_field(
            name="🎉 BONUS DAY!",
            value="Points are **DOUBLED** today!",
            inline=False
        )

    return embed
