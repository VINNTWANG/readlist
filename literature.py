import streamlit as st
import json
import datetime
import os

# --- 配置 ---
LITERATURE_DATA_FILE = "reading_list.json"
BOOKS_MAGAZINES_DATA_FILE = "books_magazines_list.json"
MY_BLOG_POSTS_FILE = "my_blog_posts.json"
WEEKLY_PLAYLIST_FILE = "weekly_playlists.json"
WEEKLY_EXERCISE_LOG_FILE = "weekly_exercise_logs.json"

STATUS_OPTIONS = ["待阅读", "阅读中", "已阅读"]
LITERATURE_CATEGORIES = ["生物", "医学", "计算机", "化学", "物理", "其他"]
BOOK_MAGAZINE_TYPES = ["书籍", "杂志"]
BOOK_STATUS_OPTIONS = ["想读", "在读", "已读"]
MY_BLOG_STATUS_OPTIONS = ["构思中", "草稿中", "待编辑", "待发布", "已发布", "搁置"]
MY_BLOG_PRIORITY_OPTIONS = ["高", "中", "低"]
PLAYLIST_STATUS_OPTIONS = ["想听", "在听", "已听过"]
EXERCISE_TYPES = ["跑步", "步行", "游泳", "自行车", "健身房(力量)", "健身房(有氧)", "瑜伽", "普拉提", "舞蹈", "球类运动", "其他"]
EXERCISE_LOG_STATUS_OPTIONS = ["计划中", "已完成", "部分完成", "未完成/跳过"]


# --- 通用辅助函数 ---
def get_current_week():
    return datetime.date.today().isocalendar()[1]

def load_json_data(filepath, default_data_structure=None):
    if default_data_structure is None: default_data_structure = []
    if not os.path.exists(filepath): return default_data_structure
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 数据完整性检查/迁移
            if filepath == LITERATURE_DATA_FILE:
                for entry in data:
                    entry.setdefault('id', data.index(entry) + 1)
                    entry.setdefault('title', "未命名文献")
                    entry.setdefault('status', STATUS_OPTIONS[0])
                    entry.setdefault('notes', "")
                    entry.setdefault('categories', [])
                    entry.setdefault('week_assigned', get_current_week())
            elif filepath == BOOKS_MAGAZINES_DATA_FILE:
                 for entry in data:
                    entry.setdefault('id', data.index(entry) + 1)
                    entry.setdefault('title', "未命名条目")
                    entry.setdefault('status', BOOK_STATUS_OPTIONS[0])
                    entry.setdefault('progress', 0)
                    entry.setdefault('issue_volume', "")
            elif filepath == MY_BLOG_POSTS_FILE:
                for entry in data:
                    entry.setdefault('id', data.index(entry) + 1)
                    entry.setdefault('title', "未命名文章")
                    entry.setdefault('status', MY_BLOG_STATUS_OPTIONS[0])
                    entry.setdefault('due_date', None)
                    entry.setdefault('publish_date', None)
                    entry.setdefault('priority', MY_BLOG_PRIORITY_OPTIONS[1])
                    entry.setdefault('topic_keywords', "")
                    entry.setdefault('outline_notes', "")
                    entry.setdefault('link_published', "")
            elif filepath == WEEKLY_PLAYLIST_FILE:
                for entry in data:
                    entry.setdefault('id', data.index(entry) + 1)
                    entry.setdefault('week_assigned', get_current_week())
                    entry.setdefault('song_title', "未命名歌曲")
                    entry.setdefault('artist', "")
                    entry.setdefault('album', "")
                    entry.setdefault('status', PLAYLIST_STATUS_OPTIONS[0])
                    entry.setdefault('notes', "")
                    entry.setdefault('date_added', datetime.date.today().isoformat())
            elif filepath == WEEKLY_EXERCISE_LOG_FILE:
                for entry in data:
                    entry.setdefault('id', data.index(entry) + 1)
                    entry.setdefault('date', datetime.date.today().isoformat())
                    entry.setdefault('exercise_type', EXERCISE_TYPES[0])
                    entry.setdefault('duration_intensity', "")
                    entry.setdefault('status', EXERCISE_LOG_STATUS_OPTIONS[0])
                    entry.setdefault('notes', "")
                    entry.setdefault('date_added', datetime.date.today().isoformat())
            return data
    except (json.JSONDecodeError, FileNotFoundError): return default_data_structure

