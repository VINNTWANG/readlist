import streamlit as st
import json
import datetime
import os
import pandas as pd # 新增
import plotly.express as px # 新增

# --- 配置 (与之前版本相同) ---
LITERATURE_DATA_FILE = "reading_list.json"; BOOKS_MAGAZINES_DATA_FILE = "books_magazines_list.json"; MY_BLOG_POSTS_FILE = "my_blog_posts.json"; WEEKLY_PLAYLIST_FILE = "weekly_playlists.json"; WEEKLY_EXERCISE_LOG_FILE = "weekly_exercise_logs.json"
STATUS_OPTIONS = ["待阅读", "阅读中", "已阅读"]; LITERATURE_CATEGORIES = ["生物", "医学", "计算机", "化学", "物理", "其他"]; BOOK_MAGAZINE_TYPES = ["书籍", "杂志"]; BOOK_STATUS_OPTIONS = ["想读", "在读", "已读"]; MY_BLOG_STATUS_OPTIONS = ["构思中", "草稿中", "待编辑", "待发布", "已发布", "搁置"]; MY_BLOG_PRIORITY_OPTIONS = ["高", "中", "低"]; PLAYLIST_STATUS_OPTIONS = ["想听", "在听", "已听过"]; EXERCISE_TYPES = ["跑步", "步行", "游泳", "自行车", "健身房(力量)", "健身房(有氧)", "瑜伽", "普拉提", "舞蹈", "球类运动", "其他"]; EXERCISE_LOG_STATUS_OPTIONS = ["计划中", "已完成", "部分完成", "未完成/跳过"]

# --- 通用辅助函数 ---
def get_current_week(): return datetime.date.today().isocalendar()[1]

def load_json_data(filepath, default_data_structure=None):
    if default_data_structure is None:
        default_data_structure = []
    if not os.path.exists(filepath):
        # 如果文件不存在，创建一个空的JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_data_structure, f, ensure_ascii=False, indent=4)
        return default_data_structure
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list): # 确保数据是列表
                st.error(f"文件 {filepath} 格式错误，应为JSON列表。将使用默认空列表。")
                return default_data_structure

            # 为加载的数据设置默认值
            if filepath == LITERATURE_DATA_FILE:
                for i, entry in enumerate(data):
                    entry.setdefault('id', entry.get('id', i + 1))
                    entry.setdefault('title', "未命名文献")
                    entry.setdefault('status', STATUS_OPTIONS[0])
                    entry.setdefault('notes', "")
                    entry.setdefault('categories', [])
                    entry.setdefault('week_assigned', get_current_week())
                    entry.setdefault('date_added', datetime.date.today().isoformat())
            elif filepath == BOOKS_MAGAZINES_DATA_FILE:
                 for i, entry in enumerate(data):
                     entry.setdefault('id', entry.get('id', i + 1))
                     entry.setdefault('title', "未命名条目")
                     entry.setdefault('type', BOOK_MAGAZINE_TYPES[0])
                     entry.setdefault('status', BOOK_STATUS_OPTIONS[0])
                     entry.setdefault('progress', 0)
                     entry.setdefault('issue_volume', "")
                     entry.setdefault('date_added', datetime.date.today().isoformat())
            elif filepath == MY_BLOG_POSTS_FILE:
                for i, entry in enumerate(data):
                    entry.setdefault('id', entry.get('id', i + 1))
                    entry.setdefault('title', "未命名文章")
                    entry.setdefault('status', MY_BLOG_STATUS_OPTIONS[0])
                    entry.setdefault('due_date', None)
                    entry.setdefault('publish_date', None)
                    entry.setdefault('priority', MY_BLOG_PRIORITY_OPTIONS[1])
                    entry.setdefault('topic_keywords', "")
                    entry.setdefault('outline_notes', "")
                    entry.setdefault('link_published', "")
                    entry.setdefault('date_added', datetime.date.today().isoformat())
            elif filepath == WEEKLY_PLAYLIST_FILE:
                for i, entry in enumerate(data):
                    entry.setdefault('id', entry.get('id', i + 1))
                    entry.setdefault('week_assigned', get_current_week())
                    entry.setdefault('song_title', "未命名歌曲")
                    entry.setdefault('artist', "")
                    entry.setdefault('album', "")
                    entry.setdefault('status', PLAYLIST_STATUS_OPTIONS[0])
                    entry.setdefault('notes', "")
                    entry.setdefault('date_added', datetime.date.today().isoformat())
            elif filepath == WEEKLY_EXERCISE_LOG_FILE:
                for i, entry in enumerate(data):
                    entry.setdefault('id', entry.get('id', i + 1))
                    entry.setdefault('date', datetime.date.today().isoformat())
                    entry.setdefault('exercise_type', EXERCISE_TYPES[0])
                    entry.setdefault('duration_intensity', "")
                    entry.setdefault('status', EXERCISE_LOG_STATUS_OPTIONS[0])
                    entry.setdefault('notes', "")
                    entry.setdefault('date_added', datetime.date.today().isoformat())
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        st.error(f"加载文件 {filepath} 失败或文件内容非标准JSON。将使用默认空列表。")
        return default_data_structure

