from datetime import datetime, timedelta
import hashlib
import os
import random
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

DB_FILE = "rozmarra_enterprise_web.db"

# ==========================================
# BRANDING & EMAIL CONFIGURATION (NEXUS GLOBAL)
# ==========================================
COMPANY_NAME = "Nexus Global"
SENDER_EMAIL = "nexusglobal633@gmail.com"
SENDER_APP_PASSWORD = "swmn iijn zdhu rpbd"  # Yahan 16-digit Google App Password daalein


def send_email_notification(to_email, subject_text, body_text):
  """Generic function to send automated emails via Nexus Global Support SMTP."""
  try:
    msg = MIMEMultipart()
    msg["From"] = f"{COMPANY_NAME} Support <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject_text
    msg.attach(MIMEText(body_text, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
    server.send_message(msg)
    server.quit()
    return True
  except Exception as e:
    return False


def hash_password(password):
  return hashlib.sha256(password.encode()).hexdigest()


def init_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            email TEXT,
            mobile TEXT,
            role TEXT,
            reg_date TEXT,
            last_active TEXT
        )
    """)
  try:
    cursor.execute("ALTER TABLE users ADD COLUMN last_active TEXT")
    conn.commit()
  except:
    pass

  admin_pass_hash = hash_password("admin123")
  cursor.execute(
      """
        INSERT OR IGNORE INTO users (username, password, email, mobile, role, reg_date, last_active) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
      (
          "admin",
          admin_pass_hash,
          SENDER_EMAIL,
          "03000000000",
          "MASTER_ADMIN",
          "2026-01-01",
          "2026-10-14 20:30",
      ),
  )

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            category TEXT,
            detail TEXT,
            amount REAL,
            payment_method TEXT,
            date_time TEXT,
            month TEXT,
            year TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            subject TEXT,
            message TEXT,
            status TEXT,
            feedback TEXT,
            date_time TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_buttons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            button_name TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()

