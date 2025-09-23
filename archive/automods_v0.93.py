#!/usr/bin/env python3
"""
CerberusX - External Modules AutoMods

To make exe on window:
    pip install pyinstaller
    pyinstaller --onefile --distpath . --name automods.exe automods.py
"""

import os
import sys
import shutil
import zipfile
import requests
import argparse
from pathlib import Path
from urllib.parse import urlparse
import platform
from datetime import datetime

class ModuleDownloader:
    def __init__(self):
        self.bin_path = self._get_base_dir() + "/"
        self.update_list = []
        self.module_folder = "modules_ext"
        self.last_download = ""
        self.run_id = self._generate_run_id()

    def _generate_run_id(self):
        """Generate a 4-digit RunID based on current hour and minute"""
        current_time = datetime.now()
        return f"{current_time.hour:02d}{current_time.minute:02d}"

    def _get_base_dir(self):
        """Get the directory containing the script or executable"""
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            return os.path.dirname(sys.executable)
        else:
            # Running as Python script
            return os.path.dirname(os.path.abspath(__file__))

    def parse_commandline(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description='CerberusX External Modules AutoMods')
        parser.add_argument('-update', type=str, help='Update specific modules (comma-separated) or ALL')
        parser.add_argument('-into', type=str, help='Target module folder', default='modules_ext')

        args = parser.parse_args()

        if args.update:
            if args.update.upper() == "ALL":
                self.update_list.append("ALL")
            else:
                self.update_list.extend([folder.strip() for folder in args.update.split(',')])

        if args.into:
            self.module_folder = args.into

    def setup_paths(self):
        """Setup module paths"""
        self.modules_ext_path = os.path.join(os.path.dirname(self.bin_path.rstrip('/')), self.module_folder) + "/"
        os.makedirs(self.modules_ext_path, exist_ok=True)

    def clear_quote(self, text):
        """Remove quotes from text"""
        return text.replace('"', '')

    def parse_input_file(self):
        """Parse the input configuration file"""
        system_name = platform.system().lower()
        config_file = os.path.join(self.bin_path, "automods.txt")
        if not os.path.exists(config_file):
            print("'automods.txt' file not found")
            return

        with open(config_file, 'r', encoding='utf-8') as file:
            for line in file:
                # Remove comments and clean line
                line = line.split("'")[0]  # Remove comments
                line = line.replace('\t', ' ')  # Replace tabs
                line = line.strip()

                if not line:
                    continue

                if '=' not in line:
                    continue

                # Parse instruction
                parts = line.split('=', 1)
                instruction = parts[0].strip().upper()
                data = parts[1].strip()

                # Check for force replace
                need_replace = False
                if '!' in instruction:
                    instruction = instruction.replace('!', '')
                    need_replace = True

                if instruction == "DOWNLOAD":
                    self.handle_download(data, need_replace)
                else:
                    self.handle_operations(instruction, data, need_replace)

    def handle_download(self, data, need_replace):
        """Handle download instruction"""
        if ',' in data:
            # Name specified
            parts = data.split(',', 1)
            url = self.clear_quote(parts[0].strip())
            name = self.clear_quote(parts[1].strip())
            self.download(url, name, need_replace)
        else:
            # Name not specified
            url = self.clear_quote(data.strip())
            self.download(url, "", need_replace)

    def handle_operations(self, instruction, data, need_replace):
        """Handle copy/move/delete instructions"""
        if instruction == "DELETE":
            if not data:
                return
            path = self.clear_quote(data.strip())
            self.handle_delete(path, need_replace)
        elif ',' not in data:
            return
        else:
            parts = data.split(',', 1)
            from_path = self.clear_quote(parts[0].strip())
            to_path = self.clear_quote(parts[1].strip())

            need_update = True
            if not need_replace:
                full_to_path = os.path.join(self.modules_ext_path, to_path)
                if os.path.exists(full_to_path):
                    need_update = False
                    if self.last_download + "/" == to_path:
                        need_update = True
                    for folder in self.update_list:
                        if folder == to_path or folder == "ALL":
                            need_update = True

            if need_update:
                full_from_path = os.path.join(self.modules_ext_path, from_path)
                full_to_path = os.path.join(self.modules_ext_path, to_path)

                # Check for existing folder or file before copy/move
                if os.path.exists(full_to_path):
                    backup_path = f"{full_to_path}_BKP{self.run_id}"
                    if not os.path.exists(backup_path):  # Only backup if no backup exists for this RunID
                        try:
                            shutil.move(full_to_path, backup_path)
                            #print(f"   Backed up existing to: {backup_path}")
                        except Exception as e:
                            pass
                            #print(f"   Warning: Could not backup {full_to_path}: {e}")

                if os.path.exists(full_from_path):
                    if instruction == "COPY":
                        if os.path.isdir(full_from_path):
                            shutil.copytree(full_from_path, full_to_path, dirs_exist_ok=True)
                        elif os.path.isfile(full_from_path):
                            os.makedirs(os.path.dirname(full_to_path), exist_ok=True)
                            shutil.copy(full_from_path, full_to_path)
                    elif instruction == "MOVE":
                        os.makedirs(os.path.dirname(full_to_path), exist_ok=True)
                        shutil.move(full_from_path, full_to_path)

    def handle_delete(self, path, need_replace):
        """Handle delete instruction without backup"""
        full_path = os.path.join(self.modules_ext_path, path)
        try:
            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path, ignore_errors=True)
                elif os.path.isfile(full_path):
                    os.remove(full_path)
            else:
                pass
        except Exception as e:
            pass

    def download(self, addr, name="", need_replace=False):
        """Download and extract module"""
        if not name:
            name = addr.split('/')[-1]

        if not need_replace:
            module_path = os.path.join(self.modules_ext_path, name)
            if os.path.isdir(module_path):
                need_update = False
                for folder in self.update_list:
                    if folder == name or folder == "ALL":
                        need_update = True
                        break
                if not need_update:
                    return

        # Determine download URL and file path
        if "github.com" in addr:
            if not addr.endswith(".zip"):
                url = addr + "/archive/master.zip"
            else:
                url = addr
        else:
            url = addr

        file_path = os.path.join(self.modules_ext_path, name + ".zip")

        # Check for existing zip file and backup if needed
        if os.path.exists(file_path):
            backup_zip = os.path.join(self.modules_ext_path, f"{name}_BKP{self.run_id}.zip")
            if not os.path.exists(backup_zip):  # Only backup if no backup exists for this RunID
                try:
                    shutil.move(file_path, backup_zip)
                    #print(f"   Backed up existing zip to: {backup_zip}")
                except Exception as e:
                    pass
                    #print(f"   Warning: Could not backup {file_path}: {e}")

        # Check for existing target folder and backup if needed
        target_dir = os.path.join(self.modules_ext_path, name)
        if os.path.exists(target_dir):
            backup_dir = f"{target_dir}_BKP{self.run_id}"
            if not os.path.exists(backup_dir):  # Only backup if no backup exists for this RunID
                try:
                    shutil.move(target_dir, backup_dir)
                    #print(f"   Backed up existing folder to: {backup_dir}")
                except Exception as e:
                    pass
                    #print(f"   Warning: Could not backup {target_dir}: {e}")

        print(f"Downloading.. {name}")
        if self.actual_download(url, file_path):
            if self.extract_zip(file_path, name):
                self.last_download = name
            else:
                print(f"   FAIL to extract {name}!")
            # Delete zip file
            try:
                os.remove(file_path)
            except:
                pass
        else:
            print(f"   FAIL to download {name}!")
            try:
                os.remove(file_path)
            except:
                pass

    def actual_download(self, url, file_path):
        """Download file using requests with proper redirect handling and progress"""
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

            response = session.get(url,
                                 allow_redirects=True,
                                 timeout=60,
                                 stream=True)
            response.raise_for_status()

            downloaded = 0
            last_progress = -10

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if downloaded % (1024 * 1024) < 8192:
                            mb_downloaded = downloaded / (1024 * 1024)
                            if mb_downloaded == 0 or int(mb_downloaded * 10) % 10 == 0:
                                print(f"   Process: <{(mb_downloaded+1):.1f}MB \r", end='')
                                sys.stdout.flush()
                    else:
                        print()
            return os.path.getsize(file_path) > 0
        except Exception as e:
            print(f"\n   Download error: {e}")
            return False

    def extract_zip(self, zip_path, target_name):
        """Extract ZIP file and handle nested folders with progress"""
        try:
            target_dir = os.path.join(self.modules_ext_path, target_name)

            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                file_list = zip_file.infolist()
                total_files = len(file_list)

                last_progress = -10

                for i, file_info in enumerate(file_list):
                    zip_file.extract(file_info, target_dir)
                    progress = int(((i + 1) / total_files) * 100)
                    if (progress % 10 == 0 or progress == 100) and progress > last_progress:
                        if progress == 100:
                            print(f"   Unzip: {progress}% ({i + 1}/{total_files} files)", end='')
                        else:
                            print(f"   Unzip: {progress}% ({i + 1}/{total_files} files)\r", end='')
                        sys.stdout.flush()
                        last_progress = progress

                print()
                self.fix_folder_name(target_dir)
                self.fix_nested_folder(target_dir, target_name)
                return True

        except Exception as e:
            print(f"\n   Extract error: {e}")
            return False

    def fix_folder_name(self, target_dir):
        """Fix nested folder structure by moving contents up"""
        try:
            entries = os.listdir(target_dir)
            if len(entries) == 1:
                nested_path = os.path.join(target_dir, entries[0])
                if os.path.isdir(nested_path):
                    for item in os.listdir(nested_path):
                        src = os.path.join(nested_path, item)
                        dst = os.path.join(target_dir, item)
                        shutil.move(src, dst)
                    os.rmdir(nested_path)
        except Exception as e:
            print(f"   Warning: Could not fix nested folder: {e}")

    def fix_nested_folder(self, target_dir, target_name):
        """Fix nested folder structure by moving contents up when nested folder matches target_name"""
        try:
            if not os.path.isdir(target_dir):
                return

            target_base = os.path.basename(os.path.normpath(target_dir))
            nested_path = os.path.join(target_dir, target_base)

            if not os.path.isdir(nested_path):
                return

            nested_contents = os.listdir(nested_path)
            if not nested_contents:
                os.rmdir(nested_path)
                return

            for item in nested_contents:
                src = os.path.join(nested_path, item)
                dst = os.path.join(target_dir, item)

                if os.path.exists(dst):
                    if os.path.isdir(dst) and os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                        shutil.rmtree(src)
                    else:
                        if os.path.isfile(dst) and os.path.isfile(src):
                            os.remove(dst)
                        shutil.move(src, dst)
                else:
                    shutil.move(src, dst)

            try:
                os.rmdir(nested_path)
            except OSError as e:
                print(f"   Warning: Could not remove nested folder (not empty or error): {e}")

        except Exception as e:
            print(f"   Error: Could not fix nested folder: {e}")

    def run(self):
        """Main execution"""
        print("CerberusX - External Modules AutoMods")
        print(f"RunID: {self.run_id}")

        self.parse_commandline()
        self.setup_paths()
        self.parse_input_file()

        print("Process complete")

if __name__ == "__main__":
    downloader = ModuleDownloader()
    downloader.run()