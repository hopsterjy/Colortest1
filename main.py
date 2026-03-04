import flet as ft
import random
import asyncio
import colorsys


def main(page: ft.Page):
    # 페이지 기본 설정
    page.title = "Kuku Kube: Pure Edition"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.fonts = {"GoogleSansFlex": "https://fonts.gstatic.com/s/googlesansflex/v8/iJWZ7v8vLBE6q_32m_8A6kC_u9FvOShI9_C99GjY.ttf"}
    page.theme = ft.Theme(font_family="GoogleSansFlex")

    # 게임 상태 관리 (이름 항목 제거)
    state = {
        "score": 0, "level": 2, "time_left": 60,
        "high_score": 0,
        "is_active": False, "mode": "Random", "difficulty": "Regular"
    }

    # UI 컴포넌트
    timer_text = ft.Text("60", size=70, weight="w500", color="blue400")
    score_text = ft.Text("SCORE: 0", size=24, weight="w500")
    best_text = ft.Text("BEST: 0", color="amber400", size=16, weight="w600") # 강조된 베스트 스코어
    grid_container = ft.Column(spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # --- 함수 로직 ---

    def generate_colors(score):
        diff_multipliers = {"Baby": 1.8, "Regular": 1.0, "Expert": 0.6}
        mult = diff_multipliers.get(state["difficulty"], 1.0)
        diff = max(0.005, (0.22 * (0.93 ** (score / 2.5))) * mult)
        
        h, s, l = random.random(), 0.5 + random.random() * 0.3, 0.4 + random.random() * 0.2
        if state["mode"] == "Saturation":
            target_s = min(1.0, s + diff)
            r1, g1, b1 = colorsys.hls_to_rgb(h, l, s)
            r2, g2, b2 = colorsys.hls_to_rgb(h, l, target_s)
        elif state["mode"] == "Brightness":
            target_l = min(1.0, l + diff)
            r1, g1, b1 = colorsys.hls_to_rgb(h, l, s)
            r2, g2, b2 = colorsys.hls_to_rgb(h, target_l, s)
        else:
            r, g, b = [random.randint(50, 180) for _ in range(3)]
            rgb_diff = int((65 * (0.91 ** (score / 2))) * mult) + 2
            return f"#{r:02x}{g:02x}{b:02x}", f"#{min(255, r+rgb_diff):02x}{min(255, g+rgb_diff):02x}{min(255, b+rgb_diff):02x}"
        return f"#{int(r1*255):02x}{int(g1*255):02x}{int(b1*255):02x}", f"#{int(r2*255):02x}{int(g2*255):02x}{int(b2*255):02x}"

    async def timer_task():
        while state["time_left"] > 0 and state["is_active"]:
            await asyncio.sleep(1)
            state["time_left"] -= 1
            timer_text.value = str(state["time_left"])
            timer_text.color = "red400" if state["time_left"] <= 10 else "blue400"
            page.update()
        if state["time_left"] <= 0 and state["is_active"]:
            end_game(None)

    def end_game(e):
        state["is_active"] = False
        menu_ui.visible = True
        exit_button.visible = False
        
        # 게임 종료 알림
        page.snack_bar = ft.SnackBar(
            ft.Text(f"Game Over! Final Score: {state['score']}"),
            open=True,
            bgcolor="grey800"
        )
        page.update()

    def on_tile_click(e):
        if not state["is_active"]: return
        if e.control.data == "target":
            state["score"] += 1
            
            # [실시간 최고점 업데이트] 디자이너의 센스: 최고점 돌파 시 즉시 반영
            if state["score"] > state["high_score"]:
                state["high_score"] = state["score"]
                best_text.value = f"BEST: {state['high_score']}"
                best_text.color = "amber400" # 최고점 달성 시 색상 강조
            
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

    def start_game(e):
        state["score"] = 0
        state["level"] = 2
        state["time_left"] = 60
        state["is_active"] = True
        menu_ui.visible, exit_button.visible = False, True
        timer_text.color, timer_text.value = "blue400", "60"
        render_game()
        page.update()
        page.run_task(timer_task)

    # --- UI 레이아웃 ---
    exit_button = ft.TextButton(
        "EXIT", icon="close_rounded", icon_color="red400",
        style=ft.ButtonStyle(color="red400"), visible=False,
        on_click=end_game
    )

    mode_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Random", label="Random"),
            ft.Radio(value="Saturation", label="Sat"),
            ft.Radio(value="Brightness", label="Light"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="Random",
        on_change=lambda e: state.update({"mode": e.data})
    )

    diff_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Baby", label="Baby"),
            ft.Radio(value="Regular", label="Regular"),
            ft.Radio(value="Expert", label="Expert"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="Regular",
        on_change=lambda e: state.update({"difficulty": e.data})
    )

    menu_ui = ft.Column([
        ft.Text("Color Mode", size=14, color="grey500"), mode_radio,
        ft.Text("Difficulty", size=14, color="grey500"), diff_radio,
        ft.Divider(height=10, color="transparent"),
        ft.ElevatedButton("START GAME", on_click=start_game, 
                         style=ft.ButtonStyle(bgcolor="blue700", color="white", padding=20))
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.add(
        ft.Row([exit_button], alignment=ft.MainAxisAlignment.END),
        ft.Column([
            timer_text,
            ft.Row([score_text, best_text], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
            ft.Divider(height=10, color="transparent"),
            menu_ui, grid_container,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)