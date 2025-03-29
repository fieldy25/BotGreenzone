import os
import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime
import logging

from myserver import server_on  # ฟังก์ชันนี้ควรเปิด Flask server เพื่อให้บอทไม่หลับ

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("BotGreenzone")

# กำหนด Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

GUILD_ID = 692383463206027304

# ปิด default help command
client = commands.Bot(command_prefix="!", intents=intents, help_command=None)
client.remove_command("help")

class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
    
    async def setup_hook(self):
        try:
            guild = discord.Object(id=GUILD_ID)
            # Sync คำสั่งเฉพาะใน guild
            synced = await self.tree.sync(guild=guild)
            logger.info(f"คำสั่ง Slash Sync สำหรับ guild สำเร็จ! (ซิงค์ {len(synced)} คำสั่ง)")
        except Exception as e:
            logger.exception("เกิดข้อผิดพลาดใน setup_hook")

client = MyClient()

@client.event
async def on_ready():
    logger.info(f"✅ บอท {client.user} พร้อมใช้งานแล้ว!")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    logger.info(f"on_message: Received message from {message.author}: {message.content}")

    try:
        if message.content.strip() == "ใคร":
            await message.channel.send("เหมือน")
            logger.info("ตอบ 'เหมือน' สำหรับข้อความ 'ใคร'")
        if message.content.strip() == "กิกี้":
            await message.channel.send("เด็กอ้วน")
            logger.info("ตอบ 'เด็กอ้วน' สำหรับข้อความ 'กิกี้'")
        if message.content.strip() == "ตอง":
            await message.channel.send("ขาใหญ่")
            logger.info("ตอบ 'ขาใหญ่' สำหรับข้อความ 'ตอง'")
        if message.content.strip() == "หมู":
            await message.channel.send("ตอง")
            logger.info("ตอบ 'ตอง' สำหรับข้อความ 'หมู'")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน on_message")

    await client.process_commands(message)

# /bothelp
@client.tree.command(name="bothelp", description="แสดงรายการคำสั่งทั้งหมด", guild=discord.Object(id=GUILD_ID))
async def bothelp(interaction: discord.Interaction):
    try:
        embed = discord.Embed(
            title="🧩 คำสั่งของบอท",
            description="นี่คือรายการคำสั่งที่สามารถใช้ได้:",
            color=discord.Color.green()
        )
        embed.add_field(name="/roll", value="ทอยเต๋า 1-6", inline=False)
        embed.add_field(name="/coinflip", value="เสี่ยงหัว-ก้อย", inline=False)
        embed.add_field(name="/mute", value="Mute สมาชิก (เลือกเป็นวินาทีหรือเป็นนาที)", inline=False)
        embed.add_field(name="/unmute", value="ปลด mute สมาชิก", inline=False)
        embed.add_field(name="/mutestatus", value="แสดงเวลาที่เหลือของ mute สำหรับสมาชิก", inline=False)
        embed.add_field(name="/8ball", value="ถามคำถามแล้วรับคำตอบแบบสุ่ม", inline=False)
        embed.set_footer(text="โดยบอทของคุณ ❤️")
        logger.info(f"/bothelp: ผู้ใช้ {interaction.user} ขอแสดงรายการคำสั่ง")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /bothelp")
        await interaction.response.send_message("เกิดข้อผิดพลาดในคำสั่ง help", ephemeral=True)

# /roll
@client.tree.command(name="roll", description="ทอยเต๋า 1-6", guild=discord.Object(id=GUILD_ID))
async def roll(interaction: discord.Interaction):
    try:
        num = random.randint(1, 6)
        logger.info(f"/roll: ผู้ใช้ {interaction.user} ได้เลข {num}")
        await interaction.response.send_message(f"🎲 คุณได้เลข **{num}**")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /roll")

# /coinflip
@client.tree.command(name="coinflip", description="เสี่ยงหัว-ก้อย", guild=discord.Object(id=GUILD_ID))
async def coinflip(interaction: discord.Interaction):
    try:
        result = random.choice(["หัว", "ก้อย"])
        logger.info(f"/coinflip: ผู้ใช้ {interaction.user} ได้ผล {result}")
        await interaction.response.send_message(f"🪙 ออก **{result}**")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /coinflip")