def save_json_data(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def get_next_id(data_list):
    if not data_list: return 1
    return max(entry.get('id', 0) for entry in data_list) + 1

def update_post_field(data_list, entry_id, field_name, new_value, data_file):
    entry_idx = next((idx for idx, item in enumerate(data_list) if item['id'] == entry_id), None)
    if entry_idx is not None:
        data_list[entry_idx][field_name] = new_value
        save_json_data(data_file, data_list)
    else: st.error("更新失败：未找到条目。")

# --- Streamlit 页面配置 ---
st.set_page_config(page_title="个人生活与学习管理", layout="wide", initial_sidebar_state="expanded")

# --- 自定义 CSS ---
st.markdown("""<style>
.main .block-container { padding-top: 1rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] > div:first-child { background-color: #e6f3ff; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] .stMarkdown p { color: #00529B; }
[data-testid="stSidebar"] .stExpander header { color: #003366; }
[data-testid="stTabs"] button[role="tab"] { background-color: #D1E7FD; color: #00529B; border-radius: 0.5rem 0.5rem 0 0; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { background-color: #0D6EFD; color: #FFFFFF; font-weight: bold; }
.stExpander { border: 1px solid #BEE0FC; border-radius: 0.5rem; margin-bottom: 1rem; }
.stExpander header { font-weight: bold; color: #00529B; }
h1.app-main-title { color: #003366; text-align: center; padding-bottom: 1rem; }
h2.tab-header { color: #00529B; border-bottom: 2px solid #0D6EFD; padding-bottom: 0.5rem; margin-top: 1rem; margin-bottom: 1.5rem; }
h3.filter-header { color: #0069D9; margin-bottom: 0.5rem; }
</style>""", unsafe_allow_html=True)

# --- 数据加载 ---
literature_list = load_json_data(LITERATURE_DATA_FILE)
books_magazines_list = load_json_data(BOOKS_MAGAZINES_DATA_FILE)
my_blog_posts_list = load_json_data(MY_BLOG_POSTS_FILE)
weekly_playlists = load_json_data(WEEKLY_PLAYLIST_FILE)
weekly_exercise_logs = load_json_data(WEEKLY_EXERCISE_LOG_FILE)

# --- 侧边栏 ---
st.sidebar.title("📝 内容与记录管理")

with st.sidebar.expander("➕ 添加新文献", expanded=False):
    with st.form("add_literature_form_sidebar_v6", clear_on_submit=True): # Key updated
        st.subheader("文献信息")
        lit_title = st.text_input("文献标题:", key="lit_title_sb_v6")
        lit_authors = st.text_input("作者 (逗号分隔):", key="lit_authors_sb_v6")
        lit_year_str = st.text_input("发表年份:", key="lit_year_sb_v6")
        lit_source = st.text_input("来源 (期刊/会议/URL):", key="lit_source_sb_v6")
        default_week_val = get_current_week()
        lit_week_str = st.text_input(f"计划阅读周 (当前: {default_week_val}):", value=str(default_week_val), key="lit_week_sb_v6")
        lit_categories = st.multiselect("文献分类:", options=LITERATURE_CATEGORIES, key="lit_cat_sb_v6")
        lit_notes = st.text_area("备注 (可选):", key="lit_notes_sb_v6")
        lit_submitted = st.form_submit_button("确认添加文献")
        if lit_submitted:
            if not lit_title: st.sidebar.error("文献标题不能为空！")
            else:
                year_val = None; week_val = default_week_val
                try:
                    if lit_year_str: year_val = int(lit_year_str)
                except ValueError: st.sidebar.warning("年份格式无效，将设置为空。")
                try:
                    if lit_week_str: week_val = int(lit_week_str)
                except ValueError: st.sidebar.warning(f"周数格式无效，将使用默认周: {default_week_val}。")
                new_lit_entry = {"id": get_next_id(literature_list),"title": str(lit_title),"authors": lit_authors,"year": year_val,"source": lit_source,"week_assigned": week_val,"status": STATUS_OPTIONS[0],"categories": lit_categories,"date_added": datetime.date.today().isoformat(),"notes": lit_notes}
                literature_list.append(new_lit_entry); save_json_data(LITERATURE_DATA_FILE, literature_list); st.sidebar.success(f"文献 '{lit_title}' 已添加."); st.rerun()

with st.sidebar.expander("➕ 添加书籍/杂志", expanded=False):
    with st.form("add_book_magazine_form_sidebar_v6", clear_on_submit=True):
        st.subheader("条目信息"); bm_title = st.text_input("标题:", key="bm_title_sb_v6"); bm_type = st.radio("类型:", options=BOOK_MAGAZINE_TYPES, key="bm_type_sb_v6", horizontal=True); bm_author_publisher = st.text_input("作者/出版社:", key="bm_author_sb_v6"); bm_progress_val = 0; bm_issue_volume_val = ""
        if bm_type == "书籍": bm_progress_val = st.slider("阅读进度 (%):", 0, 100, 0, key="bm_prog_sb_v6")
        else: bm_issue_volume_val = st.text_input("期号/卷号:", key="bm_issue_sb_v6")
        bm_notes = st.text_area("备注/摘要 (可选):", key="bm_notes_sb_v6_area"); bm_submitted = st.form_submit_button("确认添加条目")
        if bm_submitted:
            if not bm_title: st.sidebar.error("标题不能为空！")
            else: new_bm_entry = {"id": get_next_id(books_magazines_list),"title": str(bm_title),"type": bm_type,"author_publisher": bm_author_publisher,"status": BOOK_STATUS_OPTIONS[0],"progress": bm_progress_val if bm_type == "书籍" else 0,"issue_volume": bm_issue_volume_val if bm_type == "杂志" else "","date_added": datetime.date.today().isoformat(),"notes": bm_notes}; books_magazines_list.append(new_bm_entry); save_json_data(BOOKS_MAGAZINES_DATA_FILE, books_magazines_list); st.sidebar.success(f"'{bm_title}' ({bm_type}) 已添加."); st.rerun()

with st.sidebar.expander("✍️ 添加新博客文章计划", expanded=False):
    with st.form("add_my_blog_post_form_sidebar_v6", clear_on_submit=True):
        st.subheader("文章计划"); post_title = st.text_input("文章标题:", key="post_title_sb_v6"); post_topic_keywords = st.text_input("主题/关键词 (逗号分隔):", key="post_topic_sb_v6"); post_priority = st.selectbox("优先级:", options=MY_BLOG_PRIORITY_OPTIONS, index=1, key="post_prio_sb_v6"); post_due_date_val = st.date_input("计划完成日期 (可选):", value=None, key="post_due_sb_v6"); post_outline_notes = st.text_area("大纲/初步想法:", key="post_outline_sb_v6"); post_submitted = st.form_submit_button("确认添加计划")
        if post_submitted:
            if not post_title: st.sidebar.error("文章标题不能为空！")
            else: new_post_entry = {"id": get_next_id(my_blog_posts_list),"title": str(post_title),"status": MY_BLOG_STATUS_OPTIONS[0],"priority": post_priority,"due_date": post_due_date_val.isoformat() if post_due_date_val else None,"publish_date": None,"topic_keywords": post_topic_keywords,"outline_notes": post_outline_notes,"link_published": "","date_added": datetime.date.today().isoformat()}; my_blog_posts_list.append(new_post_entry); save_json_data(MY_BLOG_POSTS_FILE, my_blog_posts_list); st.sidebar.success(f"博客计划 '{post_title}' 已添加."); st.rerun()

with st.sidebar.expander("🎵 添加到歌单", expanded=False):
    with st.form("add_playlist_item_form_sidebar_v6", clear_on_submit=True):
        st.subheader("歌曲信息"); pl_song_title = st.text_input("歌曲标题:", key="pl_song_title_sb_v6"); pl_artist = st.text_input("歌手:", key="pl_artist_sb_v6"); pl_album = st.text_input("专辑 (可选):", key="pl_album_sb_v6"); pl_week_val = st.number_input("计划收听周:", min_value=1, max_value=53, value=get_current_week(), key="pl_week_sb_v6"); pl_notes = st.text_area("备注 (可选):", key="pl_notes_sb_v6"); pl_submitted = st.form_submit_button("添加到歌单")
        if pl_submitted:
            if not pl_song_title: st.sidebar.error("歌曲标题不能为空！")
            else: new_pl_entry = {"id": get_next_id(weekly_playlists),"week_assigned": pl_week_val,"song_title": str(pl_song_title),"artist": pl_artist,"album": pl_album,"status": PLAYLIST_STATUS_OPTIONS[0],"notes": pl_notes,"date_added": datetime.date.today().isoformat()}; weekly_playlists.append(new_pl_entry); save_json_data(WEEKLY_PLAYLIST_FILE, weekly_playlists); st.sidebar.success(f"歌曲 '{pl_song_title}' 已添加到歌单."); st.rerun()

with st.sidebar.expander("🏃 添加运动记录", expanded=False):
    with st.form("add_exercise_log_form_sidebar_v6", clear_on_submit=True):
        st.subheader("运动详情"); ex_date_val = st.date_input("运动日期:", value=datetime.date.today(), key="ex_date_sb_v6"); ex_type_val = st.selectbox("运动类型:", options=EXERCISE_TYPES, key="ex_type_sb_v6"); ex_duration_intensity = st.text_input("时长/强度/距离等:", placeholder="例如: 跑步5公里/30分钟", key="ex_duration_sb_v6"); ex_notes = st.text_area("备注 (可选):", key="ex_notes_sb_v6"); ex_submitted = st.form_submit_button("添加运动记录")
        if ex_submitted:
            if not ex_duration_intensity: st.sidebar.error("时长/强度等信息不能为空！")
            else: new_ex_entry = {"id": get_next_id(weekly_exercise_logs),"date": ex_date_val.isoformat(),"exercise_type": ex_type_val,"duration_intensity": ex_duration_intensity,"status": EXERCISE_LOG_STATUS_OPTIONS[0],"notes": ex_notes,"date_added": datetime.date.today().isoformat()}; weekly_exercise_logs.append(new_ex_entry); save_json_data(WEEKLY_EXERCISE_LOG_FILE, weekly_exercise_logs); st.sidebar.success(f"{ex_date_val.isoformat()} 的 {ex_type_val} 记录已添加."); st.rerun()

st.sidebar.markdown("---"); st.sidebar.caption(f"当前周: {get_current_week()}")
st.markdown("<h1 class='app-main-title'>🚀 个人生活与学习管理系统</h1>", unsafe_allow_html=True)
tab_titles = ["📄 学术文献", "📖 书籍与杂志", "✍️ 我的博客", "🎵 每周歌单", "🏃 每周运动"]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_titles)

