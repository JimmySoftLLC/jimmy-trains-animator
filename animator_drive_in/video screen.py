import tkinter as tk
import vlc

class myframe(tk.Frame):
    def __init__(self, root, width=500, height=400, bd=5):
        super(myframe, self).__init__(root)
        self.grid()
        self.frame = tk.Frame(self, width=800, height=350, bd=5)
        self.frame.configure(bg="black")
        self.frame.grid(row=0, column=0, columnspan=12, padx=8)
        self.play_button = tk.Button(self, text = 'Play', command = self.play)
        self.play_button.grid(row=1, column=0, columnspan=1, padx=8)
        self.stop_button = tk.Button(self, text = 'Pause', command = self.pause)
        self.stop_button.grid(row=1, column=1, columnspan=1, padx=8)
        self.label = tk.Label(self, text = 'Dude' fg="white", bg="black")
        self.label.grid(row=1, column=2, columnspan=1, padx=8)
        
        # self.label = tk.Label(self.frame, text="Playing Video", fg="white", bg="black")
        # self.label.pack(pady=5)

    def play(self):
        i = vlc.Instance('--no-xlib --quiet')
        self.player = i.media_player_new()
        self.player.set_mrl('file:///home/drivein/your_video.mp4')
        xid = self.frame.winfo_id()
        self.player.set_xwindow(xid)
        self.player.play()

    def pause(self):
        try:
            self.player.pause()
        except:
            pass

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Video Frame Tkinter")
    app = myframe(root)
    root.mainloop()

# # Create the main window
# root = tk.Tk()
# root.geometry("400x250")  # Set window size
# root.title("Welcome to My App")  # Set window title

# # Create a StringVar to associate with the label
# text_var = tk.StringVar()
# text_var.set("Hello, World!")

# # Create the label widget with all options
# label = tk.Label(root, 
#                  textvariable=text_var, 
#                  anchor=tk.CENTER,       
#                  bg="lightblue",      
#                  height=3,              
#                  width=30,              
#                  bd=3,                  
#                  font=("Arial", 16, "bold"), 
#                  cursor="hand2",   
#                  fg="red",             
#                  padx=15,               
#                  pady=15,                
#                  justify=tk.CENTER,    
#                  relief=tk.RAISED,     
#                  underline=0,           
#                  wraplength=250         
#                 )

# # Pack the label into the window
# label.pack(pady=20)  # Add some padding to the top


# # Run the main event loop
# root.mainloop()