import tkinter as tk
import tkinter.ttk as ttk
import urllib.request
import time
import threading
import gc

class tldScrape():
    def __init__(self):
        self.timer = 0.01
        self.tasks = []
        self.mainTasks = []
        self.paused = False
        self.root = tk.Tk()
        self.root.geometry("600x700")
        self.root.protocol("WM_DELETE_WINDOW", self.closeAll)
        self.root.title("TLD Search")
        self.root.resizable(False, False)
        self.root.grid_rowconfigure(3,weight=2)
        self.pause_cond = threading.Condition(threading.Lock())
        self.event = threading.Event()

    def app(self):
        self.domain_label = tk.Label(self.root, text="Domain:")
        self.domain_entry = tk.Entry(self.root)
        self.domain_entry.place(anchor='n', relx=.35, rely=.03)

        self.extract_button = tk.Button(
            self.root, text="Extract TLDs", command=lambda: self.start_extraction())
        self.pause_button = tk.Button(
            self.root, text="Pause", command=lambda: self.pause_extraction())
        self.resume_button = tk.Button(
            self.root, text="Resume", command=lambda: self.resume_extraction())
        self.stop_button = tk.Button(
            self.root, text="Stop", command=lambda: self.stop_extraction())
        self.extract_button.place(anchor='n', relx=.65, rely=.03)
        self.pause_button.place(anchor='center', relx=.25, rely=.125)
        self.resume_button.place(anchor='center', relx=.5, rely=.125)
        self.stop_button.place(anchor='center', relx=.75, rely=.125)

        self.progress = ttk.Progressbar(
            self.root, orient="horizontal", length=600)
        self.results_text = tk.Text(self.root, height=35, width=75)
        self.progress.place(anchor='s', relx=0.5, rely=.195)
        self.results_text.place(anchor='s', relx=0.5, rely=1)
        self.root.mainloop()

    def start_extraction(self):
        self.event.clear()
        self.extract_button.config(state="disabled")
        self.results_text.delete("1.0", tk.END)
        domain = self.domain_entry.get()
        task = threading.Thread(
            name="gabagoo", target=self.extract_tlds, args=(domain,)).start()
        self.mainTasks.append(task)

    def pause_extraction(self):
        if self.paused == False:
            self.paused = True
            self.pause_cond.acquire()
            print("Pause Button Pressed")

    def resume_extraction(self):
        if self.paused == True:
            self.paused = False
            self.pause_cond.notify()
            self.pause_cond.release()
            print("Resume Button Pressed")

    def stop_extraction(self):
        self.event.set()
        self.progress.stop()
        self.extract_button.config(state="normal")
        gc.collect()
        print("Stop Button Pressed")

    def extract_tlds(self, domain):
        try:
            with urllib.request.urlopen("https://publicsuffix.org/list/public_suffix_list.dat") as response:
                data = response.read().decode("utf-8")
                tld_data = data.split("\n")
                tlds = [line for line in tld_data if not line.strip().startswith(
                    '//') and not line.strip().startswith('*')]
                tlds = list(filter(None, tlds))
            count = len(tlds)
            print(f'Loaded {str(count)} TLDs!')
            self.results_text.insert(
                tk.END, 'Loaded ' + str(len(tlds)) + ' TLDs!\n')
            parts = domain.split('.')
            num_parts = len(parts)
            if num_parts == 1:
                secondLevelDomain = domain
            elif num_parts == 2:
                secondLevelDomain = parts[0]
            else:
                secondLevelDomain = parts[1]
            print('Domain: ' + secondLevelDomain)
            self.progress.start()
            self.results_text.insert(
                tk.END, 'Starting Scan of ' + secondLevelDomain + '!\n')
            self.progress.config(maximum=count)
            for i, tld in enumerate(tlds):
                if self.event.is_set():
                    break
                self.progress.config(value=i)
                with self.pause_cond:
                    while self.paused:
                        self.pause_cond.wait()
                    current_server = secondLevelDomain + "." + tld
                    print('thread: ', i, 'domain: ', current_server)
                    try:
                        print(f"Creating Thread for: {current_server}\n")
                        task = threading.Thread(
                            name="goo", target=self.ping_server, args=(current_server,))
                        self.tasks.append(task)
                        task.start()
                    except Exception as e:
                        print(
                            f"Thread Creation Failed: {current_server} Error: {e}\n")
                    finally:
                        time.sleep(self.timer)
                        if len(self.tasks) > 0:
                            for task in self.tasks:
                                task.join()

            self.results_text.insert(tk.END, "TLD extraction complete.\n")
        except Exception as e:
            self.results_text.insert(tk.END, f"An error occurred: {e}\n")
        finally:
            self.progress.stop()
            self.extract_button.config(state="normal")

    def ping_server(self, server: str):
        try:
            server = "http://" + server
            code = urllib.request.urlopen(server).code()
            self.results_text.insert(
                tk.END, f"Ping Successful for: {server} - {code}\n")
            print(f"Ping Successful for: {server} - {code}\n")
            return True
        except Exception as e:
            print(f"Ping Attempt Failed for: {server} Error: {e}\n")
            return False

    def closeAll(self):
        gc.collect()
        print("Garbage Collected!")
        self.root.destroy()
        self.root.quit()
        print(f"Everything Destroyed!")


if __name__ == "__main__":
    tldScrape().app()
