import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ttkthemes import ThemedTk

dark_mode = False

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            raise Exception(result.stderr.strip())
    except Exception as e:
        messagebox.showerror("Error", f"Command '{cmd}' failed:\n{str(e)}")
        return None

def list_all_drives():
    output = run_cmd("lsblk -dpno NAME | grep -v 'loop'")
    if output:
        return output.splitlines()
    return []

def refresh_drive_menu(menu):
    menu['values'] = list_all_drives()

def mount_drive():
    drive = drive_var.get()
    mount_point = mount_entry.get()
    run_cmd(f"sudo mkdir -p {mount_point}")
    result = run_cmd(f"sudo mount {drive} {mount_point}")
    if result is not None:
        messagebox.showinfo("Mount Result", f"Mounted {drive} to {mount_point}")

def unmount_drive():
    drive = drive_var.get()
    result = run_cmd(f"sudo umount {drive}")
    if result is not None:
        messagebox.showinfo("Unmount Result", f"Unmounted {drive}")

def format_drive():
    drive = drive_var.get()
    result = run_cmd(f"sudo mkfs.ext4 {drive}")
    if result is not None:
        messagebox.showinfo("Format Drive", f"{drive} formatted successfully.")

def show_mounted_drives():
    output = run_cmd("lsblk -o NAME,MOUNTPOINT,SIZE -p | grep -v 'loop'")
    messagebox.showinfo("Mounted Drives", output or "No drives mounted.")

# ========== LVM MANAGER ==========
def create_physical_volume(drive):
    result = run_cmd(f"sudo pvcreate {drive}")
    if result is not None:
        messagebox.showinfo("PV Result", result)

def create_volume_group(drive):
    vg_name = simpledialog.askstring("Input", "Enter Volume Group name:")
    result = run_cmd(f"sudo vgcreate {vg_name} {drive}")
    if result is not None:
        messagebox.showinfo("VG Result", result)

def create_logical_volume():
    lv_name = simpledialog.askstring("Input", "Enter Logical Volume name:")
    vg_name = simpledialog.askstring("Input", "Enter Volume Group name:")
    size = simpledialog.askstring("Input", "Enter size (e.g., 500M, 1G):")
    result = run_cmd(f"sudo lvcreate -L {size} -n {lv_name} {vg_name}")
    if result is not None:
        messagebox.showinfo("LV Result", result)

def delete_logical_volume():
    lv_path = simpledialog.askstring("Input", "Enter full path of Logical Volume (e.g., /dev/vg_name/lv_name):")
    result = run_cmd(f"sudo lvremove -y {lv_path}")
    if result is not None:
        messagebox.showinfo("Delete LV", result)

def delete_volume_group():
    vg_name = simpledialog.askstring("Input", "Enter Volume Group name:")
    result = run_cmd(f"sudo vgremove -y {vg_name}")
    if result is not None:
        messagebox.showinfo("Delete VG", result)

def delete_physical_volume(drive):
    result = run_cmd(f"sudo pvremove -y {drive}")
    if result is not None:
        messagebox.showinfo("Delete PV", result)

def lvm_status():
    pv = run_cmd("sudo pvdisplay")
    vg = run_cmd("sudo vgdisplay")
    lv = run_cmd("sudo lvdisplay")
    messagebox.showinfo("LVM Status", f"--- PHYSICAL VOLUMES ---\n{pv}\n\n--- VOLUME GROUPS ---\n{vg}\n\n--- LOGICAL VOLUMES ---\n{lv}")

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    theme = "black" if dark_mode else "arc"
    root.set_theme(theme)

def open_lvm_manager():
    lvm_win = tk.Toplevel(root)
    lvm_win.title("LVM Manager")
    lvm_frame = ttk.Frame(lvm_win, padding="10")
    lvm_frame.grid(row=0, column=0)

    lvm_drive_var = tk.StringVar()
    drive_list = list_all_drives()
    lvm_drive_menu = ttk.Combobox(lvm_frame, textvariable=lvm_drive_var, values=drive_list, width=30)
    lvm_drive_menu.grid(row=0, column=0, columnspan=2, pady=5)

    ttk.Button(lvm_frame, text="Create PV", command=lambda: create_physical_volume(lvm_drive_var.get())).grid(row=1, column=0, pady=5)
    ttk.Button(lvm_frame, text="Create VG", command=lambda: create_volume_group(lvm_drive_var.get())).grid(row=1, column=1, pady=5)
    ttk.Button(lvm_frame, text="Create LV", command=create_logical_volume).grid(row=2, column=0, pady=5)

    ttk.Button(lvm_frame, text="Delete LV", command=delete_logical_volume).grid(row=2, column=1, pady=5)
    ttk.Button(lvm_frame, text="Delete VG", command=delete_volume_group).grid(row=3, column=0, pady=5)
    ttk.Button(lvm_frame, text="Delete PV", command=lambda: delete_physical_volume(lvm_drive_var.get())).grid(row=3, column=1, pady=5)

    ttk.Button(lvm_frame, text="LVM Status", command=lvm_status).grid(row=4, column=0, pady=5)
    ttk.Button(lvm_frame, text="Toggle Dark Mode", command=toggle_dark_mode).grid(row=4, column=1, pady=5)

# ========== MAIN GUI ==========
root = ThemedTk(theme="arc")  # Default theme
root.title("Drive Mounter & Manager")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0)

ttk.Label(frame, text="Select Drive:").grid(row=0, column=0, sticky=tk.W)
drive_var = tk.StringVar()
drive_menu = ttk.Combobox(frame, textvariable=drive_var, values=list_all_drives(), width=30)
drive_menu.grid(row=0, column=1)
ttk.Button(frame, text="Refresh", command=lambda: refresh_drive_menu(drive_menu)).grid(row=0, column=2)

ttk.Label(frame, text="Mount Point:").grid(row=1, column=0, sticky=tk.W)
mount_entry = ttk.Entry(frame, width=30)
mount_entry.insert(0, "/mnt/usbdrive")
mount_entry.grid(row=1, column=1, pady=5)

ttk.Button(frame, text="Mount Drive", command=mount_drive).grid(row=2, column=0, pady=5)
ttk.Button(frame, text="Unmount Drive", command=unmount_drive).grid(row=2, column=1, pady=5)
ttk.Button(frame, text="Format Drive", command=format_drive).grid(row=2, column=2, pady=5)
ttk.Button(frame, text="Show Mounted", command=show_mounted_drives).grid(row=3, column=0, pady=5)

ttk.Button(frame, text="Open LVM Manager", command=open_lvm_manager).grid(row=3, column=1, pady=5)
ttk.Button(frame, text="Toggle Dark Mode", command=toggle_dark_mode).grid(row=3, column=2, pady=5)

root.mainloop()