# /mute
@client.tree.command(name="mute", description="Mute สมาชิกในเซิร์ฟเวอร์ (ทั้งข้อความและเสียง) เป็นระยะเวลาที่ระบุ", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    member="สมาชิกที่ต้องการ mute",
    duration="ระยะเวลา (ตัวเลข)",
    unit="หน่วยเวลา"
)
@app_commands.choices(unit=[
    app_commands.Choice(name="วินาที", value="s"),
    app_commands.Choice(name="นาที", value="m")
])
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, unit: str):
    try:
        logger.info(f"/mute: ผู้ใช้ {interaction.user} พยายาม mute {member} เป็นเวลา {duration} {unit}")
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("คุณไม่มีสิทธิ์ใช้คำสั่งนี้", ephemeral=True)
            logger.warning(f"/mute: ผู้ใช้ {interaction.user} ไม่มีสิทธิ์")
            return

        if unit == "m":
            seconds = duration * 60
        elif unit == "s":
            seconds = duration
        else:
            await interaction.response.send_message("หน่วยเวลาที่เลือกไม่ถูกต้อง", ephemeral=True)
            logger.warning(f"/mute: ผู้ใช้ {interaction.user} เลือกหน่วยเวลาไม่ถูกต้อง")
            return

        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
        
        full_member = interaction.guild.get_member(member.id)
        if full_member is None:
            full_member = await interaction.guild.fetch_member(member.id)
        
        await full_member.timeout(until)
        await interaction.response.send_message(f"สมาชิก {member.mention} ถูก mute เป็นเวลา {duration} {'นาที' if unit == 'm' else 'วินาที'}.")
        logger.info(f"/mute: mute สำเร็จสำหรับ {member}")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /mute")
        await interaction.response.send_message(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)

# /unmute
@client.tree.command(name="unmute", description="ปลด mute สมาชิก", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="สมาชิกที่ต้องการปลด mute")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    try:
        full_member = interaction.guild.get_member(member.id)
        if full_member is None:
            full_member = await interaction.guild.fetch_member(member.id)
        
        await full_member.timeout(None)
        await interaction.response.send_message(f"สมาชิก {member.mention} ถูกปลด mute แล้ว")
        logger.info(f"/unmute: ปลด mute สำหรับ {member}")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /unmute")
        await interaction.response.send_message(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)

# /mutestatus
@client.tree.command(name="mutestatus", description="แสดงเวลาที่เหลือของ mute สำหรับสมาชิก", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="สมาชิกที่ต้องการดูสถานะ mute")
async def mutestatus(interaction: discord.Interaction, member: discord.Member):
    try:
        full_member = interaction.guild.get_member(member.id)
        if full_member is None:
            full_member = await interaction.guild.fetch_member(member.id)
        
        timeout_until = full_member.timed_out_until
        if timeout_until is None:
            await interaction.response.send_message(f"สมาชิก {member.mention} ไม่ถูก mute")
            return
        
        now = discord.utils.utcnow()
        remaining = timeout_until - now
        if remaining.total_seconds() <= 0:
            await interaction.response.send_message(f"สมาชิก {member.mention} ไม่ถูก mute")
            return

        minutes = remaining.total_seconds() / 60
        await interaction.response.send_message(f"สมาชิก {member.mention} ถูก mute เหลือ {minutes:.2f} นาที")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /mutestatus")
        await interaction.response.send_message(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)

# /duel
@client.tree.command(name="duel", description="ให้สมาชิกสองคนมาสู้กันและสุ่มผู้ชนะ", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    member1="สมาชิกคนแรก",
    member2="สมาชิกคนที่สอง"
)
async def duel(interaction: discord.Interaction, member1: discord.Member, member2: discord.Member):
    try:
        logger.info(f"/duel: ผู้ใช้ {interaction.user} ขอ duel ระหว่าง {member1} กับ {member2}")
        if member1 == member2:
            await interaction.response.send_message("ไม่สามารถให้คนเดียวกันสู้กันได้!", ephemeral=True)
            logger.warning(f"/duel: สมาชิกเดียวกันถูกระบุ")
            return

        winner = random.choice([member1, member2])
        embed = discord.Embed(
            title="⚔️ การต่อสู้เริ่มแล้ว!",
            description=f"{member1.mention} vs {member2.mention}",
            color=discord.Color.purple()
        )
        embed.add_field(name="ผู้ชนะ", value=winner.mention, inline=False)
        await interaction.response.send_message(embed=embed)
        logger.info(f"/duel: ผู้ชนะคือ {winner}")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /duel")
        await interaction.response.send_message(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)

# /8ball
@client.tree.command(name="8ball", description="ถามคำถามแล้วรับคำตอบแบบสุ่ม", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(question="คำถามของคุณ")
async def eight_ball(interaction: discord.Interaction, question: str):
    responses = [
        "แน่นอน!", 
        "ไม่แน่นอนนะ", 
        "ลองใหม่อีกครั้ง", 
        "ฉันไม่แน่ใจ", 
        "ดูเหมือนว่ามันจะเป็นไปได้", 
        "ไม่เป็นไปตามที่คาด", 
        "แค่คิดบวกไว้!", 
        "งั้นลองดูนะ"
    ]
    answer = random.choice(responses)
    await interaction.response.send_message(f"คำถาม: {question}\nคำตอบ: {answer}")

# เรียกใช้งาน Flask server (เพื่อให้แอปไม่หลับ)
server_on()

# เรียกใช้บอทด้วย client
client.run(os.getenv('TOKEN'))