# ==========================
#      学术文献 Tab
# ==========================
with tab1:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[0]}</h2>", unsafe_allow_html=True)
    st.markdown("<h3 class='filter-header'>筛选文献</h3>", unsafe_allow_html=True)
    filter_cols = st.columns(3)
    all_lit_weeks_set = set(entry.get('week_assigned') for entry in literature_list if entry.get('week_assigned') is not None)
    all_lit_weeks = sorted(list(all_lit_weeks_set))
    sel_lit_week = filter_cols[0].selectbox("按周筛选:", options=["所有"] + all_lit_weeks, key="sel_lit_week_t1_v6")
    sel_lit_status = filter_cols[1].selectbox("按状态筛选:", options=["所有"] + STATUS_OPTIONS, key="sel_lit_status_t1_v6")
    available_categories_set = set(cat for entry in literature_list for cat in entry.get('categories', []))
    available_categories = sorted(list(available_categories_set))
    sel_lit_category = filter_cols[2].selectbox("按分类筛选:", options=["所有"] + available_categories, key="sel_lit_cat_t1_v6")

    filtered_literature = literature_list
    if sel_lit_week != "所有": filtered_literature = [e for e in filtered_literature if e.get('week_assigned') == sel_lit_week]
    if sel_lit_status != "所有": filtered_literature = [e for e in filtered_literature if e.get('status') == sel_lit_status]
    if sel_lit_category != "所有": filtered_literature = [e for e in filtered_literature if sel_lit_category in e.get('categories', [])]

    if not filtered_literature: st.info("没有符合条件的文献记录。")
    else:
        st.markdown(f"找到 **{len(filtered_literature)}** 篇文献。")
        for i, entry in enumerate(filtered_literature):
            title_display = str(entry.get('title', "无标题文献"))
            week_display = str(entry.get('week_assigned', 'N/A'))
            status_display = str(entry.get('status', 'N/A'))
            expander_label = f"{title_display} (周: {week_display}) - 状态: {status_display}"
            with st.expander(expander_label, key=f"lit_exp_t1_v6_{entry['id']}", expanded=False):
                col1, col2 = st.columns([3,1])
                with col1:
                    st.markdown(f"**ID:** `{entry.get('id', 'N/A')}`")
                    if entry.get('authors'): st.markdown(f"**作者:** {entry.get('authors')}")
                    if entry.get('year'): st.markdown(f"**年份:** {entry.get('year')}")
                    if entry.get('source'): st.markdown(f"**来源:** {entry.get('source')}")
                    if entry.get('categories'): st.markdown(f"**分类:** {', '.join(entry.get('categories',[]))}")
                    if entry.get('notes'): st.markdown(f"**备注:** {entry.get('notes')}")
                    st.caption(f"添加日期: {entry.get('date_added', 'N/A')}")
                with col2:
                    st.markdown("**更新状态:**")
                    current_status_idx = STATUS_OPTIONS.index(entry.get('status', STATUS_OPTIONS[0]))
                    new_status = st.selectbox("状态", STATUS_OPTIONS, index=current_status_idx, key=f"lit_status_select_t1_v6_{entry['id']}", label_visibility="collapsed")
                    if new_status != entry.get('status'):
                        entry_idx = next((idx for idx, item in enumerate(literature_list) if item['id'] == entry['id']), None)
                        if entry_idx is not None: literature_list[entry_idx]['status'] = new_status; save_json_data(LITERATURE_DATA_FILE, literature_list); st.success(f"文献 '{title_display}' 状态更新."); st.rerun()

