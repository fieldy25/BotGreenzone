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

# กำหนด Intents (ต้องเปิด voice_states ด้วยเพื่อรับ event ห้องพูดคุย)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

GUILD_ID = 692383463206027304

def add_xp(user_id, amount):
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 0}
    levels[user_id]["xp"] += amount
    current_level = levels[user_id]["level"]
    # กำหนด threshold (xp ที่ต้องการสำหรับเลเวลถัดไป) โดยที่แต่ละเลเวลต้องการ 100 * (level+1) xp
    threshold = 100 * (current_level + 1)
    if levels[user_id]["xp"] >= threshold:
        levels[user_id]["level"] += 1
        return True, levels[user_id]["level"]
    return False, levels[user_id]["level"]

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

    # เมื่อผู้ใช้พิมพ์ข้อความ เพิ่ม XP แบบสุ่ม (เช่น 5-10 XP)
    xp_gain = random.randint(5, 10)
    leveled_up, new_level = add_xp(message.author.id, xp_gain)
    if leveled_up:
        try:
            await message.channel.send(f"🎉 {message.author.mention} คุณเลเวลขึ้นเป็นระดับ {new_level} แล้ว!")
        except Exception as e:
            logger.exception("ไม่สามารถส่งข้อความแจ้งเตือนเลเวลอัพได้")

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

# เมื่อสมาชิกเข้าห้องพูดคุย (Voice Channel) เพิ่ม XP แบบสุ่ม (เช่น 10-20 XP)
@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        xp_gain = random.randint(10, 20)
        leveled_up, new_level = add_xp(member.id, xp_gain)
        if leveled_up:
            try:
                await member.send(f"🎉 คุณเลเวลขึ้นเป็นระดับ {new_level} แล้ว!")
            except Exception as e:
                logger.exception("ไม่สามารถส่ง DM แจ้งเตือนเลเวลอัพได้")

# Slash command: /level - ให้ผู้ใช้ตรวจสอบเลเวลและ XP ของตนเอง
@client.tree.command(name="level", description="ดูเลเวลและ XP ของคุณ", guild=discord.Object(id=GUILD_ID))
async def level(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 0}
    xp = levels[user_id]["xp"]
    lvl = levels[user_id]["level"]
    next_threshold = 100 * (lvl + 1)
    await interaction.response.send_message(
        f"{interaction.user.mention} คุณอยู่ระดับ {lvl} (XP: {xp}/{next_threshold})"
    )

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
