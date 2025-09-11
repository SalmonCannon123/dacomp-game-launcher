import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

GAMES_FILE = 'games.json'

class AdminTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Ferramenta de Administração do Fliperama v2.0")
        self.root.geometry("800x600")

        self.games = self.load_games()

        # --- Layout ---
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame da lista
        list_frame = tk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(list_frame, text="Lista de Jogos").pack(anchor=tk.W)
        self.listbox = tk.Listbox(list_frame, height=15)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Frame de edição
        edit_frame = tk.Frame(main_frame)
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(edit_frame, text="Detalhes do Jogo").pack(anchor=tk.W)

        # Usamos um grid para alinhar os campos
        fields_grid = tk.Frame(edit_frame, pady=10)
        fields_grid.pack(fill=tk.X)

        tk.Label(fields_grid, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = tk.Entry(fields_grid, width=50)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW)

        tk.Label(fields_grid, text="Comando:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.command_entry = tk.Entry(fields_grid, width=50)
        self.command_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW)

        tk.Label(fields_grid, text="Capa (Cover):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.cover_entry = tk.Entry(fields_grid, width=50)
        self.cover_entry.grid(row=2, column=1, sticky=tk.EW)
        tk.Button(fields_grid, text="Procurar...", command=lambda: self.browse_file(self.cover_entry, "Selecione a imagem da capa")).grid(row=2, column=2)

        tk.Label(fields_grid, text="Fundo (Background):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.background_entry = tk.Entry(fields_grid, width=50)
        self.background_entry.grid(row=3, column=1, sticky=tk.EW)
        tk.Button(fields_grid, text="Procurar...", command=lambda: self.browse_file(self.background_entry, "Selecione a imagem de fundo")).grid(row=3, column=2)
        
        tk.Label(fields_grid, text="Descrição:").grid(row=4, column=0, sticky=tk.NW, pady=2)
        self.description_text = tk.Text(fields_grid, height=5, width=50)
        self.description_text.grid(row=4, column=1, columnspan=2, sticky=tk.EW)

        fields_grid.columnconfigure(1, weight=1)

        # Botões de ação
        button_frame = tk.Frame(root, pady=10)
        button_frame.pack()
        tk.Button(button_frame, text="Novo Jogo", command=self.new_game).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Salvar Jogo", command=self.save_game).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remover Selecionado", command=self.remove_game).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Salvar Tudo no JSON", command=self.save_all_to_json, bg="lightblue").pack(side=tk.LEFT, padx=5)
        
        self.populate_list()
        self.selected_index = None

    def load_games(self):
        if not os.path.exists(GAMES_FILE): return []
        try:
            with open(GAMES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return []

    def populate_list(self):
        self.listbox.delete(0, tk.END)
        for game in self.games:
            self.listbox.insert(tk.END, game.get('name', 'Jogo sem nome'))

    def on_select(self, event):
        selection = self.listbox.curselection()
        if not selection: return
        
        self.selected_index = selection[0]
        game = self.games[self.selected_index]
        
        self.clear_entries()
        self.name_entry.insert(0, game.get('name', ''))
        self.command_entry.insert(0, game.get('command', ''))
        self.cover_entry.insert(0, game.get('cover_image', ''))
        self.background_entry.insert(0, game.get('background_image', ''))
        self.description_text.insert(tk.END, game.get('description', ''))

    def save_game(self):
        if self.selected_index is None:
            messagebox.showwarning("Nenhuma Seleção", "Selecione um jogo para salvar ou crie um novo.")
            return

        name = self.name_entry.get()
        if not name:
            messagebox.showwarning("Campo Obrigatório", "O campo 'Nome' é obrigatório.")
            return

        game_data = {
            'name': name,
            'command': self.command_entry.get(),
            'cover_image': self.cover_entry.get(),
            'background_image': self.background_entry.get(),
            'description': self.description_text.get("1.0", tk.END).strip()
        }

        self.games[self.selected_index] = game_data
        self.populate_list()
        # Reselect the item
        self.listbox.selection_set(self.selected_index)
        messagebox.showinfo("Sucesso", f"Alterações para '{name}' salvas na memória.\nClique em 'Salvar Tudo no JSON' para persistir.")

    def new_game(self):
        self.clear_entries()
        new_game = {'name': 'Novo Jogo', 'command': '', 'cover_image': '', 'background_image': '', 'description': ''}
        self.games.append(new_game)
        new_index = len(self.games) - 1
        self.populate_list()
        self.listbox.selection_set(new_index)
        self.listbox.see(new_index)
        self.on_select(None)
        self.name_entry.focus()
        self.name_entry.selection_range(0, tk.END)


    def remove_game(self):
        if self.selected_index is None or not self.listbox.curselection():
            messagebox.showwarning("Nenhuma Seleção", "Selecione um jogo para remover.")
            return
        
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover o jogo selecionado?"):
            del self.games[self.selected_index]
            self.populate_list()
            self.clear_entries()
            self.selected_index = None

    def save_all_to_json(self):
        try:
            with open(GAMES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.games, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Sucesso", "Lista de jogos salva com sucesso em games.json!")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")

    def browse_file(self, entry_widget, title):
        filepath = filedialog.askopenfilename(
            title=title,
            filetypes=(("Imagens", "*.png *.jpg *.jpeg *.bmp"), ("Todos os arquivos", "*.*"))
        )
        if filepath:
            try:
                relative_path = os.path.relpath(filepath)
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, relative_path)
            except ValueError:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, filepath)

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.command_entry.delete(0, tk.END)
        self.cover_entry.delete(0, tk.END)
        self.background_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminTool(root)
    root.mainloop()