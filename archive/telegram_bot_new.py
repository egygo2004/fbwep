"""
Telegram Bot for FB OTP Automation
Receives numbers file and triggers GitHub Actions
"""

import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Configuration
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '7205135297:AAEKFDTNZBj0c1I23Ri_a_PjCuWn_KUiYyY')
ALLOWED_CHAT_ID = int(os.environ.get('CHAT_ID', '664193835'))

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# Server Configuration (Supports multiple servers via Env Vars)
# Server Configuration (Supports multiple servers via Env Vars)
SERVERS = {
    "server1": {
        "name": "Server 1 (Main)",
        "repo": os.environ.get('GITHUB_REPO', 'egygo2004/fb-otp'),
        "token": os.environ.get('GITHUB_TOKEN', ''),
        "branch": os.environ.get('GITHUB_BRANCH', 'master')
    },
    "server2": {
        "name": "Server 2 (Hema)",
        "repo": "lolelarap4/fb-otp-worker",
        "token": "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",
        "branch": "main"
    }
}

# Check for additional servers in Env Vars (SERVER_2_REPO, SERVER_2_TOKEN, etc.)
for i in range(2, 7): # Support up to 6 servers
    repo_var = f"SERVER_{i}_REPO"
    token_var = f"SERVER_{i}_TOKEN"
    name_var = f"SERVER_{i}_NAME"
    branch_var = f"SERVER_{i}_BRANCH"
    
    if os.environ.get(repo_var) and os.environ.get(token_var):
        SERVERS[f"server{i}"] = {
            "name": os.environ.get(name_var, f"Server {i}"),
            "repo": os.environ.get(repo_var),
            "token": os.environ.get(token_var),
            "branch": os.environ.get(branch_var, 'master')
        }

# Server Status Tracking (persistent via DISABLED_SERVERS env var)
# Format: "server1,server3" = these servers are disabled
DISABLED_SERVERS_STR = os.environ.get('DISABLED_SERVERS', '')
DISABLED_SET = set(DISABLED_SERVERS_STR.split(',')) if DISABLED_SERVERS_STR else set()
SERVER_STATUS = {key: (key not in DISABLED_SET) for key in SERVERS.keys()}

# Heroku API Config (for updating DISABLED_SERVERS)
HEROKU_API_KEY = os.environ.get('HEROKU_API_KEY', '')
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME', 'fb-otp-bot-hema')

def update_disabled_servers_env():
    """Update DISABLED_SERVERS in Heroku config vars"""
    if not HEROKU_API_KEY:
        logger.warning("HEROKU_API_KEY not set, cannot persist server status")
        return False
    
    # Build new value
    disabled = [k for k, v in SERVER_STATUS.items() if not v]
    new_value = ','.join(disabled)
    
    try:
        url = f"https://api.heroku.com/apps/{HEROKU_APP_NAME}/config-vars"
        headers = {
            "Authorization": f"Bearer {HEROKU_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.heroku+json; version=3"
        }
        data = {"DISABLED_SERVERS": new_value}
        
        resp = requests.patch(url, headers=headers, json=data)
        if resp.status_code == 200:
            logger.info(f"Updated DISABLED_SERVERS to: {new_value}")
            return True
        else:
            logger.error(f"Failed to update Heroku config: {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error updating Heroku config: {e}")
        return False

def get_active_servers():
    """Return only active servers"""
    return {k: v for k, v in SERVERS.items() if SERVER_STATUS.get(k, True)}

# ... (omitted code) ...



