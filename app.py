from flask import Flask, render_template, request
from groq import Groq
import os
from datetime import date
from dotenv import load_dotenv
import re

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Function to convert markdown-style links to HTML anchor tags and bold text
def convert_markdown_links_to_html(text):
    # Convert markdown links to HTML anchor tags with target="_blank"
    pattern_links = r'\[([^\]]+)\]\((https?://[^\s)]+)\)'
    text = re.sub(pattern_links, r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', text)
    
    # Convert markdown bold text to HTML <strong> tags
    pattern_bold = r'\*\*([^\*]+)\*\*'
    text = re.sub(pattern_bold, r'<strong>\1</strong>', text)
    
    # Add breaks after each news item for separation
    text = text.replace('\n', '<br><br>')  # Adding line breaks to separate stories
    
    return text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        location = request.form['location']
        topic = request.form['topic']
        today = date.today()

        user_query = f"What is today's Top 5 news of {location} about Topic:{topic}, date:{today}?"

        # Connect to Groq AI with your API key
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        # Ask the AI for a news summary with links
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are a professional news anchor. Use the available tools to web scrape the latest and most relevant news from trusted sources. Present the news as if delivering it live on television—confident, clear, and engaging. Organize the stories by categories such as World, Politics, Technology, Sports, etc. Be concise and ensure each story includes only the most important facts. At the end of each article or news point, include a clickable link to the original source so the reader can verify or read more. Use proper formatting for the links."""
                },
                {"role": "user", "content": user_query}
            ],
            model="compound-beta",
        )

        # Convert markdown to clickable HTML with better formatting
        raw_news = chat_completion.choices[0].message.content
        news = convert_markdown_links_to_html(raw_news)

        # Pass the formatted news to result.html
        return render_template("result.html", news=news)

    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
