import streamlit as st
import plotly.express as px
import pandas as pd
import redshift_connector
import requests

# secrets.toml에서 Redshift 연결 정보 불러오기
REDSHIFT_HOST = st.secrets["redshift"]["host"]
REDSHIFT_PORT = st.secrets["redshift"]["port"]
REDSHIFT_DATABASE = st.secrets["redshift"]["database"]
REDSHIFT_USER = st.secrets["redshift"]["user"]
REDSHIFT_PASSWORD = st.secrets["redshift"]["password"]

###################################################
@st.cache_resource
def connect_to_redshift():
    try:
        conn = redshift_connector.connect(
            host=REDSHIFT_HOST,
            database=REDSHIFT_DATABASE,
            user=REDSHIFT_USER,
            password=REDSHIFT_PASSWORD,
            port=int(REDSHIFT_PORT)
        )
        return conn
    except Exception as e:
        st.error(f"Redshift 연결 오류: {e}")
        return None
        
######################################################
@st.cache_data
def run_query(query):
    conn = connect_to_redshift()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            st.error(f"쿼리 실행 오류: {e}")
            return None
    return None
    
##########################################################################
# 숫자 변환
def format_korean_unit(value: float, mode: str = "all") -> str:
    """
    value: 변환할 숫자 값
    mode: "jo"  -> 조 단위만 표시 (예: 123조)
        "eok" -> 조와 억 단위 표시 (예: 123조 4,567억)
        "all" -> 조, 억, 만 단위 모두 표시 (예: 123조 4,567억 890만)
    """
    value = int(value)
    jo = value // 10**12
    remainder = value % 10**12
    eok = remainder // 10**8
    remainder = remainder % 10**8
    man = remainder // 10**4

    if mode == "jo":
        return f"{jo:,}조" if jo > 0 else "0조"
    elif mode == "eok":
        parts = []
        if jo > 0:
            parts.append(f"{jo}조")
        if eok > 0:
            parts.append(f"{eok:,}억")
        return " ".join(parts) if parts else "0억"
    else:  # mode == "all"
        parts = []
        if jo > 0:
            parts.append(f"{jo}조")
        if eok > 0:
            parts.append(f"{eok:,}억")
        if man > 0:
            parts.append(f"{man:,}만")
        return " ".join(parts) if parts else "0"
    