st.set_page_config(
    page_title="Nexus Global - Expense Manager Pro", page_icon="🌐", layout="wide"
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0f172a; color: #f1f5f9; }
    section[data-testid="stSidebar"] { background-color: #1e293b; color: #f1f5f9; }
    section[data-testid="stSidebar"] div.row-widget.stRadio label, 
    section[data-testid="stSidebar"] div.stRadio p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label {
        color: #ffffff !important; font-weight: 700 !important; font-size: 15px !important;
    }
    label, .stTabs [data-baseweb="tab"] { color: #ffffff !important; font-weight: 600 !important; }
    div.stInfo { background-color: #1e293b !important; color: #ffffff !important; border: 1px solid #334155 !important; }
    div.stInfo p { color: #ffffff !important; }
    .metric-card {
        background-color: #1e293b; padding: 15px; border-radius: 8px; border-left: 5px solid #38bdf8; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #6366f1 !important; color: #ffffff !important; border-radius: 6px !important; font-weight: bold !important; border: none !important; width: 100% !important; padding: 10px !important;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover { background-color: #4f46e5 !important; color: #ffffff !important; }
    div.stDownloadButton > button { background-color: #10b981 !important; color: #ffffff !important; border-radius: 6px !important; font-weight: bold !important; border: none !important; padding: 10px !important; }
    table { width: 100%; color: #f1f5f9; background-color: #1e293b; border-collapse: collapse; border-radius: 8px; overflow: hidden; }
    th, td { padding: 12px; border-bottom: 1px solid #334155; text-align: left; }
    th { background-color: #334155; color: #38bdf8; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.username = ""
  st.session_state.role = ""
  st.session_state.selected_cat = "All"
  st.session_state.reset_otp = None
  st.session_state.reset_user = None

if not st.session_state.logged_in:
  st.markdown(
      f"<h2 style='text-align: center; color: #38bdf8; margin-top: 30px;'>🌐"
      f" {COMPANY_NAME.upper()} SECURE PORTAL</h2>",
      unsafe_allow_html=True,
  )
  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    tab1, tab2, tab3 = st.tabs(
        ["Login", "Register Consumer", "Secure OTP Password Reset"]
    )

    with tab1:
      with st.form("login_form"):
        u_input = st.text_input("Username")
        p_input = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login to System")
        if submit:
          hashed_p = hash_password(p_input)
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "SELECT role FROM users WHERE username = ? AND password = ?",
              (u_input, hashed_p),
          )
          res = cursor.fetchone()
          if res:
            cursor.execute(
                "UPDATE users SET last_active = ? WHERE username = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M"), u_input),
            )
            conn.commit()
            st.session_state.logged_in = True
            st.session_state.username = u_input
            st.session_state.role = res[0]
            conn.close()
            st.rerun()
          else:
            conn.close()
            st.error("Ghalat Username ya Password hai!")

    with tab2:
      with st.form("reg_form"):
        r_user = st.text_input("New Username")
        r_pass = st.text_input("New Password", type="password")
        r_email = st.text_input("Email Address")
        r_mob = st.text_input("Mobile Number")
        r_sub = st.form_submit_button("Register Account")
        if r_sub:
          if not r_user or not r_pass or not r_email:
            st.error("Username, Password aur Email Address lazmi hain!")
          else:
            hashed_reg_pass = hash_password(r_pass)
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            try:
              cursor.execute(
                  "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (
                      r_user,
                      hashed_reg_pass,
                      r_email,
                      r_mob,
                      "USER",
                      datetime.now().strftime("%Y-%m-%d"),
                      datetime.now().strftime("%Y-%m-%d %H:%M"),
                  ),
              )
              conn.commit()
              conn.close()

              welcome_subj = (
                  f"🎉 Welcome to {COMPANY_NAME} - Account Created Successfully!"
              )
              welcome_body = f"""Dear {r_user},

Aapka account {COMPANY_NAME} platform par kamyabi se ban gaya hai!

------------------------------------------------
Username: {r_user}
Registered Email: {r_email}
------------------------------------------------

Aap ab apne username aur password ke zariye system mein login kar sakte hain.

Regards,
{COMPANY_NAME} Team
"""
              send_email_notification(r_email, welcome_subj, welcome_body)

              st.success(
                  "Account kamyabi se ban gaya aur aapke email par welcome"
                  " message bhej diya gaya hai! Ab Login tab mein ja kar login"
                  " karein."
              )
            except sqlite3.IntegrityError:
              conn.close()
              st.error("Ye username pehlay se mojood hai!")

    with tab3:
      st.markdown(
          "<p style='font-size:13px; color:#94a3b8;'>Step 1: Get OTP on Email |"
          " Step 2: Verify OTP & Change Password</p>",
          unsafe_allow_html=True,
      )

      with st.form("request_otp_form"):
        f_user = st.text_input("Username")
        f_email = st.text_input("Registered Email Address")
        req_otp_btn = st.form_submit_button(
            "📧 Send 6-Digit Verification Code (OTP)"
        )
        if req_otp_btn:
          conn = sqlite3.connect(DB_FILE)
          cursor = conn.cursor()
          cursor.execute(
              "SELECT email FROM users WHERE username = ? AND email = ?",
              (f_user, f_email),
          )
          matched_user = cursor.fetchone()
          conn.close()

          if matched_user:
            generated_otp = str(random.randint(100000, 999999))
            st.session_state.reset_otp = generated_otp
            st.session_state.reset_user = f_user

            subj = f"🔐 Security Verification Code - {COMPANY_NAME}"
            body = (
                f"Dear User,\n\nYour Security OTP Code for password reset is:"
                f" {generated_otp}\n\nRegards,\n{COMPANY_NAME} Team"
            )
            email_sent = send_email_notification(f_email, subj, body)
            if email_sent:
              st.success(
                  f"Verification OTP code email ({f_email}) par bhej diya gaya"
                  " hai!"
              )
            else:
              st.error(
                  "Email bhejne mein masla hua! Gmail App Password check"
                  " karein."
              )
          else:
            st.error("Username aur Email record se match nahi karte!")

      st.markdown("---")

      with st.form("verify_otp_form"):
        entered_otp = st.text_input("Enter 6-Digit OTP Code")
        f_new_pass = st.text_input("Enter New Password", type="password")
        verify_btn = st.form_submit_button("🔒 Verify OTP & Reset Password")

        if verify_btn:
          if not st.session_state.reset_otp:
            st.warning(
                "Pehle 'Send Verification Code (OTP)' par click karein!"
            )
          elif entered_otp != st.session_state.reset_otp:
            st.error("Ghalat OTP Code enter kiya hai!")
          elif not f_new_pass:
            st.warning("Naya password likhna lazmi hai!")
          else:
            new_hashed = hash_password(f_new_pass)
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (new_hashed, st.session_state.reset_user),
            )
            conn.commit()
            conn.close()
            st.session_state.reset_otp = None
            st.session_state.reset_user = None
            st.success(
                "Password secure tarike se update ho gaya! Ab Login tab mein ja"
                " kar login karein."
            )
else:
  st.sidebar.markdown(
      f"### 🌐 {COMPANY_NAME}<br><span style='font-size:14px; color:#38bdf8;'>👤"
      f" {st.session_state.username} ({st.session_state.role})</span>",
      unsafe_allow_html=True,
  )
  if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

  st.sidebar.markdown("---")
  st.sidebar.markdown(
      "<p style='color: #38bdf8; font-weight: bold;'>NAVIGATION</p>",
      unsafe_allow_html=True,
  )

  if st.session_state.role == "MASTER_ADMIN":
    menu = st.sidebar.radio(
        "Admin Menu",
        [
            "👑 Customers Data & Control",
            "📊 User Activity & Analytics",
            "💬 Complaints Portal",
        ],
    )
  else:
    menu = st.sidebar.radio(
        "Menu", ["Dashboard & Analytics", "💬 Complaints Portal"]
    )

  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()

  if (
      st.session_state.role != "MASTER_ADMIN"
      and menu == "Dashboard & Analytics"
  ):
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<p style='color: #38bdf8; font-weight: bold;'>EXPENSE CATEGORIES &"
        " FILTERS</p>",
        unsafe_allow_html=True,
    )

    default_categories = [
        "All",
        "Doodh / Milk",
        "Grocery / Daal",
        "Petrol / Fuel",
        "Bills & Utilities",
        "Medical / Treatment",
        "Guest / Refreshment",
        "Miscellaneous",
    ]
    cursor.execute(
        "SELECT id, button_name FROM custom_buttons WHERE username = ?",
        (st.session_state.username,),
    )
    custom_rows = cursor.fetchall()
    custom_cats = [row[1] for row in custom_rows]
    all_cats = default_categories + custom_cats


    @st.dialog("➕ Add Expense Entry")
    def open_add_dialog(category_name):
      st.markdown(
          f"<h4 style='color: #38bdf8;'>Category: {category_name}</h4>",
          unsafe_allow_html=True,
      )
      with st.form("dialog_form"):
        d_det = st.text_input("Detail / Description")
        d_amt = st.number_input("Amount (Rs.)", min_value=1.0, step=10.0)
        d_meth = st.selectbox(
            "Payment Method", ["Cash", "Bank Transfer", "Raast", "Credit Card"]
        )
        d_sub = st.form_submit_button("Save Record")

        if d_sub:
          if not d_det:
            st.warning("Detail likhna lazmi hai!")
          else:
            now = datetime.now()
            ins_conn = sqlite3.connect(DB_FILE)
            ins_cur = ins_conn.cursor()
            ins_cur.execute(
                "INSERT INTO expenses (username, category, detail, amount,"
                " payment_method, date_time, month, year) VALUES (?, ?, ?, ?,"
                " ?, ?, ?, ?)",
                (
                    st.session_state.username,
                    category_name,
                    d_det,
                    d_amt,
                    d_meth,
                    now.strftime("%Y-%m-%d %H:%M"),
                    now.strftime("%m"),
                    now.strftime("%Y"),
                ),
            )
            ins_conn.commit()
            ins_conn.close()
            st.success("Expense record ho gaya!")
            st.rerun()


    @st.dialog("➕ Add Custom Category Button")
    def open_custom_category_dialog():
      st.markdown(
          "<h4 style='color: #38bdf8;'>Create New Expense Category</h4>",
          unsafe_allow_html=True,
      )
      with st.form("custom_cat_form"):
        new_cat_name = st.text_input("Enter New Category Name")
        c_sub = st.form_submit_button("Save Custom Category")
        if c_sub:
          if not new_cat_name:
            st.warning("Category ka naam likhna lazmi hai!")
          else:
            c_conn = sqlite3.connect(DB_FILE)
            c_cur = c_conn.cursor()
            try:
              c_cur.execute(
                  "INSERT INTO custom_buttons (username, button_name) VALUES"
                  " (?, ?)",
                  (st.session_state.username, new_cat_name),
              )
              c_conn.commit()
              st.success(
                  f"Nayi category '{new_cat_name}' kamyaabi se ban gayi!"
              )
              c_conn.close()
              st.rerun()
            except:
              st.error("Ye category pehlay se mojood hai!")
              c_conn.close()


    for idx, cat in enumerate(all_cats):
      if st.sidebar.button(f"📁 {cat}", key=f"btn_cat_{idx}_{cat}"):
        st.session_state.selected_cat = cat
        if cat != "All":
          open_add_dialog(cat)
        else:
          st.rerun()

    if custom_rows:
      st.sidebar.markdown("---")
      st.sidebar.markdown(
          "<p style='color: #f59e0b; font-size: 13px; font-weight:bold;'>Manage"
          " Custom Categories</p>",
          unsafe_allow_html=True,
      )
      for cid, cname in custom_rows:
        col_cc1, col_cc2 = st.sidebar.columns([3, 1])
        with col_cc1:
          st.text(cname)
        with col_cc2:
          if st.button("🗑️", key=f"del_cat_item_{cid}"):
            del_c_conn = sqlite3.connect(DB_FILE)
            del_c_cur = del_c_conn.cursor()
            del_c_cur.execute("DELETE FROM custom_buttons WHERE id = ?", (cid,))
            del_c_conn.commit()
            del_c_conn.close()
            st.rerun()

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("✨ Add Custom Category"):
      open_custom_category_dialog()

  if menu == "👑 Customers Data & Control":
    st.markdown(
        f"<h2 style='color: #38bdf8;'>👑 MASTER ADMIN - {COMPANY_NAME.upper()}"
        " CUSTOMER & DATA CONTROL</h2>",
        unsafe_allow_html=True,
    )

    # DATABASE BACKUP DOWNLOAD SECTION FOR ADMIN
    st.subheader("💾 Database Security & Backup")
    if os.path.exists(DB_FILE):
      with open(DB_FILE, "rb") as db_file:
        st.download_button(
            label="📥 Download Full Database Backup (.db)",
            data=db_file,
            file_name=(
                f"backup_nexus_{datetime.now().strftime('%Y%m%d_%H%M')}.db"
            ),
            mime="application/octet-stream",
        )
    st.markdown("---")

    cursor.execute(
        "SELECT username, email, mobile, role, reg_date, last_active FROM users"
        " WHERE role != 'MASTER_ADMIN'"
    )
    users_rows = cursor.fetchall()

    cursor.execute(
        "SELECT id, username, category, detail, amount, payment_method,"
        " date_time FROM expenses"
    )
    rows = cursor.fetchall()
    total_amt = sum([r[4] for r in rows]) if rows else 0.0

    m1, m2, m3 = st.columns(3)
    with m1:
      st.markdown(
          f"""<div class='metric-card'>
                <p style='margin:0; font-size: 12px; color:#94a3b8; font-weight:bold;'>REGISTERED CUSTOMERS</p>
                <h3 style='margin:0; color:white;'>{len(users_rows)} Users</h3>
            </div>""",
          unsafe_allow_html=True,
      )
    with m2:
      st.markdown(
          f"""<div class='metric-card' style='border-left-color: #10b981;'>
                <p style='margin:0; font-size: 12px; color:#94a3b8; font-weight:bold;'>GLOBAL TOTAL EXPENSES</p>
                <h3 style='margin:0; color:white;'>Rs. {total_amt:,.2f}</h3>
            </div>""",
          unsafe_allow_html=True,
      )
    with m3:
      st.markdown(
          f"""<div class='metric-card' style='border-left-color: #f59e0b;'>
                <p style='margin:0; font-size: 12px; color:#94a3b8; font-weight:bold;'>TOTAL SYSTEM RECORDS</p>
                <h3 style='margin:0; color:white;'>{len(rows)} Entries</h3>
            </div>""",
          unsafe_allow_html=True,
      )

    st.markdown("---")
    st.subheader(
        "👥 Registered Customers Information & Admin Password Reset"
    )
    if users_rows:
      for ur in users_rows:
        with st.expander(
            f"User: {ur[0]} | Email: {ur[1]} | Mobile: {ur[2]} | Last Active:"
            f" {ur[5]}"
        ):
          st.markdown(f"**Registration Date:** {ur[4]}")
          with st.form(f"admin_reset_pass_{ur[0]}"):
            new_admin_pass = st.text_input(
                f"Set New Password for {ur[0]}", type="password"
            )
            reset_sub = st.form_submit_button("Update Customer Password")
            if reset_sub:
              if not new_admin_pass:
                st.warning("Naya password likhna lazmi hai!")
              else:
                hashed_new = hash_password(new_admin_pass)
                up_pass_conn = sqlite3.connect(DB_FILE)
                up_pass_cur = up_pass_conn.cursor()
                up_pass_cur.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (hashed_new, ur[0]),
                )
                up_pass_conn.commit()
                up_pass_conn.close()
                st.success(
                    f"Customer '{ur[0]}' ka password kamyabi se tabdeel ho gaya!"
                )
        st.markdown("---")
    else:
      st.info("Abhi tak koi customer registered nahi hai.")

    st.subheader("⚙️ Global Custom Buttons Management")
    cursor.execute("SELECT id, username, button_name FROM custom_buttons")
    all_custom_buttons = cursor.fetchall()
    if all_custom_buttons:
      for c_item in all_custom_buttons:
        col_cb1, col_cb2 = st.columns([5, 1])
        with col_cb1:
          st.markdown(
              f"**ID {c_item[0]}** | **User:** {c_item[1]} | **Custom Button"
              f" Name:** {c_item[2]}"
          )
        with col_cb2:
          if st.button("🗑️ Delete Button", key=f"admin_del_cb_{c_item[0]}"):
            del_cb_conn = sqlite3.connect(DB_FILE)
            del_cb_cur = del_cb_conn.cursor()
            del_cb_cur.execute(
                "DELETE FROM custom_buttons WHERE id = ?", (c_item[0],)
            )
            del_cb_conn.commit()
            del_cb_conn.close()
            st.success(f"Custom button '{c_item[2]}' delete ho gaya!")
            st.rerun()
        st.markdown("---")
    else:
      st.info("System mein koi custom category button mojood nahi hai.")

    st.subheader("📋 Manage & Delete Customer Expense Entries")
    if rows:
      for r in rows:
        c_exp1, c_exp2 = st.columns([5, 1])
        with c_exp1:
          st.markdown(
              f"**ID {r[0]}** | **Category:** {r[2]} | **Detail:** {r[3]} |"
              f" **Amount:** Rs. {r[4]:,.2f} | **Method:** {r[5]} | **Date:**"
              f" {r[6]}"
          )
        with c_exp2:
          if st.button("🗑️ Delete Record", key=f"admin_del_exp_{r[0]}"):
            del_conn = sqlite3.connect(DB_FILE)
            del_cur = del_conn.cursor()
            del_cur.execute("DELETE FROM expenses WHERE id = ?", (r[0],))
            del_conn.commit()
            del_conn.close()
            st.success(f"Record ID {r[0]} delete ho gaya!")
            st.rerun()
        st.markdown("---")
    else:
      st.info("System mein abhi koi expense record mojood nahi hai.")

  elif menu == "📊 User Activity & Analytics":
    st.markdown(
        "<h2 style='color: #38bdf8;'>📊 SYSTEM ACTIVITY & ACTIVE USERS"
        " ANALYTICS</h2>",
        unsafe_allow_html=True,
    )

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    days_15_ago = (now - timedelta(days=15)).strftime("%Y-%m-%d")
    month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE role != 'MASTER_ADMIN' AND"
        " substr(last_active, 1, 10) = ?",
        (today_str,),
    )
    active_today = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE role != 'MASTER_ADMIN' AND"
        " substr(last_active, 1, 10) >= ?",
        (week_ago,),
    )
    active_weekly = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE role != 'MASTER_ADMIN' AND"
        " substr(last_active, 1, 10) >= ?",
        (days_15_ago,),
    )
    active_15days = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE role != 'MASTER_ADMIN' AND"
        " substr(last_active, 1, 10) >= ?",
        (month_ago,),
    )
    active_monthly = cursor.fetchone()[0]

    a1, a2, a3, a4 = st.columns(4)
    with a1:
      st.markdown(
          f"""<div class='metric-card'>
                <p style='margin:0; font-size: 11px; color:#94a3b8; font-weight:bold;'>ACTIVE TODAY</p>
                <h3 style='margin:0; color:white;'>{active_today} Users</h3>
            </div>""",
          unsafe_allow_html=True,
      )
    with a2:
      st.markdown(
          f"""<div class='metric-card' style='border-left-color: #10b981;'>
                <p style='margin:0; font-size: 11px; color:#94a3b8; font-weight:bold;'>WEEKLY (LAST 7 DAYS)</p>
                <h3 style='margin:0; color:white;'>{active_weekly} Users</h3>
            </div>""",
          unsafe_allow_html=True,
      )
    with a3:
      st.markdown(
          f"""<div class='metric-card' style='border-left-color: #f59e0b;'>
                <p style='margin:0; font-size: 11px; color:#94a3b8; font-weight:bold;'>WITHIN 15 DAYS</p>
                <h3 style='margin:0; color:white;'>{active_15days} Users</h3>
            </div>""",
          unsafe_allow_html=True,
      )
    with a4:
      st.markdown(
          f"""<div class='metric-card' style='border-left-color: #ec4899;'>
                <p style='margin:0; font-size: 11px; color:#94a3b8; font-weight:bold;'>MONTHLY (LAST 30 DAYS)</p>
                <h3 style='margin:0; color:white;'>{active_monthly} Users</h3>
            </div>""",
          unsafe_allow_html=True,
      )

    st.markdown("---")
    st.subheader("📈 Recent User Activities & Logs")
    cursor.execute(
        "SELECT username, email, mobile, reg_date, last_active FROM users WHERE"
        " role != 'MASTER_ADMIN' ORDER BY last_active DESC"
    )
    act_rows = cursor.fetchall()
    if act_rows:
      act_table = """
            <table>
                <tr>
                    <th>Username</th><th>Email</th><th>Mobile</th><th>Registered On</th><th>Last Activity Timestamp</th>
                </tr>
            """
      for ar in act_rows:
        act_table += f"<tr><td>{ar[0]}</td><td>{ar[1]}</td><td>{ar[2]}</td><td>{ar[3]}</td><td>{ar[4]}</td></tr>"
      act_table += "</table>"
      st.markdown(act_table, unsafe_allow_html=True)
    else:
      st.info("Koi activity logs mojood nahi hain.")

  elif menu == "Dashboard & Analytics" and st.session_state.role != "MASTER_ADMIN":
    st.markdown(
        f"<h2 style='color: #38bdf8;'>🚀 {COMPANY_NAME.upper()} DASHBOARD &"
        " CONTROL SYSTEM</h2>",
        unsafe_allow_html=True,
    )

    month_dict = {
        "All": "All",
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }
    month_list = list(month_dict.keys())

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
      default_m_index = int(datetime.now().strftime("%m"))
      sel_month_name = st.selectbox(
          "Month", month_list, index=default_m_index
      )
      sel_month_num = month_dict[sel_month_name]
    with col_f2:
      sel_year = st.selectbox(
          "Year", ["All", "2024", "2025", "2026", "2027", "2028"], index=3
      )
    with col_f3:
      st.markdown(
          f"<br><b>Active Filter:</b> <span"
          f" style='color:#38bdf8;'>{st.session_state.selected_cat}</span>",
          unsafe_allow_html=True,
      )

    q = "SELECT id, username, category, detail, amount, payment_method, date_time FROM expenses WHERE username = ?"
    params = [st.session_state.username]
    if st.session_state.selected_cat != "All":
      q += " AND category = ?"
      params.append(st.session_state.selected_cat)
    if sel_month_num != "All":
      q += " AND (month = ? OR month = ?)"
      params.append(sel_month_num)
      params.append(str(int(sel_month_num)))
    if sel_year != "All":
      q += " AND year = ?"
      params.append(sel_year)

    cursor.execute(q, params)
    rows = cursor.fetchall()
    total_amt = sum([r[4] for r in rows]) if rows else 0.0

    m1, m2, m3 = st.columns(3)
    with m1:
      st.markdown(
          f"""<div class='metric-card'>
                <p style='margin:0; font-size: 12px; color:#94a3b8; font-weight:bold;'>TOTAL EXPENSES ({sel_month_name}/{sel_year})</p>
                <h3 style='margin:0; color:white;'>Rs. {total_amt:,.2f}</h3>
            </div>""",
          unsafe_allow_html=True,
      )
    with m2:
      st.markdown(
          f"""<div class='metric-card' style='border-left-color: #10b981;'>
                <p style='margin:0; font-size: 12px; color:#94a3b8; font-weight:bold;'>TOTAL RECORDS</p>
                <h3 style='margin:0; color:white;'>{len(rows)} Entries</h3>
            </div>""",
          unsafe_allow_html=True,
      )
    with m3:
      st.markdown(
          f"""<div class='metric-card' style='border-left-color: #f59e0b;'>
                <p style='margin:0; font-size: 12px; color:#94a3b8; font-weight:bold;'>ACTIVE CATEGORY</p>
                <h3 style='margin:0; color:white;'>{st.session_state.selected_cat}</h3>
            </div>""",
          unsafe_allow_html=True,
      )

    st.markdown("---")
    st.subheader("📋 Expenses Record List")

    if rows:
      for r in rows:
        c_usr1, c_usr2 = st.columns([5, 1])
        with c_usr1:
          st.markdown(
              f"**ID {r[0]}** | **Category:** {r[2]} | **Detail:** {r[3]} |"
              f" **Amount:** Rs. {r[4]:,.2f} | **Method:** {r[5]} | **Date:**"
              f" {r[6]}"
          )
        with c_usr2:
          if st.button("🗑️ Delete", key=f"user_del_exp_{r[0]}"):
            u_del_conn = sqlite3.connect(DB_FILE)
            u_del_cur = u_del_conn.cursor()
            u_del_cur.execute(
                "DELETE FROM expenses WHERE id = ? AND username = ?",
                (r[0], st.session_state.username),
            )
            u_del_conn.commit()
            u_del_conn.close()
            st.success(f"Entry ID {r[0]} delete ho gayi!")
            st.rerun()
        st.markdown("---")

      csv_data = "ID,User,Category,Detail,Amount,Method,Date\n" + "\n".join(
          [f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]},{r[6]}" for r in rows]
      )
      st.download_button(
          label="📥 Download Data as Excel (CSV)",
          data=csv_data,
          file_name="expenses_report.csv",
          mime="text/csv",
      )
    else:
      st.info("Is category ya period mein koi expense record mojood nahi hai.")

  elif menu == "💬 Complaints Portal":
    st.markdown(
        f"<h2 style='color: #38bdf8;'>💬 {COMPANY_NAME.upper()} SUPPORT &"
        " COMPLAINTS CENTER</h2>",
        unsafe_allow_html=True,
    )

    if st.session_state.role == "MASTER_ADMIN":
      now_dt = datetime.now()
      today_date = now_dt.strftime("%Y-%m-%d")
      week_start = (now_dt - timedelta(days=7)).strftime("%Y-%m-%d")
      month_start = (now_dt - timedelta(days=30)).strftime("%Y-%m-%d")

      cursor.execute(
          "SELECT COUNT(*) FROM complaints WHERE substr(date_time, 1, 10) = ?",
          (today_date,),
      )
      comp_today = cursor.fetchone()[0]

      cursor.execute(
          "SELECT COUNT(*) FROM complaints WHERE substr(date_time, 1, 10) >= ?",
          (week_start,),
      )
      comp_week = cursor.fetchone()[0]

      cursor.execute(
          "SELECT COUNT(*) FROM complaints WHERE substr(date_time, 1, 10) >= ?",
          (month_start,),
      )
      comp_month = cursor.fetchone()[0]

      cursor.execute("SELECT COUNT(*) FROM complaints")
      comp_total = cursor.fetchone()[0]

      cm1, cm2, cm3, cm4 = st.columns(4)
      with cm1:
        st.markdown(
            f"""<div class='metric-card'>
                <p style='margin:0; font-size: 11px; color:#94a3b8; font-weight:bold;'>TODAY COMPLAINTS</p>
                <h3 style='margin:0; color:white;'>{comp_today}</h3>
            </div>""",
            unsafe_allow_html=True,
        )
      with cm2:
        st.markdown(
            f"""<div class='metric-card' style='border-left-color: #10b981;'>
                <p style='margin:0; font-size: 11px; color:#94a3b8; font-weight:bold;'>WEEKLY (7 DAYS)</p>
                <h3 style='margin:0; color:white;'>{comp_week}</h3>
            </div>""",
            unsafe_allow_html=True,
        )
      with cm3:
        st.markdown(
            f"""<div class='metric-card' style='border-left-color: #f59e0b;'>
                <p style='margin:0; font-size: 11px; color:#94a3b8; font-weight:bold;'>MONTHLY (30 DAYS)</p>
                <h3 style='margin:0; color:white;'>{comp_month}</h3>
            </div>""",
            unsafe_allow_html=True,
        )
      with cm4:
        st.markdown(
            f"""<div class='metric-card' style='border-left-color: #ec4899;'>
                <p style='margin:0; font-size: 11px; color:#94a3b8; font-weight:bold;'>TOTAL COMPLAINTS</p>
                <h3 style='margin:0; color:white;'>{comp_total}</h3>
            </div>""",
            unsafe_allow_html=True,
        )

      st.markdown("---")
      st.subheader("👑 Manage & Resolve Consumer Complaints")
      cursor.execute(
          "SELECT id, username, subject, message, status, feedback, date_time"
          " FROM complaints ORDER BY id DESC"
      )
      c_rows = cursor.fetchall()
      if c_rows:
        for cr in c_rows:
          with st.expander(
              f"Complaint ID #{cr[0]} | User: {cr[1]} | Subject: {cr[2]} |"
              f" [{cr[4]}] - {cr[6]}"
          ):
            st.markdown(f"**Message / Details:** {cr[3]}")
            st.markdown(f"**Current Status:** `{cr[4]}`")
            st.markdown(f"**Admin Feedback:** {cr[5]}")

            with st.form(f"resolve_form_{cr[0]}"):
              new_fb = st.text_input(
                  "Admin Feedback / Comments", value=cr[5]
              )
              new_status = st.selectbox(
                  "Update Status",
                  ["Pending", "In Progress", "Resolved"],
                  index=2
                  if cr[4] == "Resolved"
                  else (1 if cr[4] == "In Progress" else 0),
              )
              sub_res = st.form_submit_button("Update Complaint Status")
              if sub_res:
                up_conn = sqlite3.connect(DB_FILE)
                up_cur = up_conn.cursor()
                up_cur.execute(
                    "UPDATE complaints SET status = ?, feedback = ? WHERE id ="
                    " ?",
                    (new_status, new_fb, cr[0]),
                )
                up_conn.commit()
                up_conn.close()

                u_conn = sqlite3.connect(DB_FILE)
                u_cur = u_conn.cursor()
                u_cur.execute(
                    "SELECT email FROM users WHERE username = ?", (cr[1],)
                )
                u_email_res = u_cur.fetchone()
                u_conn.close()

                if u_email_res and u_email_res[0]:
                  reply_subj = (
                      f"🔔 Complaint Update - Ticket #{cr[0]} [{COMPANY_NAME}]"
                  )
                  reply_body = f"""Dear {cr[1]},

Aapki complaint (Ticket #{cr[0]}) par response/update aya hai.

------------------------------------------------
Complaint Title: {cr[2]}
Updated Status: {new_status}
Admin Feedback: {new_fb}
------------------------------------------------

Shukriya,
{COMPANY_NAME} Support Team
"""
                  send_email_notification(
                      u_email_res[0], reply_subj, reply_body
                  )

                st.success(
                    "Complaint update ho gayi aur customer ko email notification"
                    " bhej di gayi hai!"
                )
                st.rerun()

            if st.button("🗑️ Delete Complaint", key=f"del_comp_{cr[0]}"):
              del_conn = sqlite3.connect(DB_FILE)
              del_cur = del_conn.cursor()
              del_cur.execute("DELETE FROM complaints WHERE id = ?", (cr[0],))
              del_conn.commit()
              del_conn.close()
              st.success(f"Complaint ID #{cr[0]} delete ho gayi!")
              st.rerun()
      else:
        st.info("System mein filhal koi complaint mojood nahi hai.")

    else:
      st.subheader("📝 Submit New Complaint")
      st.info(
          f"💡 Direct Email Support: For urgent queries, email us at"
          f" **{SENDER_EMAIL}**"
      )

      with st.form("comp_form_user"):
        subj = st.text_input("Subject / Title")
        msg = st.text_area("Message / Complaint Details")
        c_sub = st.form_submit_button("Submit Complaint")
        if c_sub:
          if not subj or not msg:
            st.warning("Subject aur Message likhna zaroori hai!")
          else:
            dt_now = datetime.now().strftime("%Y-%m-%d %H:%M")
            ins_c_conn = sqlite3.connect(DB_FILE)
            ins_c_cur = ins_c_conn.cursor()
            ins_c_cur.execute(
                "INSERT INTO complaints (username, subject, message, status,"
                " feedback, date_time) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    st.session_state.username,
                    subj,
                    msg,
                    "Pending",
                    "No feedback yet",
                    dt_now,
                ),
            )
            ins_c_conn.commit()
            complaint_id = ins_c_cur.lastrowid
            ins_c_conn.close()

            u_conn = sqlite3.connect(DB_FILE)
            u_cur = u_conn.cursor()
            u_cur.execute(
                "SELECT email FROM users WHERE username = ?",
                (st.session_state.username,),
            )
            u_email_res = u_cur.fetchone()
            u_conn.close()

            if u_email_res and u_email_res[0]:
              u_email = u_email_res[0]
              auto_subj = (
                  f"📩 Complaint Received - Ticket #{complaint_id}"
                  f" [{COMPANY_NAME}]"
              )
              auto_body = f"""Dear {st.session_state.username},

Aapki complaint successfully system mein darj ho chuki hai.

------------------------------------------------
Ticket Ref ID: #{complaint_id}
Subject: {subj}
Date: {dt_now}
------------------------------------------------

Nexus Global Support Team aapke masle par jald se jald kaam karke isay resolve kar degi.

Regards,
{COMPANY_NAME} Support Team
"""
              send_email_notification(u_email, auto_subj, auto_body)

            st.success(
                f"Aapki complaint (Ticket Ref #{complaint_id}) kamyabi se submit"
                " ho gayi hai aur aapke email par confirmation bhej di gayi hai!"
            )
            st.rerun()

      st.markdown("---")
      st.subheader("📜 History of Lodged Complaints")
      cursor.execute(
          "SELECT subject, message, status, feedback, date_time FROM complaints"
          " WHERE username = ? ORDER BY id DESC",
          (st.session_state.username,),
      )
      c_rows = cursor.fetchall()
      if c_rows:
        ctable = """
                <table>
                    <tr>
                        <th>Subject</th>
                        <th>Message</th>
                        <th>Status</th>
                        <th>Admin Feedback</th>
                        <th>Date & Time</th>
                    </tr>
                """
        for cr in c_rows:
          ctable += f"<tr><td><b>{cr[0]}</b></td><td>{cr[1]}</td><td><span style='color:#f59e0b; font-weight:bold;'>{cr[2]}</span></td><td>{cr[3]}</td><td>{cr[4]}</td></tr>"
        ctable += "</table>"
        st.markdown(ctable, unsafe_allow_html=True)
      else:
        st.info("Aapki taraf se abhi tak koi complaint darj nahi ki gayi.")

  conn.close()
