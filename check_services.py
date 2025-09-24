#!/usr/bin/env python3
"""
Service Health Check Script for Skill Gap Analyzer
Checks if all services are running and accessible
"""

import requests
import json
import time
from pathlib import Path

class ServiceChecker:
    def __init__(self):
        self.services = {
            'python_service': {
                'name': 'Python FastAPI Service',
                'url': 'http://localhost:8000',
                'health_endpoint': '/api/health',
                'test_endpoints': [
                    '/api/skills/list',
                    '/api/skills/categories',
                    '/api/stats'
                ]
            },
            'backend': {
                'name': 'Node.js Backend',
                'url': 'http://localhost:5400',
                'health_endpoint': '/',
                'test_endpoints': []
            },
            'frontend': {
                'name': 'React Frontend',
                'url': 'http://localhost:5173',
                'health_endpoint': '/',
                'test_endpoints': []
            }
        }
    
    def check_service(self, service_key, service_config):
        """Check if a service is running and healthy"""
        print(f"\n🔍 Checking {service_config['name']}...")
        
        base_url = service_config['url']
        health_endpoint = service_config['health_endpoint']
        
        try:
            # Basic connectivity check
            response = requests.get(f"{base_url}{health_endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {service_config['name']} is running on {base_url}")
                
                # Test additional endpoints for Python service
                if service_key == 'python_service':
                    self.test_python_endpoints(base_url)
                
                return True
            else:
                print(f"⚠️  {service_config['name']} responded with status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {service_config['name']} is not accessible at {base_url}")
            return False
        except requests.exceptions.Timeout:
            print(f"⏰ {service_config['name']} timed out")
            return False
        except Exception as e:
            print(f"❌ Error checking {service_config['name']}: {e}")
            return False
    
    def test_python_endpoints(self, base_url):
        """Test specific Python service endpoints"""
        endpoints_to_test = [
            ('/api/skills/list', 'Skills List'),
            ('/api/skills/categories', 'Skill Categories'),
            ('/api/stats', 'System Statistics'),
            ('/docs', 'API Documentation')
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=3)
                if response.status_code == 200:
                    print(f"  ✅ {description}: OK")
                else:
                    print(f"  ⚠️  {description}: Status {response.status_code}")
            except:
                print(f"  ❌ {description}: Failed")
    
    def test_skill_analysis(self):
        """Test the skill gap analysis functionality"""
        print(f"\n🧪 Testing Skill Gap Analysis...")
        
        test_data = {
            "resume_text": "I have experience with Python, React, and Node.js. I've worked with databases like MongoDB and PostgreSQL.",
            "job_text": "We are looking for a developer with Python, React, Docker, and AWS experience.",
            "strategy": "hybrid",
            "detailed": False
        }
        
        try:
            # Test Python service directly
            response = requests.post(
                "http://localhost:8000/api/skill-gap/analyze-json",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Skill gap analysis working!")
                print(f"   Match percentage: {result.get('match_percentage', 'N/A')}%")
                print(f"   Matched skills: {len(result.get('matched_skills', []))}")
                print(f"   Missing skills: {len(result.get('missing_skills', []))}")
                return True
            else:
                print(f"❌ Skill analysis failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Skill analysis test failed: {e}")
            return False
    
    def test_backend_integration(self):
        """Test backend integration with Python service"""
        print(f"\n🔗 Testing Backend Integration...")
        
        test_data = {
            "resumeText": "Python developer with React experience",
            "jobText": "Looking for Python and Docker skills"
        }
        
        try:
            # Test through backend
            response = requests.post(
                "http://localhost:5400/api/ai/analyze-skill-gap",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Backend integration working!")
                return True
            else:
                print(f"❌ Backend integration failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Backend integration test failed: {e}")
            return False
    
    def show_summary(self, results):
        """Show summary of all checks"""
        print("\n" + "="*60)
        print("📊 SERVICE HEALTH CHECK SUMMARY")
        print("="*60)
        
        all_healthy = True
        for service, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {self.services[service]['name']}: {'Healthy' if status else 'Unhealthy'}")
            if not status:
                all_healthy = False
        
        print("\n" + "="*60)
        
        if all_healthy:
            print("🎉 ALL SERVICES ARE HEALTHY!")
            print("\n📋 Quick Access URLs:")
            print("   • Main App:        http://localhost:5173")
            print("   • API Docs:        http://localhost:8000/docs")
            print("   • Backend API:     http://localhost:5400")
            print("   • Health Check:    http://localhost:8000/api/health")
        else:
            print("⚠️  SOME SERVICES NEED ATTENTION!")
            print("\n🔧 Troubleshooting:")
            print("   1. Make sure all services are started")
            print("   2. Check if ports are available")
            print("   3. Verify dependencies are installed")
            print("   4. Check service logs for errors")
        
        return all_healthy
    
    def run_all_checks(self):
        """Run all health checks"""
        print("🏥 SKILL GAP ANALYZER - HEALTH CHECK")
        print("="*60)
        
        results = {}
        
        # Check each service
        for service_key, service_config in self.services.items():
            results[service_key] = self.check_service(service_key, service_config)
        
        # If Python service is healthy, run additional tests
        if results.get('python_service'):
            self.test_skill_analysis()
        
        # If both Python and backend are healthy, test integration
        if results.get('python_service') and results.get('backend'):
            self.test_backend_integration()
        
        # Show summary
        return self.show_summary(results)

def main():
    """Main entry point"""
    checker = ServiceChecker()
    
    # Run checks
    all_healthy = checker.run_all_checks()
    
    # Exit with appropriate code
    exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main()