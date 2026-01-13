# Known Issues

## Active Bugs

### 1. Application doesn't close properly
**Status:** Open  
**Severity:** Medium  
**Reported:** 2026-01-13

**Description:**  
When closing the application, multiple `MinaKontakter.exe` processes remain running in Task Manager. The application doesn't fully terminate.

**Workaround:**  
Manually end the processes in Task Manager.

**Possible cause:**  
- Tkinter mainloop not properly terminated
- Background threads not stopped
- Overlay windows or popup menus not destroyed

---

## Fixed Issues

*(None yet)*
