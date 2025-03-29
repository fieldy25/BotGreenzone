import os
import discord
from discord import app_commands
import random
import datetime

from myserver import server_on

# กำหนด Intents (ปรับตามต้องการ)
intents = discord.Intents.default()
intents.message_content = True  # ถ้าต้องการใช้คำสั่ง text นอก Slash

# สร้างคลาสสำหรับบอทพร้อม Command Tree สำหรับ Slash Commands
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        # ระบุ Guild ID สำหรับทดสอบ (ใช้ Developer Mode คัดลอก ID ของเซิร์ฟเวอร์)
        guild = discord.Object(id=692383463206027304)  # เปลี่ยน YOUR_GUILD_ID ให้ถูกต้อง
        synced = await self.tree.sync(guild=guild)
        print(f"คำสั่ง Slash Sync สำหรับ guild สำเร็จ! (ซิงค์ {len(synced)} คำสั่ง)")

client = MyClient()

@client.event
async def on_ready():
    print(f"✅ บอท {client.user} พร้อมใช้งานแล้ว!")

# ---------------------- Command bot ----------------------------- #
# on_message event เพื่อตอบกลับเมื่อผู้ใช้พิมพ์ "ข้อความที่ระบุ"
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.strip() == "ใคร":
        await message.channel.send("เหมือน")
    if message.content.strip() == "กิกี้":
        await message.channel.send("เด็กอ้วน")
    if message.content.strip() == "ตอง":
        await message.channel.send("ขาใหญ่")
    if message.content.strip() == "หมู":
        await message.channel.send("ตอง")
    # อย่าลืมให้บอทประมวลผลคำสั่งอื่น ๆ ต่อไป
    await client.process_commands(message)

# Slash Command: /roll
@client.tree.command(name="roll", description="ทอยเต๋า 1-6")
async def roll(interaction: discord.Interaction):
    num = random.randint(1, 6)
    await interaction.response.send_message(f"🎲 คุณได้เลข **{num}**")

# Slash Command: /coinflip
@client.tree.command(name="coinflip", description="เสี่ยงหัว-ก้อย")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["หัว", "ก้อย"])
    await interaction.response.send_message(f"🪙 ออก **{result}**")

# Slash Command: /help
@client.tree.command(name="help", description="แสดงรายการคำสั่งทั้งหมด")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🧩 คำสั่งของบอท",
        description="นี่คือรายการคำสั่งที่สามารถใช้ได้:",
        color=discord.Color.green()
    )
    embed.add_field(name="/roll", value="ทอยเต๋า 1-6", inline=False)
    embed.add_field(name="/coinflip", value="เสี่ยงหัว-ก้อย", inline=False)
    embed.add_field(name="/mute", value="Mute สมาชิกเป็นระยะเวลาที่ระบุ (ระบุเป็นวินาทีหรือเป็นนาที)", inline=False)
    embed.add_field(name="/help", value="แสดงรายการคำสั่งทั้งหมด", inline=False)
    embed.set_footer(text="โดยบอทของคุณ ❤️")
    await interaction.response.send_message(embed=embed)

# Slash Command: /mute
@client.tree.command(name="mute", description="Mute สมาชิกในเซิร์ฟเวอร์ (ทั้งข้อความและเสียง) เป็นระยะเวลาที่ระบุ")
@app_commands.describe(
    member="สมาชิกที่ต้องการ mute",
    duration="ระยะเวลา (ตัวเลข)",
    unit="หน่วยเวลา (seconds หรือ minutes)"
)
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, unit: str):
    # ตรวจสอบสิทธิ์ของผู้ใช้ที่เรียกใช้คำสั่ง (Moderate Members ต้องเปิดใช้งาน)
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("คุณไม่มีสิทธิ์ใช้คำสั่งนี้", ephemeral=True)
        return

    # แปลงหน่วยเวลาเป็นวินาที
    if unit.lower() in ["minute", "minutes", "m"]:
        seconds = duration * 60
    elif unit.lower() in ["second", "seconds", "s"]:
        seconds = duration
    else:
        await interaction.response.send_message("กรุณาระบุหน่วยเวลาเป็น 'seconds' หรือ 'minutes'", ephemeral=True)
        return

    # คำนวณเวลา timeout โดยใช้เวลาปัจจุบัน + ระยะเวลา
    until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
    try:
        await member.edit(timeout=until)
        await interaction.response.send_message(f"สมาชิก {member.mention} ถูก mute เป็นเวลา {duration} {unit}.")
    except Exception as e:
        await interaction.response.send_message(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)

# Slash Command: /duel
@client.tree.command(name="duel", description="ให้สมาชิกสองคนมาสู้กันและสุ่มผู้ชนะ")
@app_commands.describe(
    member1="สมาชิกคนแรก",
    member2="สมาชิกคนที่สอง"
)
async def duel(interaction: discord.Interaction, member1: discord.Member, member2: discord.Member):
    if member1 == member2:
        await interaction.response.send_message("ไม่สามารถให้คนเดียวกันสู้กันได้!", ephemeral=True)
        return

    winner = random.choice([member1, member2])
    embed = discord.Embed(
        title="⚔️ การต่อสู้เริ่มแล้ว!",
        description=f"{member1.mention} vs {member2.mention}",
        color=discord.Color.purple()
    )
    embed.add_field(name="ผู้ชนะ", value=winner.mention, inline=False)
    await interaction.response.send_message(embed=embed)

# เรียกใช้งาน Flask server (เพื่อให้แอปไม่หลับ)
server_on()

# เรียกใช้บอทด้วย client (ไม่ใช่ bot)
client.run(os.getenv('TOKEN'))