def get_server_keyboard():
    """Return keyboard for server selection"""
    keyboard = []
    row = []
    for key, data in SERVERS.items():
        row.append(InlineKeyboardButton(f"🖥️ {data['name']}", callback_data=f"select_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_selection")])
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard():
    """Return main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🔄 تقدم العملية", callback_data="progress"),
            InlineKeyboardButton("📊 حالة العمليات", callback_data="status")
        ],
        [
            InlineKeyboardButton("⚙️ إدارة السيرفرات", callback_data="manage_servers"),
            InlineKeyboardButton("📈 الاستهلاك", callback_data="usage_report")
        ],
        [
            InlineKeyboardButton("🛑 إيقاف الكل", callback_data="cancel"),
            InlineKeyboardButton("❓ مساعدة", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


import datetime
from dateutil import parser as date_parser

# ... imports ...

async def post_init(application: Application):
    """Set up bot commands menu"""
    await application.bot.set_my_commands([
        BotCommand("start", "القائمة الرئيسية"),
        BotCommand("servers", "إدارة السيرفرات"),
        BotCommand("usage", "مراقبة الاستهلاك"),
        BotCommand("status", "حالة العمليات"),
        BotCommand("cancel", "إيقاف الكل"),
        BotCommand("help", "المساعدة")
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("❌ غير مصرح لك باستخدام هذا البوت")
        return
    
    # Persistent Keyboard (Bottom Buttons)
    reply_keyboard = [
        ["/start", "/servers"],
        ["/usage", "/cancel"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        "🤖 مرحباً بك في بوت FB OTP\n\n"
        "📱 لإرسال الأرقام:\n"
        "• أرسل ملف .txt يحتوي على الأرقام\n"
        "• أو اكتب الأرقام مباشرة\n\n"
        "⬇️ اختر من القائمة:",
        reply_markup=markup
    )
    # Also show inline keyboard
    await update.message.reply_text("التحكم السريع:", reply_markup=get_main_keyboard())

def get_server_keyboard():
    """Return keyboard for server selection (active servers only)"""
    active_servers = get_active_servers()
    keyboard = []
    
    # Add Auto Distribute Button at the top (only if 2+ active servers)
    if len(active_servers) >= 2:
        keyboard.append([InlineKeyboardButton("🚀 توزيع تلقائي", callback_data="select_auto")])
    
    row = []
    for key, data in active_servers.items():
        row.append(InlineKeyboardButton(f"🖥️ {data['name']}", callback_data=f"select_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    if not active_servers:
        keyboard.append([InlineKeyboardButton("⚠️ لا سيرفرات نشطة", callback_data="no_servers")])
    
    keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_selection")])
    return InlineKeyboardMarkup(keyboard)

def get_server_management_keyboard():
    """Return keyboard for server management (toggle active/inactive)"""
    keyboard = []
    for key, data in SERVERS.items():
        status = "🟢" if SERVER_STATUS.get(key, True) else "🔴"
        btn_text = f"{status} {data['name']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"toggle_{key}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

async def show_server_management(query):
    """Show server management panel"""
    active_count = sum(1 for s in SERVER_STATUS.values() if s)
    total_count = len(SERVERS)
    
    msg = f"""⚙️ إدارة السيرفرات

🟢 = نشط (يستخدم في التوزيع)
🔴 = متوقف (لا يُستخدم)

السيرفرات النشطة: {active_count}/{total_count}

اضغط على سيرفر لتغيير حالته:"""
    
    await query.edit_message_text(msg, reply_markup=get_server_management_keyboard())

async def servers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /servers command"""
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
    
    active_count = sum(1 for s in SERVER_STATUS.values() if s)
    total_count = len(SERVERS)
    
    msg = f"""⚙️ إدارة السيرفرات

🟢 = نشط (يستخدم في التوزيع)
🔴 = متوقف (لا يُستخدم)

السيرفرات النشطة: {active_count}/{total_count}

اضغط على سيرفر لتغيير حالته:"""
    
    await update.message.reply_text(msg, reply_markup=get_server_management_keyboard())

def calculate_monthly_usage(repo: str, token: str) -> float:
    """Calculate minutes used by summing individual job durations (more accurate)"""
    try:
        url = f"https://api.github.com/repos/{repo}/actions/runs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Look back 30 days
        since_date = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat()
        params = {
            "created": f">{since_date}",
            "per_page": 100,
            "status": "completed"
        }
        
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            return -1
            
        runs = resp.json().get("workflow_runs", [])
        total_job_seconds = 0
        
        # Sum duration of each JOB (not just run) for accuracy with parallel jobs
        for run in runs:
            jobs_url = run.get('jobs_url')
            if not jobs_url:
                continue
            
            j_resp = requests.get(jobs_url, headers=headers)
            if j_resp.status_code != 200:
                continue
                
            jobs = j_resp.json().get('jobs', [])
            for job in jobs:
                if job.get('started_at') and job.get('completed_at'):
                    start = date_parser.isoparse(job['started_at'])
                    end = date_parser.isoparse(job['completed_at'])
                    duration = (end - start).total_seconds()
                    total_job_seconds += duration
        
        # GitHub bills minimum 60s per job, add 1.5x overhead factor
        OVERHEAD_FACTOR = 1.5
        estimated_minutes = (total_job_seconds / 60) * OVERHEAD_FACTOR
        
        return round(estimated_minutes, 2)
    except Exception as e:
        logger.error(f"Error calculating usage for {repo}: {e}")
        return -1

