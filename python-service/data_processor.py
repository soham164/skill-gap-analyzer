"""
Data Processing Module for Skill Gap Analyzer
Handles all data loading, text extraction, and preprocessing operations
"""

import re
import fitz  # PyMuPDF
import pandas as pd
from typing import List, Dict, Set, Optional, Tuple
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles all data processing operations for skill gap analysis"""
    
    def __init__(self, data_dir: str = "./data"):
        """
        Initialize data processor with data directory
        
        Args:
            data_dir: Directory containing skills and recommendations data
        """
        self.data_dir = Path(data_dir)
        self.canonical_skills = []
        self.skill_categories = {}
        self.skill_synonyms = {}
        self.recommendations = {}
        self.variant_to_canonical = {}
        
        # Load all data on initialization
        self._load_skills_database()
        self._load_recommendations()
        self._build_variant_mappings()
    
    def _load_skills_database(self):
        """Load comprehensive skills database with categories and synonyms"""
        
        # Extended skills database with categories
        self.skills_db = {
            "programming_languages": [
                "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", 
                "rust", "kotlin", "swift", "php", "r", "matlab", "scala", "perl", "bash",
                "powershell", "sql", "plsql", "t-sql", "objective-c", "dart", "julia",
                "haskell", "clojure", "erlang", "elixir", "f#", "visual basic", "cobol"
            ],
            "frontend": [
                "react", "angular", "vue.js", "svelte", "next.js", "nuxt.js", "gatsby",
                "html", "css", "sass", "less", "tailwind css", "bootstrap", "material ui",
                "jquery", "webpack", "babel", "redux", "mobx", "rxjs", "graphql",
                "apollo", "relay", "ember.js", "backbone.js", "alpine.js", "lit"
            ],
            "backend": [
                "node.js", "express", "django", "flask", "fastapi", "spring boot", "rails",
                "asp.net", "laravel", "symfony", "gin", "echo", "fiber", "nestjs",
                "koa", "hapi", "strapi", "graphql", "grpc", "rest api", "soap",
                "microservices", "serverless", "lambda", "api gateway"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
                "oracle", "sql server", "sqlite", "dynamodb", "firebase", "supabase",
                "couchdb", "neo4j", "influxdb", "timescaledb", "clickhouse", "mariadb",
                "memcached", "etcd", "cockroachdb", "fauna", "arangodb"
            ],
            "cloud_devops": [
                "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
                "jenkins", "gitlab ci", "github actions", "circleci", "travis ci",
                "prometheus", "grafana", "elk stack", "datadog", "new relic", "nginx",
                "apache", "load balancing", "cdn", "cloudflare", "heroku", "vercel",
                "netlify", "digitalocean", "linode", "vagrant", "puppet", "chef"
            ],
            "data_science_ml": [
                "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
                "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "plotly",
                "jupyter", "spark", "hadoop", "airflow", "mlflow", "kubeflow",
                "computer vision", "nlp", "opencv", "spacy", "nltk", "transformers",
                "hugging face", "langchain", "vector databases", "pinecone", "weaviate"
            ],
            "mobile": [
                "react native", "flutter", "ionic", "xamarin", "swift", "swiftui",
                "kotlin", "android studio", "xcode", "expo", "capacitor", "cordova",
                "native script", "android", "ios", "watchos", "tvos"
            ],
            "testing_qa": [
                "jest", "mocha", "cypress", "selenium", "playwright", "puppeteer",
                "junit", "pytest", "unittest", "testng", "jasmine", "karma", "chai",
                "postman", "insomnia", "jmeter", "gatling", "cucumber", "appium"
            ],
            "security": [
                "oauth", "jwt", "ssl/tls", "encryption", "penetration testing", "owasp",
                "burp suite", "metasploit", "nmap", "wireshark", "kali linux",
                "cryptography", "zero trust", "siem", "ids/ips", "firewall", "vpn"
            ],
            "soft_skills": [
                "agile", "scrum", "kanban", "leadership", "communication", "teamwork",
                "problem solving", "critical thinking", "project management", "jira",
                "confluence", "slack", "microsoft teams", "notion", "asana", "trello"
            ],
            "blockchain_web3": [
                "blockchain", "ethereum", "solidity", "web3.js", "ethers.js", "truffle",
                "hardhat", "smart contracts", "defi", "nft", "ipfs", "metamask",
                "polygon", "binance smart chain", "avalanche", "solana", "rust"
            ],
            "game_dev": [
                "unity", "unreal engine", "godot", "c++", "c#", "opengl", "directx",
                "vulkan", "webgl", "three.js", "babylon.js", "phaser", "game design"
            ]
        }
        
        # Flatten all skills into canonical list
        for category, skills in self.skills_db.items():
            self.canonical_skills.extend(skills)
            for skill in skills:
                self.skill_categories[skill] = category
        
        # Enhanced synonyms mapping
        self.skill_synonyms = {
            "react": ["react", "reactjs", "react.js", "react js"],
            "vue.js": ["vue", "vuejs", "vue.js", "vue js"],
            "angular": ["angular", "angularjs", "angular.js", "angular js"],
            "node.js": ["node", "nodejs", "node.js", "node js"],
            "express": ["express", "expressjs", "express.js", "express js"],
            "mongodb": ["mongodb", "mongo db", "mongo", "mongo-db"],
            "postgresql": ["postgresql", "postgres", "pgsql", "postgre sql"],
            "rest api": ["rest api", "restapi", "rest-api", "rest", "restful api"],
            "javascript": ["javascript", "js", "ecmascript", "es6", "es2015"],
            "typescript": ["typescript", "ts"],
            "python": ["python", "python3", "python 3"],
            "c++": ["c++", "cpp", "cplusplus", "c plus plus"],
            "c#": ["c#", "csharp", "c sharp", ".net"],
            "sql": ["sql", "structured query language"],
            "machine learning": ["machine learning", "ml", "machine-learning"],
            "deep learning": ["deep learning", "dl", "deep-learning"],
            "artificial intelligence": ["artificial intelligence", "ai"],
            "aws": ["aws", "amazon web services"],
            "gcp": ["gcp", "google cloud platform", "google cloud"],
            "azure": ["azure", "microsoft azure"],
            "github": ["github", "git hub"],
            "git": ["git", "version control"],
            "ci/cd": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
            "docker": ["docker", "containerization", "containers"],
            "kubernetes": ["kubernetes", "k8s", "k8", "kube"],
            "html": ["html", "html5"],
            "css": ["css", "css3", "stylesheets"],
            "sass": ["sass", "scss"],
            "jquery": ["jquery", "jquery.js", "jquery js"],
            "mysql": ["mysql", "my sql"],
            "oracle": ["oracle", "oracle db", "oracle database"],
            "redis": ["redis", "redis cache", "redis db"],
            "elasticsearch": ["elasticsearch", "elastic search", "elastic"],
            "kafka": ["kafka", "apache kafka"],
            "rabbitmq": ["rabbitmq", "rabbit mq", "rabbit"],
            "graphql": ["graphql", "graph ql"],
            "grpc": ["grpc", "g rpc"],
            "jenkins": ["jenkins", "jenkins ci"],
            "terraform": ["terraform", "tf"],
            "ansible": ["ansible", "ansible automation"],
            "linux": ["linux", "gnu/linux", "unix"],
            "windows": ["windows", "windows server", "win32"],
            "macos": ["macos", "mac os", "osx", "os x"]
        }
        
        logger.info(f"Loaded {len(self.canonical_skills)} canonical skills across {len(self.skills_db)} categories")
    
    def _load_recommendations(self):
        """Load comprehensive learning recommendations"""
        
        # Extended recommendations with multiple resources per skill
        self.recommendations = {
            # Programming Languages
            "python": {
                "courses": [
                    "Python for Everybody - Coursera",
                    "Complete Python Bootcamp - Udemy",
                    "Python Documentation - python.org"
                ],
                "difficulty": "beginner",
                "time_estimate": "3-6 months"
            },
            "javascript": {
                "courses": [
                    "JavaScript: The Complete Guide - Udemy",
                    "freeCodeCamp JavaScript Algorithms",
                    "MDN JavaScript Guide"
                ],
                "difficulty": "beginner",
                "time_estimate": "3-6 months"
            },
            "typescript": {
                "courses": [
                    "TypeScript Documentation - typescriptlang.org",
                    "Understanding TypeScript - Udemy",
                    "TypeScript Deep Dive - GitBook"
                ],
                "difficulty": "intermediate",
                "time_estimate": "1-2 months"
            },
            "java": {
                "courses": [
                    "Java Programming Masterclass - Udemy",
                    "Java MOOC - University of Helsinki",
                    "Oracle Java Documentation"
                ],
                "difficulty": "intermediate",
                "time_estimate": "4-6 months"
            },
            
            # Frontend
            "react": {
                "courses": [
                    "React Documentation - react.dev",
                    "Complete React Developer - ZTM",
                    "Epic React - Kent C. Dodds"
                ],
                "difficulty": "intermediate",
                "time_estimate": "2-3 months"
            },
            "angular": {
                "courses": [
                    "Angular - The Complete Guide - Udemy",
                    "Angular Documentation - angular.io",
                    "Angular University"
                ],
                "difficulty": "intermediate",
                "time_estimate": "3-4 months"
            },
            "vue.js": {
                "courses": [
                    "Vue Mastery - Official Vue.js Courses",
                    "Vue.js Documentation - vuejs.org",
                    "The Complete Vue.js Course - Udemy"
                ],
                "difficulty": "intermediate",
                "time_estimate": "2-3 months"
            },
            
            # Backend
            "node.js": {
                "courses": [
                    "The Complete Node.js Developer Course - Udemy",
                    "Node.js Documentation - nodejs.org",
                    "Node.js Design Patterns - Book"
                ],
                "difficulty": "intermediate",
                "time_estimate": "2-3 months"
            },
            "django": {
                "courses": [
                    "Django for Beginners - William Vincent",
                    "Django Documentation - djangoproject.com",
                    "Two Scoops of Django - Book"
                ],
                "difficulty": "intermediate",
                "time_estimate": "2-3 months"
            },
            
            # Databases
            "sql": {
                "courses": [
                    "SQL for Data Science - Coursera",
                    "The Complete SQL Bootcamp - Udemy",
                    "SQLZoo Interactive Tutorial"
                ],
                "difficulty": "beginner",
                "time_estimate": "1-2 months"
            },
            "mongodb": {
                "courses": [
                    "MongoDB University - Free Courses",
                    "MongoDB - The Complete Developer's Guide - Udemy",
                    "MongoDB Documentation"
                ],
                "difficulty": "intermediate",
                "time_estimate": "1-2 months"
            },
            
            # Cloud & DevOps
            "docker": {
                "courses": [
                    "Docker Mastery - Udemy",
                    "Docker Documentation - docker.com",
                    "Play with Docker - Interactive Labs"
                ],
                "difficulty": "intermediate",
                "time_estimate": "1-2 months"
            },
            "kubernetes": {
                "courses": [
                    "Certified Kubernetes Administrator - Linux Foundation",
                    "Kubernetes Documentation - kubernetes.io",
                    "Kubernetes the Hard Way - Kelsey Hightower"
                ],
                "difficulty": "advanced",
                "time_estimate": "3-4 months"
            },
            "aws": {
                "courses": [
                    "AWS Certified Solutions Architect - A Cloud Guru",
                    "AWS Documentation & Free Tier",
                    "AWS Well-Architected Framework"
                ],
                "difficulty": "intermediate",
                "time_estimate": "3-6 months"
            },
            
            # Data Science & ML
            "machine learning": {
                "courses": [
                    "Machine Learning - Andrew Ng (Coursera)",
                    "Fast.ai Practical Deep Learning",
                    "Hands-On Machine Learning - Book"
                ],
                "difficulty": "advanced",
                "time_estimate": "4-6 months"
            },
            "tensorflow": {
                "courses": [
                    "TensorFlow Developer Certificate - Google",
                    "TensorFlow Documentation & Tutorials",
                    "Deep Learning Specialization - Coursera"
                ],
                "difficulty": "advanced",
                "time_estimate": "3-4 months"
            }
        }
        
        # Add default recommendation for skills without specific resources
        for skill in self.canonical_skills:
            if skill not in self.recommendations:
                self.recommendations[skill] = {
                    "courses": [
                        f"Search for '{skill}' on Coursera",
                        f"Search for '{skill}' on Udemy",
                        f"Official {skill} documentation"
                    ],
                    "difficulty": "varies",
                    "time_estimate": "1-3 months"
                }
        
        logger.info(f"Loaded recommendations for {len(self.recommendations)} skills")
    
    def _build_variant_mappings(self):
        """Build comprehensive variant to canonical skill mappings"""
        
        # Reset mapping
        self.variant_to_canonical = {}
        
        # Map each canonical skill to itself
        for skill in self.canonical_skills:
            self.variant_to_canonical[skill] = skill
        
        # Add all synonym mappings
        for canonical, variants in self.skill_synonyms.items():
            for variant in variants:
                self.variant_to_canonical[variant.lower()] = canonical
        
        # Sort variants by length (longest first) for better matching
        self.sorted_variants = sorted(self.variant_to_canonical.keys(), 
                                     key=lambda x: -len(x))
        
        logger.info(f"Built {len(self.variant_to_canonical)} variant mappings")
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for skill extraction
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Normalized text string
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Keep alphanumeric and special chars used in tech (.#+-/)
        text = re.sub(r"[^a-z0-9\+\.\#\-\/\s]", " ", text)
        
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str = None, pdf_bytes: bytes = None) -> str:
        """
        Extract text from PDF file or bytes
        
        Args:
            pdf_path: Path to PDF file
            pdf_bytes: PDF file as bytes
            
        Returns:
            Extracted text string
        """
        try:
            if pdf_path:
                with fitz.open(pdf_path) as doc:
                    text = " ".join(page.get_text() for page in doc)
            elif pdf_bytes:
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                    text = " ".join(page.get_text() for page in doc)
            else:
                return ""
            
            # Clean up extracted text
            text = re.sub(r'\n+', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_sections_from_resume(self, text: str) -> Dict[str, str]:
        """
        Extract different sections from resume text
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary of section names to content
        """
        sections = {}
        
        # Common section headers
        section_patterns = [
            r"(skills?|technical skills?|core competenc\w+)",
            r"(experience|work experience|employment|professional experience)",
            r"(education|academic|qualification)",
            r"(projects?|personal projects?)",
            r"(certificat\w+|training)",
            r"(summary|objective|profile)",
            r"(achievements?|accomplishments?)"
        ]
        
        normalized = self.normalize_text(text)
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, normalized)
            for match in matches:
                start = match.start()
                # Find next section or end of text
                next_section = len(normalized)
                for next_pattern in section_patterns:
                    next_matches = re.finditer(next_pattern, normalized[start+len(match.group()):])
                    for next_match in next_matches:
                        next_section = min(next_section, start + len(match.group()) + next_match.start())
                        break
                
                section_name = match.group()
                section_content = normalized[start:next_section]
                sections[section_name] = section_content
        
        # If no sections found, treat entire text as content
        if not sections:
            sections["full_text"] = normalized
        
        return sections
    
    def get_skill_category(self, skill: str) -> str:
        """
        Get the category of a skill
        
        Args:
            skill: Skill name
            
        Returns:
            Category name or 'uncategorized'
        """
        return self.skill_categories.get(skill.lower(), 'uncategorized')
    
    def get_related_skills(self, skill: str, limit: int = 5) -> List[str]:
        """
        Get skills related to the given skill (same category)
        
        Args:
            skill: Skill name
            limit: Maximum number of related skills
            
        Returns:
            List of related skill names
        """
        category = self.get_skill_category(skill)
        if category == 'uncategorized':
            return []
        
        related = []
        for s in self.canonical_skills:
            if s != skill.lower() and self.get_skill_category(s) == category:
                related.append(s)
                if len(related) >= limit:
                    break
        
        return related
    
    def save_data(self, output_dir: str = "./data"):
        """
        Save all data to CSV files for persistence
        
        Args:
            output_dir: Directory to save data files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save canonical skills with categories
        skills_data = []
        for skill in self.canonical_skills:
            skills_data.append({
                'skill': skill,
                'category': self.get_skill_category(skill)
            })
        
        pd.DataFrame(skills_data).to_csv(
            output_path / "skills.csv", 
            index=False
        )
        
        # Save recommendations
        rec_data = []
        for skill, info in self.recommendations.items():
            rec_data.append({
                'skill': skill,
                'courses': json.dumps(info.get('courses', [])),
                'difficulty': info.get('difficulty', 'varies'),
                'time_estimate': info.get('time_estimate', 'varies')
            })
        
        pd.DataFrame(rec_data).to_csv(
            output_path / "recommendations.csv",
            index=False
        )
        
        # Save synonyms
        syn_data = []
        for canonical, variants in self.skill_synonyms.items():
            syn_data.append({
                'canonical': canonical,
                'variants': json.dumps(variants)
            })
        
        pd.DataFrame(syn_data).to_csv(
            output_path / "synonyms.csv",
            index=False
        )
        
        logger.info(f"Saved data to {output_path}")


# Example usage and testing
if __name__ == "_main_":
    # Initialize processor
    processor = DataProcessor()
    
    # Test text normalization
    test_text = "I have experience with React.js, Node.JS, and C++ programming!"
    normalized = processor.normalize_text(test_text)
    print(f"Normalized: {normalized}")
    
    # Test skill category lookup
    print(f"React category: {processor.get_skill_category('react')}")
    print(f"Related to React: {processor.get_related_skills('react')}")
    
    # Save data for persistence
    processor.save_data()
    
    print(f"\nTotal skills: {len(processor.canonical_skills)}")
    print(f"Total categories: {len(processor.skills_db)}")
    print(f"Total recommendations: {len(processor.recommendations)}")