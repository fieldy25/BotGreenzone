import os
import discord
from discord.ext import commands, app_commands
import random
import datetime
import logging

from myserver import server_on

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("BotGreenzone")

# กำหนด Intents (ปรับตามต้องการ)
intents = discord.Intents.default()
intents.message_content = True  # ถ้าต้องการใช้คำสั่ง text นอก Slash

# สร้างคลาสสำหรับบอทโดยใช้ commands.Bot
class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        try:
            # ระบุ Guild ID สำหรับทดสอบ (ใช้ Developer Mode คัดลอก ID ของเซิร์ฟเวอร์)
            guild = discord.Object(id=692383463206027304)  # เปลี่ยนเป็น Guild ID ที่ถูกต้อง
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

# Slash Command: /roll
@client.tree.command(name="roll", description="ทอยเต๋า 1-6")
async def roll(interaction: discord.Interaction):
    try:
        num = random.randint(1, 6)
        logger.info(f"/roll: ผู้ใช้ {interaction.user} ได้เลข {num}")
        await interaction.response.send_message(f"🎲 คุณได้เลข **{num}**")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /roll")

# Slash Command: /coinflip
@client.tree.command(name="coinflip", description="เสี่ยงหัว-ก้อย")
async def coinflip(interaction: discord.Interaction):
    try:
        result = random.choice(["หัว", "ก้อย"])
        logger.info(f"/coinflip: ผู้ใช้ {interaction.user} ได้ผล {result}")
        await interaction.response.send_message(f"🪙 ออก **{result}**")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /coinflip")

# Slash Command: /help
@client.tree.command(name="help", description="แสดงรายการคำสั่งทั้งหมด")
async def help_command(interaction: discord.Interaction):
    try:
        embed = discord.Embed(
            title="🧩 คำสั่งของบอท",
            description="นี่คือรายการคำสั่งที่สามารถใช้ได้:",
            color=discord.Color.green()
        )
        embed.add_field(name="/roll", value="ทอยเต๋า 1-6", inline=False)
        embed.add_field(name="/coinflip", value="เสี่ยงหัว-ก้อย", inline=False)
        embed.add_field(name="/mute", value="Mute สมาชิกเป็นระยะเวลาที่ระบุ (ระบุเป็นวินาทีหรือเป็นนาที)", inline=False)
        embed.add_field(name="/duel", value="ให้สมาชิกสองคนมาสู้กันและสุ่มผู้ชนะ", inline=False)
        embed.add_field(name="/help", value="แสดงรายการคำสั่งทั้งหมด", inline=False)
        embed.set_footer(text="โดยบอทของคุณ ❤️")
        logger.info(f"/help: ผู้ใช้ {interaction.user} ขอแสดงรายการคำสั่ง")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /help")

# Slash Command: /mute
@client.tree.command(name="mute", description="Mute สมาชิกในเซิร์ฟเวอร์ (ทั้งข้อความและเสียง) เป็นระยะเวลาที่ระบุ")
@app_commands.describe(
    member="สมาชิกที่ต้องการ mute",
    duration="ระยะเวลา (ตัวเลข)",
    unit="หน่วยเวลา (seconds หรือ minutes)"
)
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, unit: str):
    try:
        logger.info(f"/mute: ผู้ใช้ {interaction.user} พยายาม mute {member} เป็นเวลา {duration} {unit}")
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("คุณไม่มีสิทธิ์ใช้คำสั่งนี้", ephemeral=True)
            logger.warning(f"/mute: ผู้ใช้ {interaction.user} ไม่มีสิทธิ์")
            return

        if unit.lower() in ["minute", "minutes", "m"]:
            seconds = duration * 60
        elif unit.lower() in ["second", "seconds", "s"]:
            seconds = duration
        else:
            await interaction.response.send_message("กรุณาระบุหน่วยเวลาเป็น 'seconds' หรือ 'minutes'", ephemeral=True)
            logger.warning(f"/mute: ผู้ใช้ {interaction.user} ระบุหน่วยเวลาไม่ถูกต้อง")
            return

        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
        await member.edit(timeout=until)
        await interaction.response.send_message(f"สมาชิก {member.mention} ถูก mute เป็นเวลา {duration} {unit}.")
        logger.info(f"/mute: mute สำเร็จสำหรับ {member}")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /mute")
        await interaction.response.send_message(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)

# Slash Command: /duel
@client.tree.command(name="duel", description="ให้สมาชิกสองคนมาสู้กันและสุ่มผู้ชนะ")
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

# เรียกใช้งาน Flask server (เพื่อให้แอปไม่หลับ)
server_on()

# เรียกใช้บอทด้วย client
client.run(os.getenv('TOKEN'))
