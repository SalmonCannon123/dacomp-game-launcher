import pygame
import json
import subprocess
import sys
import os

# --- Configurações Visuais e de Áudio ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BACKGROUND_COLOR = (15, 15, 20) # Um azul bem escuro
FONT_COLOR = (240, 240, 240)
HIGHLIGHT_COLOR = (255, 200, 80)
DESCRIPTION_COLOR = (180, 180, 200)
GAMES_FILE = 'games.json'

COVER_SIZE = (220, 280)
COVER_SPACING = 50
SELECTED_COVER_SCALE = 1.05

# --- Inicialização ---
pygame.init()
pygame.mixer.init() # Inicializa o mixer de áudio
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DACOMP Fliperama Launcher")

# --- Carregamento de Recursos (Fontes e Sons) ---
try:
    font_title = pygame.font.Font('font/Roboto-Bold.ttf', 58)
    font_desc = pygame.font.Font('font/Roboto-Regular.ttf', 24)
except FileNotFoundError:
    font_title = pygame.font.Font(None, 64)
    font_desc = pygame.font.Font(None, 28)

try:
    sound_navigate = pygame.mixer.Sound('audio/navigate.wav')
    sound_select = pygame.mixer.Sound('audio/select.wav')
    pygame.mixer.music.set_volume(0.5)
except pygame.error as e:
    print(f"Aviso: Não foi possível carregar os arquivos de áudio: {e}")
    sound_navigate = sound_select = None

# --- Funções Auxiliares ---
def load_games():
    try:
        with open(GAMES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [{"name": "Nenhum jogo configurado", "description": "Use a admin_tool.py para adicionar jogos."}]

def launch_game(command):
    if not command: return
    if sound_select: sound_select.play()
    print(f"Executando comando: {command}")
    try:
        subprocess.Popen(command.split())
    except Exception as e:
        print(f"Erro ao executar o jogo: {e}")

def wrap_text(text, font, max_width):
    """Quebra o texto em várias linhas para caber em uma largura máxima."""
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

# --- Loop Principal ---
def main():
    games = load_games()
    loaded_covers = {}
    loaded_backgrounds = {}
    selected_index = 0
    clock = pygame.time.Clock()
    running = True

    # --- Pré-carregamento de imagens ---
    placeholder_cover = pygame.Surface(COVER_SIZE); placeholder_cover.fill((50,50,60))
    placeholder_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); placeholder_bg.fill(BACKGROUND_COLOR)
    
    for i, game in enumerate(games):
        try:
            cover_img = pygame.image.load(game.get('cover_image', '')).convert_alpha()
            loaded_covers[i] = pygame.transform.scale(cover_img, COVER_SIZE)
        except (pygame.error, FileNotFoundError):
            loaded_covers[i] = placeholder_cover
        
        try:
            bg_img = pygame.image.load(game.get('background_image', '')).convert()
            # Efeito de "blur" rápido e barato: diminui e aumenta a imagem
            small_bg = pygame.transform.smoothscale(bg_img, (SCREEN_WIDTH // 20, SCREEN_HEIGHT // 20))
            loaded_backgrounds[i] = pygame.transform.smoothscale(small_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except (pygame.error, FileNotFoundError):
            loaded_backgrounds[i] = None

    # --- Variáveis de Animação ---
    current_bg = placeholder_bg
    target_bg = placeholder_bg
    bg_alpha = 255
    
    scroll_offset_x = 0
    target_scroll_offset_x = 0
    
    current_cover_y = 0
    target_cover_y = 0

    while running:
        # --- Tratamento de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN) and selected_index < len(games) - 1:
                    selected_index += 1
                    if sound_navigate: sound_navigate.play()
                elif (event.key == pygame.K_LEFT or event.key == pygame.K_UP) and selected_index > 0:
                    selected_index -= 1
                    if sound_navigate: sound_navigate.play()
                elif event.key == pygame.K_RETURN and games:
                    launch_game(games[selected_index].get('command'))
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # --- Lógica de Animação e Atualização ---
        # Scroll suave do carrossel de capas
        target_scroll_offset_x = SCREEN_WIDTH / 2 - (selected_index * (COVER_SIZE[0] + COVER_SPACING)) - COVER_SIZE[0] / 2
        scroll_offset_x += (target_scroll_offset_x - scroll_offset_x) * 0.1

        # Transição de Fundo (fade)
        new_target_bg = loaded_backgrounds.get(selected_index) or placeholder_bg
        if target_bg is not new_target_bg:
            current_bg = target_bg.copy() # Salva o fundo antigo
            target_bg = new_target_bg
            bg_alpha = 0 # Inicia o fade-in

        if bg_alpha < 255:
            bg_alpha = min(255, bg_alpha + 15)

        # --- Lógica de Desenho ---
        # 1. Desenha o fundo (antigo e novo com fade)
        screen.blit(current_bg, (0, 0))
        target_bg.set_alpha(bg_alpha)
        screen.blit(target_bg, (0, 0))

        # 2. Desenha o painel de informações
        info_panel_surf = pygame.Surface((SCREEN_WIDTH, 300), pygame.SRCALPHA)
        info_panel_surf.fill((10, 10, 15, 180)) # Fundo semitransparente
        screen.blit(info_panel_surf, (0, 0))
        
        # Nome do Jogo
        title_surf = font_title.render(games[selected_index].get('name', ''), True, FONT_COLOR)
        screen.blit(title_surf, (50, 50))
        
        # Descrição
        desc_text = games[selected_index].get('description', '')
        wrapped_lines = wrap_text(desc_text, font_desc, SCREEN_WIDTH - 100)
        for i, line in enumerate(wrapped_lines):
            desc_surf = font_desc.render(line.strip(), True, DESCRIPTION_COLOR)
            screen.blit(desc_surf, (50, 130 + i * 30))

        # 3. Desenha as Capas (Carrossel)
        cover_y_base = SCREEN_HEIGHT * 0.75
        for i, game in enumerate(games):
            cover_img = loaded_covers[i]
            x_pos = int(scroll_offset_x + i * (COVER_SIZE[0] + COVER_SPACING))
            
            is_selected = (i == selected_index)
            target_cover_y = -80 if is_selected else 0
            
            # Animação suave de subida/descida da capa
            if is_selected:
                current_cover_y += (target_cover_y - current_cover_y) * 0.1
            
            y_pos = int(cover_y_base + (current_cover_y if is_selected else 0) - cover_img.get_height() / 2)
            
            cover_rect = cover_img.get_rect(topleft=(x_pos, y_pos))

            # Efeito de escala e destaque
            if is_selected:
                scaled_size = (int(COVER_SIZE[0] * SELECTED_COVER_SCALE), int(COVER_SIZE[1] * SELECTED_COVER_SCALE))
                scaled_img = pygame.transform.scale(cover_img, scaled_size)
                scaled_rect = scaled_img.get_rect(center=cover_rect.center)
                screen.blit(scaled_img, scaled_rect)
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, scaled_rect, 4, border_radius=5)
            else:
                screen.blit(cover_img, cover_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()