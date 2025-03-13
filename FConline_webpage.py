import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

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
    # 랭커 검색
    name = st.text_input("랭커 이름을 입력하세요:")
    if name:
        st.write(f"아래는 {name}랭커님의 정보입니다. 🎉")
        
    
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

    st.title("인기 선수 순위")
    col1, col2 = st.columns([1, 2])
    with col1:
        for player in players.keys():
            if st.button(player):
                st.session_state.selected_player = player
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


# 페이지 분기: 기본 메인 페이지와 등급별 페이지(내용은 동일)
if page == "main":
    main_page()
else:
    # 페이지 이름을 코드와 매핑 (출력할 때 보일 이름)
    grade_names = {
        "super_champions": "슈퍼 챔피언스",
        "champions": "챔피언스",
        "superchallengers": "슈퍼챌린저",
        "challengers": "챌린저",
        "worldclass": "월드클래스"
    }
    display_grade = grade_names.get(page, page)
    grade_page(display_grade)