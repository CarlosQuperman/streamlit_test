# streamlit_app.py

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# 1. SQLite 데이터베이스 설정
conn = sqlite3.connect('student_data.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        name TEXT,
        learning_progress TEXT
    )
''')
conn.commit()

# 2. Sidebar 메뉴
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Create Account", "Enter Learning Data", "Visualize Data"]
)

# 2.1 계정 생성 페이지
if page == "Create Account":
    st.header("Create New Student Account")
    username = st.text_input("Username:")
    name = st.text_input("Name:")
    if st.button("Create Account"):
        if username and name:
            try:
                c.execute(
                    "INSERT INTO students (username, name, learning_progress) VALUES (?, ?, ?)",
                    (username, name, "")
                )
                conn.commit()
                st.success("Account created successfully!")
            except sqlite3.IntegrityError:
                st.error("Username already exists.")

# 2.2 학습 데이터 입력 페이지
elif page == "Enter Learning Data":
    st.header("Enter Learning Data")
    username = st.text_input("Enter your username to load your data:")
    if username:
        c.execute("SELECT * FROM students WHERE username = ?", (username,))
        student = c.fetchone()
        if student:
            st.write(f"Welcome, {student[2]}!")
            learning_data = st.text_area("Enter your learning progress:")
            if st.button("Update Learning Data"):
                c.execute(
                    "UPDATE students SET learning_progress = ? WHERE username = ?",
                    (learning_data, username)
                )
                conn.commit()
                st.success("Learning data updated successfully!")
        else:
            st.error("No account found with this username.")

# 2.3 시각화 데이터 페이지
elif page == "Visualize Data":
    st.header("Visualize Learning Data")
    st.write("이 페이지에서 데이터 테이블을 수정하고 그래프를 생성할 수 있습니다.")

    # 테이블 크기 조정
    num_rows = st.number_input("Number of rows:", min_value=1, max_value=100, value=10)
    num_cols = st.number_input("Number of columns:", min_value=1, max_value=20, value=10)

    # 빈 데이터 프레임 생성
    default_data = pd.DataFrame({f"col_{i}": [None] * num_rows for i in range(1, num_cols + 1)})

    # 데이터 테이블 표시 및 편집
    st.write("테이블에 데이터를 입력하세요:")
    edited_data = st.data_editor(default_data)

    # 시각화에 사용할 축 선택
    x_column = st.selectbox("Choose X-Axis:", edited_data.columns)
    y_column = st.selectbox("Choose Y-Axis:", edited_data.columns)

    # 축 이름 변경
    st.write("Rename Axis Labels:")
    x_label = st.text_input("New X-Axis Label:", value=x_column)
    y_label = st.text_input("New Y-Axis Label:", value=y_column)

    chart_title = st.text_input("Chart Title:")

    if st.button("Create Plot"):
        # Plotly를 이용한 라인 플롯 생성
        fig = px.line(
            edited_data, x=x_column, y=y_column, 
            labels={x_column: x_label, y_column: y_label}, 
            title=chart_title
        )
        st.plotly_chart(fig)

    # 퀴즈 기능 추가
    st.write("퀴즈:")
    quiz_question = "강원사대부고 2학년 물리 담당 선생님 이름은?"
    correct_answer = "이중엽"
    user_answer = st.text_input(quiz_question)

    if st.button("Submit Answer"):
        if user_answer.strip() == correct_answer:
            st.success("맞았습니다!")
        else:
            st.warning("다시 생각해보세요. 성격이 아름다운 분입니다.")

    # 이미지 링크 추가 기능
    st.image("https://i.ibb.co/tX4fgfr/crazylee.png", caption="Visualization Example")

# 데이터베이스 연결 닫기
conn.close()
