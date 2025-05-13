import discord
from discord.ext import commands
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True  # 반응 이벤트 수신
intents.members = True  # 멤버 정보 접근 (사용자 이름 수집용)
bot = commands.Bot(command_prefix='/', intents=intents)

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
            "📢 **주간 공지** 📢\n내일 회의는 오프라인으로 참여하실까요?\n"
            "🤼: 오프라인 참여\n"
            "💻: 온온라인 참여\n"
            "아래 이모지를 눌러 투표해주세요!"
        )
        # 이모지 반응 추가
        await message.add_reaction("🤼")
        await message.add_reaction("💻")
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
                
                # 결과 포맷팅
                online_text = ", ".join(online_users) if online_users else "없음"
                offline_text = ", ".join(offline_users) if offline_users else "없음"
                result_message = (
                    f"투표 마감!\n"
                    f"오프라인 ({len(offline_users)}명): {offline_text}\n"
                    f"온라인 ({len(online_users)}명): {online_text}"
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
    
    # 스케줄러에 작업 추가: 화요일 11:29에 공지, 11:30에 마감 (테스트용)
    scheduler.add_job(send_announcement, 'cron', day_of_week='tue', hour=11, minute=51)
    scheduler.add_job(close_poll, 'cron', day_of_week='tue', hour=11, minute=52)
    scheduler.start()
    print("스케줄러가 시작되었습니다.")

# 투표 결과 확인 명령어
@bot.command()
async def 결과(ctx):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        async for message in channel.history(limit=100):
            if message.author == bot.user and "주간 공지" in message.content:
                online_users = []
                offline_users = []
                
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
                
                # 결과 포맷팅
                online_text = ", ".join(online_users) if online_users else "없음"
                offline_text = ", ".join(offline_users) if offline_users else "없음"
                result_message = (
                    f"투표 결과:\n"
                    f"오프라인 ({len(offline_users)}명): {online_text}\n"
                    f"온라인 ({len(online_users)}명): {offline_text}"
                )
                await ctx.send(result_message)
                return
        await ctx.send("투표 메시지를 찾을 수 없습니다.")
    else:
        await ctx.send("채널을 찾을 수 없습니다.")

# 봇 실행
bot.run(BOT_TOKEN)