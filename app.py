from flask import Flask, request, jsonify, render_template
import mysql.connector
import os # 템플릿 경로를 위해 추가

# --- 1. Flask 앱 생성 ---
app = Flask(__name__)

# --- 2. Tier 3 (DB) 연결 설정 ---
# [주의!] 'your_app_password'를 Tier 3에서 만든 실제 비밀번호로 변경하세요.
db_config = {
    'user': 'app_user',
    'password': '1234',
    'host': 'localhost', # 2티어와 3티어가 같은 VM에 있음
    'database': 'my_service'
}

# --- 3. 로그인 페이지 라우트 ---
# (GET /) - 호스트 PC에서 접속할 로그인 HTML 페이지를 보여줍니다.
@app.route('/', methods=['GET'])
def get_login_page():
    # 'templates' 폴더의 'index.html' 파일을 렌더링합니다.
    # (HTML 파일은 4단계에서 만들겠습니다)
    try:
        return render_template('index.html')
    except Exception as e:
        return f"HTML 파일을 찾을 수 없습니다: {e}"

# --- 4. 로그인 API 라우트 ---
# (POST /login) - 실제 로그인 로직을 처리합니다.
@app.route('/login', methods=['POST'])
def login():
    conn = None
    cursor = None
    try:
        # (1) 사용자가 입력한 ID/PW를 JSON 형태로 받음
        data = request.get_json()
        username = data['username']
        password = data['password']

        # (2) DB에 연결
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # (3) DB에서 사용자 정보 조회
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        # (4) 로그인 로직 실행
        # [주의!] 실제 서비스에서는 비밀번호를 해시(hash)해서 비교해야 합니다.
        if user and user['password'] == password:
            return jsonify({"status": "success", "message": "로그인 성공!"}), 200
        else:
            return jsonify({"status": "error", "message": "ID 또는 PW가 틀립니다."}), 401

    except Exception as e:
        # (5) 예외 처리
        return jsonify({"status": "error", "message": str(e)}), 500
    
    finally:
        # (6) DB 연결 종료 (필수!)
        if cursor: cursor.close()
        if conn: conn.close()

# --- 5. Flask 앱 실행 ---
if __name__ == '__main__':
    # Tier 1(Nginx)과 통신하기 위해 내부 포트 5000번으로 실행
    app.run(host='127.0.0.1', port=5000, debug=True)
