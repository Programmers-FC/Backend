import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
import redshift_connector

##################################################내가 추가한거
# secrets.toml에서 Redshift 연결 정보 불러오기
REDSHIFT_HOST = st.secrets["redshift"]["host"]
REDSHIFT_PORT = st.secrets["redshift"]["port"]
REDSHIFT_DATABASE = st.secrets["redshift"]["database"]
REDSHIFT_USER = st.secrets["redshift"]["user"]
REDSHIFT_PASSWORD = st.secrets["redshift"]["password"]

###################################################내가 추가한거
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
        
######################################################내가 추가한거
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
#------------------------------------------------------------------------------------------





# 페이지 설정
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
    
####################################################################내가 추가한거 #사이드바
st.sidebar.title("🔍 검색")
search_option = st.sidebar.radio("검색 유형을 선택하세요", ["랭커 검색"])#필요할경우 선수검색 추가

if search_option == "랭커 검색":
    ranker_name = st.sidebar.text_input("랭커 이름을 입력하세요:")
    if ranker_name and st.sidebar.button("검색"):
        change_page(f"ranker_{ranker_name}")

#elif search_option == "선수 검색":
#    player_name = st.sidebar.text_input("선수 이름을 입력하세요:")
#    if player_name and st.sidebar.button("검색"):
#        change_page(f"player_{player_name}")
##########################################################################
# 사이드바: 유저 등급 선택 버튼
st.sidebar.title("공식 경기 등급")
if st.sidebar.button("슈퍼 챔피언스"):
    change_page("super_champions")
if st.sidebar.button("챔피언스"):
    change_page("champions")
if st.sidebar.button("슈퍼챌린저"):
    change_page("superchallengers")
if st.sidebar.button("챌린저"):
    change_page("challengers")
if st.sidebar.button("월드클래스"):
    change_page("worldclass")
    
##################################################내가 추가한거
st.sidebar.title("⚽ 선수 포지션")
if st.sidebar.button("FW"):
    change_page("fw")
if st.sidebar.button("MF"):
    change_page("mf")
if st.sidebar.button("DF"):
    change_page("df")
if st.sidebar.button("GK"):
    change_page("gk")
#####################################################

