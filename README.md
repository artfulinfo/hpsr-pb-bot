# hpsr-pb-bot

A simple Flask app for retrieving personal best times using the srcomapi Python wrapper for the speedrun.com REST API. Designed primarily for use in twitch chats, where streamers can customise the command to show their own times by default (when no specific runner is included in the request). Detailed setup instructions and usage guidance can be viewed in this post https://artfulinfo.net/pbbot/.

The bot could be adapted for other speedrun communities with some configuration (e.g. defining mappings for abbreviations and associated srdc info for each games). The more simple the games' structure, the better. Custom variables make it particularly challenging to make this fully dynamic or portable.

If you are a member of the HP Speedrun community and wish to help expand category/game coverage, please feel free to raise pull requests. I do try to expand it occasionally based on demand and my availability.

If you are trying to set this up for your own community and have any questions or suggestions for improvements, feel free to email: hello@artfulinfo.net. As a disclaimer I am only interested hosting this for the HP games, so you will need to look into hosting the app, but this should be achievable cheaply/freely due to its small footprint.
