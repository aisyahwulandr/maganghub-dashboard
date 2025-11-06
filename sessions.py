import streamlit as st
import time
import uuid
import os
import bcrypt

# --- Track sessions ---
@st.cache_resource
def get_sessions():
    return {}

def track_sessions(timeout: int = 120, max_sessions: int = 50):
    """Melacak jumlah session aktif + metadata"""
    sessions = get_sessions()

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    sid = st.session_state["session_id"]

    now = time.time()
    if sid not in sessions or isinstance(sessions[sid], float):
        sessions[sid] = {"created": now, "last_seen": now}
    else:
        sessions[sid]["last_seen"] = now

    # hapus session idle
    for key, val in list(sessions.items()):
        last_seen = val["last_seen"] if isinstance(val, dict) else val
        if now - last_seen > timeout:
            del sessions[key]

    # batasi jumlah session aktif
    if len(sessions) > max_sessions:
        st.sidebar.warning(f"Jumlah maksimum pengguna ({max_sessions}) tercapai.")

    return sessions


# --- Admin authentication ---
# def admin_auth(sessions, max_attempts=5):
#     """Autentikasi admin dengan bcrypt dan tampilkan detail session"""

#     with st.sidebar.expander("👥 Pengunjung Aktif", expanded=False):
#         st.metric("Jumlah", len(sessions))

#     with st.sidebar.expander("🔑 Admin Panel", expanded=False):
#         admin_bcrypt = None
#         try:
#             admin_bcrypt = st.secrets.get("ADMIN_PASSWORD_BCRYPT")
#         except Exception:
#             pass
#         if not admin_bcrypt:
#             admin_bcrypt = os.environ.get("ADMIN_PASSWORD_BCRYPT")

#         admin_input = st.text_input("Password Admin", type="password")

#         if "admin_attempts" not in st.session_state:
#             st.session_state["admin_attempts"] = 0

#         if admin_input:
#             st.session_state["admin_attempts"] += 1

#         if not admin_bcrypt:
#             st.info("Admin password belum dikonfigurasi (secrets/env).")
#             return

#         if st.session_state["admin_attempts"] > max_attempts:
#             st.error("Terlalu banyak percobaan. Coba lagi nanti.")
#             return

#         if admin_input:
#             ok = bcrypt.checkpw(admin_input.encode(), admin_bcrypt.encode())
#             if ok:
#                 st.success("✅ Autentikasi berhasil")
#                 st.write("**Detail session:**")
#                 for sid, info in sessions.items():
#                     st.write({
#                         "Session ID": sid[:8] + "...",
#                         "Created": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info["created"])),
#                         "Last Seen": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info["last_seen"]))
#                     })
#             else:
#                 st.error("❌ Password salah")
