import pytz
import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta
from discord.ext import commands
import matplotlib.pyplot as plt
import os
import json
import seaborn as sns
import pandas as pd


# Initialize the bot with a command prefix and the necessary intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


# Initialize a dictionary to store user placements
if os.path.exists('placements.json'):
    with open('placements.json', 'r') as f:
        placements = json.load(f)
else:
    placements = {}


# Initialize a dictionary to keep track of the race points
race_points = {'team': 0, 'opponent': 0, 'races': 0}

# Define the points system
points_system = {1: 15, 2: 12, 3: 10, 4: 9, 5: 8, 6: 7, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command(name='startwar', help='Starts the match')
async def startwar(ctx):
    # Reset the points and race count
    race_points['team'] = 0
    race_points['opponent'] = 0
    race_points['races'] = 0
    await ctx.channel.send("The match has started!")


@bot.command(name='race', help='Enter the positions to calculate points. Format: /race 1,2,3,4,5,6')
async def race(ctx, *, positions: str):
    try:
        position_list = [int(pos.strip()) for pos in positions.split(',')]
        if len(position_list) != 6:
            await ctx.send("Error: Please enter exactly 6 positions.")
            return

        team_points = sum(points_system.get(pos, 0) for pos in position_list)
        opponent_positions = [pos for pos in range(1, 13) if pos not in position_list]
        opponent_points = sum(points_system.get(pos, 0) for pos in opponent_positions)

        race_points['team'] += team_points
        race_points['opponent'] += opponent_points
        race_points['races'] += 1

        # Calculate the points difference
        points_difference = race_points['team'] - race_points['opponent']

        # Send a response with the race results and the points difference
        await ctx.send(
            f"Race {race_points['races']}: Team Points - {team_points}, Opponent Points - {opponent_points}.\n"
            f"Total: Team - {race_points['team']}, Opponent - {race_points['opponent']}.\n"
            f"Points Difference: {points_difference} (Team - Opponent).")
    except ValueError:
        await ctx.send("Error: Positions must be numbers.")


timezone_mappings = {
    "CET": "Europe/Berlin",
    "EST": "America/New_York",
    "PST": "America/Los_Angeles",
    "GMT": "Europe/London",
    "JST": "Asia/Tokyo",
    "AEST": "Australia/Sydney",
    "CST": "Asia/Shanghai",
    "BRT": "America/Sao_Paulo",
    "PKT": "Asia/Karachi",
    "AWST": "Australia/Perth",
}


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command()
async def gather(ctx, timezone_abbreviation: str, time_input: str):
    # Convert abbreviation to a timezone name
    timezone = timezone_mappings.get(timezone_abbreviation.upper())
    if timezone is None:
        await ctx.send(f"Unknown timezone abbreviation: {timezone_abbreviation}")
        return

    user_timezone = pytz.timezone(timezone)
    now = datetime.now(user_timezone)

    if '-' in time_input:  # Handle time range
        try:
            start_time_str, end_time_str = time_input.split('-')
            start_hour, start_minute = map(int, start_time_str.split(':'))
            end_hour, end_minute = map(int, end_time_str.split(':'))
            start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            end_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)

            # Ensure end_time is after start_time
            if end_time <= start_time:
                end_time += timedelta(days=1)

            current_time = start_time
            while current_time <= end_time:
                unix_timestamp = int(current_time.timestamp())
                timestamp_message = f"<t:{unix_timestamp}:t>"
                await ctx.send(timestamp_message)
                current_time += timedelta(hours=1)  # Increment by one hour
        except Exception as e:
            await ctx.send(f"Error processing time range: {str(e)}")
            return
    else:  # Handle single time
        try:
            hour, minute = map(int, time_input.split(':'))
            single_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            unix_timestamp = int(single_time.timestamp())
            timestamp_message = f"<t:{unix_timestamp}:t>"
            await ctx.send(timestamp_message)
        except Exception as e:
            await ctx.send(f"Error processing time: {str(e)}")


# Initialize dictionaries to store user placements and session data
data_file = 'placements.json'


# List of valid track abbreviations
valid_tracks = [
    "MKS", "WP", "SSC", "TR", "MC", "TH", "TM", "SGF", "SA", "DS", "ED", "MW", "CC", "BDD", "BC", "RR",
    "rMMM", "rMC", "rCCB", "rTT", "rDDD", "rDP3", "rRRY", "rDKJ", "rWS", "rSL", "rMP", "rYV", "rTTC",
    "rPPS", "rGV", "rRRD", "dYC", "dEA", "dDD", "dMC", "dWGM", "dRR", "dIIO", "dHC", "dBP", "dCL",
    "dWW", "dAC", "dNBC", "dRIR", "dSBS", "dBB", "bPP", "bTC", "bCMo", "bCMa", "bTB", "bSR", "bSG",
    "bNH", "bNYM", "bMC3", "bKD", "bWP", "bSS", "bSL", "bMG", "bSHS", "bLL", "bBL", "bRRM", "bMT",
    "bBB", "bPG", "bMM", "bRR7", "bAD", "bRP", "bDKS", "bYI", "bBR", "bMC", "bWS", "bSSy", "bAtD",
    "bDC", "bMH", "bSCS", "bLAL", "bSW", "bKC", "bVV", "bRA", "bDKM", "bDCt", "bPPC", "bMD", "bRIW",
    "bBC3", "bRRW"
]