# 이미지 없는 경우
default_image_url = "https://clipart-library.com/new_gallery/131-1313837_transparent-white-silhouette-png.png"
# 이미지가 존재하는지 확인하는 함수
def check_image_exists(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except Exception as e:
        return False
##########################################################################

# 페이지 주소 설정
st.set_page_config(
    page_title="FC온라인 대시보드", # 웹페이지 주소 이름
    layout="wide",
)

# 현재 URL에서 Query Parameter 가져오기 (기본값: main)
query_params = st.query_params
page = query_params.get("page", "main")  

# 버튼 클릭 시 URL 변경 후 페이지 전환하는 함수
def change_page(new_page):
    st.query_params["page"] = new_page  # URL Query Parameter 업데이트
    st.rerun()  # 페이지 즉시 업데이트

##########################################################################
##### 사이드바 설정 #####
# 1. 검색
# 2. 공식경기등급
# 3. 선수 포지션

# 1. 검색
st.sidebar.title("🔍 검색")
search_option = st.sidebar.radio("검색 유형을 선택하세요", ["랭커 검색"]) #필요할경우 선수검색 추가

if search_option == "랭커 검색":
    ranker_name = st.sidebar.text_input("랭커 이름을 입력하세요:")
    if ranker_name and st.sidebar.button("검색"):
        change_page(f"ranker_{ranker_name}")

#elif search_option == "선수 검색":
#    player_name = st.sidebar.text_input("선수 이름을 입력하세요:")
#    if player_name and st.sidebar.button("검색"):
#        change_page(f"player_{player_name}")

# 2. 공식경기 등급
st.sidebar.title("공식 경기 등급")
if st.sidebar.button("슈퍼 챔피언스"):
    change_page("super_champions")
if st.sidebar.button("챔피언스"):
    change_page("champions")
# if st.sidebar.button("슈퍼챌린저"):
#     change_page("superchallengers")
# if st.sidebar.button("챌린저"):
#     change_page("challengers")
# if st.sidebar.button("월드클래스"):
#     change_page("worldclass")

# 3. 선수 포지션
st.sidebar.title("⚽ 선수 포지션")
if st.sidebar.button("FW"):
    change_page("fw")
if st.sidebar.button("MF"):
    change_page("mf")
if st.sidebar.button("DF"):
    change_page("df")
if st.sidebar.button("GK"):
    change_page("gk")
    
# st.sidebar.title("메인 페이지로")
# if st.sidebar.button("메인 페이지"):
#     change_page("main")
##########################################################################

# 메인 페이지 (기본 화면)와 등급별 페이지의 공통 내용을 위한 함수
def main_page():
    st.title("FC온라인 대시보드 🚀")
    
    if st.button("데이터 새로고침"):
        st.cache_data.clear()  
        st.rerun()
    
    
    # 우상단 업데이트 날짜
    query_update = "SELECT MAX(created_at) AS last_update FROM analytics.ranking_info;"
    df_update = run_query(query_update)
    last_update = df_update.loc[0, "last_update"] if not df_update.empty else "정보 없음"
    
    formatted_date = f"{last_update.year}년 {last_update.month}월 {last_update.day}일"
    
    st.markdown(
    f"<div style='text-align: right; font-size:24px;'>데이터 업데이트:{formatted_date}</div>", unsafe_allow_html=True)
    
    st.header("TOP 1000 랭커")
    
    ##########################################################################
    # # 카드 4개: 평균 승률, 평균 구단가치, 인기 팀컬러, 평균 강화레벨
    # 1) 평균 승률
    query_avg_win = "SELECT AVG(winning_rate) AS avg_winning_rate FROM analytics.ranking_info;"
    df_avg_win = run_query(query_avg_win)
    avg_winning_rate = df_avg_win.loc[0, "avg_winning_rate"] if not df_avg_win.empty else 0
    
    # 2) 평균 구단가치
    query_avg_worth = "SELECT AVG(team_worth) AS avg_team_worth FROM analytics.ranking_info;"
    df_avg_worth = run_query(query_avg_worth)
    avg_team_worth = df_avg_worth.loc[0, "avg_team_worth"] if not df_avg_worth.empty else 0
    
    # 3) 인기 팀컬러
    query_team_color = """
    SELECT team_color
    FROM analytics.team_color_info
    GROUP BY team_color
    ORDER BY COUNT(*) DESC
    LIMIT 1;
    """
    df_team_color = run_query(query_team_color)
    popular_team_color = df_team_color.loc[0, "team_color"] if not df_team_color.empty else "정보 없음"
    
    # 4) 평균 강화 레벨
    query_avg_enhance = "SELECT AVG(spgrade) AS avg_enhance_level FROM analytics.match_info;"
    df_avg_enhance = run_query(query_avg_enhance)
    avg_enhance_level = df_avg_enhance.loc[0, "avg_enhance_level"] if not df_avg_enhance.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("평균 승률", f"{avg_winning_rate:.1f}%")
    col2.metric("평균 구단가치", f"{format_korean_unit(avg_team_worth, mode='eok')}")
    col3.metric("인기 팀컬러", popular_team_color)
    col4.metric("평균 강화레벨", f"{avg_enhance_level}")
    
    st.markdown("---")
    
    ##########################################################################
    # --- 오늘의 인기선수 순위 10명 ---
    st.header("오늘의 인기 선수 TOP 10")
    
    top10_query = """
    WITH top_players AS (
        SELECT 
            spid, 
            COUNT(*) AS usage_count, 
            LEFT(spid, 3) AS season_id
        FROM analytics.match_info
        GROUP BY spid
        ORDER BY usage_count DESC
        LIMIT 10
    )
    SELECT 
        p.name,
        tp.usage_count,
        tp.spid AS spid,
        si.image_url AS season_img_url,
        CASE 
            WHEN COUNT(CASE WHEN pri.prediction = 1 THEN 1 END) = 0 THEN '후기 없음'
            WHEN COUNT(CASE WHEN pri.prediction = 1 THEN 1 END) >= COUNT(CASE WHEN pri.prediction = 0 THEN 1 END) THEN '긍정'
            ELSE '부정'
        END AS emotion_analysis
    FROM top_players tp
    JOIN analytics.player_info p ON tp.spid = p.spid
    LEFT JOIN analytics.player_image_info pii ON tp.spid = pii.spid
    LEFT JOIN analytics.season_info si ON tp.season_id = si.season_id
    LEFT JOIN analytics.player_review_info pri ON tp.spid = pri.spid
    GROUP BY p.name, tp.spid, tp.usage_count, pii.url, si.image_url
    ORDER BY tp.usage_count DESC;
    """
    
    top10_player = run_query(top10_query)
    
    popular_players = top10_player.to_dict('records') # 쿼리 결과를 딕셔너리 리스트로 변환
    
    if "toggle_details" not in st.session_state:
        st.session_state.toggle_details = {}
        
    # 5열씩 2행 배치 (예시)
    num_cols = 5
    rows = [popular_players[i : i + num_cols] for i in range(0, len(popular_players), num_cols)]
    
    for row in rows:
        cols = st.columns(num_cols)
        for idx, player in enumerate(row):
            with cols[idx]:
                # 선수 이미지 URL 포매팅: spid를 이용해 생성
                player_image_url = f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{player['spid']}.png"
                if not check_image_exists(player_image_url):
                    player_image_url = default_image_url
                st.image(player_image_url,width=100)
                
                # 토글 상태 초기화
                if player["name"] not in st.session_state.toggle_details:
                    st.session_state.toggle_details[player["name"]] = False


                # 버튼 클릭 시 상태 토글 (선수 이름 버튼)
                if st.button(player["name"], key=f"btn_{player['name']}"):
                    st.session_state.toggle_details[player["name"]] = not st.session_state.toggle_details[player["name"]]
                
                # 토글 상태가 True이면 상세 정보 표시:
                if st.session_state.toggle_details[player["name"]]:
                    season_img = player.get('season_img_url')
                    
                    st.markdown(f"""
                        <div style='display: flex; align-items: center; gap: 5px;'>
                            <img src="{season_img}" width="50"/>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.write('')
                    
                    st.write(f"**{player['usage_count']}명의 랭커가 사용하고 있어요**")
                    
                    # 감정분석 결과를 멘트로 변환해서 출력
                    emotion_analysis = player['emotion_analysis']

                    if emotion_analysis == '긍정':
                        message = "😃 감독들에게 평가가 좋아요!"
                    elif emotion_analysis == '부정':
                        message = "😞 평가가 좋지는 않네요.."
                    else:
                        message = "📢 후기가 없어요."
                    
                    st.write(f"**{message}**")
                    
    st.markdown("---")


    ##########################################################################
    # 등급별 구단 가치, 등급별 강화 레벨 수준, 포지션별 평균 강화 레벨
    category_order = [
    "슈퍼챔피언스", "챔피언스", "슈퍼챌린저",
    "챌린저 1부", "챌린저 2부", "챌린저 3부",
    "월드클래스 1부", "월드클래스 2부", "월드클래스 3부"
    ]
    
    rename_map = {
    "슈퍼챌린지": "슈퍼챌린저",
    "챌린지1": "챌린저 1부",
    "챌린지2": "챌린저 2부",
    "챌린지3": "챌린저 3부",
    "월드클래스1": "월드클래스 1부",
    "월드클래스2": "월드클래스 2부",
    "월드클래스3": "월드클래스 3부"
    }
        
    # 1. 등급별 구단 가치
    query_team_value = """
    SELECT 
        d.division_name AS 등급,
        AVG(r.team_worth) AS "평균 팀 가치"
    FROM analytics.ranking_info r
    JOIN analytics.division_info d ON r.division_id = d.division_id
    GROUP BY d.division_name
    ORDER BY d.division_name;
    """

    df_team_value = run_query(query_team_value)
    df_team_value["등급"] = df_team_value["등급"].replace(rename_map)
    df_team_value["구단가치"] = df_team_value["평균 팀 가치"].apply(lambda x: format_korean_unit(x, mode='jo'))
    
    
    fig_team_value = (
    px.bar(
        df_team_value,
        x="등급",
        y="평균 팀 가치",       
        text="구단가치",
        category_orders={"등급": category_order},
        color="등급",
        title="등급별 평균 구단 가치",
        color_discrete_sequence = px.colors.qualitative.T10
    )
    .update_traces(
        textposition="inside",
        width = 0.8,
        textfont_size=20)
    .update_layout(
        title={'font': {'size': 25}},
        plot_bgcolor="black",
        paper_bgcolor="black",
        font_color="white",
        xaxis=dict(showgrid=False, color="white"),
        yaxis=dict(showgrid=False, color="white", tickfont=dict(size=20)),
        showlegend=False,
        bargap=0.2,
        bargroupgap=0.1,
        xaxis_title="등급",
        yaxis_title="평균 구단 가치"
    )
    )

    # 2. 등급별 강화레벨 수준
    query_avg_grade = """
    SELECT 
        d.division_name AS 등급,
        COALESCE(AVG(mi.spgrade), 0) AS "평균 강화 레벨"
    FROM analytics.division_info d
    JOIN analytics.ranking_info r 
        ON d.division_id = r.division_id
    LEFT JOIN analytics.match_info mi 
        ON r.gamer_nickname = mi.gamer_nickname
    GROUP BY d.division_name
    ORDER BY d.division_name;
    """
    
    df_grade = run_query(query_avg_grade)
    df_grade["등급"] = df_grade["등급"].replace(rename_map)
    # "평균 강화 레벨"이 0인 행은 제거
    df_grade = df_grade[df_grade["평균 강화 레벨"] != 0]
    
    fig_grade = (
    px.bar(
        df_grade,
        x="등급",
        y="평균 강화 레벨",
        text = "평균 강화 레벨",
        category_orders={"등급": category_order},
        color="등급",
        title="등급별 평균 강화 레벨",
        color_discrete_sequence=px.colors.qualitative.T10
    )
    .update_traces(
        textposition="inside",
        width=0.7,
        textfont_size=20
    )
    .update_layout(
        title={'font': {'size': 25}},
        plot_bgcolor="black",
        paper_bgcolor="black",
        font_color="white",
        xaxis=dict(showgrid=False, color="white"),
        yaxis=dict(showgrid=False, color="white", tickfont=dict(size=20)),
        showlegend=False,
        bargap=0.2,
        bargroupgap=0.1,
        xaxis_title="등급",
        yaxis_title="평균 강화 레벨"
    )
    )

        
    ##########################################################################
    # 3. 포지션별 강화 레벨 
    query_avg_position = """
    SELECT 
        position_cat AS 포지션,
        AVG(spgrade) AS "평균 강화 레벨"
    FROM (
        SELECT 
            spgrade,
            CASE
                WHEN "position" IN (1,2,3,4,5,6,7,8) THEN 'DF'
                WHEN "position" IN (20,21,22,23,24,25,26,27) THEN 'FW'
                WHEN "position" = 0 THEN 'GK'
                WHEN "position" = 28 THEN 'SUB'
                ELSE 'MF'
            END AS position_cat
        FROM analytics.match_info
    ) t
    GROUP BY position_cat
    ORDER BY position_cat;
    """
    
    df_position = run_query(query_avg_position)
    position_order = ["FW", "MF", "DF", "GK", "SUB"]

    fig_position = (
        px.bar(
        df_position,
        x="포지션",
        y="평균 강화 레벨",
        text="평균 강화 레벨",
        category_orders={"포지션": position_order},
        title="포지션별 평균 강화 레벨 수준",
        color="포지션",
        color_discrete_sequence=px.colors.qualitative.T10
    )
    .update_xaxes(
        tickfont=dict(size=25)
    )
    .update_traces(
        textposition="inside",
        width=0.7,
        textfont_size=20)
        .update_layout(
        title={'font': {'size': 25}},
        plot_bgcolor="black",
        paper_bgcolor="black",
        font_color="white",
        xaxis=dict(showgrid=False, color="white", tickfont=dict(size=20)),
        yaxis=dict(showgrid=False, color="white", tickfont=dict(size=20)),
        showlegend=False,
        bargap=0.2,
        bargroupgap=0.1,
        xaxis_title="포지션",
        yaxis_title="평균 강화 레벨"
        )
    )

    # # 4. 게이머 레벨 분포
    # query_gamer_level = """
    # SELECT gamer_level AS "레벨"
    # FROM analytics.ranking_info;
    # """
    
    # df_levels = run_query(query_gamer_level)
    # fig_violin = (
    # px.violin(
    #     df_levels,
    #     y="레벨",
    #     box=True,        # 박스플롯 요소 포함 (중앙값, 사분위수)
    #     points="all",
    #     hover_data=df_levels.columns,
    #     title="감독 레벨 분포",
    #     color_discrete_sequence = ['#4ECDC4']
    # )
    # .update_layout(
    #     plot_bgcolor="black",
    #     paper_bgcolor="black",
    #     font_color="white",
    #     title={'font': {'size': 25}},
    #     xaxis=dict(showgrid=False, color="white", tickfont=dict(size=20)),
    #     yaxis=dict(showgrid=True, color="white", tickfont=dict(size=20))
    # )
    # )
    

    
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_position, use_container_width=True) 

    with col2:
        st.plotly_chart(fig_grade, use_container_width=True)
        
    st.plotly_chart(fig_team_value, use_container_width=True)
    
##########################################################################
# 등급별 페이지
def grade_page(grade_key: str):
    grade_name_map = {
    "super_champions": "슈퍼챔피언스",
    "champions": "챔피언스",
    "superchallengers": "슈퍼챌린저",
    "challengers": "챌린저",
    "worldclass": "월드클래스"
    }
    grade_name = grade_name_map.get(grade_key, None)
    st.title(f"⚽ {grade_name} TOP 10 랭커 정보")

    # 1. 랭커 정보
    query_ranker_info = """
    WITH team_color_summary AS (
        SELECT
            gamer_nickname,
            MIN(team_color) AS team_color
        FROM analytics.team_color_info
        GROUP BY gamer_nickname
    ),
    ranked_players AS (
        SELECT
            r.division_id,
            r.ranking AS 순위,
            r.gamer_nickname AS 닉네임,
            r.team_worth AS 팀_가치,
            r.winning_rate AS 승률,
            r.total_win AS 승,
            r.total_draw  AS 무,
            r.total_lose  AS 패,
            tc.team_color AS 팀컬러,
            r.formation AS 포메이션,
            ROW_NUMBER() OVER (
                PARTITION BY r.division_id
                ORDER BY r.ranking ASC
            ) AS rn
        FROM (
            SELECT DISTINCT gamer_nickname, ranking, division_id, team_worth, winning_rate, total_win, total_draw, total_lose, formation
            FROM analytics.ranking_info
        ) r
        JOIN analytics.division_info d
            ON r.division_id = d.division_id
        LEFT JOIN team_color_summary tc
            ON r.gamer_nickname = tc.gamer_nickname
    )
    SELECT
        d.division_name AS 등급,
        p.순위,
        p.닉네임,
        p.팀_가치,
        p.승률,
        p.승,
        p.무,
        p.패,
        p.팀컬러,
        p.포메이션
    FROM ranked_players p
    JOIN analytics.division_info d
        ON p.division_id = d.division_id
    WHERE p.division_id IN (0, 1, 2, 3, 6)
    AND p.rn <= 10
    ORDER BY d.division_name, p.순위;
    """

    df_rankers = run_query(query_ranker_info)
    rename_map = {
    "슈퍼챌린지": "슈퍼챌린저",
    "챌린지1": "챌린저",
    "월드클래스1": "월드클래스",
    }

    df_rankers["등급"] = df_rankers["등급"].replace(rename_map)
    df_rankers["팀 가치"] = df_rankers["팀_가치"].astype(float).apply(lambda x: format_korean_unit(x, mode='eok'))
    
    grade_df = df_rankers[df_rankers["등급"] == grade_name]
    
    display_df = grade_df[["닉네임", "팀 가치", "팀컬러", "포메이션", "승률", "승", "무", "패" ]]
    display_df["승률"] = display_df["승률"].astype(float)
    display_df = display_df.reset_index(drop=True)
    display_df.index = display_df.index + 1
    styled_df = display_df.style \
        .format({
            "승률": lambda x: f"{float(x):.2f}%"
        }) \
        .set_table_styles([
            {
                'selector': 'th',
                'props': [
                    ('font-size', '50px'),
                    ('text-align', 'center'),
                    ('background-color', '#333'),
                    ('color', 'white')
                ]
            },
            {
                'selector': 'td',
                'props': [
                    ('font-size', '22px'),
                    ('text-align', 'center')
                ]
            }
        ])

    st.table(styled_df)

    # 2) 인기 선수
    st.subheader(f"{grade_name} 인기 선수 Top10")
    rename_map = {
        "슈퍼챌린지": "슈퍼챌린저",
        "챌린지1": "챌린저",
        "챌린지2": "챌린저",
        "챌린지3": "챌린저",
        "월드클래스1": "월드클래스",
        "월드클래스2": "월드클래스",
        "월드클래스3": "월드클래스"
    }
    
    query_division_top10_players = """
    WITH usage_count AS (
        SELECT
            d.division_name AS 등급,
            mi.spid,
            COUNT(mi.spid) AS usage_count
        FROM analytics.match_info mi
        JOIN analytics.ranking_info r
            ON mi.gamer_nickname = r.gamer_nickname
        JOIN analytics.division_info d
            ON r.division_id = d.division_id
        GROUP BY d.division_name, mi.spid
    ),
    ranked_players AS (
        SELECT
            등급,
            spid,
            usage_count,
            ROW_NUMBER() OVER (PARTITION BY 등급 ORDER BY usage_count DESC) AS rn
        FROM usage_count
    )
    SELECT
        rp.등급,
        p.name AS 선수이름,
        rp.spid,
        rp.usage_count,
        s.image_url AS season_img_url,
        CASE 
            WHEN COUNT(CASE WHEN pri.prediction = 1 THEN 1 END) = 0 THEN '후기 없음'
            WHEN COUNT(CASE WHEN pri.prediction = 1 THEN 1 END) >= COUNT(CASE WHEN pri.prediction = 0 THEN 1 END) THEN '긍정'
            ELSE '부정'
        END AS emotion_analysis
    FROM ranked_players rp
    JOIN analytics.player_info p
        ON rp.spid = p.spid
    LEFT JOIN analytics.season_info s
        ON LEFT(rp.spid, 3) = s.season_id
    LEFT JOIN analytics.player_review_info pri
        ON rp.spid = pri.spid
    WHERE rp.rn <= 10
    GROUP BY rp.등급, p.name, rp.spid, rp.usage_count, s.image_url
    ORDER BY rp.등급, rp.usage_count DESC;
    """

    df_popular_players = run_query(query_division_top10_players)
    df_popular_players["등급"] = df_popular_players["등급"].replace(rename_map)
    
    df_filtered = df_popular_players[df_popular_players["등급"] == grade_name]
    if df_filtered.empty:
        st.warning(f"{grade_name} 인기 선수 데이터가 없습니다.")
        return

    if "selected_player" not in st.session_state:
        st.session_state.selected_player = None

    col1, col2 = st.columns([1, 2])
    with col1:
        for player, spid in zip(df_filtered["선수이름"], df_filtered["spid"]):
            if st.button(player, key=spid):
                st.session_state.selected_player = spid

    with col2:
        if st.session_state.selected_player:
            player_info = df_filtered[df_filtered["spid"] == st.session_state.selected_player]
            if not player_info.empty:
                player_info = player_info.iloc[0]

                emotion_analysis = player_info['emotion_analysis']
                if emotion_analysis == '긍정':
                    message = "😃 이 선수는 감독들에게 평가가 좋아요!"
                elif emotion_analysis == '부정':
                    message = "😞 이 선수의 평가가 좋지는 않네요.."
                else:
                    message = "📢 이 선수의 후기가 없어요. 첫 번째 후기를 남겨주세요"
                
                
                
                with st.expander(f"📌 {player_info['선수이름']} 상세 정보", expanded=True):
                    st.image(player_info["season_img_url"])
                    player_image_url = f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{player_info['spid']}.png"
                    if not check_image_exists(player_image_url):
                        player_image_url = default_image_url
                    st.image(player_image_url,width=100)
                    st.write(f"**선수 이름:** {player_info['선수이름']}")
                    st.write(f"**사용 횟수:** {player_info['usage_count']}")
                    st.subheader(f"**{message}**")

                if st.button("⬅ 선수 선택 초기화"):
                    st.session_state.selected_player = None
                    st.rerun()

    st.markdown("---")
    
    # 3. 인기 포메이션
    query_popular_formation_by_division = """
    WITH formation_rank AS (
        SELECT 
            d.division_name AS 등급,
            r.formation AS 포메이션,
            COUNT(*) AS 사용횟수,
            ROW_NUMBER() OVER (
                PARTITION BY d.division_name 
                ORDER BY COUNT(*) DESC
            ) AS rn
        FROM analytics.ranking_info r
        JOIN analytics.division_info d 
            ON r.division_id = d.division_id
        GROUP BY d.division_name, r.formation
    )
    SELECT 등급, 포메이션, 사용횟수
    FROM formation_rank
    WHERE rn <= 10
    ORDER BY 등급, rn;
    """
    
    df_formations = run_query(query_popular_formation_by_division)
    df_formations = df_formations[df_formations["등급"] == grade_name]
    
    fig_formation = (
    px.bar(
        df_formations,
        x="포메이션",
        y="사용횟수",
        color="포메이션",
        text="사용횟수",
        title=f"{grade_name} 인기 포메이션",
        color_discrete_sequence=px.colors.qualitative.T10
    )
    .update_traces(textposition="outside")
    .update_layout(
        title={'font': {'size': 25}},
        plot_bgcolor="black",
        paper_bgcolor="black",
        font_color="white",
        showlegend=False,
        xaxis=dict(showgrid=False, color="white", tickfont=dict(size=16)),
        yaxis=dict(showgrid=False, color="white", tickfont=dict(size=20))
    )
    )
    
    # 4. 인기 팀 컬러
    query_popular_team_color_by_division = """
    WITH color_rank AS (
        SELECT 
            d.division_name AS 등급,
            tc.team_color AS 팀컬러,
            COUNT(*) AS 사용횟수,
            ROW_NUMBER() OVER (
                PARTITION BY d.division_name
                ORDER BY COUNT(*) DESC
            ) AS rn
        FROM analytics.ranking_info r
        JOIN analytics.division_info d 
            ON r.division_id = d.division_id
        LEFT JOIN analytics.team_color_info tc 
            ON r.gamer_nickname = tc.gamer_nickname
        GROUP BY d.division_name, tc.team_color
    )
    SELECT 등급, 팀컬러, 사용횟수
    FROM color_rank
    WHERE rn <= 7
    ORDER BY 등급, rn;
    """
    df_team_color = run_query(query_popular_team_color_by_division)
    df_team_color = df_team_color[df_team_color["등급"] == grade_name]
    
    fig_team_color = (
    px.pie(
        df_team_color,
        values="사용횟수",
        names="팀컬러",
        title=f"{grade_name} 인기 팀컬러 TOP 10",
        color="팀컬러",
        color_discrete_sequence=px.colors.qualitative.T10,
        hole=0.5
    )
    .update_traces(
        textposition="outside",
        textinfo="percent+label"  
    )
    .update_layout(
        # width=800,
        # height=600,
        plot_bgcolor="black",
        paper_bgcolor="black",
        font_color="white",
        title={'font': {'size': 25}},
        legend=dict(font=dict(size=20))
    )
    )
    
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_formation, use_container_width=True)

    with col2:
        st.plotly_chart(fig_team_color, use_container_width=True)
    # 뒤로가기 버튼 (메인 페이지로)
    if st.button("⬅ 메인 화면으로 돌아가기"):
        change_page("main")