# 메인 페이지 (기본 화면)와 등급별 페이지의 공통 내용을 위한 함수
def main_page():
    st.title("FC온라인 대시보드 🚀")
    
    # 최신 데이터 업데이트 날짜
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(f"<div style='text-align: right;'>최신 업데이트: {update_time}</div>", unsafe_allow_html=True)
    
    st.header("Overview")
    
    # 집계된 유저 수, 전체 평균 승률, 최고 승률 포메이션 (예시 데이터)
    total_users = 15000
    overall_win_rate = "67.5%"  # 예시
    best_formation = "4-3-3"    # 예시
    
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 랭커 수", f"{total_users:,}")
    col2.metric("전체 평균 승률", overall_win_rate)
    col3.metric("최고 승률 포메이션", best_formation)
    st.markdown("---")
    
    # ------------------------------------------------

        
    
    # ------------------------------------------------
    # 인기 선수 
    st.header("인기 선수 TOP 3")
    

    top5_players = [
        {
            "name": "토니 크로스",
            "img_url": "https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p807182521.png"
        },
        {
            "name": "음바페",
            "img_url": "https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p265231747.png"
        },
        {
            "name": "벨링엄",
            "img_url": "https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p290252371.png"
        }        
    ]
    
    # 3개 칼럼 생성
    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]

    # 각 칼럼에 선수 이미지와 이름을 표시
    for i, player in enumerate(top5_players):
        with columns[i]:
            st.image(player["img_url"], caption=player["name"])
    
    # ------------------------------------------------
    # 샘플 데이터 준비
    df_team_value = pd.DataFrame({
        "등급": ["슈퍼 챔피언스", "챔피언스", "슈퍼챌린저", "챌린저", "월드클래스"],
        "평균 팀 가치": [50000, 30000, 25000, 30000, 25000]
    })

    df_enhance = pd.DataFrame({
        "등급": ["슈퍼 챔피언스", "챔피언스", "슈퍼챌린저", "챌린저", "월드클래스"],
        "평균 강화 레벨": [8.5, 7.3, 5.6, 5.3, 5.8]
    })

    # 등급별 구단 가치 그래프
    fig_team_value = px.bar(
        df_team_value,
        x="등급",
        y="평균 팀 가치",
        text="평균 팀 가치",
        title="등급별 구단 가치",
        color="등급",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_team_value.update_layout(
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        showlegend=False
    )
    fig_team_value.update_traces(textposition="outside")

    # 등급별 강화 레벨 그래프
    fig_enhance = px.bar(
        df_enhance,
        x="등급",
        y="평균 강화 레벨",
        text="평균 강화 레벨",
        title="등급별 강화 레벨 수준",
        color="등급",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_enhance.update_layout(
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        showlegend=False
    )
    fig_enhance.update_traces(textposition="outside")

    # 2칸으로 화면 분할
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_team_value, use_container_width=True)

    with col2:
        st.plotly_chart(fig_enhance, use_container_width=True)



    # 선수 데이터 예시
    players = {
        "Lionel Messi": {"국적": "아르헨티나", "팀": "인터 마이애미", "포지션": "FW", "득점": 800},
        "Cristiano Ronaldo": {"국적": "포르투갈", "팀": "알 나스르", "포지션": "FW", "득점": 850},
        "Kylian Mbappé": {"국적": "프랑스", "팀": "파리 생제르맹", "포지션": "FW", "득점": 250},
    }

    # 세션 상태 초기화
    if "selected_player" not in st.session_state:
        st.session_state.selected_player = None

    st.title("⚽ 축구 선수 순위")
    col1, col2 = st.columns([1, 2])
    with col1:
        for player in players.keys():
            if st.button(player):
                st.session_state.selected_player = playerㅊㅊㅊ
    with col2:
        if st.session_state.selected_player:
            player = st.session_state.selected_player
            st.subheader(f"📌 {player} 상세 정보")
            st.write(f"**국적:** {players[player]['국적']}")
            st.write(f"**팀:** {players[player]['팀']}")
            st.write(f"**포지션:** {players[player]['포지션']}")
            st.write(f"**총 득점:** {players[player]['득점']}골")
            st.image("https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p265231747.png")
            
            if st.button("⬅ 선수 선택 초기화"):
                st.session_state.selected_player = None
                st.rerun()

    # 선수별 득점 데이터 및 차트
    df = pd.DataFrame({
        "선수": ["Messi", "Ronaldo", "Mbappé", "Haaland", "Neymar"],
        "횟수": [800, 850, 250, 180, 400]
    })
    st.title("인기 선수 비교")
    fig = px.bar(df, x="선수", y="횟수", title="랭커의 선수별 사용횟수", text="횟수")
    st.plotly_chart(fig)

def grade_page(grade):
    st.title(f"{grade} 랭커 분석")

    # 1) 랭커 정보 (순위, 이름, 팀 가치, 승률(승|무|패), 팀 컬러, 포메이션)
    st.subheader("랭커 정보")
    ranker_data = [
        {
            "순위": 1, 
            "이름": "DNFS", 
            "팀 가치": 200000, 
            "승률(승|무|패)": "80% (40|5|5)",
            "팀 컬러": "레알 마드리드",
            "포메이션": "4-3-3"
        },
        {
            "순위": 2, 
            "이름": "람머스", 
            "팀 가치": 180000, 
            "승률(승|무|패)": "75% (30|10|10)",
            "팀 컬러": "맨체스터 시티",
            "포메이션": "4-2-3-1"
        },
        {
            "순위": 3, 
            "이름": "KWAK", 
            "팀 가치": 150000, 
            "승률(승|무|패)": "70% (28|8|14)",
            "팀 컬러": "바이에른 뮌헨",
            "포메이션": "4-4-2"
        }
    ]
    df_ranker = pd.DataFrame(ranker_data)
    st.table(df_ranker)

    # 2) 인기 선수 (순위, 시즌, 이름)
    st.subheader("인기 선수")
    # 예시 데이터
    popular_players = [
        {"순위": 1, "시즌": "LIVE", "선수명": "음바페"},
        {"순위": 2, "시즌": "BTB", "선수명": "메시"},
        {"순위": 3, "시즌": "EBS", "선수명": "손흥민"},
        {"순위": 4, "시즌": "VTR", "선수명": "홀란드"},
        {"순위": 5, "시즌": "BTB", "선수명": "호날두"}
    ]
    df_players = pd.DataFrame(popular_players)
    st.table(df_players)

    # 3) 인기 포메이션
    st.subheader("인기 포메이션")
    # 예시 데이터를 바 차트로 표현
    df_formation = pd.DataFrame({
        "포메이션": ["4-3-3", "4-2-3-1", "4-4-2", "5-3-2"],
        "사용 횟수": [40, 35, 20, 5]
    })
    fig_formation = px.bar(
        df_formation,
        x="포메이션",
        y="사용 횟수",
        text="사용 횟수",
        title="인기 포메이션",
        color="포메이션"
    )
    fig_formation.update_traces(textposition="outside")
    fig_formation.update_layout(showlegend=False)
    st.plotly_chart(fig_formation, use_container_width=True)

    # 4) 인기 팀 컬러
    st.subheader("인기 팀 컬러")
    # 예시 데이터를 파이 차트로 표현
    df_team_color = pd.DataFrame({
        "팀 컬러": ["레알 마드리드", "맨체스터 시티", "바이에른 뮌헨", "리버풀", "바르셀로나"],
        "사용 비중": [30, 25, 20, 15, 10]
    })
    fig_team_color = px.pie(
        df_team_color,
        names="팀 컬러",
        values="사용 비중",
        title="인기 팀 컬러"
    )
    st.plotly_chart(fig_team_color, use_container_width=True)

    # 뒤로가기 버튼 (메인 페이지로)
    if st.button("⬅ 메인 화면으로 돌아가기"):
        change_page("main")
        
###################################################################내가 추가한거# 포지션 카테고리# 이거 추가하면 됩니다!
def position_page(position):
    st.title(f"랭커들이 애용하는 {position} 포지션 선수 분석")

    st.subheader(f"{position} 포지션 인기 선수 Top10:")
   
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
                    st.image(f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png")

                    # 긍정 & 부정 리뷰 개수 계산
                    positive_count = sum(player_reviews["prediction"] == 1)
                    negative_count = sum(player_reviews["prediction"] == 0)
                    total_reviews = len(player_reviews)

                    # ✅ 멘트 설정
                    if total_reviews == 0:
                        message = "📢 이 선수의 후기는 없어요. 당신이 첫 번째 후기를 남겨주세요!"
                    elif positive_count > negative_count:
                        message = "😃 이 선수는 감독들한테 평가가 좋아요!"
                    elif negative_count > positive_count:
                        message = "😞 이 선수의 평가는 좋지는 않네요.."
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
        st.subheader("세부 포지션 비중")
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
        fig = px.pie(
        detail_position_data,
        names="name",
        values="num",
        title="포지션 별 비중"
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

        
##############################################################################내가 추가한거#랭커검색# 이거 추가하면 됩니다!
def ranker_page(name):
    st.title(f"랭커 {name} 정보")
    st.write(f"{name}의 선수정보")
    
    query=f"""select a.gamer_nickname,a.gamer_level, b.division_name,a.team_worth,a.winning_rate,a.total_win,a.total_draw ,a.total_lose ,a.formation
    from analytics.ranking_info a
    join analytics.division_info b on a.division_id = b.division_id
    where a.gamer_nickname = '{name}'
    limit 1;"""
    data=run_query(query)
    division=data.loc[0,"division_name"]
    worth=data.loc[0,"team_worth"]
    level=data.loc[0,"gamer_level"]
    winning_rate=data.loc[0,"winning_rate"]
    win=data.loc[0,"total_win"]
    draw=data.loc[0,"total_draw"]
    lose=data.loc[0,"total_lose"]
    formation=data.loc[0,"formation"]
    #경영님 데이터 호출하기
    st.write(f"등급:{division}")
    st.write(f"감독레벨:{level}")
    st.write(f"구단가치:{worth}")
    st.write(f"승률:{winning_rate}")
    st.write(f"승리횟수:{win}")
    st.write(f"무승부횟수:{draw}")
    st.write(f"패배횟수:{lose}")
    st.write(f"사용포메이션:{formation}")
    
    
    
    if st.button("⬅ 메인 화면으로 돌아가기"):
        change_page("main")
    
################################################################################내가 추가한거#선수검색
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
#                    st.image(f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png")
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
#
#
#
#
#

###############################################################################내가 추가한거 # 이것도 추가해야돼요
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
###################################################################################################
