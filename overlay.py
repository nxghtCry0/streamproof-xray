import dearpygui.dearpygui as dpg
import ctypes
from ctypes import windll, wintypes
import math
from streamproof import enable_streamproof
import win32api
import win32con

# Constants
LWA_COLORKEY = 0x00000001
LWA_ALPHA = 0x00000002
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

class Camera:
    def __init__(self, fov=90):
        self.fov = fov
        self.win_x = 0
        self.win_y = 0
        self.win_w = 1920
        self.win_h = 1080
        self.center_x = 960
        self.center_y = 540

    def update_window_rect(self, x, y, w, h):
        self.win_x = x
        self.win_y = y
        self.win_w = w
        self.win_h = h
        # Force Screen Center as requested
        # self.center_x = x + w / 2
        # self.center_y = y + h / 2
        self.aspect_ratio = w / h

    def world_to_screen(self, p_pos, p_yaw, p_pitch, target_x, target_y, target_z):
        # Position Relative to Camera
        cam_x, cam_y, cam_z = p_pos['x'], p_pos['y'] + 1.62, p_pos['z']
        
        rel_x = target_x - cam_x
        rel_y = target_y - cam_y
        rel_z = target_z - cam_z

        # Yaw Rotation
        theta = math.radians(-p_yaw)
        x_r = rel_x * math.cos(theta) - rel_z * math.sin(theta)
        z_r = rel_x * math.sin(theta) + rel_z * math.cos(theta)
        y_r = rel_y

        # Pitch Rotation
        phi = math.radians(-p_pitch)
        y_final = y_r * math.cos(phi) - z_r * math.sin(phi)
        z_final = y_r * math.sin(phi) + z_r * math.cos(phi)

        # Projection
        if z_final > 0.1: # Clip behind camera
            # Math: screen_x = center_x + (x / z) * scale_x
            # scale_x = (width / 2) / tan(hfov / 2)
            
            tan_half_fov = math.tan(math.radians(self.fov / 2))
            
            scale_x = (self.win_w / 2) / tan_half_fov
             # For square pixels, scale_y should be consistent with scale_x based on aspect?
            # Usually: scale_y = scale_x if pixels are square.
            scale_y = scale_x # Assuming square pixels
            
            # Match rotation/projection fix
            # screen_x should be inverted because in our math x_r positive means "Right" in world space relative to cam?, 
            # but we need to verify coordinate system.
            # User says "Left side is the right side ingame".
            # Flipping the sign of X offset fixes horizontal mirroring.
            
            screen_x = self.center_x - (x_r * scale_x / z_final)
            screen_y = self.center_y - (y_final * scale_y / z_final)
            
            return screen_x, screen_y
            
        return None

