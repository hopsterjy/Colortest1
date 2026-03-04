import flet as ft
import random
import asyncio
import colorsys

def main(page: ft.Page):
    # 폰트 및 페이지 설정
    page.fonts = {"GoogleSansFlex": "https://fonts.gstatic.com/s/googlesansflex/v8/iJWZ7v8vLBE6q_32m_8A6kC_u9FvOShI9_C99GjY.ttf"}
    page.theme = ft.Theme(font_family="GoogleSansFlex")
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 게임 상태
    state = {
        "score": 0, "level": 2, "time_left": 60,
        "high_score": 0, "high_score_name": "None",
        "is_active": False, 
        "mode": "Random",
        "difficulty": "Regular"
    }

    # UI 컴포넌트
    timer_text = ft.Text("60", size=70, weight="w500", color="blue400")
    score_text = ft.Text("SCORE: 0", size=24, weight="w500")
    best_text = ft.Text(f"BEST: 0 (None)", color="grey500", size=14)
    grid_container = ft.Column(spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    exit_button = ft.TextButton(
        "EXIT", icon_color="red400",
        style=ft.ButtonStyle(color="red400"), visible=False,
        on_click=lambda e: exit_game()
    )

    # 설정 메뉴: 컬러 모드
    mode_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Random", label="Random"),
            ft.Radio(value="Saturation", label="Sat"),
            ft.Radio(value="Brightness", label="Light"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="Random",
        on_change=lambda e: state.update({"mode": e.data})
    )

    # 설정 메뉴: 난이도 (추가된 부분)
    diff_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Baby", label="Baby"),
            ft.Radio(value="Regular", label="Regular"),
            ft.Radio(value="Expert", label="Expert"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="Regular",
        on_change=lambda e: state.update({"difficulty": e.data})
    )
    
    start_button = ft.ElevatedButton(
        "START GAME", on_click=lambda e: start_game(),
        style=ft.ButtonStyle(bgcolor="blue700", color="white", padding=20, shape=ft.RoundedRectangleBorder(radius=10))
    )

    menu_ui = ft.Column([
        ft.Text("Color Mode", size=14, color="grey500"),
        mode_radio,
        ft.Text("Difficulty", size=14, color="grey500"),
        diff_radio,
        ft.Divider(height=10, color="transparent"),
        start_button
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=True)

    name_input = ft.TextField(label="New Record! Enter Name", autofocus=True)

    # 색상 알고리즘 (난이도 가중치 반영)
    def generate_colors(score):
        # 난이도별 가중치 설정
        diff_multipliers = {"Baby": 1.8, "Regular": 1.0, "Expert": 0.6}
        mult = diff_multipliers.get(state["difficulty"], 1.0)

        # 기본 색상 차이 계산 (지수 함수)
        diff = max(0.005, (0.22 * (0.93 ** (score / 2.5))) * mult)
        
        h, s, l = random.random(), 0.5 + random.random() * 0.3, 0.4 + random.random() * 0.2
        target_h, target_s, target_l = h, s, l
        
        if state["mode"] == "Saturation": target_s = min(1.0, s + diff)
        elif state["mode"] == "Brightness": target_l = min(1.0, l + diff)
        else: # Random RGB
            r, g, b = [random.randint(50, 180) for _ in range(3)]
            rgb_diff = int((65 * (0.91 ** (score / 2))) * mult) + 2
            return f"#{r:02x}{g:02x}{b:02x}", f"#{min(255, r+rgb_diff):02x}{min(255, g+rgb_diff):02x}{min(255, b+rgb_diff):02x}"

        def hsl_to_hex(h, s, l):
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        return hsl_to_hex(h, s, l), hsl_to_hex(target_h, target_s, target_l)

    async def timer_task():
        while state["time_left"] > 0 and state["is_active"]:
            await asyncio.sleep(1)
            state["time_left"] -= 1
            timer_text.value = str(state["time_left"])
            if state["time_left"] <= 10: timer_text.color = "red400"
            page.update()
        if state["time_left"] <= 0 and state["is_active"]: end_game()

    def save_score(e):
        state["high_score"] = state["score"]
        state["high_score_name"] = name_input.value if name_input.value else "Guest"
        best_text.value = f"BEST: {state['high_score']} ({state['high_score_name']})"
        page.close(dialog)
        page.update()

    dialog = ft.AlertDialog(
        modal=True, title=ft.Text("🏆 New High Score!"),
        content=name_input,
        actions=[ft.TextButton("Save Record", on_click=save_score)]
    )

    def exit_game():
        state["is_active"] = False
        menu_ui.visible = True
        exit_button.visible = False
        grid_container.controls.clear()
        timer_text.value, timer_text.color = "60", "blue400"
        score_text.value = "SCORE: 0"
        page.update()

    def end_game():
        state["is_active"] = False
        menu_ui.visible = True
        exit_button.visible = False
        if state["score"] > state["high_score"]:
            page.open(dialog)
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"Game Over! Score: {state['score']}"), open=True)
        page.update()

    def on_tile_click(e):
        if not state["is_active"]: return
        if e.control.data == "target":
            state["score"] += 1
            if state["score"] % 5 == 0:
                state["level"] = min(14, state["level"] + 1)
            render_game()
        page.update()

    def render_game():
        score_text.value = f"SCORE: {state['score']}"
        grid_container.controls.clear()
        base_color, target_color = generate_colors(state["score"])
        target_index = random.randint(0, (state["level"]**2) - 1)
        
        available_width = min(page.width - 40, 500) 
        tile_size = (available_width - (state["level"] - 1) * 3) / state["level"]

        for i in range(state["level"]):
            row = ft.Row(spacing=3, alignment=ft.MainAxisAlignment.CENTER)
            for j in range(state["level"]):
                is_target = (i * state["level"] + j) == target_index
                row.controls.append(
                    ft.Container(
                        width=tile_size, height=tile_size,
                        bgcolor=target_color if is_target else base_color,
                        border_radius=3, data="target" if is_target else "normal",
                        on_click=on_tile_click,
                        animate_scale=ft.Animation(150, "easeOut")
                    )
                )
            grid_container.controls.append(row)
        page.update()

    def start_game():
        state.update({"score": 0, "level": 2, "time_left": 60, "is_active": True})
        menu_ui.visible, exit_button.visible = False, True
        timer_text.color, timer_text.value = "blue400", "60"
        render_game()
        page.run_task(timer_task)

    page.add(
        ft.Row([exit_button], alignment=ft.MainAxisAlignment.END),
        ft.Column([
            timer_text, score_text, best_text,
            ft.Divider(height=10, color="transparent"),
            menu_ui,
            ft.Divider(height=10, color="transparent"),
            grid_container,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)