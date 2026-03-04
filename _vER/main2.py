import flet as ft
import random
import asyncio

def main(page: ft.Page):
    # 1. Google Sans Flex 폰트 설정
    page.fonts = {
        "GoogleSansFlex": "https://fonts.gstatic.com/s/googlesansflex/v8/iJWZ7v8vLBE6q_32m_8A6kC_u9FvOShI9_C99GjY.ttf"
    }
    page.theme = ft.Theme(font_family="GoogleSansFlex")
    page.title = "Kuku Kube: UI Expert Edition"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 800
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 40

    # 게임 상태 변수
    state = {
        "score": 0,
        "level": 2,
        "time_left": 60,
        "high_score": 0,
        "high_score_name": "None",
        "is_active": False
    }

    # UI 컴포넌트
    timer_text = ft.Text("60", size=60, weight="w500", color="blue400")
    score_text = ft.Text("SCORE: 0", size=24, weight="w500")
    best_text = ft.Text(f"BEST: 0 (None)", color="grey500", size=14)
    grid_container = ft.Column(spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    name_input = ft.TextField(label="Enter Your Name", autofocus=True)

    # 2. 무한 난이도 알고리즘 (LaTeX 적용)
    # 색상 차이(diff)는 다음 식을 따릅니다:
    # $$diff = \lfloor 60 \times 0.91^{(level / 1.5)} \rfloor + 2$$
    def get_difficulty_diff(lvl):
        # 레벨이 올라갈수록 diff가 급격히 줄어들다가, 최소 2를 유지하여 '불가능'은 아니게 만듭니다.
        return int(60 * (0.91 ** (lvl / 1.5))) + 2

    # 3. 비동기 타이머 함수 (수정됨)
    async def timer_task():
        while state["time_left"] > 0 and state["is_active"]:
            await asyncio.sleep(1)
            state["time_left"] -= 1
            timer_text.value = str(state["time_left"])
            
            # 10초 남았을 때 UI 경고 (디자이너의 세심함!)
            if state["time_left"] <= 10:
                timer_text.color = "red400"
            page.update()
            
        if state["time_left"] <= 0:
            end_game()

    # 4. 하이스코어 저장 팝업
    def save_score(e):
        state["high_score"] = state["score"]
        state["high_score_name"] = name_input.value if name_input.value else "Guest"
        best_text.value = f"BEST: {state['high_score']} ({state['high_score_name']})"
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("🏆 New High Score!"),
        content=name_input,
        actions=[ft.TextButton("Save My Record", on_click=save_score)]
    )

    def end_game():
        state["is_active"] = False
        if state["score"] > state["high_score"]:
            page.dialog = dialog
            dialog.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"Game Over! Score: {state['score']}"), open=True)
        page.update()

    def on_tile_click(e):
        if not state["is_active"]: return
        if e.control.data == "target":
            state["score"] += 1
            # 5점마다 그리드 크기 증가 (최대 10x10)
            if state["score"] % 5 == 0:
                state["level"] = min(10, state["level"] + 1)
            render_game()
        page.update()

    def render_game():
        score_text.value = f"SCORE: {state['score']}"
        grid_container.controls.clear()
        
        # 베이스 컬러 생성
        r, g, b = random.randint(50, 180), random.randint(50, 180), random.randint(50, 180)
        base_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # 난이도 적용 (현재 점수를 레벨 인자로 사용)
        diff = get_difficulty_diff(state["score"])
        target_color = f"#{min(255, r+diff):02x}{min(255, g+diff):02x}{min(255, b+diff):02x}"
        
        target_idx = random.randint(0, (state["level"]**2) - 1)
        tile_size = (400 - (state["level"] * 10)) / state["level"]

        for i in range(state["level"]):
            row = ft.Row(spacing=3, alignment=ft.MainAxisAlignment.CENTER)
            for j in range(state["level"]):
                is_target = (i * state["level"] + j) == target_idx
                row.controls.append(
                    ft.Container(
                        width=tile_size, height=tile_size,
                        bgcolor=target_color if is_target else base_color,
                        border_radius=2,
                        data="target" if is_target else "normal",
                        on_click=on_tile_click,
                        animate_scale=ft.Animation(200, "easeOut")
                    )
                )
            grid_container.controls.append(row)
        page.update()

    def start_game(e):
        state["score"] = 0
        state["level"] = 2
        state["time_left"] = 60
        state["is_active"] = True
        timer_text.color = "blue400"
        render_game()
        # 핵심 변경: asyncio.run 대신 page.run_task 사용!
        page.run_task(timer_task)

    # 초기 레이아웃
    page.add(
        ft.Column([
            timer_text,
            score_text,
            best_text,
            ft.Divider(height=30, color="transparent"),
            grid_container,
            ft.Divider(height=40, color="transparent"),
            ft.ElevatedButton(
                "START GAME", 
                on_click=start_game,
                style=ft.ButtonStyle(
                    color="white",
                    bgcolor="blue700",
                    padding=2,
                    shape=ft.RoundedRectangleBorder(radius=2)
                )
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)