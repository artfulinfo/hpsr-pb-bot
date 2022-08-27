from flask import Flask
import srcomapi
import srcomapi.datatypes as dt
import datetime
import re

app = Flask(__name__)

api = srcomapi.SpeedrunCom()
api.debug = 1

# Map abbreviations to full game names
game_map = {
    # PC
    "hp1": "Harry Potter and the Philosopher's Stone (PC)",
    "hp2": "Harry Potter and the Chamber of Secrets (PC)",
    "hp3": "Harry Potter and the Prisoner of Azkaban (PC)",
    "hp1pc": "Harry Potter and the Philosopher's Stone (PC)",
    "hp2pc": "Harry Potter and the Chamber of Secrets (PC)",
    "hp3pc": "Harry Potter and the Prisoner of Azkaban (PC)",
    "hp4": "Harry Potter and the Goblet of Fire",
    "hp5": "Harry Potter and the Order of the Phoenix",
    "hp6": "Harry Potter and the Half Blood Prince",
    "hp7.1": "Harry Potter and the Deathly Hallows Part 1",
    "hp7.2": "Harry Potter and the Deathly Hallows Part 2",

    # PS1
    "hp1ps1": "Harry Potter and the Philosopher's Stone (PS1)",
    "hp2ps1": "Harry Potter and the Chamber of Secrets (PS1)",

    # 6GEN
    "hp16gen": "Harry Potter and the Philosopher's Stone (PS2,GCN,Xbox)",
    "hp36gen": "Harry Potter and the Prisoner of Azkaban (PS2,Xbox,GCN)",

    # GBC
    "hp1gbc": "Harry Potter and the Philosopher's Stone (GBC)",
    "hp2gbc": "Harry Potter and the Chamber of Secrets (GBC)",

    # GBA
    "hp1gba": "Harry Potter and the Philosopher's Stone (GBA)",
    "hp2gba": "Harry Potter and the Chamber of Secrets (GBA)",
    "hp3gba": "Harry Potter and the Prisoner of Azkaban (GBA)",

    # DBB
    "dbb": "Disney's Brother Bear",

    # Multiruns
    "multi":  "Harry Potter Multiruns",
    "hpmulti":  "Harry Potter Multiruns",
    "hp123pc":  "Harry Potter Multiruns",

    # Category extensions
    "hpce": "Harry Potter Category Extensions"

}

# Map abbreviations for category to full API names
# % Symbol received by request will appear as "%25"
# Clean name returned in response for readability
category_map = {
    'any': {'name': '<Category "Any%">', 'clean': 'Any%'},
    'any%25': {'name': '<Category "Any%">', 'clean': 'Any%'},
    '100': {'name': '<Category "100%">', 'clean': '100%'},
    '100%25': {'name': '<Category "100%">', 'clean': '100%'},
    'warpless': {'name': '<Category "Warpless">', 'clean': 'Warpless'},
    'glitchless': {'name': '<Category "Glitchless">', 'clean': 'Glitchless'},
    'gless': {'name': '<Category "Glitchless">', 'clean': 'Glitchless'},
    'awc': {'name': '<Category "All Wizard Cards">', 'clean': 'All Wizard Cards'},
    'allreq': {'name': '<Category "All Requirements">', 'clean': 'All Requirements'},
    'ng': {'name': '<Category "NG+">', 'clean': 'NG+'},
    'allshields': {'name': '<Category "All Shields">', 'clean': 'All Shields'},
    'allcrests': {'name': '<Category "All Crests">', 'clean': 'All Crests'},
    'boostless': {'name': '<Category "Boostless">', 'clean': 'Boostless'},
    'trifecta': {'name': '<Category "PC Trifecta">', 'clean': 'Trifecta'},
    'octofecta': {'name': '<Category "PC Octofecta">', 'clean': 'Octofecta'},
    '7duo': {'name': '<Category "7PC Duofecta">', 'clean': '7PC Duofecta'},
    'ps1duo': {'name': '<Category "PS1 Duofecta">', 'clean': 'PS1 Duofecta'},
    '6gentrifecta': {'name': '<Category "6th Gen Trifecta">', 'clean': '6th Gen Trifecta'},
    'fs': {'name': '<Category "Full Series">', 'clean': 'Full Series'},
    'gbcduo': {'name': '<Category "GBC Duofecta">', 'clean': 'GBC Duofecta'},
    'gbapenta': {'name': '<Category "GBA Pentafecta">', 'clean': 'GBA Pentafecta'},
    'handheldocto': {'name': '<Category "Handheld Octofecta">', 'clean': 'Handheld Octofecta'},
    'handheldoctofecta': {'name': '<Category "Handheld Octofecta">', 'clean': 'Handheld Octofecta'},
    'chungus': {'name': '<Category "2PC">', 'clean': 'Chungus%', 'cecode': 'rqv2jkw1'},
    'chungus%25': {'name': '<Category "2PC">', 'clean': 'Chungus%', 'cecode': 'rqv2jkw1'},
    'awcgless': {'name': '<Category "2PC">', 'clean': 'AWC Glitchless', 'cecode': '0q5p0erl'},
    'awcglitchless': {'name': '<Category "2PC">', 'clean': 'AWC Glitchless', 'cecode': '0q5p0erl'}
}