class Overlay:
    def __init__(self, target_title="Minecraft*", calibration_key='x'):
        dpg.create_context()
        self.title = "Streamproof Xray Overlay DPG"
        self.target_title = target_title
        
        # Calibration Key Setup
        if len(calibration_key) == 1:
            self.calib_vk = ord(calibration_key.upper())
        else:
            self.calib_vk = 0x58 # Default X
            
        self.center_offset_x = 0
        self.center_offset_y = 0
        
        user32 = windll.user32
        self.width = user32.GetSystemMetrics(0)
        self.height = user32.GetSystemMetrics(1)
        
        # Transparent Viewport
        dpg.create_viewport(title=self.title, width=self.width, height=self.height, 
                           x_pos=0, y_pos=0, always_on_top=True, decorated=False, clear_color=[0, 0, 0, 255])
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.maximize_viewport() 
        
        self.camera = Camera(fov=90)
        
        with dpg.window(label="OverlayWindow", width=self.width, height=self.height, pos=[0,0], 
                       no_title_bar=True, no_resize=True, no_move=True, no_scrollbar=True, 
                       no_collapse=True, no_background=True, tag="MainWin"):
             pass
        
        self._apply_attributes()
        
    def track_game_window(self):
        try:
            # simple fuzzy match
            def enum_cb(hwnd, results):
                win_text = win32gui.GetWindowText(hwnd)
                # match wildcard roughly
                pattern = self.target_title.replace("*", "")
                if pattern.lower() in win_text.lower():
                    results.append(hwnd)
            
            hwnds = []
            win32gui.EnumWindows(enum_cb, hwnds)
            
            if hwnds:
                target_hwnd = hwnds[0]
                rect = RECT()
                windll.user32.GetClientRect(target_hwnd, ctypes.byref(rect))
                
                # Client to Screen
                pt = POINT(rect.left, rect.top)
                windll.user32.ClientToScreen(target_hwnd, ctypes.byref(pt))
                
                w = rect.right - rect.left
                h = rect.bottom - rect.top
                
                self.camera.update_window_rect(pt.x, pt.y, w, h)
                return True
        except Exception as e:
            # print(f"Tracking error: {e}")
            pass
        return False

    def check_calibration(self):
        if win32api.GetAsyncKeyState(self.calib_vk) & 0x8000:
            cursor_pos = win32api.GetCursorPos()
            self.camera.center_x = cursor_pos[0]
            self.camera.center_y = cursor_pos[1]
            
            if self.camera.win_w > 0:
                estimated_cx = self.camera.win_x + self.camera.win_w / 2
                estimated_cy = self.camera.win_y + self.camera.win_h / 2
                self.center_offset_x = cursor_pos[0] - estimated_cx
                self.center_offset_y = cursor_pos[1] - estimated_cy
            return True, (self.camera.center_x, self.camera.center_y)
        return False, None

    def _apply_attributes(self):
        hwnd = windll.user32.FindWindowW(None, self.title)
        if hwnd:
            styles = windll.user32.GetWindowLongW(hwnd, -20)
            windll.user32.SetWindowLongW(hwnd, -20, styles | WS_EX_LAYERED | WS_EX_TRANSPARENT)
            windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, 0, LWA_COLORKEY)
            # enable_streamproof(hwnd) # Disabled for debugging per user request

    def update(self):
        if dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            self.clear()
            
            is_calibrating, new_center = self.check_calibration()
            found = self.track_game_window()
            
            if found:
                # Apply stored offset
                self.camera.center_x += self.center_offset_x
                self.camera.center_y += self.center_offset_y
            
            if is_calibrating:
                 dpg.draw_text((new_center[0] + 20, new_center[1]), "CALIBRATING CENTER", color=(255, 255, 0, 255), parent="MainWin")
            
            # Crosshair
            cx, cy = self.camera.center_x, self.camera.center_y
            dpg.draw_line((cx - 10, cy), (cx + 10, cy), color=(255, 0, 0, 255), thickness=2, parent="MainWin")
            dpg.draw_line((cx, cy - 10), (cx, cy + 10), color=(255, 0, 0, 255), thickness=2, parent="MainWin")
            
            if not found:
                 dpg.draw_text((20, 100), "Searching for Game Window...", color=(255, 100, 100, 255), parent="MainWin")
            
            return True
        return False

    def clear(self):
        dpg.delete_item("MainWin", children_only=True)

    def draw_text(self, text, x, y, color=(255, 255, 255, 255)):
        if isinstance(color, str):
             if color.startswith("#"):
                h = color.lstrip('#')
                if len(h) == 6:
                    color = tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)
                else:
                    color = (255, 255, 255, 255)
        dpg.draw_text((x, y), text, color=color, size=20, parent="MainWin")

    def draw_box(self, player_data, block_x, block_y, block_z, color_dict):
        r = color_dict.get('r', 255)
        g = color_dict.get('g', 255)
        b = color_dict.get('b', 255)
        a = color_dict.get('a', 255)
        color = (r, g, b, a)
        
        corners = [
            (0,0,0), (1,0,0), (0,1,0), (1,1,0),
            (0,0,1), (1,0,1), (0,1,1), (1,1,1)
        ]
        
        screen_points = []
        for cx, cy, cz in corners:
            sp = self.camera.world_to_screen(
                player_data, 
                player_data['yaw'], 
                player_data['pitch'], 
                block_x + cx, 
                block_y + cy, 
                block_z + cz
            )
            screen_points.append(sp)

        lines = [
            (0,1), (1,3), (3,2), (2,0), # Front
            (4,5), (5,7), (7,6), (6,4), # Back
            (0,4), (1,5), (2,6), (3,7)  # Connecting
        ]
        
        for p1_idx, p2_idx in lines:
            p1 = screen_points[p1_idx]
            p2 = screen_points[p2_idx]
            if p1 and p2:
                dpg.draw_line(p1, p2, color=color, thickness=2, parent="MainWin")

    def close(self):
        dpg.destroy_context()
