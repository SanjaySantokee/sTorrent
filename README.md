# sTorrent
This is a simple BitTorrent client implemented in Python using the `libtorrent-rasterbar` library and `PyQt5` for the user interface. The client allows a user to download a .torrent file by specifying its path.

## Requirements
- Python 3+
- libtorrent-rasterbar
- PyQt5

## 🛠 **Usage**

1. **Running the Script**  
   - Clone the repository and navigate to the project folder:  
     ```bash
     git clone https://github.com/yourusername/sTorrent.git
     cd sTorrent
     ```
   - Install the required dependencies:  
     ```bash
     pip install -r requirements.txt
     ```
   - Run the script:  
     ```bash
     python main.py
     ```

2. **Building the Executable**  
   - Install PyInstaller if not already installed:  
     ```bash
     pip install pyinstaller
     ```
   - Build the executable using PyInstaller:  
     ```bash
     pyinstaller --onefile --noconsole --hidden-import=libtorrent --icon=app_icon.ico main.py
     ```
     - The executable will be located in the `/dist` folder.  
   - Run the executable:  
     ```bash
     ./dist/main.exe
     ```

3. **Using the Application**  
   - Open the application by running the script (`python main.py`) or the executable (`./dist/main.exe`).  
   - In the UI:
     - Enter the path to the `.torrent` file you wish to download, or use the **Browse** button to locate it.  
     - Click the **"Download"** button.  
   - The download progress will be displayed in the progress bar.  
   - Once the download is complete:
     - A "Download Complete" message will appear.  
     - A notification will pop up on your system (if enabled).  
   - To access the downloaded files:
     - Double-click the entry in the **Download History** list to open the download directory.  

4. **Where to Find Downloads**  
   - Files are saved in the following directory:
     - **Windows**: `C:\Users\<Username>\AppData\Roaming\sTorrent\storrent_downloads`  
     - **macOS/Linux**: `~/.storrent/storrent_downloads`  



~~~ 
Note: It is not legal to download copyrighted material using torrents. Or, is it?
~~~