# Solo games that require standard processing
standard_games = [
    "hp1pc",
    "hp2pc",
    "hp3pc",
    "hp5",
    "hp6",
    "hp7p1",
    "hp7p2",
    "hp1ps1",
    "hp2ps1",
    "hp1_6th_gen",
    "hp3ps2xboxgcn",
    "hp1gba",
    "hp2gba",
    "hp3gba",
    "hp1gbc",
    "hp2gbc",
    "disneys_brother_bear"]

# Multiruns may have any% and / or 100%, requiring additional processing
multiruns = [
    "trifecta",
    "octofecta",
    "7duo",
    "ps1duo",
    "6gentrifecta",
    "fs",
    "gbcduo",
    "gbapenta",
    "handheldocto"
]

# Games utilising custom variables require individual treatment

# Route created by StreamElements command using pathescape


@app.route('/<game>+<cat>', defaults={'player': 'artfulinfo'})
@app.route("/<game>+<cat>+<player>")
def personal_best(game, cat, player="artfulinfo"):
    game = game.lower()
    cat = cat.lower()
    if game_map.get(game) and not category_map.get(cat):
        return "Category is invalid, check which ones are supported here: https://artfulinfo.net/pb-options"
    elif not game_map.get(game) and category_map.get(cat):
        return "Game is invalid, check which ones are supported here: https://artfulinfo.net/pb-options"
    elif not game_map.get(game) and not category_map.get(cat):
        return "Game and category invalid, check which ones are supported here: https://artfulinfo.net/pb-options"
    # Validate inputs are alphanumeric or underscores
    if re.match(r'[A-Za-z0-9_]', game) and re.match(r'[a-zA-Z0-9_]', cat) and re.match(r'[A-Za-z0-9_]', player):

        # Convert to their api friendly format and search on game name
        game_code = api.search(srcomapi.datatypes.Game, {
                               "name": game_map[game]})[0]
        category = category_map[cat]['name']

        # Get personal bests for user & game combination
        pbs = api.get(
            "users/{}/personal-bests?game={}&embed=variables".format(player, game_code.id))
        # Locate category specified by user
        for c in range(len(game_code.categories)):
            if str(game_code.categories[c]) == category:
                category = game_code.categories[c]
                abr = str(game_code.abbreviation)
                # Validate it is a full game category, not level
                if category.type == "per-game":
                    if abr in standard_games:
                        for r in range(len(pbs)):
                            if str(pbs[r]['run']['category']) == category.id:
                                run = pbs[r]['run']
                                # Get PB info
                                place = pbs[r]['place']
                                seconds_input = run['times']["primary_t"]
                                time = str(datetime.timedelta(
                                    seconds=seconds_input))
                                link = run['weblink']
                                return "{} has a PB of {} (#{}) in {} {} {}".format(player.capitalize(), time, str(place), game.upper(), category_map[cat]['clean'].title(), link)
                    elif abr == "hp4":
                        for r in range(len(pbs)):
                            if str(pbs[r]['run']['category']) == category.id:
                                # Limit to single player only
                                if str(pbs[r]['run']['values']['dlo3pjrl']) == "5lerwd5q":
                                    run = pbs[r]['run']
                                    # Get PB info
                                    place = pbs[r]['place']
                                    seconds_input = run['times']["primary_t"]
                                    time = str(datetime.timedelta(
                                        seconds=seconds_input))
                                    link = run['weblink']
                                    # Format and return the response
                                    return "{} has a PB of {} (#{}) in {} {} {}".format(player.capitalize(), time, str(place), game.upper(), category_map[cat]['clean'].title(), link)
                    # Handle multiruns
                    elif abr == "hp123pc":
                        any_exists = 0
                        hundo_exists = 0
                        if cat.lower() in multiruns:
                            for r in range(len(pbs)):
                                if str(pbs[r]['run']['category']) == category.id:
                                    if str(pbs[r]['run']['values']['789k439l']) == "4qyn2371":  # Any%
                                        run_a = pbs[r]['run']
                                        # Get PB info
                                        place_a = pbs[r]['place']
                                        seconds_input = run_a['times']["primary_t"]
                                        time_a = str(datetime.timedelta(
                                            seconds=seconds_input))
                                        link_a = run_a['weblink']
                                        any_exists = 1
                                    elif str(pbs[r]['run']['values']['789k439l']) == "810xn351":  # 100%
                                        run_h = pbs[r]['run']
                                        # Get PB info
                                        place_h = pbs[r]['place']
                                        seconds_input = run_h['times']["primary_t"]
                                        time_h = str(datetime.timedelta(
                                            seconds=seconds_input))
                                        link_h = run_h['weblink']
                                        hundo_exists = 1

                            if any_exists == 1 and hundo_exists == 1:
                                # Format and return the response
                                return "{} has {} PBs of: {} (#{}) in Any% {} | {} (#{}) in 100% {}".format(player.capitalize(), category_map[cat]['clean'], time_a, str(place_a), link_a, time_h, str(place_h), link_h)

                            elif any_exists == 1 and hundo_exists == 0:
                                # Format and return the response
                                return "{} has {} PB of: {} (#{}) in Any% {}".format(player.capitalize(), category_map[cat]['clean'], time_a, str(place_a), link_a)
                            elif any_exists == 0 and hundo_exists == 1:
                                # Format and return the response
                                return "{} has {} PB of: {} (#{}) in 100% {}".format(player.capitalize(), category_map[cat]['clean'], time_h, str(place_h), link_h)
                    elif abr == "hpce":
                        for r in range(len(pbs)):
                            if str(pbs[r]['run']['category']) == category.id:
                                # filter using the category code
                                if str(pbs[r]['run']['values']['2lg3d4on']) == category_map[cat]['cecode']:
                                    run = pbs[r]['run']
                                    # Get PB info
                                    place = pbs[r]['place']
                                    seconds_input = run['times']["primary_t"]
                                    time = str(datetime.timedelta(seconds=seconds_input))[:-3] if str(datetime.timedelta(
                                        seconds=seconds_input))[-7] == '.' else str(datetime.timedelta(seconds=seconds_input))
                                    link = run['weblink']
                                    # Format and return the response
                                    return "{} has a PB of {} (#{}) in {} {} {}".format(player.capitalize(), time, str(place), game.upper(), category_map[cat]['clean'].title(), link)

    else:
        # Failed character validation
        return "Invalid entry, check the docs for supported inputs: https://artfulinfo.net/tech/docs/twitch-pb-bot/"


