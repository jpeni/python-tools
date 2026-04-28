import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2
from PyPDF2.generic import Transformation
import threading
import os

class PDFBookletConverter:
    def __init__(self, master):
        self.master = master
        self.master.title('PDF Booklet Converter')
        self.master.geometry('600x600')
        self.master.resizable(False, False)
        self.pdf_file = None
        
        self.create_widgets()

    def create_widgets(self):
        # Main container with scrollbar
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text='PDF Booklet & 4-Up Converter', 
                               font=('Arial', 16, 'bold'), fg='#2c3e50')
        title_label.pack(pady=15)
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text='Step 1: Select PDF File', padding=15)
        file_frame.pack(pady=10, fill='x')
        
        self.file_label = tk.Label(file_frame, text='No file selected', fg='gray', font=('Arial', 10))
        self.file_label.pack(pady=5)
        
        self.select_button = tk.Button(file_frame, text='📁 Browse for PDF', command=self.select_file, 
                                       width=30, bg='#3498db', fg='white', padx=10, pady=5)
        self.select_button.pack(pady=5)

        # Format selection section
        format_frame = ttk.LabelFrame(main_frame, text='Step 2: Choose Output Format', padding=15)
        format_frame.pack(pady=10, fill='x')
        
        self.format_var = tk.StringVar(value='2up')
        
        # 2-Up option
        ttk.Radiobutton(format_frame, text='📄 2-Up (2 pages per sheet - Booklet Format)', 
                       variable=self.format_var, value='2up').pack(anchor=tk.W, pady=5)
        tk.Label(format_frame, text='   Ideal for duplex printing and booklet folding', 
                fg='gray', font=('Arial', 9)).pack(anchor=tk.W, padx=20)
        
        # 4-Up option
        ttk.Radiobutton(format_frame, text='📊 4-Up (4 pages per sheet - Grid Format)', 
                       variable=self.format_var, value='4up').pack(anchor=tk.W, pady=5)
        tk.Label(format_frame, text='   All 4 letter pages on 1 sheet • Reduces paper usage', 
                fg='gray', font=('Arial', 9)).pack(anchor=tk.W, padx=20)

        # Options section
        options_frame = ttk.LabelFrame(main_frame, text='Step 3: Optional Settings', padding=15)
        options_frame.pack(pady=10, fill='x')
        
        # Margins option
        margins_frame = tk.Frame(options_frame)
        margins_frame.pack(anchor=tk.W, pady=5)
        tk.Label(margins_frame, text='Page Margins:', font=('Arial', 9)).pack(side=tk.LEFT)
        self.margin_var = tk.StringVar(value='none')
        ttk.Combobox(margins_frame, textvariable=self.margin_var, 
                    values=['none', 'small', 'medium', 'large'], width=12, state='readonly').pack(side=tk.LEFT, padx=5)
        
        # Orientation option for 4-up
        orientation_frame = tk.Frame(options_frame)
        orientation_frame.pack(anchor=tk.W, pady=5)
        tk.Label(orientation_frame, text='4-Up Layout:', font=('Arial', 9)).pack(side=tk.LEFT)
        self.layout_var = tk.StringVar(value='grid')
        ttk.Combobox(orientation_frame, textvariable=self.layout_var, 
                    values=['grid', 'booklet'], width=12, state='readonly').pack(side=tk.LEFT, padx=5)

        # Output location section
        output_frame = ttk.LabelFrame(main_frame, text='Step 4: Output Location', padding=15)
        output_frame.pack(pady=10, fill='x')
        
        self.output_label = tk.Label(output_frame, text='Same location as input file', 
                                    fg='gray', font=('Arial', 9))
        self.output_label.pack(pady=5)
        
        output_button_frame = tk.Frame(output_frame)
        output_button_frame.pack(fill='x')
        tk.Button(output_button_frame, text='Choose Output Location', command=self.choose_output_location,
                 width=20, bg='#95a5a6', fg='white', padx=5, pady=3).pack(side=tk.LEFT, padx=5)

        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text='Conversion Progress', padding=10)
        progress_frame.pack(pady=10, fill='x')
        
        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', 
                                       length=500, mode='determinate', length=100)
        self.progress.pack(fill='x', pady=5)
        
        self.progress_label = tk.Label(progress_frame, text='0%', font=('Arial', 9))
        self.progress_label.pack()

        # Status section
        status_frame = ttk.LabelFrame(main_frame, text='Status', padding=10)
        status_frame.pack(pady=10, fill='x')
        
        self.status_label = tk.Label(status_frame, text='Ready', fg='blue', font=('Arial', 10, 'bold'))        
        self.status_label.pack(anchor=tk.W)

        # Convert button
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        self.convert_button = tk.Button(button_frame, text='🚀 Convert to PDF', 
                                       command=self.convert_pdf, width=30, 
                                       bg='#27ae60', fg='white', font=('Arial', 11, 'bold'),
                                       padx=15, pady=8)
        self.convert_button.pack()
        
        self.output_location = None

    def select_file(self):
        self.pdf_file = filedialog.askopenfilename(
            filetypes=[('PDF files', '*.pdf'), ('All files', '*.*')]
        )
        if self.pdf_file:
            filename = os.path.basename(self.pdf_file)
            self.file_label.config(text=f'✓ Selected: {filename}', fg='green')

    def choose_output_location(self):
        self.output_location = filedialog.askdirectory(title='Choose output folder')
        if self.output_location:
            self.output_label.config(text=f'Output: {self.output_location}', fg='green')

    def convert_pdf(self):
        if not self.pdf_file:
            messagebox.showwarning('No file selected', 'Please select a PDF file to convert.')
            return

        format_type = self.format_var.get()
        self.progress['value'] = 0
        self.progress_label.config(text='0%')
        self.status_label.config(text='Converting...', fg='blue')
        self.master.update_idletasks()

        thread = threading.Thread(target=self.process_conversion, args=(format_type,))
        thread.daemon = True
        thread.start()

    def process_conversion(self, format_type):
        try:
            if format_type == '2up':
                self.convert_2up()
            else:
                self.convert_4up()
        except Exception as e:
            self.status_label.config(text=f'❌ Error: {str(e)}', fg='red')
            messagebox.showerror('Conversion Error', f'An error occurred:\n{str(e)}')

    def convert_2up(self):
        output_dir = self.output_location if self.output_location else os.path.dirname(self.pdf_file)
        output_filename = os.path.basename(self.pdf_file).replace('.pdf', '_2up.pdf')
        output_file = os.path.join(output_dir, output_filename)
        
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
            progress_value = (count / num_pages) * 100
            self.progress['value'] = progress_value
            self.progress_label.config(text=f'{int(progress_value)}%')
            self.master.update_idletasks()

        # Writing the output file
        with open(output_file, 'wb') as f:
            pdf_writer.write(f)

        self.finalize_conversion(output_file)

    def convert_4up(self):
        output_dir = self.output_location if self.output_location else os.path.dirname(self.pdf_file)
        output_filename = os.path.basename(self.pdf_file).replace('.pdf', '_4up.pdf')
        output_file = os.path.join(output_dir, output_filename)
        
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
                self.add_page_to_grid(new_page, pages_to_add[0], 0, new_page_height / 2)
            if len(pages_to_add) > 1:
                self.add_page_to_grid(new_page, pages_to_add[1], new_page_width / 2, new_page_height / 2)
            if len(pages_to_add) > 2:
                self.add_page_to_grid(new_page, pages_to_add[2], 0, 0)
            if len(pages_to_add) > 3:
                self.add_page_to_grid(new_page, pages_to_add[3], new_page_width / 2, 0)

            # Update progress
            progress_value = (page_index / num_pages) * 100
            self.progress['value'] = progress_value
            self.progress_label.config(text=f'{int(progress_value)}%')
            self.master.update_idletasks()

        # Writing the output file
        with open(output_file, 'wb') as f:
            pdf_writer.write(f)

        self.finalize_conversion(output_file)

    def add_page_to_grid(self, target_page, source_page, x_offset, y_offset):
        """Add a scaled page to a specific grid position"""
        scale_x = 0.5
        scale_y = 0.5
        
        transformation = Transformation().scale(sx=scale_x, sy=scale_y).translate(tx=x_offset, ty=y_offset)
        source_page.add_transformation(transformation)
        target_page.merge_page(source_page)

    def finalize_conversion(self, output_file):
        self.status_label.config(text=f'✓ Complete! Saved: {os.path.basename(output_file)}', fg='green')
        self.progress['value'] = 100
        self.progress_label.config(text='100%')
        self.master.update_idletasks()
        messagebox.showinfo('Success', f'PDF converted successfully!\n\nSaved as:\n{output_file}')

if __name__ == '__main__':
    root = tk.Tk()
    app = PDFBookletConverter(root)
    root.mainloop()