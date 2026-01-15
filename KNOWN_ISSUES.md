# Known Issues

## Active Bugs

*(Currently testing - no confirmed active bugs)*

---

## Fixed Issues

### 1. Application doesn't close properly
**Status:** Fixed (2026-01-15)  
**Severity:** Medium  
**Reported:** 2026-01-13

**Description:**  
When closing the application, multiple `MinaKontakter.exe` processes remained running in Task Manager.

**Fix:**  
- Added `quit()` call before `destroy()` to properly stop Tkinter mainloop
- Close all overlay windows and menus before exit

---

### 2. File dialog hangs when selecting database location
**Status:** Fixed (2026-01-15)  
**Severity:** Medium  

**Description:**  
Clicking "Choose location" button in setup dialog caused Windows loading spinner with no response.

**Fix:**  
- Added `grab_release()` before file dialogs and `grab_set()` after

---

### 3. Create database fails with argument error
**Status:** Fixed (2026-01-15)  
**Severity:** High  

**Description:**  
`DatabaseManager.create_database()` takes 4 positional arguments but 5 were given.

**Fix:**  
- Added missing `language` parameter to `create_database()` method
