import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog, simpledialog, messagebox
from aes import AES
from aes import unpad
from imagehide import encode
from imageextract import decode

# Define the uploads folder path
UPLOADS_FOLDER = "uploads"

def show_error(message):
    messagebox.showerror("Error", message)

def encrypt_message():
    text = simpledialog.askstring("Input", "Enter the text to be encrypted:")
    key = get_key("encryption")
    iv = get_iv()
    if key and iv:
        obj = AES(key)
        cipher = obj.encrypt_cbc(text, iv)
        enctext = ''.join(chr(j) for i in cipher for j in i)
        messagebox.showinfo("Encrypted Message", f"Here is your encrypted message: {enctext}")

def decrypt_message():
    messagebox.showinfo("Note", "A list needs to be passed as encrypted text. Modify code accordingly.")
    key = get_key("decryption")
    iv = get_iv()
    if key and iv:
        cipher = [[82, 214, 73, 255, 189, 148, 31, 109, 36, 213, 241, 19, 240, 128, 113, 142],
                  [248, 241, 148, 140, 143, 63, 222, 195, 202, 210, 244, 74, 102, 0, 190, 200],
                  [29, 45, 179, 186, 183, 88, 115, 91, 115, 240, 60, 133, 170, 156, 139, 215]]
        obj = AES(key)
        try:
            msg = obj.decrypt_cbc(cipher, iv)
            msgstr = ''.join(chr(j) for i in msg for j in i)
            messagebox.showinfo("Decrypted Message", f"Here is your decrypted message: {unpad(msgstr)}")
        except ValueError:
            show_error("Decryption failed! The key or IV may be incorrect.")
# Global variables to store key and IV for validation
stored_key = None
stored_iv = None

def encrypt_message_and_hide():
    global stored_key, stored_iv
    text = simpledialog.askstring("Input", "Enter the text to be encrypted:")
    key = get_key("encryption")
    iv = get_iv()
    if key and iv:
        stored_key = key  # Store the key for validation
        stored_iv = iv  # Store the IV for validation

        obj = AES(key)
        cipher = obj.encrypt_cbc(text, iv)
        img_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image files", "*.jpg *.bmp")])

        if img_path:
            dialog = tk.Toplevel(root)
            dialog.title("Image Preview")
            dialog.geometry("400x300")

            img = Image.open(img_path)
            img_resized = img.resize((300, 200), Image.Resampling.LANCZOS)
            img_display = ImageTk.PhotoImage(img_resized)

            img_label = tk.Label(dialog, image=img_display)
            img_label.image = img_display
            img_label.pack(pady=10)

            def on_ok():
                dialog.destroy()
                img_filename = os.path.basename(img_path)
                saved_img_path = os.path.join(UPLOADS_FOLDER, img_filename)
                os.makedirs(UPLOADS_FOLDER, exist_ok=True)
                img.save(saved_img_path)

                encode(saved_img_path, cipher)
                messagebox.showinfo("Success", f"Message encrypted and hidden in {saved_img_path}!")

                dialog.destroy()
                

            def on_cancel():
                dialog.destroy()

            button_ok = ttk.Button(dialog, text="OK", command=on_ok)
            button_ok.pack(side=tk.LEFT, padx=20, pady=10)
            button_cancel = ttk.Button(dialog, text="Cancel", command=on_cancel)
            button_cancel.pack(side=tk.RIGHT, padx=20, pady=10)

            dialog.grab_set()
            dialog.transient(root)

def decrypt_image():
    global stored_key, stored_iv
    img_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image files", "*.jpg *.bmp")])

    if img_path:
        if "hidden.bmp" not in os.path.basename(img_path):
            show_error("Please enter the encrypted image.")
            return

        dialog = tk.Toplevel(root)
        dialog.title("Image Preview")
        dialog.geometry("400x300")

        img = Image.open(img_path)
        img_resized = img.resize((300, 200), Image.Resampling.LANCZOS)
        img_display = ImageTk.PhotoImage(img_resized)

        img_label = tk.Label(dialog, image=img_display)
        img_label.image = img_display
        img_label.pack(pady=10)

        # Function to validate key and IV
        def get_validated_key_iv():
            # Prompt for the correct key until it matches the stored key or the user cancels
            while True:
                key = get_key("decryption")
                if key is None:  # User pressed Cancel
                    return None, None
                if key == stored_key:
                    break
                else:
                    show_error("Incorrect key! Please enter the correct key used during encryption.")

            # Prompt for the correct IV until it matches the stored IV or the user cancels
            while True:
                iv = get_iv()
                if iv is None:  # User pressed Cancel
                    return None, None
                if iv == stored_iv:
                    break
                else:
                    show_error("Incorrect initialization vector! Please enter the correct IV used during encryption.")
            
            return key, iv

        def on_ok():
            dialog.destroy()
            rval = decode(img_path)
            nlist, tlist = [], []
            for i, item in enumerate(rval, 1):
                tlist.append(item)
                if i % 16 == 0:
                    nlist.append(list(tlist))
                    tlist.clear()

            # Get validated key and IV before decryption
            key, iv = get_validated_key_iv()
            if key is None or iv is None:  # If user canceled, stop the decryption
                show_error("Decryption canceled.")
                dialog.destroy()
                return

            obj = AES(key)
            try:
                msg = obj.decrypt_cbc(nlist, iv)
                msgstr = ''.join(chr(j) for i in msg for j in i)
                messagebox.showinfo("Decrypted Message", f"Here is your decrypted message: {unpad(msgstr)}")
            except ValueError:
                show_error("Decryption failed! The key or IV may be incorrect.")

            dialog.destroy()

            

        def on_cancel():
            dialog.destroy()

        button_ok = ttk.Button(dialog, text="OK", command=on_ok)
        button_ok.pack(side=tk.LEFT, padx=20, pady=10)
        button_cancel = ttk.Button(dialog, text="Cancel", command=on_cancel)
        button_cancel.pack(side=tk.RIGHT, padx=20, pady=10)

        dialog.grab_set()
        dialog.transient(root)

