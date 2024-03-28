import discord
from discord.ext import commands
import json
import time

intents = discord.Intents.all()
intents.messages = True

bot = commands.Bot(command_prefix=".", intents=intents)

class ClockinSystem:
    def __init__(self):
        self.clock_data = {}
        self.filename = "time.json"
        self.load_clock_data()

    def load_clock_data(self):
        try:
            with open(self.filename, "r") as f:
                self.clock_data = json.load(f)
        except FileNotFoundError:
            self.clock_data = {}

    def save_clock_data(self):
        with open(self.filename, "w") as f:
            json.dump(self.clock_data, f, indent=4)

    async def start_clock(self, user_id):
        if user_id not in self.clock_data:
            self.clock_data[user_id] = {}
        clock_id = f"clock_id_{len(self.clock_data[user_id]) + 1}"
        self.clock_data[user_id][clock_id] = {"clock_in": time.time(), "clock_out": None}
        self.save_clock_data()

    async def stop_clock(self, user_id):
        if user_id in self.clock_data:
            for clock_id, clock_event in self.clock_data[user_id].items():
                if clock_event["clock_out"] is None:
                    self.clock_data[user_id][clock_id]["clock_out"] = time.time()
                    break  # Stop at the first unclosed clock event
            self.save_clock_data()

    async def get_clock_status(self, user_id):
        if user_id in self.clock_data:
            statuses = []
            for clock_id, clock_event in self.clock_data[user_id].items():
                clock_in = clock_event["clock_in"]
                clock_out = clock_event["clock_out"]
                clock_in_str = time.strftime('%H:%M:%S', time.localtime(clock_in))
                clock_out_str = time.strftime('%H:%M:%S', time.localtime(clock_out)) if clock_out is not None else "N/A"
                total_time_str = "N/A" if clock_out is None else time.strftime('%H:%M:%S', time.gmtime(clock_out - clock_in))
                date_str = time.strftime('%d.%m.%Y', time.localtime(clock_in))
                statuses.append({
                    "id": clock_id,
                    "date": date_str,
                    "clock_in": clock_in_str,
                    "clock_out": clock_out_str,
                    "total_time": total_time_str
                })
            return statuses
        else:
            return None


@bot.event
async def on_ready():
    print(f"-> {bot.user} up!")
    activity = discord.Activity(type=discord.ActivityType.playing, name="cu mama lu sile")
    await bot.change_presence(activity=activity)

@bot.slash_command(name="clock", description="smekeru")
async def clock(ctx):
    embed = discord.Embed(
        title="Sistem pontaj automatizat",
        description="",
        color=0x49ecb3
    )
    view = ClockinSystemView()
    embed.set_thumbnail(url="https://cdn-icons-png.freepik.com/512/7586/7586439.png")
    embed.add_field(name="Info", value="Pentru a porni/închide pontajul sau a verifica starea actuală a pontajului, folosește butoanele de mai jos.", inline=False)
    embed.set_footer(text="linux1337 utilities", icon_url=f"{ctx.author.avatar}")
    await ctx.respond(embed=embed, view=view)

class ClockinSystemView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.clockin_system = ClockinSystem()

    @discord.ui.button(label="Start", row=0, style=discord.ButtonStyle.success, emoji="✅")
    async def start_button_callback(self, button, interaction):
        user_id = str(interaction.user.id)
        await self.clockin_system.start_clock(user_id)
        embed = discord.Embed(
            title="Clock in",
            description="You have successfully clocked in!",
            color=0x49ecb3
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Stop", row=0, style=discord.ButtonStyle.danger, emoji="✖")
    async def stop_button_callback(self, button, interaction):
        user_id = str(interaction.user.id)
        await self.clockin_system.stop_clock(user_id)
        embed = discord.Embed(
            title="Clock out",
            description="You have successfully clocked out!",
            color=0x49ecb3
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Verify", row=0, style=discord.ButtonStyle.primary, emoji="ℹ")
    async def verify_button_callback(self, button, interaction):
        user_id = str(interaction.user.id)
        statuses = await self.clockin_system.get_clock_status(user_id)
        if statuses is None:
            embed = discord.Embed(
                title="Verificare clock-uri",
                description="You haven't started the clock yet.",
                color=0x49ecb3
            )
            embed.set_thumbnail(url="https://cdn-icons-png.freepik.com/512/7586/7586439.png")
            embed.set_footer(text="made by linux for rol3x with love")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Verificare clock-uri",
                color=0x49ecb3
            )
            embed.set_thumbnail(url="https://cdn-icons-png.freepik.com/512/7586/7586439.png")
            for status in statuses:
                embed.add_field(
                    name=f"{status['id']} - {status['date']}",
                    value=f"Clock in: {status['clock_in']}\nClock out: {status['clock_out']}\nTotal time: {status['total_time']}",
                    inline=True
                )
            embed.set_footer(text="linux1337 utilities", icon_url=f"https://i.imgur.com/dkTXmho.png")
            await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run("TOKEN")