# ==========================
#      书籍与杂志 Tab
# ==========================
with tab2:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[1]}</h2>", unsafe_allow_html=True)
    st.markdown("<h3 class='filter-header'>筛选条目</h3>", unsafe_allow_html=True)
    bm_filter_cols = st.columns(2)
    sel_bm_type = bm_filter_cols[0].selectbox("按类型筛选:", options=["所有"] + BOOK_MAGAZINE_TYPES, key="sel_bm_type_t2_v6")
    sel_bm_status = bm_filter_cols[1].selectbox("按状态筛选:", options=["所有"] + BOOK_STATUS_OPTIONS, key="sel_bm_status_t2_v6")
    filtered_books_magazines = books_magazines_list
    if sel_bm_type != "所有": filtered_books_magazines = [e for e in filtered_books_magazines if e.get('type') == sel_bm_type]
    if sel_bm_status != "所有": filtered_books_magazines = [e for e in filtered_books_magazines if e.get('status') == sel_bm_status]
    if not filtered_books_magazines: st.info("没有符合条件的书籍或杂志记录。")
    else:
        st.markdown(f"找到 **{len(filtered_books_magazines)}** 个条目。")
        for i, entry in enumerate(filtered_books_magazines):
            icon = "📘" if entry.get('type') == "书籍" else "📰"
            title_display = str(entry.get('title', "无标题"))
            status_display = str(entry.get('status', 'N/A'))
            expander_label = f"{icon} {title_display} - 状态: {status_display}"
            with st.expander(expander_label, key=f"bm_exp_t2_v6_{entry['id']}", expanded=False):
                cols_bm_main, cols_bm_actions = st.columns([3,1])
                with cols_bm_main:
                    st.markdown(f"**ID:** `{entry.get('id', 'N/A')}`")
                    st.markdown(f"**添加日期:** {entry.get('date_added', 'N/A')}")
                    if entry.get('author_publisher'): st.markdown(f"**作者/出版社:** {entry.get('author_publisher')}")
                    if entry.get('type') == "杂志" and entry.get('issue_volume'): st.markdown(f"**期号/卷号:** {entry.get('issue_volume')}")
                    if entry.get('notes'):
                        with st.expander("查看备注/摘要", key=f"bm_notes_exp_t2_v6_{entry['id']}", expanded=False): st.markdown(entry['notes'])
                with cols_bm_actions:
                    st.markdown("**更新状态:**")
                    current_bm_status_idx = BOOK_STATUS_OPTIONS.index(entry.get('status', BOOK_STATUS_OPTIONS[0]))
                    new_bm_status = st.selectbox("状态", BOOK_STATUS_OPTIONS, index=current_bm_status_idx, key=f"bm_status_select_t2_v6_{entry['id']}", label_visibility="collapsed")
                    if new_bm_status != entry.get('status'):
                        bm_entry_idx = next((idx for idx, item in enumerate(books_magazines_list) if item['id'] == entry['id']), None)
                        if bm_entry_idx is not None: books_magazines_list[bm_entry_idx]['status'] = new_bm_status; save_json_data(BOOKS_MAGAZINES_DATA_FILE, books_magazines_list); st.success(f"条目 '{title_display}' 状态更新."); st.rerun()
                    if entry.get('type') == "书籍":
                        st.markdown("**更新进度:**")
                        current_progress = entry.get('progress', 0)
                        new_progress = st.slider("进度", 0, 100, current_progress, 5, key=f"bm_progress_slider_t2_v6_{entry['id']}", label_visibility="collapsed")
                        if new_progress != current_progress:
                            bm_entry_idx = next((idx for idx, item in enumerate(books_magazines_list) if item['id'] == entry['id']), None)
                            if bm_entry_idx is not None: books_magazines_list[bm_entry_idx]['progress'] = new_progress; status_changed = False
                            if new_progress == 100 and books_magazines_list[bm_entry_idx]['status'] != "已读": books_magazines_list[bm_entry_idx]['status'] = "已读"; status_changed = True; st.toast("书籍完成！🎉", icon="📚")
                            elif new_progress > 0 and books_magazines_list[bm_entry_idx]['status'] == "想读": books_magazines_list[bm_entry_idx]['status'] = "在读"; status_changed = True; st.toast("开始阅读！🚀", icon="📖")
                            save_json_data(BOOKS_MAGAZINES_DATA_FILE, books_magazines_list);
                            if status_changed or new_progress != current_progress: st.rerun()

