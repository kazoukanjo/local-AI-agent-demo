from .desktop import open_app,open_path,open_url,list_installed_apps
from .files import find_files,read_file
from ..browser.manager import browser

FUNCTIONS={
'open_app':open_app,'open_path':open_path,'open_url':open_url,'list_installed_apps':list_installed_apps,
'find_files':find_files,'read_file':read_file,
'browser_goto':browser.goto,'browser_snapshot':browser.snapshot,
'browser_fill':browser.semantic_fill,'browser_click':browser.semantic_click,
}
