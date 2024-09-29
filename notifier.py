import asyncio
import discord
import requests
from dotenv import load_dotenv
import os
import html2text
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime

load_dotenv()

# Read environment variables
discord_token = os.getenv('DISCORD_BOT_TOKEN')
discord_channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
api_url = os.getenv('API_URL', 'https://jotihunt.nl/api/2.0/articles')  # Default API URL
article_base_url = os.getenv('ARTICLE_BASE_URL', 'https://jotihunt.nl/article/')  # Default base URL
sent_articles_file = 'sent_articles.json'  # File to store sent articles

# Initialize Discord client
intents = discord.Intents.default()
discord_client = discord.Client(intents=intents)

# Load sent articles from file or initialize as empty set
if os.path.exists(sent_articles_file):
    with open(sent_articles_file, 'r') as f:
        sent_articles = set(json.load(f))
else:
    sent_articles = set()

def save_sent_articles():
    """Saves the set of sent articles to a file."""
    with open(sent_articles_file, 'w') as f:
        json.dump(list(sent_articles), f)

def clean_html_to_markdown(html):
    """
    Cleans the HTML content using BeautifulSoup and converts it to Markdown.
    """
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the first image and remove all <figure> elements
    first_image_url = None
    for figure in soup.find_all('figure'):
        if not first_image_url:
            img = figure.find('img')
            if img and img.get('src'):
                first_image_url = img['src']
        figure.decompose()  # Remove the <figure> element

    # Initialize the html2text converter
    converter = html2text.HTML2Text()
    converter.ignore_links = False  # Keep links
    converter.ignore_images = True  # Ignore inline images, handled separately
    converter.body_width = 0  # Disable word wrapping to prevent unexpected breaks
    converter.single_line_break = True  # Optimize to reduce unnecessary spacing
    converter.skip_internal_links = True  # Skip internal links

    # Convert the remaining HTML content to Markdown
    markdown_content = converter.handle(str(soup))

    return markdown_content.strip(), first_image_url

def format_dutch_date(iso_date_str):
    """
    Converts ISO date string to a readable Dutch format.
    """
    dt = datetime.fromisoformat(iso_date_str.replace("Z", "+00:00"))
    return dt.strftime("%d/%m/%Y %H:%M")

async def fetch_articles():
    """
    Fetches articles from the provided API.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return []

async def send_articles_to_discord():
    """
    Fetches articles and sends any new ones to the specified Discord channel.
    """
    articles = await fetch_articles()
    
    if not articles:
        print("No articles found.")
        return
    
    channel = discord_client.get_channel(discord_channel_id)
    
    new_articles_found = False
    for article in reversed(articles):
        article_id = str(article.get('id', 'unknown'))  # Use article ID as string
        if article_id not in sent_articles:
            # Mark article as sent by adding it to the set
            sent_articles.add(article_id)
            new_articles_found = True

            # Extract article details
            title = article.get('title', 'Geen titel')
            message_content = article['message'].get('content', '')
            cleaned_message, first_image_url = clean_html_to_markdown(message_content)
            publish_at = article.get('publish_at', '')
            formatted_date = format_dutch_date(publish_at) if publish_at else "Onbekende datum"
            original_post_url = f"{article_base_url}{article_id}"

            # Create a Discord embed for the article using Markdown
            embed = discord.Embed(title=title, description=cleaned_message, color=0x00ff00)
            embed.set_footer(text=f"Gepubliceerd op: {formatted_date}")

            # Add the first image if available
            if first_image_url:
                embed.set_image(url=first_image_url)

            # Add a button for the original post link (if supported in your Discord bot setup)
            view = discord.ui.View()
            button = discord.ui.Button(label="Origineel bericht", url=original_post_url)
            view.add_item(button)

            # Send the embed to the channel with the view (button)
            if channel:
                await channel.send(embed=embed, view=view)

    # Save the updated list of sent articles to file if any new articles were found
    if new_articles_found:
        save_sent_articles()

async def periodic_fetch():
    """Fetches new articles every 5 seconds."""
    while True:
        print("Fetching new articles...")
        await send_articles_to_discord()
        await asyncio.sleep(5)  # Wait for 5 seconds before fetching again

@discord_client.event
async def on_ready():
    print(f'Discord: Logged in as {discord_client.user}')
    # Start the periodic fetch task
    await periodic_fetch()

async def main():
    await discord_client.start(discord_token)

# Run the script
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
