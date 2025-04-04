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

# กำหนดชุดคำที่หมายถึง "ใคร/Who" ในหลายภาษา
who_words = {
    "ใคร",       # ไทย
    "who",       # อังกฤษ
    "qui",       # ฝรั่งเศส
    "wer",       # เยอรมัน
    "chi",       # อิตาลี
    "quem",      # โปรตุเกส
    "quién",     # สเปน
    "кто",       # รัสเซีย
    "谁",        # จีน (ตัวย่อ)
    "誰",        # จีน (ตัวเต็ม) / ญี่ปุ่น (อ่านว่า dare)
    "dare",      # ญี่ปุ่น (อ่านแบบโรมัน)
    "누구",      # เกาหลี
    "kdo",       # เช็ก / สโลวัก
    "kto",       # โปแลนด์
    "ki",        # ฮังการี
    "cine",      # โรมาเนีย
    "kuka",      # ฟินแลนด์
    "vem",       # สวีเดน
    "hvem",      # นอร์เวย์, เดนมาร์ก
    "wie",       # ดัตช์
    "ποιος",     # กรีก (ชาย)
    "ποια",      # กรีก (หญิง)
    "מי",        # ฮีบรู
    "من",        # อาหรับ
    "कौन",      # ฮินดี
    "কে",        # เบงกาลี
    "siapa",     # อินโดนีเซีย / มาเลย์
    "ai",        # เวียดนาม
    "kes",       # เอสโตเนีย
    "kas",       # ลิทัวเนีย / ลัตเวีย
    "hver",      # ไอซ์แลนด์
    "ვინ",       # จอร์เจีย
    "ով",        # อาร์เมเนีย (ออกเสียง "ov")
    "kim",       # ตุรกี
    "kî",        # คูร์ด
    "obani",     # ดููลู (Zulu)
    "tani",      # โยรูบา (Yoruba)
    "ማን",       # อัมฮาริก (Amharic)
}

GUILD_ID = 692383463206027304

# ใช้ instance เดียวจาก MyClient เท่านั้น (ปิด default help command)
class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
    
    async def setup_hook(self):
        try:
            guild = discord.Object(id=GUILD_ID)
            # Sync คำสั่งเฉพาะใน guild นี้
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
        if message.content.strip().lower() in who_words:
            await message.channel.send("เหมือน")
            logger.info("ตอบ 'เหมือน' สำหรับข้อความที่มีความหมายว่า 'who'")
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

# /help
@client.tree.command(name="help", description="แสดงรายการคำสั่งทั้งหมด", guild=discord.Object(id=GUILD_ID))
async def bothelp(interaction: discord.Interaction):
    try:
        embed = discord.Embed(
            title="🧩 คำสั่งของบอท",
            description="นี่คือรายการคำสั่งที่สามารถใช้ได้:",
            color=discord.Color.green()
        )
        embed.add_field(name="/8ball", value="ถามคำถามแล้วรับคำตอบแบบสุ่ม", inline=False)
        embed.add_field(name="/duel", value="ให้สมาชิก 1vs1 แล้วหาคนที่ไม่กระจอก", inline=False)
        embed.add_field(name="/mute", value="Mute สมาชิก (เลือกเป็นวินาทีหรือเป็นนาที)", inline=False)
        embed.add_field(name="/mutestatus", value="แสดงเวลาที่เหลือของ mute สำหรับสมาชิก", inline=False)
        embed.add_field(name="/unmute", value="ปลด mute สมาชิก", inline=False)
        embed.set_footer(text="โดยฟิวส์ดี้ ❤️")
        logger.info(f"/bothelp: ผู้ใช้ {interaction.user} ขอแสดงรายการคำสั่ง")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /bothelp")
        await interaction.response.send_message("เกิดข้อผิดพลาดในคำสั่ง help", ephemeral=True)

# /mute - mute สมาชิกตามระยะเวลาที่ระบุ (เลือกระหว่าง วินาที กับ นาที)
@client.tree.command(name="mute", description="Mute สมาชิกในเซิร์ฟเวอร์เป็นระยะเวลาที่ระบุ", guild=discord.Object(id=GUILD_ID))
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

        # คำนวณเป็นวินาที
        if unit == "m":
            seconds = duration * 60
        elif unit == "s":
            seconds = duration
        else:
            await interaction.response.send_message("หน่วยเวลาที่เลือกไม่ถูกต้อง", ephemeral=True)
            logger.warning(f"/mute: ผู้ใช้ {interaction.user} เลือกหน่วยเวลาไม่ถูกต้อง")
            return

        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
        
        # รับ full member object จาก guild
        full_member = interaction.guild.get_member(member.id)
        if full_member is None:
            full_member = await interaction.guild.fetch_member(member.id)
        
        # ใช้เมธอด timeout แบบ positional argument (ส่ง until)
        await full_member.timeout(until)
        await interaction.response.send_message(
            f"สมาชิก {member.mention} ถูก mute เป็นเวลา {duration} {'นาที' if unit=='m' else 'วินาที'}."
        )
        logger.info(f"/mute: mute สำเร็จสำหรับ {member}")
    except Exception as e:
        logger.exception("เกิดข้อผิดพลาดใน /mute")
        await interaction.response.send_message(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)

# /unmute - ปลด mute สมาชิก
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

# /mutestatus - แสดงเวลาที่เหลือของ mute สำหรับสมาชิก
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

# /duel - ให้สมาชิกสองคนมาสู้กันและสุ่มผู้ชนะ
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

# /8ball - ถามคำถามแล้วรับคำตอบแบบสุ่ม
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
