import streamlit as st
from database_final import init_db, insert_page, get_all_pages, migrate_from_json
from search_final import search_fulltext
from crawler_final import crawl_url
from ranking_final import get_engine, rebuild_index 

init_db()

st.set_page_config(page_title='Tech0 Search V1.0', page_icon="🔍", layout="wide")
st.title('🔍Tech0 Search')
st.caption('PROJECT ZERO - 社内ナレッジ検索エンジン')

@st.cache_resource
def load_and_index():
    pages = get_all_pages()
    if pages:
        rebuild_index(pages)
    return pages

pages = load_and_index
engine = get_engine

with st.sidebar:
    st.header("DB の状態")

    if st.session_state.get("migrated") is not None:
        st.success(f"{st.session_state['migrated']} 件を DB に移行しました")
        st.session_state["migrated"] = None
    pages = get_all_pages()
    st.metric("登録ページ数", f"{len(pages)} 件")
    if st.button(" pages_w2.json から DB へ移行"):
        n = migrate_from_json("pages_w2.json")
        st.session_state["migrated"] = n
        st.rerun()

tab1, tab2, tab3 = st.tabs(['検索', 'クロール', '一覧'])

with tab1:
    st.subheader("🔍 全文検索（本文まで探す）")
    query = st.text_input("🔑 キーワードを入力")
    if query:
        pages = get_all_pages()
        results = search_fulltext(query, pages)
       
        st.markdown(f"**検索結果: {len(results)}件**")
        st.divider()
        for r in results:
            st.markdown(f"### [{r['title']}]({r['url']})")
            st.markdown(f"🔢 マッチ数: **{r['match_count']}** 回")
            if r.get("preview"):
                st.caption(r["preview"])
            st.divider()

with tab2:
    st.subheader("🤖 クロールして DB に登録")
    url_input = st.text_input("クロールしたいURL")
    if st.button("🤖 クロール実行"):
        if url_input:
            with st.spinner(f"クロール中: {url_input}"):
                result = crawl_url(url_input)
            if result.get("crawl_status") == "success":
                insert_page(result)
                st.success(f"✅ DB に登録: {result['title']} ({result['word_count']} 語) ")
            else:
                st.error(f"✖ 取得失敗: {result.get('error')}")

    st.divider()
    st.markdown("**一括クロール**（URLを改行区切りで入力）")
    urls_text = st.text_area("URLリスト", height=120)
    if st.button("🕵 一括クロール実行"):
        urls = [u.strip() for u in urls_text.splitlines() if u.strip().startswith("http")]
        ok = 0
        for u in urls:
            with st.spinner(f"クロール中: {u}"):
                result = crawl_url(u)
            if result.get("crawl_status") == "success":
                insert_page(result)
                ok += 1
            st.info(f"{ok} / {len(urls)} 件を DB に登録しました")

with tab3:
    pages = get_all_pages()
    st.subheader(f"📚 DB 登録済みページ一覧 ({len(pages)}件) ")
    for page in pages:
        with st.expander(f"📄 {page['title']}"):
            st.markdown(page.get("description", "") or "（説明なし）")
            st.caption(f"👤 {page.get('author') or '不明'} 📊 {page.get('word_count', 0)} 語")
            st.caption(f"🔗 {page['url']}")