def get_key(action):
    key = simpledialog.askstring("Input", f"Enter 16 bytes long {action} key:")
    if key is None:
        return None  # Return None if the user presses Cancel
    while key and (len(key) != 16):
        show_error(f"The length of the key needs to be 16 bytes. Please enter a valid {action} key:")
        key = simpledialog.askstring("Input", f"Enter 16 bytes long {action} key:")
        if key is None:
            return None  # Return None if the user presses Cancel
    return key

def get_iv():
    iv = simpledialog.askstring("Input", "Enter 16 bytes long initialization vector:")
    if iv is None:
        return None  # Return None if the user presses Cancel
    while iv and (len(iv) != 16):
        show_error("The length of the initialization vector needs to be 16 bytes. Please enter a valid IV:")
        iv = simpledialog.askstring("Input", "Enter 16 bytes long initialization vector:")
        if iv is None:
            return None  # Return None if the user presses Cancel
    return iv

# Function to update the background image when window is resized
def resize_background(event):
    new_width = event.width
    new_height = event.height
    resized_bg_image = bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    new_bg_photo = ImageTk.PhotoImage(resized_bg_image)
    canvas.background = new_bg_photo  # Keep a reference to avoid garbage collection
    canvas.create_image(0, 0, image=new_bg_photo, anchor="nw")

# Create the main tkinter window
root = tk.Tk()
root.title("AES Encryption and LSB Steganography")
root.geometry('600x500')

# Load the background image
bg_image = Image.open("/home/nandu/Downloads/AES_STEGANOGRAPHY/Source code/background_image.jpg")  # Replace with your background image path

# Create a Canvas to display the background image
canvas = tk.Canvas(root, width=600, height=500)
canvas.pack(fill="both", expand=True)

# Load initial background image and display it
bg_photo = ImageTk.PhotoImage(bg_image.resize((600, 500), Image.Resampling.LANCZOS))
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Bind the window resize event to update the background image
root.bind('<Configure>', resize_background)

# Define button styles using ttk
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12, 'bold'), foreground='white', background='#3498DB', padding=10)
style.map('TButton',
          foreground=[('pressed', 'white'), ('active', '#F39C12')],
          background=[('pressed', '!disabled', '#2980B9'), ('active', '#3498DB')])

# Load images for the cards (replace with your actual image paths)
card1_image = Image.open("/home/nandu/Downloads/AES_STEGANOGRAPHY/Source code/card1_bg.jpg")
card1_image = card1_image.resize((250, 150), Image.Resampling.LANCZOS)
card1_photo = ImageTk.PhotoImage(card1_image)

card2_image = Image.open("/home/nandu/Downloads/AES_STEGANOGRAPHY/Source code/card2_bg.jpg")
card2_image = card2_image.resize((250, 150), Image.Resampling.LANCZOS)
card2_photo = ImageTk.PhotoImage(card2_image)

# Create card frames with white background and raised borders
card_1 = tk.Frame(root, width=250, height=150, bd=2, relief='raised', bg='white')
card_2 = tk.Frame(root, width=250, height=150, bd=2, relief='raised', bg='white')

# Place the card frames
card_1.place(x=300, y=220, width=250, height=150)
card_2.place(x=800, y=220, width=250, height=150)

# Add images to the cards
card1_label = tk.Label(card_1, image=card1_photo)
card1_label.pack()

card2_label = tk.Label(card_2, image=card2_photo)
card2_label.pack()

# Define button styles using ttk.Style
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12, 'bold'), padding=10,
                background='#696969', foreground='white')
style.map('TButton',
          background=[('pressed', '#2980B9'), ('active', '#F39C12')],
          foreground=[('pressed', 'white'), ('active', 'white')])

# Add buttons below the cards
button_encrypt_hide = ttk.Button(root, text="Encrypt", command=encrypt_message_and_hide)
button_decrypt_image = ttk.Button(root, text="Decrypt", command=decrypt_image)

# Place buttons below the cards
button_encrypt_hide.place(x=340, y=410, width=150, height=40)
button_decrypt_image.place(x=840, y=410, width=150, height=40)

# Run the tkinter event loop
root.mainloop()
