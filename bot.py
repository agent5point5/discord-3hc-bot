import json
import random
from datetime import datetime
import discord
from discord.ext import commands

# ---------------------------------------------------------
# 1. DEFINE YOUR EFFECT POOL (Exactly 37 Effects)
# ---------------------------------------------------------
EFFECT_POOL = [
    "BCC Wooden Planks Obsolete",
    "BCC Cross Melt",
    "S_WarpTransform",
    "S_PsykoStripes",
    "S_DistortChroma",
    "Turbulent Displace",
    "BCC Colorize",
    "S_DissolveZap",
    "S_Emboss",
    "S_WipePixelate",
    "S_CloudsVortex",
    "S_FeedbackBubble",
    "BCC Brick",
    "S_Luna",
    "S_Glint",
    "Psyko Blobs",
    "S_WarpPolar",
    "S_Grid",
    "S_WarpRipple",
    "S_WarpTunnel",
    "S_WarpVortex",
    "S_PrismLens",
    "S_RackDefocus",
    "S_Plasma",
    "S_WarpMagnify",
    "S_WipeChecker",
    "BCC Rays Puffy",
    "Hydrochrome",
    "S_Solarize",
    "Card Dance",
    "Posterize Time",
    "S_EdgeRays",
    "S_Zap",
    "S_HalfTone",
    "S_Kaleido",
    "S_Glow",
    "BCC Fast Film Process"
]  # 37 distinct Sapphire, BCC, and native AE/PR effects

DATA_FILE = "claimed_effects.json"

# ---------------------------------------------------------
# 2. JSON TRACKING HELPER FUNCTIONS
# ---------------------------------------------------------
def load_claimed_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_claimed_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

claimed_users = load_claimed_data()

# ---------------------------------------------------------
# 3. BOT INITIALIZATION & BUTTON VIEW
# ---------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class OneTimeEffectPickerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Keeps button persistent across bot restarts

    @discord.ui.button(
        label="press this button to get your effects", 
        style=discord.ButtonStyle.primary, 
        custom_id="one_time_effect_btn"
    )
    async def get_effects_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id_str = str(interaction.user.id)

        # CHECK 1: Has the user already claimed their effects?
        if user_id_str in claimed_users:
            already_claimed = claimed_users[user_id_str]
            effects_given = "\n• " + "\n• ".join(already_claimed["effects"])
            await interaction.response.send_message(
                f"❌ You have already claimed your effects! You received:{effects_given}",
                ephemeral=True
            )
            return

        # CHECK 2: Pick 3 unique random effects from the pool
        selected_effects = random.sample(EFFECT_POOL, 3)
        formatted_list = "\n• " + "\n• ".join(selected_effects)
        formatted_message = f"🐔 **Here are your 3 assigned effects:**{formatted_list}"

        try:
            # Direct Message the user
            await interaction.user.send(formatted_message)
            
            # Save claim data to file
            claimed_users[user_id_str] = {
                "username": str(interaction.user),
                "effects": selected_effects,
                "timestamp": datetime.utcnow().isoformat()
            }
            save_claimed_data(claimed_users)

            # Confirm to the user in the channel (only visible to them)
            await interaction.response.send_message("Check your DMs! 📩 (This was your one-time claim)", ephemeral=True)

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Couldn't send you a DM! Please enable Direct Messages from server members in your Privacy Settings and try again.",
                ephemeral=True
            )

# ---------------------------------------------------------
# 4. BOT EVENTS AND ADMIN COMMANDS
# ---------------------------------------------------------
@bot.event
async def on_ready():
    bot.add_view(OneTimeEffectPickerView())  # Register persistent view
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_effects_button(ctx):
    """Admin command to post the button in a channel."""
    embed = discord.Embed(
        title="3hc Effect Generator",
        description="Click the button to get your effects.\n\n you can only press it once",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, view=OneTimeEffectPickerView())

@bot.command()
@commands.has_permissions(administrator=True)
async def view_claims(ctx):
    """Admin command to list all users and their assigned effects."""
    if not claimed_users:
        await ctx.send("No users have claimed effects yet.")
        return

    summary = "**📋 Effect Assignment Log:**\n"
    for uid, info in claimed_users.items():
        effects_str = ", ".join(info['effects'])
        summary += f"• **{info['username']}** (`{uid}`): `{effects_str}`\n"
    
    await ctx.send(summary)

# ---------------------------------------------------------
# 5. RUN THE BOT
# ---------------------------------------------------------
import os
bot.run(os.environ.get("DISCORD_TOKEN"))
