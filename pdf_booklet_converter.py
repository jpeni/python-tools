import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2
from PyPDF2.generic import RectangleObject, Transformation
import threading
import os

class PDFBookletConverter:
    def __init__(self, master):
        self.master = master
        self.master.title('PDF Booklet Converter')
        self.master.geometry('500x450')
        self.pdf_file = None
        
        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.master, text='PDF Booklet Converter', font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # File selection
        self.file_label = tk.Label(self.master, text='No file selected', fg='gray')
        self.file_label.pack(pady=5)
        
        self.select_button = tk.Button(self.master, text='Select PDF File', command=self.select_file, width=30)
        self.select_button.pack(pady=10)

        # Format selection frame
        format_frame = ttk.LabelFrame(self.master, text='Output Format', padding=10)
        format_frame.pack(pady=10, padx=20, fill='x')
        
        self.format_var = tk.StringVar(value='2up')
        
        ttk.Radiobutton(format_frame, text='2-Up (2 pages per sheet)', variable=self.format_var, value='2up').pack(anchor=tk.W)
        ttk.Radiobutton(format_frame, text='4-Up (4 pages per sheet)', variable=self.format_var, value='4up').pack(anchor=tk.W)

        # Info frame
        info_frame = ttk.LabelFrame(self.master, text='Information', padding=10)
        info_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        info_text = (
            '2-Up: 2 pages side-by-side (landscape)\n'
            '  • Ideal for booklet printing\n'
            '  • Print with duplex enabled\n\n'
            '4-Up: 4 pages in 2x2 grid (landscape)\n'
            '  • 4 letter pages on 1 sheet\n'
            '  • Reduces paper usage'
        )
        tk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)

        # Convert button
        self.convert_button = tk.Button(self.master, text='Convert to PDF', command=self.convert_pdf, width=30, bg='green', fg='white')
        self.convert_button.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.master, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=10, padx=20, fill='x')

        # Status label
        self.status_label = tk.Label(self.master, text='Status: Ready', fg='blue')        
        self.status_label.pack(pady=10)

    def select_file(self):
        self.pdf_file = filedialog.askopenfilename(
            filetypes=[('PDF files', '*.pdf'), ('All files', '*.*')]
        )
        if self.pdf_file:
            filename = os.path.basename(self.pdf_file)
            self.file_label.config(text=f'Selected: {filename}', fg='black')

    def convert_pdf(self):
        if not self.pdf_file:
            messagebox.showwarning('No file selected', 'Please select a PDF file to convert.')
            return

        format_type = self.format_var.get()
        self.progress['value'] = 0
        self.status_label.config(text='Converting...', fg='blue')
        self.master.update_idletasks()

        thread = threading.Thread(target=self.process_conversion, args=(format_type,))
        thread.start()

    def process_conversion(self, format_type):
        try:
            if format_type == '2up':
                self.convert_2up()
            else:
                self.convert_4up()
        except Exception as e:
            self.status_label.config(text=f'Error: {str(e)}', fg='red')
            messagebox.showerror('Conversion Error', f'An error occurred:\n{str(e)}')

    def convert_2up(self):
        output_file = self.pdf_file.replace('.pdf', '_2up.pdf')
        pdf_reader = PyPDF2.PdfReader(self.pdf_file)
        pdf_writer = PyPDF2.PdfWriter()

        num_pages = len(pdf_reader.pages)
        count = 0

        # Arranging pages for 2-up booklet printing
        for i in range(0, num_pages, 2):
            if i + 1 < num_pages:
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

        self.finalize_conversion(output_file)

    def convert_4up(self):
        output_file = self.pdf_file.replace('.pdf', '_4up.pdf')
        pdf_reader = PyPDF2.PdfReader(self.pdf_file)
        pdf_writer = PyPDF2.PdfWriter()

        num_pages = len(pdf_reader.pages)
        page_index = 0

        # Letter size: 8.5" x 11" = 612 x 792 points
        # 4-up landscape: 11" x 8.5" = 792 x 612 points
        new_page_width = 792
        new_page_height = 612

        while page_index < num_pages:
            # Create a new blank page
            new_page = pdf_writer.add_blank_page(width=new_page_width, height=new_page_height)
            
            # Get 4 pages (or fewer if at the end)
            pages_to_add = []
            for j in range(4):
                if page_index < num_pages:
                    pages_to_add.append(pdf_reader.pages[page_index])
                    page_index += 1

            # Add pages in 2x2 grid
            # Top-left, Top-right, Bottom-left, Bottom-right
            if len(pages_to_add) > 0:
                # Top-left
                self.add_page_to_grid(new_page, pages_to_add[0], 0, new_page_height / 2)
            if len(pages_to_add) > 1:
                # Top-right
                self.add_page_to_grid(new_page, pages_to_add[1], new_page_width / 2, new_page_height / 2)
            if len(pages_to_add) > 2:
                # Bottom-left
                self.add_page_to_grid(new_page, pages_to_add[2], 0, 0)
            if len(pages_to_add) > 3:
                # Bottom-right
                self.add_page_to_grid(new_page, pages_to_add[3], new_page_width / 2, 0)

            # Update progress
            self.progress['value'] = (page_index / num_pages) * 100
            self.master.update_idletasks()

        # Writing the output file
        with open(output_file, 'wb') as f:
            pdf_writer.write(f)

        self.finalize_conversion(output_file)

    def add_page_to_grid(self, target_page, source_page, x_offset, y_offset):
        """Add a scaled page to a specific grid position"""
        # Scale to fit in half the page dimensions
        scale_x = 0.5
        scale_y = 0.5
        
        # Create transformation: scale and translate
        transformation = Transformation().scale(sx=scale_x, sy=scale_y).translate(tx=x_offset, ty=y_offset)
        source_page.add_transformation(transformation)
        target_page.merge_page(source_page)

    def finalize_conversion(self, output_file):
        self.status_label.config(text=f'Conversion complete! Saved as: {os.path.basename(output_file)}', fg='green')
        self.progress['value'] = 100
        self.master.update_idletasks()
        messagebox.showinfo('Success', f'PDF converted successfully!\n\nSaved as:\n{output_file}')

if __name__ == '__main__':
    root = tk.Tk()
    app = PDFBookletConverter(root)
    root.mainloop()