# ==========================
#      我的博客写作 Tab
# ==========================
with tab3:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[2]}</h2>", unsafe_allow_html=True); st.markdown("<h3 class='filter-header'>筛选文章计划</h3>", unsafe_allow_html=True)
    post_filter_cols = st.columns(2); sel_post_status = post_filter_cols[0].selectbox("按状态筛选:", options=["所有"] + MY_BLOG_STATUS_OPTIONS, key="sel_post_status_t3_v6"); sel_post_priority = post_filter_cols[1].selectbox("按优先级筛选:", options=["所有"] + MY_BLOG_PRIORITY_OPTIONS, key="sel_post_priority_t3_v6")
    filtered_posts = my_blog_posts_list
    if sel_post_status != "所有": filtered_posts = [p for p in filtered_posts if p.get('status') == sel_post_status]
    if sel_post_priority != "所有": filtered_posts = [p for p in filtered_posts if p.get('priority') == sel_post_priority]
    if not filtered_posts: st.info("没有符合条件的博客文章计划。")
    else:
        st.markdown(f"共有 **{len(filtered_posts)}** 篇文章计划。")
        for i, post in enumerate(filtered_posts):
            title_display = str(post.get('title', "无标题文章"))
            priority_display = str(post.get('priority', 'N/A'))
            status_display = str(post.get('status', 'N/A'))
            due_date_display_str = f" (计划: {post.get('due_date', 'N/A')})" if post.get('due_date') else ""
            expander_header = f"[{priority_display}] {title_display} - 状态: {status_display}{due_date_display_str}"
            with st.expander(expander_header, key=f"post_exp_t3_v6_{post['id']}", expanded=False):
                cols_post_main, cols_post_actions = st.columns([3, 1])
                with cols_post_main:
                    st.markdown(f"**ID:** `{post.get('id', 'N/A')}`")
                    st.markdown(f"**主题/关键词:** {post.get('topic_keywords', 'N/A')}")
                    if post.get('outline_notes'):
                        with st.expander("查看大纲/笔记", key=f"post_outline_t3_v6_{post['id']}", expanded=False):
                            current_outline_notes = post['outline_notes']
                            new_outline_notes = st.text_area("大纲/笔记内容:", value=current_outline_notes, height=150, key=f"post_outline_area_t3_v6_{post['id']}")
                            if new_outline_notes != current_outline_notes: update_post_field(my_blog_posts_list, post['id'], 'outline_notes', new_outline_notes, MY_BLOG_POSTS_FILE); st.rerun()
                    if post.get('status') == "已发布":
                        if post.get('link_published'): st.markdown(f"**已发布链接:** [{post['link_published']}]({post['link_published']})")
                        else:
                            new_link = st.text_input("输入已发布链接:", key=f"post_link_input_t3_v6_{post['id']}")
                            if st.button("保存链接", key=f"post_save_link_btn_t3_v6_{post['id']}"):
                                if new_link: update_post_field(my_blog_posts_list, post['id'], 'link_published', new_link, MY_BLOG_POSTS_FILE); st.rerun()
                        st.markdown(f"**发布日期:** {post.get('publish_date', 'N/A')}")
                    st.caption(f"添加日期: {post.get('date_added', 'N/A')}")
                with cols_post_actions:
                    st.markdown("**更新状态:**"); current_post_status_idx = MY_BLOG_STATUS_OPTIONS.index(post.get('status', MY_BLOG_STATUS_OPTIONS[0])); new_post_status = st.selectbox("状态", MY_BLOG_STATUS_OPTIONS, index=current_post_status_idx, key=f"post_status_select_t3_v6_{post['id']}", label_visibility="collapsed")
                    if new_post_status != post.get('status'): update_post_field(my_blog_posts_list, post['id'], 'status', new_post_status, MY_BLOG_POSTS_FILE); 
                    if new_post_status == "已发布" and not post.get('publish_date'): update_post_field(my_blog_posts_list, post['id'], 'publish_date', datetime.date.today().isoformat(), MY_BLOG_POSTS_FILE); st.rerun()
                    st.markdown("**更新优先级:**"); current_priority_idx = MY_BLOG_PRIORITY_OPTIONS.index(post.get('priority', MY_BLOG_PRIORITY_OPTIONS[1])); new_priority = st.selectbox("优先级", MY_BLOG_PRIORITY_OPTIONS, index=current_priority_idx, key=f"post_priority_select_t3_v6_{post['id']}", label_visibility="collapsed")
                    if new_priority != post.get('priority'): update_post_field(my_blog_posts_list, post['id'], 'priority', new_priority, MY_BLOG_POSTS_FILE); st.rerun()
                    st.markdown("**计划完成日期:**"); current_due_date_val = None;
                    if post.get('due_date'):
                        try: current_due_date_val = datetime.datetime.strptime(post['due_date'], "%Y-%m-%d").date()
                        except ValueError: current_due_date_val = None # Handle invalid date format
                    new_due_date = st.date_input("日期", value=current_due_date_val, key=f"post_due_date_input_t3_v6_{post['id']}", label_visibility="collapsed"); new_due_date_str = new_due_date.isoformat() if new_due_date else None
                    if new_due_date_str != post.get('due_date'): update_post_field(my_blog_posts_list, post['id'], 'due_date', new_due_date_str, MY_BLOG_POSTS_FILE); st.rerun()

