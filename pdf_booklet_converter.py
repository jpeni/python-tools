import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2
import threading

class PDFBookletConverter:
    def __init__(self, master):
        self.master = master
        self.master.title('PDF Booklet Converter')
        self.master.geometry('400x300')

        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.master, text='Select a PDF file to convert to booklet:')
        self.label.pack(pady=10)

        self.select_button = tk.Button(self.master, text='Select PDF', command=self.select_file)
        self.select_button.pack(pady=10)

        self.convert_button = tk.Button(self.master, text='Convert to Booklet', command=self.convert_pdf)
        self.convert_button.pack(pady=10)

        self.progress = ttk.Progressbar(self.master, orient='horizontal', length=300, mode='determinate')
        self.progress.pack(pady=20)

        self.status_label = tk.Label(self.master, text='Status: ')        
        self.status_label.pack(pady=10)

    def select_file(self):
        self.pdf_file = filedialog.askopenfilename(filetypes=[('PDF files', '*.pdf')])
        if self.pdf_file:
            self.status_label.config(text='Selected: ' + self.pdf_file)

    def convert_pdf(self):
        if not hasattr(self, 'pdf_file'):
            messagebox.showwarning('No file selected', 'Please select a PDF file to convert.')
            return

        self.progress['value'] = 0
        self.status_label.config(text='Converting...')

        thread = threading.Thread(target=self.process_conversion)
        thread.start()

    def process_conversion(self):
        output_file = self.pdf_file.replace('.pdf', '_booklet.pdf')
        pdf_reader = PyPDF2.PdfReader(self.pdf_file)
        pdf_writer = PyPDF2.PdfWriter()

        num_pages = len(pdf_reader.pages)
        count = 0

        # Arranging pages for booklet printing
        for i in range(0, num_pages, 2):
            if i + 1 < num_pages:
                # Each pair of pages is arranged like this:
                # Last page of the first half, First page of the second half
                pdf_writer.add_page(pdf_reader.pages[num_pages - i - 1])
                pdf_writer.add_page(pdf_reader.pages[i])
                count += 2
            else:
                pdf_writer.add_page(pdf_reader.pages[num_pages - i - 1])
                count += 1

            # Update progress
            self.progress['value'] = (count / num_pages) * 100
            self.master.update_idletasks()

        # Writing the output file
        with open(output_file, 'wb') as f:
            pdf_writer.write(f)

        self.status_label.config(text='Conversion complete! Output saved as: ' + output_file)

        # Reset progress
        self.progress['value'] = 100

if __name__ == '__main__':
    root = tk.Tk()
    app = PDFBookletConverter(root)
    root.mainloop()