# Routes defined for users who want to host the bot on their channel (reconfigures default if no player provided)
@app.route('/custom/<cowner>+<cgame>+<ccat>', defaults={'cplayer': 'usechannel'})
@app.route("/custom/<cowner>+<cgame>+<ccat>+<cplayer>")
def personal_best_custom(cowner, cgame, ccat, cplayer="usechannel"):
    if cplayer == "usechannel":
        return personal_best(cgame, ccat, cowner)
    else:
        return personal_best(cgame, ccat, cplayer)


@app.route("/custom/<cowner>+help")
@app.route("/help")
def help(cowner='usechannel'):
    return "Search for Harry Potter Speedrun PBs using this format '!pb gamecode categorycode srdcusername', use '!pb options' to see the list of supported types. For more info or if you want the command on your channel: https://artfulinfo.net/pbbot/"


@app.route("/custom/<cowner>+options")
@app.route("/options")
def options(cowner='usechannel'):
    return "Format: '!pb gamecode categorycode srdcusername' | Example: '!pb hp1 any% nixxo' | Full list of options: https://artfulinfo.net/pb-options"


# Common error handlers
@app.route("/custom/<cowner>+<game>")
def missing_game_c(cowner, game):
    if len(game) > 1:
        return "Make sure to specify both a game and a category. Format: '!pb gamecode categorycode srdcusername' | Example: '!pb hp1 any% nixxo' | Full list of options: https://artfulinfo.net/pb-options"
    else:
        return "Search for Harry Potter Speedrun PBs using this format '!pb gamecode categorycode srdcusername', use '!pb options' to see the list of supported types. For more info or if you want the command on your channel: https://artfulinfo.net/pbbot/"


@app.route("/<game>")
def missing_game(game):
    if len(game) > 1:
        return "Make sure to specify both a game and a category. Format: '!pb gamecode categorycode srdcusername' | Example: '!pb hp1 any% nixxo' | Full list of options: https://artfulinfo.net/pb-options"
    else:
        return "Search for Harry Potter Speedrun PBs using this format '!pb gamecode categorycode srdcusername', use '!pb options' to see the list of supported types. For more info or if you want the command on your channel: https://artfulinfo.net/pbbot/"


@app.errorhandler(500)
def internal_error(error):
    return "No PB found for this criteria."


@app.errorhandler(408)
def timeout_error(error):
    # Return timeout error
    return "Request timed out, please try typing the command again."


if __name__ == "__main__":
    app.run()
