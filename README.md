# MinaKontakter (My Contacts)

A local, offline contact manager for Windows with encrypted database and modern GUI.

> ⚠️ **Warning**: This application stores sensitive personal data. Always use a strong password and keep backups in a secure location.

> ⚠️ **No Password Recovery**: If you forget your password, there is NO way to recover your data. The encryption is designed to be unbreakable without the correct password.

## Features

- **Completely Local** - No cloud sync, no telemetry, no internet required
- **Encrypted Database** - AES-256-GCM with Argon2id key derivation
- **Secure Password Protection** - 7-16 characters with strength indicator
- **Contact Management** - Name, phones, emails, address, company, title, birthday, notes, tags, photo
- **Social Media Links** - LinkedIn, Twitter/X, Facebook, Instagram, GitHub, Telegram, WhatsApp, Signal, Website
- **Quick Actions** - Click phone number for options: Copy, open in Telegram/WhatsApp/Signal
- **Search & Filter** - Quick search, tag filter, favourites
- **Import/Export** - CSV format (compatible with Outlook export)
- **Backup** - Manual and automatic, encrypted
- **Multi-language** - Swedish and English (UK)

## System Requirements

- Windows 10/11
- Python 3.11 or later

## Installation

1. **Clone or download the project**
   ```bash
   git clone https://github.com/2unreal4u/MinaKontakter.git
   cd MinaKontakter
   ```

2. **Create virtual environment (recommended)**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

## Running the Application

```powershell
python run.py
```

### First Run

1. Choose where to save the database
2. Choose backup location
3. Select language (Swedish/English)
4. Create a password (7-16 characters, at least 1 letter and 1 digit)
5. Done! Start adding contacts

## Usage

### Add Contact
Click "+ Add contact" in the left panel.

### Edit Contact
Select a contact in the list and click "Edit".

### Search
Type in the search field. Search matches name, phone, email, company.

### Filter by Tags
Click a tag to filter. Click "Favourites" to show only favourites.

### Phone Number Actions
Click on any phone number to get options:
- Copy number
- Open in Telegram
- Open in WhatsApp
- Open in Signal
- Call (if supported)

### Import from CSV
Menu → File → Import CSV

### Export to CSV
Menu → File → Export CSV

### Backup
- **Manual**: Menu → File → Backup now
- **Automatic**: Settings → Automatic backup on close

## Security

### Encryption
- **Algorithm**: AES-256-GCM (authenticated encryption)
- **Key Derivation**: Argon2id (memory-hard, ASIC-resistant)
- **Salt**: 16 bytes cryptographically random per database

### Password Requirements
- 7-16 characters
- At least 1 letter (a-z, A-Z)
- At least 1 digit (0-9)
- Special characters allowed

### Recommendations
- Use a strong password (strength indicator shows level)
- Keep backups on a separate device
- Consider BitLocker/VeraCrypt for extra protection
- Close the application when not in use

## File Formats

### Database File (.krdb)
Encrypted binary file. Cannot be read without password.

### Backup (.krdb.backup)
Same format as database, timestamped.

### CSV Format
```csv
Name,Phone1,Phone1Type,Email1,Email1Type,Street,PostalCode,City,Country,Company,Title,Birthday,Notes,Tags,LinkedIn,Twitter
"John Doe","+44701234567","mobile","john@email.com","work","Main St 12","SW1A 1AA","London","UK","Company Ltd","CEO","1985-03-15","Notes here","tag1,tag2","linkedin.com/in/johndoe","@johndoe"
```

## Troubleshooting

### "Wrong password"
Check that you are typing the correct password. There is NO password recovery.

### "Database is corrupted"
Restore from backup via Menu → File → Restore backup.

### Application won't start
1. Check that Python 3.11+ is installed
2. Check that all dependencies are installed
3. Run `pip install -r requirements.txt` again

## Building Standalone Executable

```powershell
pip install pyinstaller
python -m PyInstaller MinaKontakter.spec --clean
```

The executable will be created in the `dist/` folder.

## License

MIT License - Free to use and modify.

## Disclaimer

This software is provided "as is", without warranty of any kind. The author is not responsible for any data loss or security breaches. Use at your own risk.

## Author

Created with assistance from AI (Claude/Anthropic).