###################################################################
# 포지션 카테고리
def position_page(position):
    st.title(f"랭커들이 애용하는 {position} 포지션 선수 분석")

    st.subheader(f"{position} 포지션 인기 선수 Top10")
    
    # 선수 이름, 시즌, 감정분석 결과 등을 시각화하는 쿼리
    query1 = f"""
    SELECT a.name, a.spid, a.num, b.season_id, b.name as season_name, b.image_url
    FROM (
        SELECT name, a.season_id, a.spid, num
        FROM (
            SELECT spid, COUNT(*) AS "num", LEFT(spid, 3) AS season_id
            FROM (
                SELECT *, CASE
                    WHEN "position" IN (1,2,3,4,5,6,7,8) THEN 'df'
                    WHEN "position" IN (20,21,22,23,24,25,26,27) THEN 'fw'
                    WHEN "position" = 0 THEN 'gk'
                    WHEN "position" = 28 THEN 'sub'
                    ELSE 'mf' END AS position_cat
                FROM analytics.match_info
            )
            WHERE position_cat = '{position}'
            GROUP BY spid
            ORDER BY num DESC
            LIMIT 10
        ) a
        JOIN analytics.player_info b ON a.spid = b.spid
        ORDER BY num DESC
    ) a
    JOIN analytics.season_info b ON a.season_id = b.season_id
    ORDER BY num DESC;
    """
    player_data = run_query(query1)

    # 세션 상태 초기화
    if "selected_player" not in st.session_state:
        st.session_state.selected_player = None

    col1, col2 = st.columns([1, 2])  # 왼쪽(버튼) 1, 오른쪽(상세정보) 2 비율

    # 왼쪽: 선수 목록 버튼 (세로 배치)
    with col1:
        for player, spid in zip(player_data["name"], player_data["spid"]):
            if st.button(player, key=spid):  # 버튼 클릭 시 선수 선택
                st.session_state.selected_player = spid

    # 오른쪽: 상세 정보 표시
    with col2:
        if st.session_state.selected_player:
            # 선수 정보 필터링
            player_info = player_data[player_data["spid"] == st.session_state.selected_player]

            if not player_info.empty:  # ✅ 선수 데이터가 존재하는 경우에만 실행
                player_info = player_info.iloc[0]  # 첫 번째 행 가져오기

                # 감정 분석 데이터 가져오기
                query2 = f"SELECT * FROM analytics.player_review_info WHERE spid = {st.session_state.selected_player}"
                player_reviews = run_query(query2)

                # 📌 상세 정보 팝업 (expander)
                with st.expander(f"📌 {player_info['name']} 상세 정보", expanded=True):
                    st.image(player_info["image_url"])
                    st.write(f"**시즌:** {player_info['season_name']}")
                    spid = player_info["spid"]
                    player_image_url = f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png"
                    if not check_image_exists(player_image_url):
                        player_image_url = default_image_url
                    st.image(player_image_url,width=100)

                    # 긍정 & 부정 리뷰 개수 계산
                    positive_count = sum(player_reviews["prediction"] == 1)
                    negative_count = sum(player_reviews["prediction"] == 0)
                    total_reviews = len(player_reviews)

                    # ✅ 멘트 설정
                    if total_reviews == 0:
                        message = "📢 이 선수의 후기가 없어요. 첫 번째 후기를 남겨주세요!"
                    elif positive_count > negative_count:
                        message = "😃 이 선수는 감독들에게 평가가 좋아요!"
                    elif negative_count > positive_count:
                        message = "😞 이 선수의 평가가 좋지는 않네요.."
                    else:
                        message = "🤔 이 선수는 당신이 쓰기 나름이에요!"

                    # ✅ 멘트 출력
                    st.subheader(message)

                # 뒤로 가기 버튼
                if st.button("⬅ 선수 선택 초기화"):
                    st.session_state.selected_player = None
                    st.rerun()

    col3, col4 = st.columns([1, 2])

    with col4:
        # st.subheader("세부 포지션 비중")
        query3=f"""SELECT b.name, COUNT(*) AS "num"
            FROM (
                SELECT *, CASE
                    WHEN "position" IN (1,2,3,4,5,6,7,8) THEN 'df'
                    WHEN "position" IN (20,21,22,23,24,25,26,27) THEN 'fw'
                    WHEN "position" = 0 THEN 'gk'
                    WHEN "position" = 28 THEN 'sub'
                    ELSE 'mf' END AS position_cat
                FROM analytics.match_info
            ) a
            join analytics.position_info b on a.position=b.spposition
            WHERE position_cat = '{position}'
            GROUP BY b.name
            ORDER BY num DESC"""
        detail_position_data=run_query(query3)
        st.subheader("포지션 별 비중")
        fig = (
        px.pie(
            detail_position_data,
            names="name",
            values="num",
            # title="포지션 별 비중",
            color_discrete_sequence=px.colors.qualitative.T10,
            hole=0.5
            )
        .update_traces(
            textposition="outside",
            textinfo="percent+label"
            )
        .update_layout(
            plot_bgcolor="black",
            paper_bgcolor="black",
            font_color="white",
            # title={'font': {'size': 25}},
            legend=dict(font=dict(size=30))
            )
        )
        st.plotly_chart(fig)
        
        # Streamlit에서 파이 차트 표시
        
    with col3:
        st.subheader("평균 강화등급")
        query4=f"""select avg(spgrade)
        FROM (SELECT *, CASE
        WHEN "position" IN (1,2,3,4,5,6,7,8) THEN 'df'
        WHEN "position" IN (20,21,22,23,24,25,26,27) THEN 'fw'
        WHEN "position" = 0 THEN 'gk'
        WHEN "position" = 28 THEN 'sub'
        ELSE 'mf' END AS position_cat
        FROM analytics.match_info)
        WHERE position_cat = '{position}'"""
        data=run_query(query4)
        avg_spgrade=data.loc[0,"avg"]
        st.metric(label="강화등급",value=avg_spgrade)

    if st.button("⬅ 메인 화면으로 돌아가기"):
        change_page("main")

        