# ==========================
#      每周歌单 Tab
# ==========================
with tab4:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[3]}</h2>", unsafe_allow_html=True); st.markdown("<h3 class='filter-header'>筛选歌单</h3>", unsafe_allow_html=True)
    pl_filter_cols = st.columns(2); all_pl_weeks_set = set(entry.get('week_assigned', get_current_week()) for entry in weekly_playlists); all_pl_weeks = sorted(list(all_pl_weeks_set)); sel_pl_week = pl_filter_cols[0].selectbox("按周筛选:", options=["所有"] + all_pl_weeks, key="sel_pl_week_t4_v6"); sel_pl_status = pl_filter_cols[1].selectbox("按状态筛选:", options=["所有"] + PLAYLIST_STATUS_OPTIONS, key="sel_pl_status_t4_v6")
    filtered_playlist = weekly_playlists
    if sel_pl_week != "所有": filtered_playlist = [s for s in filtered_playlist if s.get('week_assigned') == sel_pl_week]
    if sel_pl_status != "所有": filtered_playlist = [s for s in filtered_playlist if s.get('status') == sel_pl_status]
    if not filtered_playlist: st.info("本周歌单为空或无符合筛选的歌曲。")
    else:
        st.markdown(f"歌单中 **{len(filtered_playlist)}** 首歌曲。")
        for i, song in enumerate(filtered_playlist):
            title_display = str(song.get('song_title', "无标题歌曲"))
            artist_display = str(song.get('artist', '未知歌手'))
            week_display = str(song.get('week_assigned', 'N/A'))
            status_display = str(song.get('status', 'N/A'))
            expander_label = f"{title_display} - {artist_display} (周{week_display}) - 状态: {status_display}"
            with st.expander(expander_label, key=f"pl_exp_t4_v6_{song['id']}", expanded=False):
                col1, col2 = st.columns([3,1]);
                with col1:
                    st.markdown(f"**ID:** `{song.get('id', 'N/A')}`")
                    if song.get('album'): st.markdown(f"**专辑:** {song.get('album')}")
                    if song.get('notes'): st.markdown(f"**备注:** {song.get('notes')}")
                    st.caption(f"添加日期: {song.get('date_added', 'N/A')}")
                with col2:
                    st.markdown("**更新状态:**")
                    current_pl_status_idx = PLAYLIST_STATUS_OPTIONS.index(song.get('status', PLAYLIST_STATUS_OPTIONS[0]))
                    new_pl_status = st.selectbox("状态", PLAYLIST_STATUS_OPTIONS, index=current_pl_status_idx, key=f"pl_status_select_t4_v6_{song['id']}", label_visibility="collapsed")
                    if new_pl_status != song.get('status'):
                        song_idx = next((idx for idx, item in enumerate(weekly_playlists) if item['id'] == song['id']), None)
                        if song_idx is not None: weekly_playlists[song_idx]['status'] = new_pl_status; save_json_data(WEEKLY_PLAYLIST_FILE, weekly_playlists); st.success(f"歌曲 '{title_display}' 状态更新."); st.rerun()