async def show_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show usage report for all servers"""
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
        
    status_msg = await update.message.reply_text("⏳ جاري فحص السيرفرات (قد يستغرق لحظات)...")
    
    report = "📊 تقرير استهلاك السيرفرات (آخر 30 يوم):\n\n"
    
    for key, server in SERVERS.items():
        minutes = calculate_monthly_usage(server['repo'], server['token'])
        
        if minutes >= 0:
            status_moji = "🟢"
            usage_text = f"{minutes} دقيقة"
        else:
            status_moji = "🔴"
            usage_text = "خطأ في الاتصال"
            
        report += f"{status_moji} **{server['name']}**\n"
        report += f"   • الاستهلاك: {usage_text}\n"
        report += f"   • الريبو: `{server['repo']}`\n\n"
        
    report += "💡 الاستهلاك المجاني لكل حساب: ~2000 دقيقة/شهر."
    
    await status_msg.edit_text(report, parse_mode='Markdown')

async def usage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /usage command"""
    await show_usage(update, context)

async def handle_server_selection(query, context, server_key):
    """Execute dispatch using the selected server"""
    if 'pending_numbers' not in context.user_data:
        await query.edit_message_text("❌ حدث خطأ: لا توجد أرقام محفوظة. أرسل الملف مرة أخرى.", reply_markup=get_main_keyboard())
        return
        
    numbers = context.user_data['pending_numbers']
    batch_size = 5
    
    # --- AUTO DISTRIBUTE LOGIC ---
    if server_key == "auto":
        active_servers = get_active_servers()  # FIX: Use active servers only
        total_servers = len(active_servers)
        if total_servers == 0:
             await query.edit_message_text("❌ لا توجد سيرفرات نشطة! اذهب لـ /servers لتفعيل سيرفر.", reply_markup=get_main_keyboard())
             return

        # Clear data
        del context.user_data['pending_numbers']
        
        await query.edit_message_text(
            f"🚀 **توزيع الحمل الذكي (Auto Distribute)**\n"
            f"📊 الأرقام: {len(numbers)}\n"
            f"🖥️ السيرفرات النشطة: {total_servers}\n"
            f"⚙️ جاري التوزيع...",
            parse_mode='Markdown'
        )
        
        server_keys = list(active_servers.keys())  # FIX: Use active server keys
        total_batches = (len(numbers) + batch_size - 1) // batch_size
        success_count = 0
        
        for i in range(0, len(numbers), batch_size):
            batch = numbers[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            # Round Robin Selection
            current_server_key = server_keys[(batch_num - 1) % total_servers]
            current_server = active_servers[current_server_key]  # FIX: Use active_servers
            
            # Trigger
            if trigger_github_workflow(batch, current_server['repo'], current_server['token'], current_server.get('branch', 'master')):
                success_count += 1
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"✅ {current_server['name']} | دفعة {batch_num}/{total_batches}"
                )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"❌ {current_server['name']} | فشل دفعة {batch_num}"
                )
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"🏁 انتهى التوزيع التلقائي!\n({success_count}/{total_batches} ناجحة)",
            reply_markup=get_main_keyboard()
        )
        return
    # -----------------------------

    server = SERVERS.get(server_key)
    if not server:
        await query.edit_message_text("❌ هذا السيرفر غير موجود", reply_markup=get_main_keyboard())
        return
        
    # Clear data
    del context.user_data['pending_numbers']
    
    await query.edit_message_text(
        f"✅ تم اختيار: {server['name']}\n"
        f"⚙️ جاري معالجة {len(numbers)} رقم...\n"
        f"🚀 الإرسال بنظام الدفعات (5 أرقام)..."
    )
    
    total_batches = (len(numbers) + batch_size - 1) // batch_size
    
    success_count = 0
    for i in range(0, len(numbers), batch_size):
        batch = numbers[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        # Trigger with specific server creds
        if trigger_github_workflow(batch, server['repo'], server['token'], server.get('branch', 'master')):
            success_count += 1
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"✅ {server['name']} | دفعة {batch_num}/{total_batches} ({len(batch)} أرقام)"
            )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ {server['name']} | فشل دفعة {batch_num}"
            )
            
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"🏁 انتهى الإرسال لـ {server['name']}!\n({success_count}/{total_batches} ناجحة)",
        reply_markup=get_main_keyboard()
    )



