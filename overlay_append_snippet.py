
    def check_calibration(self):
        # Check Global Key State
        if win32api.GetAsyncKeyState(self.calib_vk) & 0x8000:
            cursor_pos = win32api.GetCursorPos() # (x, y) global
            
            # Update Camera Center
            self.camera.center_x = cursor_pos[0]
            self.camera.center_y = cursor_pos[1]
            
            # Calculate Offset relative to window center if tracking
            if self.camera.win_w > 0:
                estimated_cx = self.camera.win_x + self.camera.win_w / 2
                estimated_cy = self.camera.win_y + self.camera.win_h / 2
                self.center_offset_x = cursor_pos[0] - estimated_cx
                self.center_offset_y = cursor_pos[1] - estimated_cy
            
            return True, (self.camera.center_x, self.camera.center_y)
        return False, None