# ==========================
#      每周运动 Tab
# ==========================
with tab5:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[4]}</h2>", unsafe_allow_html=True); st.markdown("<h3 class='filter-header'>筛选运动记录</h3>", unsafe_allow_html=True)
    ex_filter_cols = st.columns(3); ex_weeks_set = set(datetime.date.fromisoformat(e['date']).isocalendar()[1] for e in weekly_exercise_logs if e.get('date')); ex_weeks = sorted(list(ex_weeks_set), reverse=True); sel_ex_week = ex_filter_cols[0].selectbox("按周筛选:", options=["所有"] + ex_weeks, key="sel_ex_week_t5_v6"); sel_ex_type = ex_filter_cols[1].selectbox("按运动类型筛选:", options=["所有"] + EXERCISE_TYPES, key="sel_ex_type_t5_v6"); sel_ex_status = ex_filter_cols[2].selectbox("按状态筛选:", options=["所有"] + EXERCISE_LOG_STATUS_OPTIONS, key="sel_ex_status_t5_v6")
    filtered_exercise_logs = weekly_exercise_logs
    if sel_ex_week != "所有": filtered_exercise_logs = [log for log in filtered_exercise_logs if log.get('date') and datetime.date.fromisoformat(log['date']).isocalendar()[1] == sel_ex_week]
    if sel_ex_type != "所有": filtered_exercise_logs = [log for log in filtered_exercise_logs if log.get('exercise_type') == sel_ex_type]
    if sel_ex_status != "所有": filtered_exercise_logs = [log for log in filtered_exercise_logs if log.get('status') == sel_ex_status]
    if not filtered_exercise_logs: st.info("没有符合条件的运动记录。")
    else:
        st.markdown(f"共有 **{len(filtered_exercise_logs)}** 条运动记录。")
        for i, log_entry in enumerate(filtered_exercise_logs):
            log_date_str = log_entry.get('date', '未知日期')
            log_date_display = log_date_str # Default value
            try:
                log_date_obj = datetime.date.fromisoformat(log_date_str)
                day_of_week = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][log_date_obj.weekday()]
                log_date_display = f"{log_date_str} (周{day_of_week})"
            except ValueError: # Handle invalid date format from json
                pass

            type_display = str(log_entry.get('exercise_type', 'N/A'))
            status_display = str(log_entry.get('status', 'N/A'))
            expander_label = f"{log_date_display}: {type_display} - 状态: {status_display}"
            with st.expander(expander_label, key=f"ex_exp_t5_v6_{log_entry['id']}", expanded=False):
                col1, col2 = st.columns([3,1])
                with col1:
                    st.markdown(f"**ID:** `{log_entry.get('id', 'N/A')}`")
                    st.markdown(f"**详情:** {log_entry.get('duration_intensity', 'N/A')}")
                    if log_entry.get('notes'): st.markdown(f"**备注:** {log_entry.get('notes')}")
                    st.caption(f"记录添加于: {log_entry.get('date_added', 'N/A')}")
                with col2:
                    st.markdown("**更新状态:**")
                    current_ex_status_idx = EXERCISE_LOG_STATUS_OPTIONS.index(log_entry.get('status', EXERCISE_LOG_STATUS_OPTIONS[0]))
                    new_ex_status = st.selectbox("状态", EXERCISE_LOG_STATUS_OPTIONS, index=current_ex_status_idx, key=f"ex_status_select_t5_v6_{log_entry['id']}", label_visibility="collapsed")
                    if new_ex_status != log_entry.get('status'):
                        log_idx = next((idx for idx, item in enumerate(weekly_exercise_logs) if item['id'] == log_entry['id']), None)
                        if log_idx is not None: weekly_exercise_logs[log_idx]['status'] = new_ex_status; save_json_data(WEEKLY_EXERCISE_LOG_FILE, weekly_exercise_logs); st.success(f"运动记录状态更新."); st.rerun()
