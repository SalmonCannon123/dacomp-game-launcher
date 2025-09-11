import pygame
import json
import subprocess
import sys

# --- Configurações ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
BACKGROUND_COLOR = (30, 30, 30)
FONT_COLOR = (240, 240, 240)
HIGHLIGHT_COLOR = (200, 150, 0)
GAMES_FILE = 'games.json'
COVER_SIZE = (200, 250)
PLACEHOLDER_COVER = 'covers/placeholder.png'

# --- Inicialização do Pygame ---
pygame.init()
pygame.joystick.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DACOMP Fliperama Launcher")
font_large = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)

# Verifica se há joysticks conectados
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
if joysticks:
    print(f"Joystick '{joysticks[0].get_name()}' detectado.")

# --- Funções Auxiliares ---
def load_games():
    """Carrega a lista de jogos do arquivo JSON."""
    try:
        with open(GAMES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def launch_game(command):
    """Executa o comando para lançar um jogo."""
    print(f"Executando comando: {command}")
    try:
        # Usamos Popen para não bloquear o launcher.
        # O comando é dividido para funcionar melhor no Linux.
        subprocess.Popen(command.split())
    except Exception as e:
        print(f"Erro ao executar o jogo: {e}")

# --- Loop Principal ---
def main():
    games = load_games()
    loaded_covers = {}
    selected_index = 0
    clock = pygame.time.Clock()
    running = True

    # Pré-carrega as capas
    for i, game in enumerate(games):
        try:
            cover = pygame.image.load(game['cover_image']).convert()
            loaded_covers[i] = pygame.transform.scale(cover, COVER_SIZE)
        except pygame.error:
            # Se a capa não for encontrada, usa um placeholder
            cover = pygame.image.load(PLACEHOLDER_COVER).convert()
            loaded_covers[i] = pygame.transform.scale(cover, COVER_SIZE)

    while running:
        # --- Tratamento de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Eventos de Teclado (para desenvolvimento)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN and selected_index < len(games) - 1:
                    selected_index += 1
                elif event.key == pygame.K_UP and selected_index > 0:
                    selected_index -= 1
                elif event.key == pygame.K_RETURN: # Tecla Enter
                    if games:
                        launch_game(games[selected_index]['command'])
                elif event.key == pygame.K_ESCAPE:
                    running = False

            # Eventos de Joystick (o principal para o fliperama)
            if event.type == pygame.JOYAXISMOTION:
                # Eixo 1 é geralmente o direcional vertical
                if event.axis == 1:
                    if event.value > 0.5 and selected_index < len(games) - 1:
                        selected_index += 1
                        pygame.time.wait(150) # Pequeno delay para não pular vários jogos
                    elif event.value < -0.5 and selected_index > 0:
                        selected_index -= 1
                        pygame.time.wait(150)

            if event.type == pygame.JOYBUTTONDOWN:
                # Botão 0 é geralmente o botão 'A' ou de confirmação
                if event.button == 0:
                    if games:
                        launch_game(games[selected_index]['command'])

        # --- Lógica de Desenho ---
        screen.fill(BACKGROUND_COLOR)

        # Desenha a lista de jogos
        if not games:
            text_surf = font_large.render("Nenhum jogo encontrado!", True, FONT_COLOR)
            screen.blit(text_surf, (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, 100))
        else:
            for i, game in enumerate(games):
                # Posição do item na lista
                y_pos = 100 + i * 80
                
                # Desenha o retângulo de seleção
                if i == selected_index:
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR, (50, y_pos - 10, SCREEN_WIDTH - 100, 70), 3)

                # Desenha o nome do jogo
                text_surf = font_large.render(game['name'], True, FONT_COLOR)
                screen.blit(text_surf, (80, y_pos))

            # Mostra a capa do jogo selecionado
            if selected_index < len(loaded_covers):
                cover_rect = loaded_covers[selected_index].get_rect(center=(SCREEN_WIDTH * 0.75, SCREEN_HEIGHT / 2))
                screen.blit(loaded_covers[selected_index], cover_rect)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()