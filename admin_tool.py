import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

GAMES_FILE = 'games.json'

class AdminTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Ferramenta de Administração do Fliperama")

        self.games = self.load_games()

        # --- Layout ---
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Lista de jogos
        self.listbox = tk.Listbox(frame, height=15)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Painel de edição
        edit_frame = tk.Frame(root, padx=10)
        edit_frame.pack(fill=tk.X, expand=True)
        
        tk.Label(edit_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W)
        self.name_entry = tk.Entry(edit_frame, width=50)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW)

        tk.Label(edit_frame, text="Comando:").grid(row=1, column=0, sticky=tk.W)
        self.command_entry = tk.Entry(edit_frame, width=50)
        self.command_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW)

        tk.Label(edit_frame, text="Capa:").grid(row=2, column=0, sticky=tk.W)
        self.cover_entry = tk.Entry(edit_frame, width=50)
        self.cover_entry.grid(row=2, column=1, sticky=tk.EW)
        tk.Button(edit_frame, text="Procurar...", command=self.browse_cover).grid(row=2, column=2)

        # Botões de ação
        button_frame = tk.Frame(root, pady=10)
        button_frame.pack()
        tk.Button(button_frame, text="Adicionar Jogo", command=self.add_game).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remover Selecionado", command=self.remove_game).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Salvar Alterações", command=self.save_games).pack(side=tk.LEFT, padx=5)
        
        self.populate_list()

    def load_games(self):
        if not os.path.exists(GAMES_FILE):
            return []
        try:
            with open(GAMES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def populate_list(self):
        self.listbox.delete(0, tk.END)
        for game in self.games:
            self.listbox.insert(tk.END, game['name'])

    def on_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        game = self.games[index]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, game['name'])
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, game['command'])
        self.cover_entry.delete(0, tk.END)
        self.cover_entry.insert(0, game['cover_image'])

    def add_game(self):
        name = self.name_entry.get()
        command = self.command_entry.get()
        cover = self.cover_entry.get()
        
        if not all([name, command, cover]):
            messagebox.showwarning("Campos Vazios", "Por favor, preencha todos os campos.")
            return

        new_game = {'name': name, 'cover_image': cover, 'command': command}
        self.games.append(new_game)
        self.populate_list()
        self.clear_entries()

    def remove_game(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Nenhuma Seleção", "Selecione um jogo para remover.")
            return
        
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover o jogo selecionado?"):
            del self.games[selection[0]]
            self.populate_list()
            self.clear_entries()

    def save_games(self):
        try:
            with open(GAMES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.games, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Sucesso", "Lista de jogos salva com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")

    def browse_cover(self):
        filepath = filedialog.askopenfilename(
            title="Selecione a imagem da capa",
            filetypes=(("Imagens", "*.png *.jpg *.jpeg *.bmp"), ("Todos os arquivos", "*.*"))
        )
        if filepath:
            # Converte para caminho relativo se estiver dentro da pasta do projeto
            try:
                relative_path = os.path.relpath(filepath)
                self.cover_entry.delete(0, tk.END)
                self.cover_entry.insert(0, relative_path)
            except ValueError: # Ocorre se estiver em um drive diferente (Windows)
                self.cover_entry.delete(0, tk.END)
                self.cover_entry.insert(0, filepath)


    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.command_entry.delete(0, tk.END)
        self.cover_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminTool(root)
    root.mainloop()