import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, Menu
from main import main
import config
import os
import requests
import threading
from queue import Queue, Empty
from urllib.parse import urlparse
import json
from tkinter import font as tkfont

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        """Display text in tooltip window"""
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        """Hide tooltip window"""
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Web Scraper")
        self.root.geometry("1000x800")
        
        # Configure theme
        self.theme = "light"
        self.configure_theme()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create menu bar
        self.create_menu()
        
        # Create main container
        self.mainframe = ttk.Frame(root, padding="20")
        self.mainframe.grid(column=0, row=0, sticky="NSEW")
        self.mainframe.columnconfigure(0, weight=1)
        
        # Input Section
        input_frame = ttk.LabelFrame(self.mainframe, text="Scraping Settings", padding="10")
        input_frame.grid(column=0, row=0, sticky="EW", pady=5)
        input_frame.columnconfigure(1, weight=1)
        
        # URL input
        ttk.Label(input_frame, text="Website URL:").grid(column=0, row=0, sticky="W")
        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.grid(column=1, row=0, sticky="EW", padx=5)
        self.url_entry.insert(0, "https://")
        ToolTip(self.url_entry, "Enter the full URL of the website you want to scrape")

        # Output directory
        ttk.Label(input_frame, text="Output Directory:").grid(column=0, row=1, sticky="W")
        self.output_entry = ttk.Entry(input_frame, width=50)
        self.output_entry.grid(column=1, row=1, sticky="EW", padx=5)
        self.output_entry.insert(0, config.OUTPUT_DIR)
        ToolTip(self.output_entry, "Select where to save the scraped content")
        browse_btn = ttk.Button(input_frame, text="Browse...", command=self.select_output_dir)
        browse_btn.grid(column=2, row=1, padx=5)
        ToolTip(browse_btn, "Choose a directory to save scraped files")

        # Options frame
        options_frame = ttk.Frame(input_frame)
        options_frame.grid(column=0, row=2, columnspan=3, sticky="EW", pady=5)
        
        # Depth control
        ttk.Label(options_frame, text="Max Depth:").grid(column=0, row=0, sticky="W")
        self.depth_var = tk.IntVar(value=1)
        depth_spin = ttk.Spinbox(options_frame, from_=1, to=10, textvariable=self.depth_var, width=5)
        depth_spin.grid(column=1, row=0, padx=5)
        ToolTip(depth_spin, "Set how many levels deep to follow links (1=current page only)")

        # Thread control
        ttk.Label(options_frame, text="Threads:").grid(column=2, row=0, padx=10, sticky="W")
        self.threads_var = tk.IntVar(value=config.MAX_WORKERS)
        threads_spin = ttk.Spinbox(options_frame, from_=1, to=10, textvariable=self.threads_var, width=5)
        threads_spin.grid(column=3, row=0)
        ToolTip(threads_spin, "Number of parallel threads to use for scraping")

        # Content type filters
        ttk.Label(options_frame, text="Content Types:").grid(column=4, row=0, padx=10, sticky="W")
        self.content_types = {
            'text': tk.BooleanVar(value=True),
            'images': tk.BooleanVar(value=True),
            'tables': tk.BooleanVar(value=True),
            'links': tk.BooleanVar(value=True)
        }
        text_cb = ttk.Checkbutton(options_frame, text="Text", variable=self.content_types['text'])
        text_cb.grid(column=5, row=0, padx=5)
        ToolTip(text_cb, "Extract text content from pages")
        
        images_cb = ttk.Checkbutton(options_frame, text="Images", variable=self.content_types['images'])
        images_cb.grid(column=6, row=0, padx=5)
        ToolTip(images_cb, "Extract image URLs from pages")
        
        tables_cb = ttk.Checkbutton(options_frame, text="Tables", variable=self.content_types['tables'])
        tables_cb.grid(column=7, row=0, padx=5)
        ToolTip(tables_cb, "Extract table data from pages")
        
        links_cb = ttk.Checkbutton(options_frame, text="Links", variable=self.content_types['links'])
        links_cb.grid(column=8, row=0, padx=5)
        ToolTip(links_cb, "Follow and extract links from pages")

        # Start/Stop buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(column=0, row=3, columnspan=3, pady=10)
        self.start_btn = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_btn.grid(column=0, row=0, padx=5)
        ToolTip(self.start_btn, "Begin scraping the website")
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_scraping, state="disabled")
        self.stop_btn.grid(column=1, row=0, padx=5)
        ToolTip(self.stop_btn, "Stop the current scraping process")

        # Progress Section
        progress_frame = ttk.LabelFrame(self.mainframe, text="Progress", padding="10")
        progress_frame.grid(column=0, row=1, sticky="EW", pady=5)
        progress_frame.columnconfigure(0, weight=1)

        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
        ToolTip(self.progress, "Shows the progress of the current scraping job")
        self.progress.grid(column=0, row=0, sticky="EW")

        # Status label
        self.status = ttk.Label(progress_frame, text="Ready")
        self.status.grid(column=0, row=1, pady=5)
        ToolTip(self.status, "Current status of the scraper")

        # Statistics frame
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(column=0, row=2, sticky="EW", pady=5)
        
        self.total_label = ttk.Label(stats_frame, text="Total pages: 0")
        self.total_label.grid(column=0, row=0, padx=10)
        ToolTip(self.total_label, "Total number of pages discovered")
        
        self.success_label = ttk.Label(stats_frame, text="Successful: 0")
        self.success_label.grid(column=1, row=0, padx=10)
        ToolTip(self.success_label, "Number of pages successfully scraped")
        
        self.failed_label = ttk.Label(stats_frame, text="Failed: 0")
        self.failed_label.grid(column=2, row=0, padx=10)
        ToolTip(self.failed_label, "Number of pages that failed to scrape")

        # Results Section
        results_frame = ttk.LabelFrame(self.mainframe, text="Extracted Data", padding="10")
        results_frame.grid(column=0, row=2, sticky="NSEW", pady=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            width=100,
            height=20,
            wrap=tk.WORD,
            font=tkfont.Font(family="Consolas", size=10)
        )
        self.results_text.grid(column=0, row=0, sticky="NSEW")
        self.results_text.config(state='disabled')
        ToolTip(self.results_text, "Displays extracted content in real-time")

        # Logs Section
        logs_frame = ttk.LabelFrame(self.mainframe, text="Logs", padding="10")
        logs_frame.grid(column=0, row=3, sticky="NSEW", pady=5)
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame,
            width=100,
            height=10,
            wrap=tk.WORD,
            font=tkfont.Font(family="Consolas", size=9)
        )
        self.logs_text.grid(column=0, row=0, sticky="NSEW")
        self.logs_text.config(state='disabled')
        ToolTip(self.logs_text, "Displays logs and error messages")
        
        # Configure grid weights for better resizing
        self.mainframe.rowconfigure(0, weight=0)
        self.mainframe.rowconfigure(1, weight=0)
        self.mainframe.rowconfigure(2, weight=1)
        self.mainframe.rowconfigure(3, weight=1)

        # Message queue for thread communication
        self.queue = Queue()
        self.scraping_active = False

    def create_menu(self):
        """Create menu bar"""
        menubar = Menu(self.root)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_command(label="Export Logs", command=self.export_logs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view_menu)
        
        self.root.config(menu=menubar)

    def configure_theme(self):
        """Configure theme colors"""
        if self.theme == "dark":
            self.root.configure(bg="#2d2d2d")
            ttk.Style().theme_use('alt')
        else:
            self.root.configure(bg="white")
            ttk.Style().theme_use('clam')

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.theme = "dark" if self.theme == "light" else "light"
        self.configure_theme()

    def export_results(self):
        """Export results to file"""
        if not self.results_text.get("1.0", "end-1c"):
            messagebox.showwarning("Warning", "No results to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get("1.0", "end-1c"))
                messagebox.showinfo("Success", "Results exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")

    def export_logs(self):
        """Export logs to file"""
        if not self.logs_text.get("1.0", "end-1c"):
            messagebox.showwarning("Warning", "No logs to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.get("1.0", "end-1c"))
                messagebox.showinfo("Success", "Logs exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {str(e)}")

    def select_output_dir(self):
        """Select output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory)

    def start_scraping(self):
        """Handle the start scraping button click"""
        if self.scraping_active:
            return

        url = self.url_entry.get().strip()
        output_dir = self.output_entry.get().strip()

        if not all([url, output_dir]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        # Validate URL format
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError("Invalid URL format")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid URL: {str(e)}")
            return

        # Validate and create output directory
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create output directory: {str(e)}")
            return

        # Update config
        config.OUTPUT_DIR = os.path.abspath(output_dir)
        config.MAX_WORKERS = self.threads_var.get()

        # Verify URL is accessible
        try:
            response = requests.head(url, timeout=5)
            if response.status_code >= 400:
                messagebox.showerror("Error", f"URL returned status {response.status_code}")
                return
        except Exception as e:
            messagebox.showerror("Error", f"URL verification failed: {str(e)}")
            return

        # Clear previous results and logs
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
        
        self.logs_text.config(state='normal')
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.config(state='disabled')

        # Initialize scraping state
        self.scraping_active = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status.config(text="Scraping in progress...")
        self.progress.config(mode="indeterminate")
        self.progress.start()
        
        # Clear previous statistics
        self.total_label.config(text="Total pages: 0")
        self.success_label.config(text="Successful: 0")
        self.failed_label.config(text="Failed: 0")
        
        # Start scraping in separate thread
        self.scrape_thread = threading.Thread(
            target=self.run_scraping,
            args=(url,),
            daemon=True
        )
        self.scrape_thread.start()
        
        # Start checking for updates
        self.root.after(100, self.process_queue)
        
    def stop_scraping(self):
        """Stop the scraping process"""
        self.scraping_active = False
        self.status.config(text="Stopping...")
        
    def run_scraping(self, url):
        """Run the scraping process in a separate thread"""
        try:
            result = main(url, self.queue, self.depth_var.get())
            self.queue.put(("complete", result))
        except Exception as e:
            self.queue.put(("error", str(e)))
            
    def process_queue(self):
        """Process messages from the scraping thread"""
        try:
            while True:
                msg_type, content = self.queue.get_nowait()
                
                if msg_type == "complete":
                    self.finish_scraping(success=True)
                    
                elif msg_type == "error":
                    self.finish_scraping(success=False, error=content)
                    
                elif msg_type == "progress":
                    self.total_label.config(text=f"Total pages: {content['total']}")
                    self.success_label.config(text=f"Successful: {content['success']}")
                    self.failed_label.config(text=f"Failed: {content['failed']}")
                    self.progress.config(value=content['success'], maximum=content['total'])
                    
                elif msg_type == "data":
                    self.results_text.config(state='normal')
                    self.results_text.insert(tk.END, content + "\n")
                    self.results_text.config(state='disabled')
                    self.results_text.see(tk.END)
                    
                elif msg_type == "log":
                    self.logs_text.config(state='normal')
                    self.logs_text.insert(tk.END, content + "\n")
                    self.logs_text.config(state='disabled')
                    self.logs_text.see(tk.END)
                    
        except Empty:
            pass
            
        # Schedule next check if still active
        if self.scraping_active:
            self.root.after(100, self.process_queue)

    def finish_scraping(self, success=True, error=None):
        """Finish the scraping process"""
        self.scraping_active = False
        self.progress.stop()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        if success:
            self.status.config(text="Scraping complete!")
            messagebox.showinfo("Success", "Scraping completed successfully!")
        else:
            self.status.config(text="Scraping failed")
            messagebox.showerror("Error", f"Scraping failed: {error}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()