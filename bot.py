import discord
from discord.ext import commands
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz
from dotenv import load_dotenv

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True  # 반응 이벤트 수신
intents.members = True  # 멤버 정보 접근 (사용자 이름 수집용)
bot = commands.Bot(command_prefix='/', intents=intents)

load_dotenv()
# 환경 변수에서 토큰과 채널 ID 가져오기
BOT_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # 공지 채널 ID (정수로 변환)

# 스케줄러 초기화
scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Seoul'))

# 공지 및 투표 메시지 보내는 함수
async def send_announcement():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        # 투표 메시지 작성
        message = await channel.send(
            "# 📢 **주간 공지** 📢\n## 내일 회의는 어떻게 참여하실까요?(내일 9시30분까지)\n"
            "🤼: 오프라인 참여\n"
            "💻: 온라인 참여\n"
            "❌: 미참여\n"
            "아래 이모지를 눌러 투표해주세요!\n@everyone"
        )
        # 이모지 반응 추가
        await message.add_reaction("🤼")
        await message.add_reaction("💻")
        await message.add_reaction("❌")
    else:
        print("채널을 찾을 수 없습니다. CHANNEL_ID를 확인하세요.")

# 투표 마감 함수
async def close_poll():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        async for message in channel.history(limit=100):
            if message.author == bot.user and "주간 공지" in message.content:
                online_users = []
                offline_users = []
                no_users = []
                
                for reaction in message.reactions:
                    # ✅ 반응한 사용자
                    if str(reaction.emoji) == "🤼":
                        async for user in reaction.users():
                            if user != bot.user:  # 봇 자신 제외
                                online_users.append(f"{user.display_name}")
                    # ❌ 반응한 사용자
                    if str(reaction.emoji) == "💻":
                        async for user in reaction.users():
                            if user != bot.user:  # 봇 자신 제외
                                offline_users.append(f"{user.display_name}")
                    if str(reaction.emoji) == "❌":
                        async for user in reaction.users():
                            if user != bot.user:  # 봇 자신 제외
                                no_users.append(f"{user.display_name}")
                
                # 결과 포맷팅
                online_text = ", ".join(online_users) if online_users else "없음"
                offline_text = ", ".join(offline_users) if offline_users else "없음"
                no_text = ", ".join(no_users) if no_users else "없음"
                result_message = (
                    f"#참여 인원\n"
                    f"- 오프라인🤼 ({len(offline_users)}명): {online_text}\n"
                    f"- 온라인💻 ({len(online_users)}명): {offline_text}\n"
                    f"- 미참여❌ ({len(no_users)}명): {no_text}"
                )
                await channel.send(result_message)
                return
        print("투표 메시지를 찾을 수 없습니다.")
    else:
        print("채널을 찾을 수 없습니다.")

# 봇 시작 시 실행
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    
    # 스케줄러에 작업 추가
    scheduler.add_job(send_announcement, 'cron', day_of_week='fri', hour=12, minute=00)
    scheduler.add_job(close_poll, 'cron', day_of_week='fri', hour=9, minute=30)
    scheduler.start()
    print("스케줄러가 시작되었습니다.")

# 투표 명령어
@bot.command()
async def 회의계획(ctx):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        # 투표 메시지 작성
        message = await channel.send(
            "# 📢 **회의 계획** 📢\n## 회의는 어떻게 참여하실까요?\n"
            "🤼: 오프라인 참여\n"
            "💻: 온라인 참여\n"
            "❌: 미참여\n"
            "아래 이모지를 눌러 투표해주세요!\n@everyone"
        )
        # 이모지 반응 추가
        await message.add_reaction("🤼")
        await message.add_reaction("💻")
        await message.add_reaction("❌")
    else:
        channel.send("채널을 찾을 수 없습니다. CHANNEL_ID를 확인하세요.")

# 투표 결과 확인 명령어
@bot.command()
async def 회의인원(ctx):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        async for message in channel.history(limit=100):
            if message.author == bot.user and "회의 계획" in message.content:
                online_users = []
                offline_users = []
                no_users = []
                
                for reaction in message.reactions:
                    # ✅ 반응한 사용자
                    if str(reaction.emoji) == "🤼":
                        async for user in reaction.users():
                            if user != bot.user:  # 봇 자신 제외
                                online_users.append(f"{user.display_name}")
                    # ❌ 반응한 사용자
                    if str(reaction.emoji) == "💻":
                        async for user in reaction.users():
                            if user != bot.user:  # 봇 자신 제외
                                offline_users.append(f"{user.display_name}")
                    if str(reaction.emoji) == "❌":
                        async for user in reaction.users():
                            if user != bot.user:  # 봇 자신 제외
                                no_users.append(f"{user.display_name}")
                
                # 결과 포맷팅
                online_text = ", ".join(online_users) if online_users else "없음"
                offline_text = ", ".join(offline_users) if offline_users else "없음"
                no_text = ", ".join(no_users) if no_users else "없음"
                
                result_message = (
                    f"# 참여인원\n"
                    f"- 오프라인🤼 ({len(offline_users)}명): {online_text}\n"
                    f"- 온라인💻 ({len(online_users)}명): {offline_text}\n"
                    f"- 미참여❌ ({len(no_users)}명): {no_text}"
                )
                await ctx.send(result_message)
                return
        await ctx.send("투표 메시지를 찾을 수 없습니다.")
    else:
        await ctx.send("채널을 찾을 수 없습니다.")

# 채널 설정 명령어
@bot.command()
async def 채널설정(ctx, channel_id: int):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ 이 명령어는 관리자만 사용할 수 있습니다.")
        return

    global CHANNEL_ID

    channel = bot.get_channel(channel_id)
    before_channel = bot.get_channel(CHANNEL_ID)
    if channel:
        before_channel_id = CHANNEL_ID
        CHANNEL_ID = channel_id
        await ctx.send(f"✅ 설정되었습니다.\n공지 채널: {before_channel.name} (ID: {before_channel_id}) -> {channel.name} (ID: {CHANNEL_ID})")
    else:
        await ctx.send("❌ 채널을 찾을 수 없습니다. 올바른 채널 ID인지 확인해주세요.")


# 봇 실행
bot.run(BOT_TOKEN)