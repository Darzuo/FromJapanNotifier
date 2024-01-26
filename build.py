import PyInstaller.__main__
import shutil

PyInstaller.__main__.run([
    '--noconfirm',
    '--onedir',
    '--console',
    '--icon',
    'OneMap.ico',
    'FJN.py',
])

shutil.copyfile('notification.mp3', 'dist/FJN/notification.mp3')
shutil.copyfile('notification.mp3', 'build/FJN/notification.mp3')
shutil.copyfile('OneMap.ico', 'dist/FJN/OneMap.ico')
shutil.copyfile('OneMap.ico', 'build/FJN/OneMap.ico')