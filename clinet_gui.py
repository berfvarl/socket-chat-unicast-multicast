import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
from datetime import datetime

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Gelişmiş Sohbet Uygulaması")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # GUI - Üst Panel (Bağlantı durumu ve çıkış butonu)
        top_frame = tk.Frame(master)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = tk.Label(top_frame, text="Durum: Bağlanılmadı", fg="red")
        self.status_label.pack(side=tk.LEFT)

        self.disconnect_btn = tk.Button(top_frame, text="Bağlantıyı Kes", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.RIGHT)

        # Sohbet Alanı
        self.chat_area = scrolledtext.ScrolledText(master, state='disabled', wrap='word', font=('Arial', 10))
        self.chat_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Mesaj Giriş Alanı
        bottom_frame = tk.Frame(master)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.msg_entry = tk.Entry(bottom_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", self.send_message)
        self.msg_entry.bind("<Control-Return>", self.send_message)

        self.send_button = tk.Button(bottom_frame, text="Gönder", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.prompt_username()

    def prompt_username(self):
        self.username = simpledialog.askstring("Kullanıcı Adı", "Kullanıcı adınızı girin:", parent=self.master)
        if self.username:
            try:
                self.sock.connect(("localhost", 5555))
                self.sock.send(self.username.encode())
                threading.Thread(target=self.receive_messages, daemon=True).start()
                self.status_label.config(text=f"Durum: Bağlı ({self.username})", fg="green")
                self.disconnect_btn.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Bağlantı Hatası", f"Sunucuya bağlanılamadı.\n{e}")
                self.master.destroy()
        else:
            self.master.destroy()

    def receive_messages(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode()
                self.display_message(msg)
            except:
                break

    def display_message(self, msg):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

    def send_message(self, event=None):
        msg = self.msg_entry.get().strip()
        if msg:
            try:
                self.sock.send(msg.encode())
                self.display_message(f"{self.username} (Siz): {msg}")
                self.msg_entry.delete(0, tk.END)
            except:
                messagebox.showwarning("Uyarı", "Mesaj gönderilemedi.")

    def disconnect(self):
        try:
            self.sock.close()
        except:
            pass
        self.status_label.config(text="Durum: Bağlantı kesildi", fg="red")
        self.disconnect_btn.config(state=tk.DISABLED)
        self.msg_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)

# Ana uygulama başlatma
if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", client.disconnect)
    root.mainloop()

