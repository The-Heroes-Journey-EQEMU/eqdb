#!/usr/bin/env python3
"""
Unified Development Server for EQDB
Starts both the Python Flask backend and the npm frontend dev server
"""

import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path

class DevServer:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_flask_server(self):
        """Start the Flask backend server"""
        print("🚀 Starting Flask backend server...")
        try:
            # Change to the project root directory
            os.chdir(Path(__file__).parent)
            
            # Start Flask server
            flask_process = subprocess.Popen([
                sys.executable, 'api_server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            self.processes.append(flask_process)
            
            # Monitor Flask output
            for line in flask_process.stdout:
                if not self.running:
                    break
                print(f"[Flask] {line.rstrip()}")
                
        except Exception as e:
            print(f"❌ Error starting Flask server: {e}")
            
    def start_npm_server(self):
        """Start the npm frontend dev server"""
        print("🚀 Starting npm frontend dev server...")
        try:
            # Change to the frontend directory
            fe_dir = Path(__file__).parent / 'fe'
            os.chdir(fe_dir)
            
            # Check if node_modules exists, if not run npm install
            if not (fe_dir / 'node_modules').exists():
                print("📦 Installing npm dependencies...")
                subprocess.run(['npm', 'install'], check=True)
            
            # Start npm dev server
            npm_process = subprocess.Popen([
                'npm', 'run', 'dev'
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            self.processes.append(npm_process)
            
            # Monitor npm output
            for line in npm_process.stdout:
                if not self.running:
                    break
                print(f"[NPM] {line.rstrip()}")
                
        except Exception as e:
            print(f"❌ Error starting npm server: {e}")
            
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down development servers...")
        self.running = False
        
        # Terminate all processes
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Warning: Could not terminate process: {e}")
                
        print("✅ Development servers stopped")
        sys.exit(0)
        
    def run(self):
        """Run both servers concurrently"""
        print("🎮 EQDB Development Server")
        print("=" * 40)
        print("Starting both backend and frontend servers...")
        print()
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start Flask server in a separate thread
        flask_thread = threading.Thread(target=self.start_flask_server, daemon=True)
        flask_thread.start()
        
        # Give Flask a moment to start
        time.sleep(2)
        
        # Start npm server in a separate thread
        npm_thread = threading.Thread(target=self.start_npm_server, daemon=True)
        npm_thread.start()
        
        print()
        print("✅ Development servers started!")
        print("📱 Frontend: http://localhost:3100")
        print("🔧 Backend API: http://localhost:5001")
        print("📚 API Documentation: http://localhost:5001/api/v1/")
        print()
        print("Press Ctrl+C to stop all servers")
        print()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    dev_server = DevServer()
    dev_server.run()