##############################################################################
def ranker_page(name):
    # 1. 랭커 기본 정보 
    st.title(f"{name}님의 정보")
    
    query = f"""
    SELECT 
        a.gamer_nickname,
        a.gamer_level, 
        b.division_name,
        a.team_worth,
        a.winning_rate,
        a.total_win,
        a.total_draw,
        a.total_lose,
        a.formation
    FROM analytics.ranking_info a
    JOIN analytics.division_info b 
        ON a.division_id = b.division_id
    WHERE a.gamer_nickname = '{name}'
    LIMIT 1;
    """
    data = run_query(query)
    if data is None or data.empty:
        st.error("랭커 정보를 불러오지 못했습니다.")
        return

    # 등급 재매핑
    rename_map = {
        "슈퍼챌린지": "슈퍼챌린저",
        "챌린지1": "챌린저 1부",
        "챌린지2": "챌린저 2부",
        "챌린지3": "챌린저 3부",
        "월드클래스1": "월드클래스 1부",
        "월드클래스2": "월드클래스 2부",
        "월드클래스3": "월드클래스 3부"
    }
    division = data.loc[0, "division_name"]
    if division in rename_map:
        division = rename_map[division]

    # 변수 할당
    worth = data.loc[0, "team_worth"]
    level = data.loc[0, "gamer_level"]
    winning_rate = data.loc[0, "winning_rate"]
    win = data.loc[0, "total_win"]
    draw = data.loc[0, "total_draw"]
    lose = data.loc[0, "total_lose"]
    formation = data.loc[0, "formation"]

    # 구단 가치 포맷팅
    formatted_worth = format_korean_unit(worth, mode="all")

    # 기본 정보 카드
    col1, col2, col3 = st.columns(3)
    col1.metric("등급", division)
    col2.metric("감독 레벨", level)
    col3.metric("구단 가치", formatted_worth)
    
    # 2. 승률, 포메이션
    colA, colB = st.columns(2)
    with colA:
        st.markdown(
            f"""
            <div style="text-align: left;">
                <h2 style="font-size:35px; margin-bottom: 0;">승률: {float(winning_rate):.1f}%</h2>
                <p style="font-size:20px; margin-top: 0;">승: {win}  /  무: {draw}  /  패: {lose}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with colB:
        st.markdown(
            f"""
            <div style="text-align: left; margin-top:20px;">
                <h2 style="font-size:35px;">포메이션: {formation}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    # 3. 랭커의 선수 목록
    query_used_players = f"""
    WITH used_players AS (
        SELECT
            mi.spid,
            mi.season_id,
            mi.position,
            mi.spgrade
        FROM analytics.match_info mi
        WHERE mi.gamer_nickname = '{name}'
    )
    SELECT
        p.name AS 선수이름,
        up.spid,
        up.season_id,
        up.position,
        up.spgrade,
        s.image_url AS season_img_url
    FROM used_players up
    JOIN analytics.player_info p
        ON up.spid = p.spid
    LEFT JOIN analytics.season_info s
        ON LEFT(up.spid::varchar, 3) = s.season_id
    ORDER BY p.name;
    """
    df_used = run_query(query_used_players)
    if df_used is None or df_used.empty:
        st.info("이 랭커가 사용하는 선수 데이터가 없습니다.")
        return

    st.subheader(f"{name}님의 선수 목록")
    
    df_used["position_group"] = df_used["position"].apply(
        lambda x: "df" if x in [1,2,3,4,5,6,7,8]
        else ("fw" if x in [20,21,22,23,24,25,26,27]
        else ("gk" if x == 0
        else ("sub" if x == 28
        else "mf")))
    )
    pos_map = {
        "fw": "공격수",
        "mf": "미드필더",
        "df": "수비수",
        "gk": "골키퍼",
        "sub": "교체선수"
    }
    df_used["포지션_그룹"] = df_used["position_group"].map(lambda x: pos_map.get(x, x))
    order = ["공격수", "미드필더", "수비수", "골키퍼", "교체선수"]
    df_used["포지션_그룹"] = pd.Categorical(df_used["포지션_그룹"], categories=order, ordered=True)
    
    # 포지션 그룹별로 선수 목록 표시 (한 줄에 5명씩)
    for group, group_df in df_used.groupby("포지션_그룹"):
        st.write(f"{group}")
        num_cols = 5
        rows = [group_df[i:i+num_cols] for i in range(0, len(group_df), num_cols)]
        for row_df in rows:
            cols = st.columns(num_cols)
            for idx, rowData in enumerate(row_df.itertuples()):
                with cols[idx]:
                    html = f"""
                    <div style="display: flex; align-items: center;">
                        <img src="{rowData.season_img_url}" style="margin-right: 5px;">
                        <span style="font-size: 16px; margin: 0;">{rowData.선수이름}</span>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
                    player_image_url = f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{str(rowData.spid)}.png"
                    if not check_image_exists(player_image_url):
                        player_image_url = default_image_url
                    st.image(player_image_url,width=100)

    if st.button("⬅ 메인 화면으로 돌아가기"):
        change_page("main")



################################################################################
##선수검색
#def player_page(name):
#    st.title(f"{name}선수 리스트")
# 
#    query1=f"""
#    select a.spid, a.season_id, b.name, c.name as season_name,c.image_url,concat(c.name,b.name) as full_name
#    from analytics.match_info a
#    join analytics.player_info b on a.spid=b.spid
#    join analytics.season_info c on a.season_id=c.season_id
#    where b.name ='{name}';"""
#    
#    player_data=run_query(query1)
#    
#    if "selected_player" not in st.session_state:
#        st.session_state.selected_player = None
#
#    col1, col2 = st.columns([1, 2])  # 왼쪽(버튼) 1, 오른쪽(상세정보) 2 비율
#
#    # 왼쪽: 선수 목록 버튼 (세로 배치)
#    with col1:
#        for player, spid in zip(player_data["full_name"], player_data["spid"]):
#            if st.button(player, key=spid):  # 버튼 클릭 시 선수 선택
#                st.session_state.selected_player = spid
#
#    # 오른쪽: 상세 정보 표시
#    with col2:
#        if st.session_state.selected_player:
#            # 선수 정보 필터링
#            player_info = player_data[player_data["spid"] == st.session_state.selected_player]
#
#            if not player_info.empty:  # ✅ 선수 데이터가 존재하는 경우에만 실행
#                player_info = player_info.iloc[0]  # 첫 번째 행 가져오기
#
#                # 감정 분석 데이터 가져오기
#                query2 = f"SELECT * FROM analytics.player_review_info WHERE spid = {st.session_state.selected_player}"
#                player_reviews = run_query(query2)
#
#                # 📌 상세 정보 팝업 (expander)
#                with st.expander(f"📌 {player_info['name']} 상세 정보", expanded=True):
#                    st.image(player_info["image_url"])
#                    st.write(f"**시즌:** {player_info['season_name']}")
#                    spid = player_info["spid"]
#                    player_image_url = f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png"
#                    if not check_image_exists(player_image_url):
#                        player_image_url = default_image_url
#                    st.image(player_image_url,width=100)
#                   
#                    # 긍정 & 부정 리뷰 개수 계산
#                    positive_count = sum(player_reviews["prediction"] == 1)
#                    negative_count = sum(player_reviews["prediction"] == 0)
#                    total_reviews = len(player_reviews)
#
#                    # ✅ 멘트 설정
#                    if total_reviews == 0:
#                        message = "📢 이 선수의 후기는 없어요. 당신이 첫 번째 후기를 남겨주세요!"
#                    elif positive_count > negative_count:
#                        message = "😃 이 선수는 감독들한테 평가가 좋아요!"
#                    elif negative_count > positive_count:
#                        message = "😞 이 선수의 평가는 좋지는 않네요.."
#                    else:
#                        message = "🤔 이 선수는 당신이 쓰기 나름이에요!"
#
#                    # ✅ 멘트 출력
#                    st.subheader(message)
#
#                # 뒤로 가기 버튼
#                if st.button("⬅ 선수 선택 초기화"):
#                    st.session_state.selected_player = None
#                    st.rerun()
#
# 
#
#    if st.button("⬅ 메인 화면으로 돌아가기"):
#        change_page("main")

###############################################################################
# 페이지 분기: 기본 메인 페이지와 등급별 페이지(내용은 동일)
if page == "main":
    main_page()
elif page in ["super_champions", "champions", "superchallengers", "challengers", "worldclass"]:
    grade_page(page)
elif page in ["fw", "mf", "df", "gk"]:
    position_page(page)
elif page.startswith("ranker_"):
    ranker_page(page.replace("ranker_", ""))
elif page.startswith("player_"):
    player_page(page.replace("player_", ""))