def save_json_data(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_next_id(data_list):
    if not data_list:
        return 1
    return max(entry.get('id', 0) for entry in data_list if isinstance(entry, dict)) + 1


def update_entry_field(data_list, entry_id, field_name, new_value, data_file): # Renamed for clarity
    entry_idx = next((idx for idx, item in enumerate(data_list) if isinstance(item, dict) and item.get('id') == entry_id), None)
    if entry_idx is not None:
        data_list[entry_idx][field_name] = new_value
        save_json_data(data_file, data_list)
    else:
        st.error(f"更新失败：未找到 ID 为 {entry_id} 的条目。")

def delete_entry_by_id(data_list, entry_id, data_file):
    original_len = len(data_list)
    # Ensure all items are dicts and have 'id' before filtering
    data_list[:] = [entry for entry in data_list if not (isinstance(entry, dict) and entry.get('id') == entry_id)]
    if len(data_list) < original_len:
        save_json_data(data_file, data_list)
        st.success(f"ID 为 {entry_id} 的条目已删除。")
        return True
    else:
        st.warning(f"删除失败：未找到 ID 为 {entry_id} 的条目。")
        return False


# --- Streamlit 页面配置 和 CSS (与之前版本相同) ---
st.set_page_config(page_title="个人生活与学习管理", layout="wide", initial_sidebar_state="expanded")
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
h3.stats-subheader { color: #007BFF; margin-top: 1.5rem; margin-bottom: 0.8rem; border-left: 4px solid #007BFF; padding-left: 0.5rem;}
</style>""", unsafe_allow_html=True)

# --- 数据加载 ---
literature_list = load_json_data(LITERATURE_DATA_FILE, [])
books_magazines_list = load_json_data(BOOKS_MAGAZINES_DATA_FILE, [])
my_blog_posts_list = load_json_data(MY_BLOG_POSTS_FILE, [])
weekly_playlists = load_json_data(WEEKLY_PLAYLIST_FILE, [])
weekly_exercise_logs = load_json_data(WEEKLY_EXERCISE_LOG_FILE, [])


# --- 侧边栏 ---
st.sidebar.title("📝 内容与记录管理")

with st.sidebar.expander("➕ 添加新文献", expanded=False):
    with st.form("add_literature_form_sidebar_v8", clear_on_submit=True): # Key updated
        st.subheader("文献信息")
        lit_title = st.text_input("文献标题:", key="lit_title_sb_v8")
        lit_authors = st.text_input("作者 (逗号分隔):", key="lit_authors_sb_v8")
        lit_year_str = st.text_input("发表年份:", key="lit_year_sb_v8")
        lit_source = st.text_input("来源 (期刊/会议/URL):", key="lit_source_sb_v8")
        default_week_val = get_current_week()
        lit_week_str = st.text_input(f"计划阅读周 (当前: {default_week_val}):", value=str(default_week_val), key="lit_week_sb_v8")
        lit_categories = st.multiselect("文献分类:", options=LITERATURE_CATEGORIES, key="lit_cat_sb_v8")
        lit_notes = st.text_area("备注 (可选):", key="lit_notes_sb_v8")
        lit_submitted = st.form_submit_button("确认添加文献")

        if lit_submitted:
            if not lit_title:
                st.sidebar.error("文献标题不能为空！")
            else:
                year_val = None
                week_val = default_week_val
                try:
                    if lit_year_str: year_val = int(lit_year_str)
                except ValueError: st.sidebar.warning("年份格式无效，将设置为空。")
                try:
                    if lit_week_str: week_val = int(lit_week_str)
                except ValueError: st.sidebar.warning(f"周数格式无效，将使用默认周: {default_week_val}。")

                new_lit_entry = {
                    "id": get_next_id(literature_list), "title": str(lit_title), "authors": lit_authors,
                    "year": year_val, "source": lit_source, "week_assigned": week_val,
                    "status": STATUS_OPTIONS[0], "categories": lit_categories,
                    "date_added": datetime.date.today().isoformat(), "notes": lit_notes
                }
                literature_list.append(new_lit_entry)
                save_json_data(LITERATURE_DATA_FILE, literature_list)
                st.sidebar.success(f"文献 '{lit_title}' 已添加.")
                st.rerun()

with st.sidebar.expander("➕ 添加书籍/杂志", expanded=False):
    with st.form("add_book_magazine_form_sidebar_v8", clear_on_submit=True): # Key updated
        st.subheader("条目信息"); bm_title = st.text_input("标题:", key="bm_title_sb_v8"); bm_type = st.radio("类型:", options=BOOK_MAGAZINE_TYPES, key="bm_type_sb_v8", horizontal=True); bm_author_publisher = st.text_input("作者/出版社:", key="bm_author_sb_v8"); bm_progress_val = 0; bm_issue_volume_val = ""
        if bm_type == "书籍": bm_progress_val = st.slider("阅读进度 (%):", 0, 100, 0, key="bm_prog_sb_v8")
        else: bm_issue_volume_val = st.text_input("期号/卷号:", key="bm_issue_sb_v8")
        bm_notes = st.text_area("备注/摘要 (可选):", key="bm_notes_sb_v8_area"); bm_submitted = st.form_submit_button("确认添加条目")
        if bm_submitted:
            if not bm_title: st.sidebar.error("标题不能为空！")
            else:
                new_bm_entry = {"id": get_next_id(books_magazines_list),"title": str(bm_title),"type": bm_type,"author_publisher": bm_author_publisher,"status": BOOK_STATUS_OPTIONS[0],"progress": bm_progress_val if bm_type == "书籍" else 0,"issue_volume": bm_issue_volume_val if bm_type == "杂志" else "","date_added": datetime.date.today().isoformat(),"notes": bm_notes}
                books_magazines_list.append(new_bm_entry); save_json_data(BOOKS_MAGAZINES_DATA_FILE, books_magazines_list); st.sidebar.success(f"'{bm_title}' ({bm_type}) 已添加."); st.rerun()

with st.sidebar.expander("✍️ 添加新博客文章计划", expanded=False):
    with st.form("add_my_blog_post_form_sidebar_v8", clear_on_submit=True): # Key updated
        st.subheader("文章计划"); post_title = st.text_input("文章标题:", key="post_title_sb_v8"); post_topic_keywords = st.text_input("主题/关键词 (逗号分隔):", key="post_topic_sb_v8"); post_priority = st.selectbox("优先级:", options=MY_BLOG_PRIORITY_OPTIONS, index=1, key="post_prio_sb_v8"); post_due_date_val = st.date_input("计划完成日期 (可选):", value=None, key="post_due_sb_v8"); post_outline_notes = st.text_area("大纲/初步想法:", key="post_outline_sb_v8"); post_submitted = st.form_submit_button("确认添加计划")
        if post_submitted:
            if not post_title: st.sidebar.error("文章标题不能为空！")
            else:
                new_post_entry = {"id": get_next_id(my_blog_posts_list),"title": str(post_title),"status": MY_BLOG_STATUS_OPTIONS[0],"priority": post_priority,"due_date": post_due_date_val.isoformat() if post_due_date_val else None,"publish_date": None,"topic_keywords": post_topic_keywords,"outline_notes": post_outline_notes,"link_published": "","date_added": datetime.date.today().isoformat()}
                my_blog_posts_list.append(new_post_entry); save_json_data(MY_BLOG_POSTS_FILE, my_blog_posts_list); st.sidebar.success(f"博客计划 '{post_title}' 已添加."); st.rerun()

with st.sidebar.expander("🎵 添加到歌单", expanded=False):
    with st.form("add_playlist_item_form_sidebar_v8", clear_on_submit=True): # Key updated
        st.subheader("歌曲信息"); pl_song_title = st.text_input("歌曲标题:", key="pl_song_title_sb_v8"); pl_artist = st.text_input("歌手:", key="pl_artist_sb_v8"); pl_album = st.text_input("专辑 (可选):", key="pl_album_sb_v8"); pl_week_val = st.number_input("计划收听周:", min_value=1, max_value=53, value=get_current_week(), key="pl_week_sb_v8"); pl_notes = st.text_area("备注 (可选):", key="pl_notes_sb_v8"); pl_submitted = st.form_submit_button("添加到歌单")
        if pl_submitted:
            if not pl_song_title: st.sidebar.error("歌曲标题不能为空！")
            else:
                new_pl_entry = {"id": get_next_id(weekly_playlists),"week_assigned": pl_week_val,"song_title": str(pl_song_title),"artist": pl_artist,"album": pl_album,"status": PLAYLIST_STATUS_OPTIONS[0],"notes": pl_notes,"date_added": datetime.date.today().isoformat()}
                weekly_playlists.append(new_pl_entry); save_json_data(WEEKLY_PLAYLIST_FILE, weekly_playlists); st.sidebar.success(f"歌曲 '{pl_song_title}' 已添加到歌单."); st.rerun()

with st.sidebar.expander("🏃 添加运动记录", expanded=False):
    with st.form("add_exercise_log_form_sidebar_v8", clear_on_submit=True): # Key updated
        st.subheader("运动详情"); ex_date_val = st.date_input("运动日期:", value=datetime.date.today(), key="ex_date_sb_v8"); ex_type_val = st.selectbox("运动类型:", options=EXERCISE_TYPES, key="ex_type_sb_v8"); ex_duration_intensity = st.text_input("时长/强度/距离等:", placeholder="例如: 跑步5公里/30分钟", key="ex_duration_sb_v8"); ex_notes = st.text_area("备注 (可选):", key="ex_notes_sb_v8"); ex_submitted = st.form_submit_button("添加运动记录")
        if ex_submitted:
            if not ex_duration_intensity: st.sidebar.error("时长/强度等信息不能为空！")
            else:
                new_ex_entry = {"id": get_next_id(weekly_exercise_logs),"date": ex_date_val.isoformat(),"exercise_type": ex_type_val,"duration_intensity": ex_duration_intensity,"status": EXERCISE_LOG_STATUS_OPTIONS[0],"notes": ex_notes,"date_added": datetime.date.today().isoformat()}
                weekly_exercise_logs.append(new_ex_entry); save_json_data(WEEKLY_EXERCISE_LOG_FILE, weekly_exercise_logs); st.sidebar.success(f"{ex_date_val.isoformat()} 的 {ex_type_val} 记录已添加."); st.rerun()

st.sidebar.markdown("---"); st.sidebar.caption(f"当前周: {get_current_week()}")
st.markdown("<h1 class='app-main-title'>🚀 个人生活与学习管理系统</h1>", unsafe_allow_html=True)

tab_titles = ["📄 学术文献", "📖 书籍与杂志", "✍️ 我的博客", "🎵 每周歌单", "🏃 每周运动", "📊 统计与概览"] # 新增 Tab
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tab_titles) # 新增 Tab

# ==========================
#      学术文献 Tab
# ==========================
with tab1:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[0]}</h2>", unsafe_allow_html=True)
    # ... (筛选器部分保持不变) ...
    st.markdown("<h3 class='filter-header'>筛选文献</h3>", unsafe_allow_html=True)
    filter_cols = st.columns(3)
    all_lit_weeks_set = set(entry.get('week_assigned') for entry in literature_list if entry.get('week_assigned') is not None)
    all_lit_weeks = sorted(list(all_lit_weeks_set))
    sel_lit_week = filter_cols[0].selectbox("按周筛选:", options=["所有"] + all_lit_weeks, key="sel_lit_week_t1_v8")
    sel_lit_status = filter_cols[1].selectbox("按状态筛选:", options=["所有"] + STATUS_OPTIONS, key="sel_lit_status_t1_v8")
    available_categories_set = set(cat for entry in literature_list for cat in entry.get('categories', []))
    available_categories = sorted(list(available_categories_set))
    sel_lit_category = filter_cols[2].selectbox("按分类筛选:", options=["所有"] + available_categories, key="sel_lit_cat_t1_v8")

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
            with st.expander(expander_label, expanded=False):
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
                    new_status = st.selectbox("状态", STATUS_OPTIONS, index=current_status_idx, key=f"lit_status_select_t1_v8_{entry['id']}", label_visibility="collapsed")
                    if new_status != entry.get('status'):
                        update_entry_field(literature_list, entry['id'], 'status', new_status, LITERATURE_DATA_FILE)
                        st.success(f"文献 '{title_display}' 状态更新."); st.rerun()
                    
                    st.markdown("---") # 分隔线
                    if st.button("🗑️ 删除", key=f"del_lit_t1_v8_{entry['id']}", help="删除此文献记录"):
                        if delete_entry_by_id(literature_list, entry['id'], LITERATURE_DATA_FILE):
                            st.rerun()
# ==========================
#      书籍与杂志 Tab
# ==========================
with tab2:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[1]}</h2>", unsafe_allow_html=True)
    # ... (筛选器部分保持不变) ...
    st.markdown("<h3 class='filter-header'>筛选条目</h3>", unsafe_allow_html=True)
    bm_filter_cols = st.columns(2)
    sel_bm_type = bm_filter_cols[0].selectbox("按类型筛选:", options=["所有"] + BOOK_MAGAZINE_TYPES, key="sel_bm_type_t2_v8")
    sel_bm_status = bm_filter_cols[1].selectbox("按状态筛选:", options=["所有"] + BOOK_STATUS_OPTIONS, key="sel_bm_status_t2_v8")
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
            with st.expander(expander_label, expanded=False):
                cols_bm_main, cols_bm_actions = st.columns([3,1])
                with cols_bm_main:
                    st.markdown(f"**ID:** `{entry.get('id', 'N/A')}`")
                    st.markdown(f"**添加日期:** {entry.get('date_added', 'N/A')}")
                    if entry.get('author_publisher'): st.markdown(f"**作者/出版社:** {entry.get('author_publisher')}")
                    if entry.get('type') == "杂志" and entry.get('issue_volume'): st.markdown(f"**期号/卷号:** {entry.get('issue_volume')}")
                    if entry.get('notes'):
                        with st.expander("查看备注/摘要", expanded=False): st.markdown(entry['notes'])
                with cols_bm_actions:
                    st.markdown("**更新状态:**")
                    current_bm_status_idx = BOOK_STATUS_OPTIONS.index(entry.get('status', BOOK_STATUS_OPTIONS[0]))
                    new_bm_status = st.selectbox("状态", BOOK_STATUS_OPTIONS, index=current_bm_status_idx, key=f"bm_status_select_t2_v8_{entry['id']}", label_visibility="collapsed")
                    if new_bm_status != entry.get('status'):
                        update_entry_field(books_magazines_list, entry['id'], 'status', new_bm_status, BOOKS_MAGAZINES_DATA_FILE)
                        st.success(f"条目 '{title_display}' 状态更新."); st.rerun()
                    if entry.get('type') == "书籍":
                        st.markdown("**更新进度:**")
                        current_progress = entry.get('progress', 0)
                        new_progress = st.slider("进度", 0, 100, current_progress, 5, key=f"bm_progress_slider_t2_v8_{entry['id']}", label_visibility="collapsed")
                        if new_progress != current_progress:
                            update_entry_field(books_magazines_list, entry['id'], 'progress', new_progress, BOOKS_MAGAZINES_DATA_FILE)
                            status_changed_by_progress = False
                            # 查找更新后的条目以检查状态
                            updated_entry_idx = next((idx for idx, item in enumerate(books_magazines_list) if item['id'] == entry['id']), None)
                            if updated_entry_idx is not None:
                                current_entry_status = books_magazines_list[updated_entry_idx]['status']
                                if new_progress == 100 and current_entry_status != "已读":
                                    update_entry_field(books_magazines_list, entry['id'], 'status', "已读", BOOKS_MAGAZINES_DATA_FILE)
                                    status_changed_by_progress = True; st.toast("书籍完成！🎉", icon="📚")
                                elif new_progress > 0 and new_progress < 100 and current_entry_status == "想读":
                                     update_entry_field(books_magazines_list, entry['id'], 'status', "在读", BOOKS_MAGAZINES_DATA_FILE)
                                     status_changed_by_progress = True; st.toast("开始阅读！🚀", icon="📖")
                            st.rerun()

                    st.markdown("---") # 分隔线
                    if st.button("🗑️ 删除", key=f"del_bm_t2_v8_{entry['id']}", help="删除此条目"):
                        if delete_entry_by_id(books_magazines_list, entry['id'], BOOKS_MAGAZINES_DATA_FILE):
                            st.rerun()

# ==========================
#      我的博客写作 Tab
# ==========================
with tab3:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[2]}</h2>", unsafe_allow_html=True)
    # ... (筛选器部分保持不变) ...
    st.markdown("<h3 class='filter-header'>筛选文章计划</h3>", unsafe_allow_html=True)
    post_filter_cols = st.columns(2); sel_post_status = post_filter_cols[0].selectbox("按状态筛选:", options=["所有"] + MY_BLOG_STATUS_OPTIONS, key="sel_post_status_t3_v8"); sel_post_priority = post_filter_cols[1].selectbox("按优先级筛选:", options=["所有"] + MY_BLOG_PRIORITY_OPTIONS, key="sel_post_priority_t3_v8")
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
            with st.expander(expander_header, expanded=False):
                cols_post_main, cols_post_actions = st.columns([3, 1])
                with cols_post_main:
                    st.markdown(f"**ID:** `{post.get('id', 'N/A')}`")
                    st.markdown(f"**主题/关键词:** {post.get('topic_keywords', 'N/A')}")
                    if post.get('outline_notes') or post.get('status') != "已发布": # 允许编辑笔记除非已发布
                        with st.expander("查看/编辑大纲/笔记", expanded=False):
                            current_outline_notes = post.get('outline_notes','')
                            new_outline_notes = st.text_area("大纲/笔记内容:", value=current_outline_notes, height=150, key=f"post_outline_area_t3_v8_{post['id']}")
                            if new_outline_notes != current_outline_notes:
                                if st.button("保存笔记", key=f"save_notes_blog_t3_v8_{post['id']}"): # 添加保存按钮
                                    update_entry_field(my_blog_posts_list, post['id'], 'outline_notes', new_outline_notes, MY_BLOG_POSTS_FILE)
                                    st.rerun()
                    if post.get('status') == "已发布":
                        if post.get('link_published'): st.markdown(f"**已发布链接:** [{post['link_published']}]({post['link_published']})")
                        else:
                            new_link = st.text_input("输入已发布链接:", key=f"post_link_input_t3_v8_{post['id']}")
                            if st.button("保存链接", key=f"post_save_link_btn_t3_v8_{post['id']}"):
                                if new_link:
                                    update_entry_field(my_blog_posts_list, post['id'], 'link_published', new_link, MY_BLOG_POSTS_FILE)
                                    st.rerun()
                        st.markdown(f"**发布日期:** {post.get('publish_date', 'N/A')}")
                    st.caption(f"添加日期: {post.get('date_added', 'N/A')}")
                with cols_post_actions:
                    st.markdown("**更新状态:**"); current_post_status_idx = MY_BLOG_STATUS_OPTIONS.index(post.get('status', MY_BLOG_STATUS_OPTIONS[0])); new_post_status = st.selectbox("状态", MY_BLOG_STATUS_OPTIONS, index=current_post_status_idx, key=f"post_status_select_t3_v8_{post['id']}", label_visibility="collapsed")
                    if new_post_status != post.get('status'):
                        update_entry_field(my_blog_posts_list, post['id'], 'status', new_post_status, MY_BLOG_POSTS_FILE)
                        if new_post_status == "已发布" and not post.get('publish_date'):
                            update_entry_field(my_blog_posts_list, post['id'], 'publish_date', datetime.date.today().isoformat(), MY_BLOG_POSTS_FILE)
                        st.rerun()

                    st.markdown("**更新优先级:**"); current_priority_idx = MY_BLOG_PRIORITY_OPTIONS.index(post.get('priority', MY_BLOG_PRIORITY_OPTIONS[1])); new_priority = st.selectbox("优先级", MY_BLOG_PRIORITY_OPTIONS, index=current_priority_idx, key=f"post_priority_select_t3_v8_{post['id']}", label_visibility="collapsed")
                    if new_priority != post.get('priority'):
                        update_entry_field(my_blog_posts_list, post['id'], 'priority', new_priority, MY_BLOG_POSTS_FILE); st.rerun()

                    st.markdown("**计划完成日期:**"); current_due_date_val = None;
                    if post.get('due_date'):
                        try: current_due_date_val = datetime.datetime.strptime(post['due_date'], "%Y-%m-%d").date()
                        except ValueError: current_due_date_val = None
                    new_due_date = st.date_input("日期", value=current_due_date_val, key=f"post_due_date_input_t3_v8_{post['id']}", label_visibility="collapsed"); new_due_date_str = new_due_date.isoformat() if new_due_date else None
                    if new_due_date_str != post.get('due_date'):
                        update_entry_field(my_blog_posts_list, post['id'], 'due_date', new_due_date_str, MY_BLOG_POSTS_FILE); st.rerun()
                    
                    st.markdown("---")
                    if st.button("🗑️ 删除", key=f"del_blog_t3_v8_{post['id']}", help="删除此博客计划"):
                        if delete_entry_by_id(my_blog_posts_list, post['id'], MY_BLOG_POSTS_FILE):
                            st.rerun()

# ==========================
#      每周歌单 Tab
# ==========================
with tab4:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[3]}</h2>", unsafe_allow_html=True)
    # ... (筛选器部分保持不变) ...
    st.markdown("<h3 class='filter-header'>筛选歌单</h3>", unsafe_allow_html=True)
    pl_filter_cols = st.columns(2); all_pl_weeks_set = set(entry.get('week_assigned', get_current_week()) for entry in weekly_playlists); all_pl_weeks = sorted(list(all_pl_weeks_set)); sel_pl_week = pl_filter_cols[0].selectbox("按周筛选:", options=["所有"] + all_pl_weeks, key="sel_pl_week_t4_v8"); sel_pl_status = pl_filter_cols[1].selectbox("按状态筛选:", options=["所有"] + PLAYLIST_STATUS_OPTIONS, key="sel_pl_status_t4_v8")
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
            with st.expander(expander_label, expanded=False):
                col1, col2 = st.columns([3,1]);
                with col1:
                    st.markdown(f"**ID:** `{song.get('id', 'N/A')}`")
                    if song.get('album'): st.markdown(f"**专辑:** {song.get('album')}")
                    if song.get('notes'): st.markdown(f"**备注:** {song.get('notes')}")
                    st.caption(f"添加日期: {song.get('date_added', 'N/A')}")
                with col2:
                    st.markdown("**更新状态:**")
                    current_pl_status_idx = PLAYLIST_STATUS_OPTIONS.index(song.get('status', PLAYLIST_STATUS_OPTIONS[0]))
                    new_pl_status = st.selectbox("状态", PLAYLIST_STATUS_OPTIONS, index=current_pl_status_idx, key=f"pl_status_select_t4_v8_{song['id']}", label_visibility="collapsed")
                    if new_pl_status != song.get('status'):
                        update_entry_field(weekly_playlists, song['id'], 'status', new_pl_status, WEEKLY_PLAYLIST_FILE)
                        st.success(f"歌曲 '{title_display}' 状态更新."); st.rerun()
                    
                    st.markdown("---")
                    if st.button("🗑️ 删除", key=f"del_pl_t4_v8_{song['id']}", help="从歌单删除此歌曲"):
                        if delete_entry_by_id(weekly_playlists, song['id'], WEEKLY_PLAYLIST_FILE):
                            st.rerun()

# ==========================
#      每周运动 Tab
# ==========================
with tab5:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[4]}</h2>", unsafe_allow_html=True)
    # ... (筛选器部分保持不变) ...
    st.markdown("<h3 class='filter-header'>筛选运动记录</h3>", unsafe_allow_html=True)
    ex_filter_cols = st.columns(3)
    ex_weeks_set = set(datetime.date.fromisoformat(e['date']).isocalendar()[1] for e in weekly_exercise_logs if e.get('date'))
    ex_weeks = sorted(list(ex_weeks_set), reverse=True)
    sel_ex_week = ex_filter_cols[0].selectbox("按周筛选:", options=["所有"] + ex_weeks, key="sel_ex_week_t5_v8")
    sel_ex_type = ex_filter_cols[1].selectbox("按运动类型筛选:", options=["所有"] + EXERCISE_TYPES, key="sel_ex_type_t5_v8")
    sel_ex_status = ex_filter_cols[2].selectbox("按状态筛选:", options=["所有"] + EXERCISE_LOG_STATUS_OPTIONS, key="sel_ex_status_t5_v8")
    filtered_exercise_logs = weekly_exercise_logs
    if sel_ex_week != "所有": filtered_exercise_logs = [log for log in filtered_exercise_logs if log.get('date') and datetime.date.fromisoformat(log['date']).isocalendar()[1] == sel_ex_week]
    if sel_ex_type != "所有": filtered_exercise_logs = [log for log in filtered_exercise_logs if log.get('exercise_type') == sel_ex_type]
    if sel_ex_status != "所有": filtered_exercise_logs = [log for log in filtered_exercise_logs if log.get('status') == sel_ex_status]

    if not filtered_exercise_logs: st.info("没有符合条件的运动记录。")
    else:
        st.markdown(f"共有 **{len(filtered_exercise_logs)}** 条运动记录。")
        for i, log_entry in enumerate(filtered_exercise_logs):
            log_date_str = log_entry.get('date', '未知日期')
            log_date_display = log_date_str
            try:
                log_date_obj = datetime.date.fromisoformat(log_date_str)
                day_of_week = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][log_date_obj.weekday()]
                log_date_display = f"{log_date_str} ({day_of_week})"
            except ValueError: pass
            type_display = str(log_entry.get('exercise_type', 'N/A'))
            status_display = str(log_entry.get('status', 'N/A'))
            expander_label = f"{log_date_display}: {type_display} - 状态: {status_display}"
            with st.expander(expander_label, expanded=False):
                col1, col2 = st.columns([3,1]);
                with col1:
                    st.markdown(f"**ID:** `{log_entry.get('id', 'N/A')}`")
                    st.markdown(f"**详情:** {log_entry.get('duration_intensity', 'N/A')}")
                    if log_entry.get('notes'): st.markdown(f"**备注:** {log_entry.get('notes')}")
                    st.caption(f"记录添加于: {log_entry.get('date_added', 'N/A')}")
                with col2:
                    st.markdown("**更新状态:**")
                    current_ex_status_idx = EXERCISE_LOG_STATUS_OPTIONS.index(log_entry.get('status', EXERCISE_LOG_STATUS_OPTIONS[0]))
                    new_ex_status = st.selectbox("状态", EXERCISE_LOG_STATUS_OPTIONS, index=current_ex_status_idx, key=f"ex_status_select_t5_v8_{log_entry['id']}", label_visibility="collapsed")
                    if new_ex_status != log_entry.get('status'):
                        update_entry_field(weekly_exercise_logs, log_entry['id'], 'status', new_ex_status, WEEKLY_EXERCISE_LOG_FILE)
                        st.success(f"运动记录状态更新."); st.rerun()
                    
                    st.markdown("---")
                    if st.button("🗑️ 删除", key=f"del_ex_t5_v8_{log_entry['id']}", help="删除此运动记录"):
                        if delete_entry_by_id(weekly_exercise_logs, log_entry['id'], WEEKLY_EXERCISE_LOG_FILE):
                            st.rerun()

# ==========================
#      统计与概览 Tab
# ==========================
with tab6:
    st.markdown(f"<h2 class='tab-header'>{tab_titles[5]}</h2>", unsafe_allow_html=True)

    # --- 学术文献统计 ---
    st.markdown("<h3 class='stats-subheader'>学术文献统计</h3>", unsafe_allow_html=True)
    if not literature_list:
        st.info("暂无学术文献数据。")
    else:
        df_lit = pd.DataFrame(literature_list)
        col_lit1, col_lit2 = st.columns(2)
        with col_lit1:
            st.metric("文献总数", len(df_lit))
            status_counts_lit = df_lit['status'].value_counts()
            fig_lit_status = px.pie(status_counts_lit, values=status_counts_lit.values, names=status_counts_lit.index, title="文献状态分布")
            st.plotly_chart(fig_lit_status, use_container_width=True)
        with col_lit2:
            if 'categories' in df_lit.columns and not df_lit['categories'].empty:
                # 处理列表类型的 categories
                df_lit_categories_exploded = df_lit.explode('categories')
                category_counts = df_lit_categories_exploded['categories'].value_counts()
                if not category_counts.empty:
                    fig_lit_cat = px.bar(category_counts, x=category_counts.index, y=category_counts.values, title="文献分类统计", labels={'x':'分类', 'y':'数量'})
                    st.plotly_chart(fig_lit_cat, use_container_width=True)
                else:
                    st.caption("无分类数据")
            else:
                st.caption("无分类数据")


    # --- 书籍与杂志统计 ---
    st.markdown("<h3 class='stats-subheader'>书籍与杂志统计</h3>", unsafe_allow_html=True)
    if not books_magazines_list:
        st.info("暂无书籍与杂志数据。")
    else:
        df_bm = pd.DataFrame(books_magazines_list)
        col_bm1, col_bm2 = st.columns(2)
        with col_bm1:
            st.metric("条目总数", len(df_bm))
            type_counts_bm = df_bm['type'].value_counts()
            fig_bm_type = px.pie(type_counts_bm, values=type_counts_bm.values, names=type_counts_bm.index, title="书籍/杂志类型分布")
            st.plotly_chart(fig_bm_type, use_container_width=True)
        with col_bm2:
            df_books_only = df_bm[df_bm['type'] == '书籍']
            if not df_books_only.empty:
                status_counts_books = df_books_only['status'].value_counts()
                fig_books_status = px.bar(status_counts_books, x=status_counts_books.index, y=status_counts_books.values, title="书籍阅读状态", labels={'x':'状态', 'y':'数量'})
                st.plotly_chart(fig_books_status, use_container_width=True)
            else:
                st.caption("无书籍数据进行状态统计")


    # --- 我的博客统计 ---
    st.markdown("<h3 class='stats-subheader'>我的博客统计</h3>", unsafe_allow_html=True)
    if not my_blog_posts_list:
        st.info("暂无博客文章计划数据。")
    else:
        df_blog = pd.DataFrame(my_blog_posts_list)
        col_blog1, col_blog2 = st.columns(2)
        with col_blog1:
            st.metric("博客计划总数", len(df_blog))
            status_counts_blog = df_blog['status'].value_counts()
            fig_blog_status = px.pie(status_counts_blog, values=status_counts_blog.values, names=status_counts_blog.index, title="博客文章状态分布")
            st.plotly_chart(fig_blog_status, use_container_width=True)
        with col_blog2:
            priority_counts_blog = df_blog['priority'].value_counts()
            fig_blog_prio = px.bar(priority_counts_blog, x=priority_counts_blog.index, y=priority_counts_blog.values, title="博客文章优先级分布", labels={'x':'优先级', 'y':'数量'})
            st.plotly_chart(fig_blog_prio, use_container_width=True)


    # --- 每周歌单统计 ---
    st.markdown("<h3 class='stats-subheader'>每周歌单统计</h3>", unsafe_allow_html=True)
    if not weekly_playlists:
        st.info("暂无歌单数据。")
    else:
        df_pl = pd.DataFrame(weekly_playlists)
        col_pl1, col_pl2 = st.columns(2)
        with col_pl1:
            st.metric("歌单歌曲总数", len(df_pl))
            status_counts_pl = df_pl['status'].value_counts()
            fig_pl_status = px.pie(status_counts_pl, values=status_counts_pl.values, names=status_counts_pl.index, title="歌曲状态分布")
            st.plotly_chart(fig_pl_status, use_container_width=True)
        with col_pl2:
            # 歌曲数量按周统计 (如果周数较多，条形图可能更好)
            if 'week_assigned' in df_pl.columns:
                week_counts_pl = df_pl['week_assigned'].value_counts().sort_index()
                if not week_counts_pl.empty:
                    fig_pl_week = px.bar(week_counts_pl, x=week_counts_pl.index, y=week_counts_pl.values, title="每周计划歌曲数", labels={'x':'周数', 'y':'歌曲数'})
                    st.plotly_chart(fig_pl_week, use_container_width=True)
                else:
                    st.caption("无周分配数据")
            else:
                st.caption("无周分配数据")


    # --- 每周运动统计 ---
    st.markdown("<h3 class='stats-subheader'>每周运动统计</h3>", unsafe_allow_html=True)
    if not weekly_exercise_logs:
        st.info("暂无运动记录数据。")
    else:
        df_ex = pd.DataFrame(weekly_exercise_logs)
        col_ex1, col_ex2 = st.columns(2)

        with col_ex1:
            st.metric("运动记录总数", len(df_ex))
            type_counts_ex = df_ex['exercise_type'].value_counts()
            fig_ex_type = px.bar(type_counts_ex, y=type_counts_ex.index, x=type_counts_ex.values, orientation='h', title="运动类型统计", labels={'y':'类型', 'x':'次数'})
            fig_ex_type.update_layout(yaxis={'categoryorder':'total ascending'}) # 按次数排序
            st.plotly_chart(fig_ex_type, use_container_width=True)
        with col_ex2:
            status_counts_ex = df_ex['status'].value_counts()
            fig_ex_status = px.pie(status_counts_ex, values=status_counts_ex.values, names=status_counts_ex.index, title="运动记录状态分布")
            st.plotly_chart(fig_ex_status, use_container_width=True)

        # 运动次数按周统计
        if 'date' in df_ex.columns:
            try:
                df_ex['parsed_date'] = pd.to_datetime(df_ex['date'], errors='coerce')
                df_ex_valid_dates = df_ex.dropna(subset=['parsed_date'])
                if not df_ex_valid_dates.empty:
                    df_ex_valid_dates['week_of_year'] = df_ex_valid_dates['parsed_date'].dt.isocalendar().week
                    exercise_freq_weekly = df_ex_valid_dates['week_of_year'].value_counts().sort_index()
                    fig_ex_freq = px.line(exercise_freq_weekly, x=exercise_freq_weekly.index, y=exercise_freq_weekly.values, title="每周运动次数", markers=True, labels={'x':'周数', 'y':'次数'})
                    st.plotly_chart(fig_ex_freq, use_container_width=True)
                else:
                    st.caption("无有效日期进行周统计")
            except Exception as e:
                st.caption(f"处理运动日期时出错: {e}")
