import flet as ft
import random

def main(page: ft.Page):
    # 1. 기본 앱 설정 (iOS/Mac 느낌의 다크모드)
    page.title = "Kuku Kube: Designer Edition"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 800
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30

    score = 0
    level = 2  # 시작 그리드 (2x2)

    # UI 요소들
    score_text = ft.Text(f"SCORE: {score}", size=40, weight="bold", color="white")
    grid_container = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def generate_colors(level):
        # 디자이너의 감각: 너무 쨍하지 않은 파스텔톤 랜덤 베이스 컬러
        r = random.randint(60, 200)
        g = random.randint(60, 200)
        b = random.randint(60, 200)
        base = f"#{r:02x}{g:02x}{b:02x}"
        
        # 난이도 조절: 레벨이 높을수록 차이(diff)가 줄어들어 찾기 힘들어짐
        diff = max(4, 60 - (level * 3)) 
        target = f"#{min(255, r+diff):02x}{min(255, g+diff):02x}{min(255, b+diff):02x}"
        return base, target

    def on_tile_click(e):
        nonlocal score, level
        if e.control.data == "target":
            score += 1
            # 5점마다 그리드 크기 증가 (최대 10x10)
            if score % 5 == 0:
                level = min(10, level + 1)
            render_game()
        else:
            # 틀리면 살짝 흔들리는 효과 (점수 감점도 가능)
            page.snack_bar = ft.SnackBar(ft.Text("Oops! Try again."), open=True)
            page.update()

    def render_game():
        score_text.value = f"SCORE: {score}"
        grid_container.controls.clear()
        
        base_color, target_color = generate_colors(level)
        target_index = random.randint(0, (level * level) - 1)

        # 그리드 생성
        tile_size = (380 - (level * 8)) / level
        
        for i in range(level):
            row = ft.Row(spacing=8, alignment=ft.MainAxisAlignment.CENTER)
            for j in range(level):
                current_idx = i * level + j
                is_target = current_idx == target_index
                
                row.controls.append(
                    ft.Container(
                        width=tile_size,
                        height=tile_size,
                        bgcolor=target_color if is_target else base_color,
                        border_radius=10, # 둥근 모서리 디자인
                        on_click=on_tile_click,
                        data="target" if is_target else "normal",
                        animate_scale=ft.Animation(300, "bounceOut"),
                        on_hover=lambda e: setattr(e.control, "opacity", 0.8 if e.data == "true" else 1)
                    )
                )
            grid_container.controls.append(row)
        page.update()

    # 화면 구성
    page.add(
        ft.Column([
            ft.Text("Color Sensitivity Test", size=16, color="grey500"),
            score_text,
            ft.Divider(height=40, color="transparent"),
            grid_container,
            ft.ElevatedButton("RESET", on_click=lambda _: reset_game())
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    def reset_game():
        nonlocal score, level
        score = 0
        level = 2
        render_game()

    render_game()

# 실행
ft.app(target=main)