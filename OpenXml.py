import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET

class XMLViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Viewer and Editor")
        self.root.configure(bg="#314252")  # Fondo principal
        
        # Treeview con columnas
        self.treeview = ttk.Treeview(root, columns=("Value"), show="tree headings")
        self.treeview.heading("#0", text="Tag")  # Etiqueta
        self.treeview.heading("Value", text="Value")  # Valor
        self.treeview.column("#0", width=250)
        self.treeview.column("Value", width=350)
        self.treeview.pack(fill="both", expand=True, pady=10, padx=10)
        
        # Frame para los botones
        btn_frame = tk.Frame(root, bg="#314252")  # Fondo del frame
        btn_frame.pack(pady=10)

        # Configuración de estilo para botones
        self.btn_style = {  # Cambiado a un atributo de clase
            "bg": "#3E5369",  # Fondo de botón
            "fg": "white",    # Color de texto
            "activebackground": "#1E2A38",  # Fondo activo
            "activeforeground": "white",   # Texto activo
            "relief": "raised",
            "bd": 2,
            "width": 15
        }
        
        load_btn = tk.Button(btn_frame, text="Load XML", command=self.load_xml, **self.btn_style)
        load_btn.pack(side="left", padx=5)
        
        update_btn = tk.Button(btn_frame, text="Update Node", command=self.update_node, **self.btn_style)
        update_btn.pack(side="left", padx=5)
        
        save_btn = tk.Button(btn_frame, text="Save XML", command=self.save_xml, **self.btn_style)
        save_btn.pack(side="left", padx=5)

        save_as_btn = tk.Button(btn_frame, text="Save As New XML", command=self.save_as_new_xml, **self.btn_style)
        save_as_btn.pack(side="left", padx=5)

        clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_screen, **self.btn_style)
        clear_btn.pack(side="left", padx=5)
        
        # Variables internas
        self.xml_tree = None
        self.xml_file = None
        self.unsaved_changes = False  # Bandera para detectar cambios no guardados

    def load_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_path:
            self.treeview.delete(*self.treeview.get_children())
            self.xml_file = file_path
            self.xml_tree = ET.parse(file_path)
            root_element = self.xml_tree.getroot()
            self.populate_treeview(root_element, "")
            self.unsaved_changes = False

    def populate_treeview(self, element, parent):
        tree_id = self.treeview.insert(parent, "end", text=element.tag, values=(element.text,))
        for child in element:
            self.populate_treeview(child, tree_id)

    def update_node(self):
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No node selected!")
            return

        item = selected_item[0]
        tag = self.treeview.item(item, "text")
        current_value = self.treeview.item(item, "values")[0]

        new_value = self.ask_new_value(tag, current_value)
        if new_value is not None:
            self.treeview.item(item, values=(new_value,))
            self.update_xml_tree(item, new_value)
            self.unsaved_changes = True

    def ask_new_value(self, tag, current_value):
        """Solicita un nuevo valor al usuario."""
        new_value_window = tk.Toplevel(self.root)
        new_value_window.title("Update Node Value")
        new_value_window.configure(bg="#314252")  # Fondo del popup
        
        tk.Label(new_value_window, text=f"Editing Tag: {tag}", bg="#314252", fg="white").pack(pady=5)
        tk.Label(new_value_window, text="Current Value:", bg="#314252", fg="white").pack(pady=5)
        tk.Label(new_value_window, text=current_value, fg="cyan", bg="#314252").pack(pady=5)
        tk.Label(new_value_window, text="New Value:", bg="#314252", fg="white").pack(pady=5)
        
        entry = tk.Entry(new_value_window)
        entry.insert(0, current_value)
        entry.pack(pady=5)
        
        def confirm():
            new_value_window.new_value = entry.get()
            new_value_window.destroy()
        
        tk.Button(new_value_window, text="OK", command=confirm, **self.btn_style).pack(pady=5)
        self.root.wait_window(new_value_window)
        
        return getattr(new_value_window, "new_value", None)

    def update_xml_tree(self, treeview_id, new_value):
        element = self.get_xml_element(treeview_id)
        if element is not None:
            element.text = new_value

    def get_xml_element(self, treeview_id):
        path = []
        while treeview_id:
            path.insert(0, self.treeview.item(treeview_id, "text"))
            treeview_id = self.treeview.parent(treeview_id)
        if self.xml_tree is not None:
            element = self.xml_tree.getroot()
            for tag in path[1:]:
                element = element.find(tag)
                if element is None:
                    break
            return element
        return None

    def save_xml(self):
        if self.xml_tree and self.xml_file:
            self.xml_tree.write(self.xml_file)
            self.unsaved_changes = False
            messagebox.showinfo("Info", "XML saved successfully!")

    def save_as_new_xml(self):
        if self.xml_tree:
            file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
            if file_path:
                self.xml_tree.write(file_path)
                self.unsaved_changes = False
                messagebox.showinfo("Info", "XML saved as new file!")

    def clear_screen(self):
        if self.unsaved_changes:
            response = messagebox.askyesno("Unsaved Changes", "Un nodo fue modificado, desea continuar sin guardar?")
            if not response:
                return
        self.treeview.delete(*self.treeview.get_children())
        self.xml_tree = None
        self.xml_file = None
        self.unsaved_changes = False

if __name__ == "__main__":
    root = tk.Tk()
    app = XMLViewer(root)
    root.mainloop()