# Initialize dictionaries to store user placements and session data
data_file = 'placements.json'


# Function to load data from JSON file
def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
            # Migrate old data format to new format if necessary
            for user_id, placements in data.items():
                data[user_id] = [(p, '') if isinstance(p, int) else p for p in placements]
            return data
    return {}


# Function to save data to JSON file
def save_data(data):
    with open(data_file, 'w') as f:
        json.dump(data, f)


# Load initial data
placements_data = load_data()
sessions = {}


# Function to save a Seaborn chart to a PNG file
def save_chart(data, title, path):
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x='Position', y='Count', data=data, palette='viridis')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(range(1, 13))
    plt.title(title)
    plt.savefig(path)
    plt.close()


# Command to start a session
@bot.command()
async def session(ctx, action: str):
    user_id = str(ctx.author.id)

    if action == "start":
        sessions[user_id] = []
        await ctx.send(f"Session started for {ctx.author.name}.")
    elif action == "end":
        if user_id not in sessions:
            await ctx.send(f"No session found for {ctx.author.name}.")
            return

        session_placements = sessions.pop(user_id)
        if user_id not in placements_data:
            placements_data[user_id] = []

        # Merge session data into regular placements
        placements_data[user_id].extend(session_placements)
        save_data(placements_data)

        # Create and send session-specific bar chart
        data = pd.DataFrame(session_placements, columns=['Position', 'Track'])
        chart_data = data['Position'].value_counts().reindex(range(1, 13), fill_value=0).reset_index()
        chart_data.columns = ['Position', 'Count']

        chart_path = f"{ctx.author.name}_session_placement_chart.png"
        save_chart(chart_data, f'Session Placement Distribution for {ctx.author.name}', chart_path)

        await ctx.send(file=discord.File(chart_path))
        os.remove(chart_path)

        await ctx.send(f"Session ended and data merged for {ctx.author.name}.")


# Command to submit a placement
@bot.command()
async def place(ctx, position: int, track: str):
    if track not in valid_tracks:
        await ctx.send("Please use a correct track abbreviation.")
        return

    user_id = str(ctx.author.id)

    if user_id in sessions:
        sessions[user_id].append((position, track))
        await ctx.send(f"Placement {position} on track {track} saved for {ctx.author.name} in current session.")
    else:
        if user_id not in placements_data:
            placements_data[user_id] = []
        placements_data[user_id].append((position, track))
        save_data(placements_data)
        await ctx.send(f"Placement {position} on track {track} saved for {ctx.author.name}.")


# Command to show user stats
@bot.command()
async def stats(ctx, user: discord.User, track: str = None):
    user_id = str(user.id)
    if user_id not in placements_data or len(placements_data[user_id]) == 0:
        await ctx.send(f"No placements found for {user.name}.")
        return

    user_placements = placements_data[user_id]
    if track:
        filtered_placements = [p for p in user_placements if p[1] == track]
        if not filtered_placements:
            await ctx.send(f"No placements found for {user.name} on track {track}.")
            return
        data = pd.DataFrame(filtered_placements, columns=['Position', 'Track'])
        title = f'Placement Distribution for {user.name} on {track}'
    else:
        data = pd.DataFrame(user_placements, columns=['Position', 'Track'])
        title = f'Placement Distribution for {user.name}'

    chart_data = data['Position'].value_counts().reindex(range(1, 13), fill_value=0).reset_index()
    chart_data.columns = ['Position', 'Count']

    chart_path = f"{user.name}_placement_chart.png"
    save_chart(chart_data, title, chart_path)

    await ctx.send(file=discord.File(chart_path))
    os.remove(chart_path)


# Command to show average score
@bot.command()
async def average(ctx):
    user_id = str(ctx.author.id)
    if user_id not in placements_data or len(placements_data[user_id]) == 0:
        await ctx.send(f"No placements found for {ctx.author.name}.")
        return

    user_placements = [p[0] for p in placements_data[user_id]]
    average_score = sum(user_placements) / len(user_placements)

    await ctx.send(f"{ctx.author.name}'s average placement is {average_score:.2f}.")