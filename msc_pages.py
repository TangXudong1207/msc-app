### msc_pages.py ###
import page_auth
import page_ai
import page_social
import page_admin
import msc_i18n as i18n

# 透传函数 (Export functions)
# 这样 msc_main.py 就不需要修改任何导入路径

def render_login_page():
    page_auth.render_login_page()

def render_onboarding(username):
    page_auth.render_onboarding(username)

def render_ai_page(username):
    page_ai.render_ai_page(username)

def render_friends_page(username, unread_counts):
    page_social.render_friends_page(username, unread_counts)

# 关键在这里，确保这里调用的是 page_social.render_world_page()
def render_world_page():
    page_social.render_world_page()

def render_admin_dashboard():
    page_admin.render_admin_dashboard()
