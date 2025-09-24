#!/usr/bin/env python3
"""
Comprehensive setup and run script for Skill Gap Analyzer
Handles all three services: Backend (Node.js), Frontend (React), Python Service (FastAPI)
"""

import subprocess
import sys
import os
import time
import json
import threading
from pathlib import Path

class SkillGapAnalyzerSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.python_service_dir = self.project_root / "python-service"
        
        # Port configuration
        self.ports = {
            'backend': 5400,  # From .env file
            'frontend': 5173,  # Vite default
            'python_service': 8000  # FastAPI default
        }
        
        self.processes = {}
    
    def check_prerequisites(self):
        """Check if required tools are installed"""
        print("🔍 Checking prerequisites...")
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            print(f"✅ Node.js: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Node.js not found. Please install Node.js from https://nodejs.org/")
            return False
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            print(f"✅ npm: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ npm not found. Please install npm")
            return False
        
        # Check Python
        try:
            result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
            print(f"✅ Python: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Python not found. Please install Python 3.8+")
            return False
        
        # Check pip
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, text=True)
            print(f"✅ pip: {result.stdout.strip()}")
        except:
            print("❌ pip not found. Please install pip")
            return False
        
        return True
    
    def setup_python_service(self):
        """Setup Python service with virtual environment and dependencies"""
        print("\n🐍 Setting up Python service...")
        
        os.chdir(self.python_service_dir)
        
        # Create virtual environment if it doesn't exist
        venv_path = self.python_service_dir / "venv"
        if not venv_path.exists():
            print("Creating Python virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        
        # Determine Python executable in venv
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:  # Unix/Linux/Mac
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        # Install dependencies
        print("Installing Python dependencies...")
        subprocess.run([str(pip_exe), 'install', '--upgrade', 'pip'], check=True)
        
        # Install requirements
        if (self.python_service_dir / "requirements.txt").exists():
            subprocess.run([str(pip_exe), 'install', '-r', 'requirements.txt'], check=True)
        
        # Install additional dependencies that might be missing
        additional_deps = [
            'uvicorn[standard]',
            'python-multipart',
            'redis',
            'pydantic',
            'python-jose[cryptography]'
        ]
        
        for dep in additional_deps:
            try:
                subprocess.run([str(pip_exe), 'install', dep], check=True)
            except subprocess.CalledProcessError:
                print(f"⚠️  Could not install {dep}, continuing...")
        
        # Download spaCy model
        print("Downloading spaCy English model...")
        try:
            subprocess.run([str(python_exe), '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
        except subprocess.CalledProcessError:
            print("⚠️  Could not download spaCy model, will try to continue...")
        
        print("✅ Python service setup complete")
        return str(python_exe)
    
    def setup_backend(self):
        """Setup Node.js backend"""
        print("\n🚀 Setting up Backend (Node.js)...")
        
        os.chdir(self.backend_dir)
        
        # Install dependencies
        if (self.backend_dir / "package.json").exists():
            print("Installing backend dependencies...")
            subprocess.run(['npm', 'install'], check=True)
        
        print("✅ Backend setup complete")
    
    def setup_frontend(self):
        """Setup React frontend"""
        print("\n⚛️  Setting up Frontend (React)...")
        
        os.chdir(self.frontend_dir)
        
        # Install dependencies
        if (self.frontend_dir / "package.json").exists():
            print("Installing frontend dependencies...")
            subprocess.run(['npm', 'install'], check=True)
        
        print("✅ Frontend setup complete")
    
    def check_ports(self):
        """Check if required ports are available"""
        print("\n🔌 Checking port availability...")
        
        import socket
        
        for service, port in self.ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"⚠️  Port {port} ({service}) is already in use")
            else:
                print(f"✅ Port {port} ({service}) is available")
    
    def start_python_service(self, python_exe):
        """Start Python FastAPI service"""
        print(f"\n🐍 Starting Python service on port {self.ports['python_service']}...")
        
        os.chdir(self.python_service_dir)
        
        def run_python_service():
            try:
                # Start with uvicorn
                subprocess.run([
                    str(python_exe), '-m', 'uvicorn', 
                    'api_server:app', 
                    '--host', '0.0.0.0', 
                    '--port', str(self.ports['python_service']),
                    '--reload'
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Python service failed: {e}")
        
        thread = threading.Thread(target=run_python_service, daemon=True)
        thread.start()
        
        # Wait a bit for service to start
        time.sleep(3)
        return thread
    
    def start_backend(self):
        """Start Node.js backend"""
        print(f"\n🚀 Starting Backend on port {self.ports['backend']}...")
        
        os.chdir(self.backend_dir)
        
        def run_backend():
            try:
                subprocess.run(['npm', 'run', 'dev'], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Backend failed: {e}")
        
        thread = threading.Thread(target=run_backend, daemon=True)
        thread.start()
        
        # Wait a bit for service to start
        time.sleep(2)
        return thread
    
    def start_frontend(self):
        """Start React frontend"""
        print(f"\n⚛️  Starting Frontend on port {self.ports['frontend']}...")
        
        os.chdir(self.frontend_dir)
        
        def run_frontend():
            try:
                subprocess.run(['npm', 'run', 'dev'], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Frontend failed: {e}")
        
        thread = threading.Thread(target=run_frontend, daemon=True)
        thread.start()
        
        return thread
    
    def wait_for_service(self, port, service_name, timeout=30):
        """Wait for a service to be ready"""
        import socket
        
        print(f"⏳ Waiting for {service_name} to be ready...")
        
        for i in range(timeout):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"✅ {service_name} is ready!")
                return True
            
            time.sleep(1)
        
        print(f"❌ {service_name} failed to start within {timeout} seconds")
        return False
    
    def show_status(self):
        """Show status of all services"""
        print("\n" + "="*60)
        print("🎉 SKILL GAP ANALYZER - ALL SERVICES RUNNING")
        print("="*60)
        print(f"🐍 Python Service (FastAPI): http://localhost:{self.ports['python_service']}")
        print(f"🚀 Backend (Node.js):        http://localhost:{self.ports['backend']}")
        print(f"⚛️  Frontend (React):         http://localhost:{self.ports['frontend']}")
        print("="*60)
        print("\n📋 Available Endpoints:")
        print(f"   • API Documentation:     http://localhost:{self.ports['python_service']}/docs")
        print(f"   • Health Check:          http://localhost:{self.ports['python_service']}/api/health")
        print(f"   • Skills List:           http://localhost:{self.ports['python_service']}/api/skills/list")
        print(f"   • Main Application:      http://localhost:{self.ports['frontend']}")
        print("\n🛑 Press Ctrl+C to stop all services")
    
    def run_all(self):
        """Main method to setup and run all services"""
        print("🚀 SKILL GAP ANALYZER - COMPREHENSIVE SETUP & RUN")
        print("="*60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Setup all services
        python_exe = self.setup_python_service()
        self.setup_backend()
        self.setup_frontend()
        
        # Check ports
        self.check_ports()
        
        # Start services
        try:
            # Start Python service first (backend depends on it)
            python_thread = self.start_python_service(python_exe)
            self.wait_for_service(self.ports['python_service'], "Python Service")
            
            # Start backend
            backend_thread = self.start_backend()
            self.wait_for_service(self.ports['backend'], "Backend")
            
            # Start frontend
            frontend_thread = self.start_frontend()
            self.wait_for_service(self.ports['frontend'], "Frontend")
            
            # Show status
            self.show_status()
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 Shutting down all services...")
                return True
                
        except Exception as e:
            print(f"\n❌ Error starting services: {e}")
            return False

def main():
    """Main entry point"""
    setup = SkillGapAnalyzerSetup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'setup':
            # Just setup, don't run
            setup.check_prerequisites()
            setup.setup_python_service()
            setup.setup_backend()
            setup.setup_frontend()
            print("\n✅ Setup complete! Run 'python setup_and_run.py' to start all services.")
        
        elif command == 'check':
            # Just check status
            setup.check_prerequisites()
            setup.check_ports()
        
        else:
            print("Usage: python setup_and_run.py [setup|check]")
            print("  setup - Only setup dependencies")
            print("  check - Only check prerequisites and ports")
            print("  (no args) - Setup and run all services")
    
    else:
        # Setup and run everything
        success = setup.run_all()
        if success:
            print("✅ All services stopped successfully")
        else:
            print("❌ Some services failed to start")
            sys.exit(1)

if __name__ == "__main__":
    main()