async def show_progress(query):
    """Show progress of current running workflow"""
    try:
        headers = {
            "Authorization": f"Bearer {SERVERS['server1']['token']}", # Default to main server for checking
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Check for running workflows
        running_found = False
        for status in ["in_progress", "queued", "waiting"]:
            url = f"https://api.github.com/repos/{SERVERS['server1']['repo']}/actions/runs?status={status}&per_page=1"
            response = requests.get(url, headers=headers)
            runs = response.json().get('workflow_runs', [])
            
            if runs:
                run = runs[0]
                running_found = True
                
                # Get workflow start time
                created = run['created_at'][:16].replace('T', ' ')
                run_id = run['id']
                
                # Try to get jobs info for progress
                jobs_url = f"https://api.github.com/repos/{SERVERS['server1']['repo']}/actions/runs/{run_id}/jobs"
                jobs_response = requests.get(jobs_url, headers=headers)
                jobs_data = jobs_response.json().get('jobs', [])
                
                # Build progress message
                if status == "queued":
                    status_text = "📥 في قائمة الانتظار"
                    progress_bar = "⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%"
                elif status == "waiting":
                    status_text = "⏳ منتظر"
                    progress_bar = "🟨⬜⬜⬜⬜⬜⬜⬜⬜⬜ 10%"
                else:
                    status_text = "🔄 قيد التنفيذ"
                    # Estimate progress based on steps
                    if jobs_data:
                        job = jobs_data[0]
                        steps = job.get('steps', [])
                        completed = sum(1 for s in steps if s.get('status') == 'completed')
                        total = len(steps) if steps else 1
                        percent = int((completed / total) * 100)
                        filled = percent // 10
                        progress_bar = "🟩" * filled + "⬜" * (10 - filled) + f" {percent}%"
                    else:
                        progress_bar = "🟩🟩🟩⬜⬜⬜⬜⬜⬜⬜ ~30%"
                
                msg = f"""🔄 تقدم العملية الحالية

{status_text}
📅 بدأت: {created}
🆔 ID: {run_id}

{progress_bar}

اضغط 🔄 للتحديث"""
                
                await query.edit_message_text(msg, reply_markup=get_main_keyboard())
                return
        
        if not running_found:
            await query.edit_message_text(
                "📭 لا توجد عمليات جارية حالياً\n\n"
                "أرسل أرقام لبدء عملية جديدة!",
                reply_markup=get_main_keyboard()
            )
            
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ: {e}", reply_markup=get_main_keyboard())


async def show_status(query):
    """Show GitHub Actions status"""
    try:
        url = f"https://api.github.com/repos/{SERVERS['server1']['repo']}/actions/runs?per_page=5"
        headers = {
            "Authorization": f"Bearer {SERVERS['server1']['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        runs = response.json().get('workflow_runs', [])
        
        if not runs:
            await query.edit_message_text("📭 لا توجد عمليات سابقة", reply_markup=get_main_keyboard())
            return
        
        status_msg = "📊 آخر 5 عمليات:\n\n"
        for run in runs[:5]:
            status_emoji = "✅" if run['conclusion'] == 'success' else "❌" if run['conclusion'] == 'failure' else "⏳"
            status_msg += f"{status_emoji} {run['created_at'][:16].replace('T', ' ')} - {run['status']}\n"
        
        await query.edit_message_text(status_msg, reply_markup=get_main_keyboard())
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ: {e}", reply_markup=get_main_keyboard())


async def cancel_all_workflows(query):
    """Cancel all running and queued workflows"""
    try:
        total_cancelled = 0
        total_checked = 0
        
        # Iterate through all configured servers
        for key, server in SERVERS.items():
            if not server['token']: continue
            
            headers = {
                "Authorization": f"Bearer {server['token']}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Get workflows
            server_runs = []
            for status in ["in_progress", "queued", "waiting"]:
                url = f"https://api.github.com/repos/{server['repo']}/actions/runs?status={status}"
                try:
                    response = requests.get(url, headers=headers)
                    runs = response.json().get('workflow_runs', [])
                    server_runs.extend(runs)
                except: pass
            
            total_checked += len(server_runs)
            
            # Cancel each
            for run in server_runs:
                try:
                    cancel_url = f"https://api.github.com/repos/{server['repo']}/actions/runs/{run['id']}/cancel"
                    cancel_response = requests.post(cancel_url, headers=headers)
                    if cancel_response.status_code == 202:
                        total_cancelled += 1
                except: pass
        
        if total_checked == 0:
            await query.edit_message_text("📭 لا توجد عمليات جارية أو منتظرة للإيقاف", reply_markup=get_main_keyboard())
            return
            
        await query.edit_message_text(
            f"🛑 تم إيقاف {total_cancelled} عمليات من أصل {total_checked}",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ: {e}", reply_markup=get_main_keyboard())


async def show_help(query):
    """Show help message"""
    help_text = """❓ المساعدة

📱 لإرسال الأرقام:
• أرسل ملف .txt يحتوي على الأرقام
• أو اكتب الأرقام مباشرة (كل رقم في سطر)

📊 حالة العمليات:
يعرض آخر 5 عمليات

🛑 إيقاف الكل:
يوقف جميع العمليات الجارية

📋 الأوامر:
/start - القائمة الرئيسية
/status - حالة العمليات
/cancel - إيقاف الكل"""
    
    await query.edit_message_text(help_text, reply_markup=get_main_keyboard())


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
    await show_status(update.message)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
    await cancel_all_workflows(update.message)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("select_"):
        await handle_server_selection(query, context, data.split("_")[1])
    elif data.startswith("toggle_"):
        # Toggle server status
        server_key = data.replace("toggle_", "")
        if server_key in SERVER_STATUS:
            SERVER_STATUS[server_key] = not SERVER_STATUS[server_key]
            status_text = "🟢 نشط" if SERVER_STATUS[server_key] else "🔴 متوقف"
            
            # Persist to Heroku env var
            persisted = update_disabled_servers_env()
            persist_icon = "💾" if persisted else "⚠️"
            
            await query.answer(f"{persist_icon} {SERVERS[server_key]['name']}: {status_text}")
        await show_server_management(query)
    elif data == "manage_servers":
        await show_server_management(query)
    elif data == "usage_report":
        # Show usage inline (simplified)
        await query.edit_message_text("⏳ جاري فحص السيرفرات...")
        report = "📊 تقرير الاستهلاك (آخر 30 يوم):\n\n"
        for key, server in SERVERS.items():
            minutes = calculate_monthly_usage(server['repo'], server['token'])
            status = "🟢" if SERVER_STATUS.get(key, True) else "🔴"
            usage_text = f"{minutes} دقيقة" if minutes >= 0 else "خطأ"
            report += f"{status} **{server['name']}**: {usage_text}\n"
        report += "\n💡 المجاني: ~2000 دقيقة/شهر لكل حساب."
        await query.edit_message_text(report, parse_mode='Markdown', reply_markup=get_main_keyboard())
    elif data == "no_servers":
        await query.answer("اذهب لـ /servers لتفعيل سيرفرات")
    elif data == "back_to_main":
        await query.edit_message_text("التحكم السريع:", reply_markup=get_main_keyboard())
    elif data == "cancel_selection":
        if 'pending_numbers' in context.user_data:
            del context.user_data['pending_numbers']
        await query.edit_message_text("❌ تم إلغاء العملية", reply_markup=get_main_keyboard())
    elif data == "progress":
        await show_progress(query)
    elif data == "status":
        await show_status(query)
    elif data == "cancel":
        await cancel_all_workflows(query)
    elif data == "help":
        await show_help(query)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle received document - Step 1: Store and Ask for Server"""
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
    
    document = update.message.document
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ يرجى إرسال ملف .txt فقط")
        return
    
    file = await context.bot.get_file(document.file_id)
    file_content = await file.download_as_bytearray()
    numbers_text = file_content.decode('utf-8')
    
    numbers = [line.strip() for line in numbers_text.split('\n') if line.strip() and not line.startswith('#')]
    
    if not numbers:
        await update.message.reply_text("❌ الملف فارغ")
        return
    
    # Store numbers in context
    context.user_data['pending_numbers'] = numbers
    
    await update.message.reply_text(
        f"✅ تم استلام {len(numbers)} رقم\n"
        f"📡 الرجاء اختيار السيرفر للتنفيذ:",
        reply_markup=get_server_keyboard()
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text - Step 1: Store and Ask for Server"""
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
    
    text = update.message.text
    if text.startswith('/'): return
    
    numbers = [line.strip() for line in text.split('\n') if line.strip()]
    if not numbers: return
    
    # Store numbers in context
    context.user_data['pending_numbers'] = numbers
    
    await update.message.reply_text(
        f"✅ تم استلام {len(numbers)} رقم\n"
        f"📡 الرجاء اختيار السيرفر للتنفيذ:",
        reply_markup=get_server_keyboard()
    )


def trigger_github_workflow(numbers: list, repo: str, token: str, branch: str = 'master') -> bool:
    """Trigger GitHub Actions workflow with dynamic credentials"""
    try:
        url = f"https://api.github.com/repos/{repo}/actions/workflows/fb_otp.yml/dispatches"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "ref": branch,
            "inputs": {
                "numbers": "\n".join(numbers)
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        # GitHub API returns 204 (No Content) or 200 (with workflow_run_id) on success
        if response.status_code in [200, 204]:
            logger.info(f"Workflow triggered for {repo}: Status={response.status_code}")
            return True
        else:
            # Log detailed error info
            logger.error(f"GitHub API Error for {repo}: Status={response.status_code}, Body={response.text[:200]}")
            return False
    except Exception as e:
        logger.error(f"Error triggering workflow: {e}")
        return False


# --- DEPLOYMENT HELPERS ---
import base64

def update_github_file(repo: str, token: str, file_path: str, content: str, branch: str = 'master') -> bool:
    """Update a file in a GitHub repository via API"""
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 1. Get current file SHA (if exists)
    # Must also pass branch to get correct SHA
    params = {"ref": branch}
    sha = None
    resp = requests.get(url, headers=headers, params=params)
    
    if resp.status_code == 200:
        sha = resp.json().get('sha')
    elif resp.status_code == 404:
        pass # Create new
    else:
        logger.error(f"Error getting file info for {repo}/{file_path} (ref={branch}): {resp.status_code}")
        return False

    # 2. Update/Create file
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    data = {
        "message": "Auto-deploy: Update script via Bot",
        "content": encoded_content,
        "branch": branch 
    }
    if sha:
        data["sha"] = sha
        
    put_resp = requests.put(url, headers=headers, json=data)
    if put_resp.status_code in [200, 201]:
        return True
    else:
        logger.error(f"Error updating file {repo}/{file_path}: {put_resp.status_code} {put_resp.text}")
        return False

async def deploy_scripts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deploy local files to all active servers"""
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return

    status_msg = await update.message.reply_text("🚀 جاري نشر التحديثات على السيرفرات...")
    
    # Read local files
    files_to_deploy = {
        "fb_otp_browser.py": "fb_otp_browser.py",
        ".github/workflows/fb_otp.yml": ".github/workflows/fb_otp.yml",
        "requirements.txt": "requirements.txt"
    }
    
    file_contents = {}
    try:
        for local_path, remote_path in files_to_deploy.items():
            with open(local_path, 'r', encoding='utf-8') as f:
                file_contents[remote_path] = f.read()
    except Exception as e:
        await status_msg.edit_text(f"❌ خطأ في قراءة الملفات المحلية: {e}")
        return

    results = []
    for key, server in SERVERS.items():
        # Skip if token is missing
        if not server['token']:
            results.append(f"⚠️ {server['name']}: لا يوجد توكن")
            continue
            
        # Use configured branch, default to master
        branch = server.get('branch', 'master')
        
        # Deploy all files
        files_success = []
        for remote_path, content in file_contents.items():
            success = update_github_file(server['repo'], server['token'], remote_path, content, branch)
            files_success.append(success)
        
        # All files must succeed
        all_success = all(files_success)
        icon = "✅" if all_success else "❌"
        results.append(f"{icon} {server['name']} ({sum(files_success)}/{len(files_success)} files)")
        
    report = "📊 **تقرير النشر (Deploy Report)**:\n\n" + "\n".join(results)
    report += "\n\n📦 الملفات المنشورة:\n• fb_otp_browser.py\n• .github/workflows/fb_otp.yml\n• requirements.txt"
    await status_msg.edit_text(report, parse_mode='Markdown')


def main():
    """Start the bot"""
    logger.info("Starting Telegram Bot...")
    
    # Build application
    application = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("servers", servers_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("usage", usage_command))
    application.add_handler(CommandHandler("deploy_scripts", deploy_scripts_command))
    
    # Button callback handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
