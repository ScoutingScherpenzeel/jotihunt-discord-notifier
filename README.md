# Jotihunt Discord Notifier

This is a simple Discord bot that fetches Jotihunt articles from the Jotihunt API and sends them to a specified Discord channel.

## Installation

The easiest way to install and run the bot is to use Docker.

1. Copy the `docker-compose.yml` file to your server.
2. Edit the environment variables in the `docker-compose.yml` file, or create a `.env` file with the same variables and set the `env_file` variable in the `docker-compose.yml` file to the path of the `.env` file
3. Run `docker-compose up -d`
4. The script will run in the background and will send messages to the Discord channel specified in the `DISCORD_CHANNEL_ID` environment variable.
5. Happy hunting!

## Creating and inviting a Discord bot

1. Go to the [Discord Developer Portal](https://discordapp.com/developers/applications/)
2. Create a new application
3. Go to the bot tab
4. Click on "Reset Token"
5. Save the token
6. Go to the OAuth2 tab
7. Click on "Add redirect" and enter any URL, save changes
8. Select scopes "bot" and "identify" in the URL generator
9. Pick your previously created redirect URL
10. Select needed permissions for the bot (at least "Send Messages", but "Administrator" will definitely work)
11. Open the URL in a browser and add the bot to your server

## Retrieving the Discord channel ID

1. Go to the Discord channel you want to forward messages to
2. Right click on the channel name and select "Copy ID" (might need Developer mode)