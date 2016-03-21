import cx_Freeze
import sys
import traceback

base = None

version = "1.1.1"

if sys.platform == "win32":
	base = "Win32GUI"

bdist_msi_options = {
    "upgrade_code": "{78b1f650-672f-4163-9cbc-88a76fc03173}"
    }

executables = [cx_Freeze.Executable(u"BaiduMain.pyw",base=base,icon="icon.ico",shortcutName="Baidu站长提交工具",shortcutDir="DesktopFolder")]

cx_Freeze.setup(
	name = u"Baidu站长平台提交工具",
	options = {"bdist_msi" : bdist_msi_options, 
	"build_exe" : {"packages":["dbm","tkinter","traceback","shelve","base64",
	"re","gzip","zlib","urllib","datetime","copy","http.cookiejar","urllib.request",
	"time","os","sys","urllib.robotparser","threading","queue","webbrowser",
	"configparser","winreg","tkinter.filedialog","tkinter.messagebox","tkinter.ttk","bs4"],
	"include_files" : ["icon.ico","update.txt"],
	"optimize" : 2
	}},
	version = version,
	description = "Baidu站长平台提交工具",
	executables = executables,
	author = "guiqiqi187@gmail.com"
)
