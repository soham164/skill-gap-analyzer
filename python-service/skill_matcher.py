"""
Skill Matching Model for Skill Gap Analyzer
Implements various matching algorithms including exact, fuzzy, and semantic matching
"""

import re
import spacy
import numpy as np
from typing import List, Dict, Set, Tuple, Optional
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchingStrategy(Enum):
    """Enum for different matching strategies"""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    CONTEXTUAL = "contextual"


@dataclass
class SkillMatch:
    """Data class for skill match results"""
    skill: str
    confidence: float
    method: str
    context: Optional[str] = None
    category: Optional[str] = None


class SkillMatcher:
    """Advanced skill matching model with multiple strategies"""
    
    def __init__(self, data_processor, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize skill matcher with data processor and models
        
        Args:
            data_processor: DataProcessor instance
            model_name: Name of sentence transformer model
        """
        self.processor = data_processor
        
        # Load NLP models
        logger.info("Loading spaCy model...")
        self.nlp = spacy.load("en_core_web_sm")
        
        logger.info(f"Loading sentence transformer: {model_name}...")
        self.sbert_model = SentenceTransformer(model_name)
        
        # Initialize TF-IDF vectorizer for keyword matching
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self._initialize_tfidf()
        
        # Cache for embeddings
        self.skill_embeddings = None
        self._cache_skill_embeddings()
        
        # Configuration
        self.config = {
            'exact_match_boost': 1.0,
            'semantic_threshold': 0.55,
            'fuzzy_threshold': 0.85,
            'context_window': 50,  # characters around skill mention
            'min_confidence': 0.3
        }
    
    def _initialize_tfidf(self):
        """Initialize TF-IDF vectorizer with canonical skills"""
        
        if not self.processor.canonical_skills:
            logger.warning("No canonical skills available for TF-IDF")
            return
        
        # Create corpus from skills and their variants
        corpus = []
        for skill in self.processor.canonical_skills:
            # Add skill itself
            corpus.append(skill)
            # Add variants if available
            if skill in self.processor.skill_synonyms:
                corpus.extend(self.processor.skill_synonyms[skill])
        
        # Initialize and fit TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=5000,
            stop_words='english'
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
        
        logger.info(f"Initialized TF-IDF with {len(corpus)} skill variants")
    
    def _cache_skill_embeddings(self):
        """Pre-compute and cache skill embeddings for faster matching"""
        
        if not self.processor.canonical_skills:
            logger.warning("No canonical skills available for embedding")
            return
        
        logger.info("Computing skill embeddings...")
        
        # Create skill descriptions for better semantic matching
        skill_descriptions = []
        for skill in self.processor.canonical_skills:
            # Add context to improve embedding quality
            category = self.processor.get_skill_category(skill)
            description = f"{skill} {category} technology programming development"
            skill_descriptions.append(description)
        
        # Compute embeddings
        self.skill_embeddings = self.sbert_model.encode(
            skill_descriptions,
            convert_to_tensor=True,
            show_progress_bar=False
        )
        
        logger.info(f"Cached embeddings for {len(self.processor.canonical_skills)} skills")
    
    def exact_match(self, text: str) -> List[SkillMatch]:
        """
        Perform exact and variant matching
        
        Args:
            text: Normalized text to search
            
        Returns:
            List of exact skill matches
        """
        matches = []
        normalized = self.processor.normalize_text(text)
        
        # Sort variants by length (longest first) for better matching
        for variant in self.processor.sorted_variants:
            # Use word boundaries but allow special chars in skill names
            pattern = r"\b" + re.escape(variant) + r"\b"
            
            if re.search(pattern, normalized):
                canonical = self.processor.variant_to_canonical[variant]
                
                # Find context around the match
                match_obj = re.search(pattern, normalized)
                if match_obj:
                    start = max(0, match_obj.start() - self.config['context_window'])
                    end = min(len(normalized), match_obj.end() + self.config['context_window'])
                    context = normalized[start:end]
                else:
                    context = None
                
                # Check if already found (avoid duplicates)
                if not any(m.skill == canonical for m in matches):
                    matches.append(SkillMatch(
                        skill=canonical,
                        confidence=1.0 * self.config['exact_match_boost'],
                        method="exact",
                        context=context,
                        category=self.processor.get_skill_category(canonical)
                    ))
        
        return matches
    
    def fuzzy_match(self, text: str) -> List[SkillMatch]:
        """
        Perform fuzzy matching using TF-IDF similarity
        
        Args:
            text: Text to match against
            
        Returns:
            List of fuzzy skill matches
        """
        if self.tfidf_vectorizer is None:
            return []
        
        matches = []
        normalized = self.processor.normalize_text(text)
        
        # Vectorize input text
        text_vector = self.tfidf_vectorizer.transform([normalized])
        
        # Compute similarities
        similarities = cosine_similarity(text_vector, self.tfidf_matrix).flatten()
        
        # Find high-similarity matches
        threshold_indices = np.where(similarities >= self.config['fuzzy_threshold'])[0]
        
        skills_found = set()
        for idx in threshold_indices:
            # Map index back to skill (considering variants)
            skill_idx = idx % len(self.processor.canonical_skills)
            skill = self.processor.canonical_skills[skill_idx]
            
            if skill not in skills_found:
                skills_found.add(skill)
                matches.append(SkillMatch(
                    skill=skill,
                    confidence=float(similarities[idx]),
                    method="fuzzy",
                    category=self.processor.get_skill_category(skill)
                ))
        
        return matches
    
    def semantic_match(self, text: str, top_k: int = 10) -> List[SkillMatch]:
        """
        Perform semantic matching using sentence transformers
        
        Args:
            text: Text to match against
            top_k: Number of top matches to return
            
        Returns:
            List of semantic skill matches
        """
        if self.skill_embeddings is None:
            return []
        
        matches = []
        normalized = self.processor.normalize_text(text)
        
        if not normalized:
            return matches
        
        # Encode input text
        text_embedding = self.sbert_model.encode(
            [normalized],
            convert_to_tensor=True,
            show_progress_bar=False
        )
        
        # Compute cosine similarities
        cos_scores = util.cos_sim(text_embedding, self.skill_embeddings)[0]
        
        # Get top-k matches
        top_results = torch.topk(cos_scores, k=min(top_k, len(cos_scores)))
        
        for score, idx in zip(top_results.values, top_results.indices):
            if score >= self.config['semantic_threshold']:
                skill = self.processor.canonical_skills[idx]
                matches.append(SkillMatch(
                    skill=skill,
                    confidence=float(score),
                    method="semantic",
                    category=self.processor.get_skill_category(skill)
                ))
        
        return matches
    
    def contextual_match(self, text: str) -> List[SkillMatch]:
        """
        Perform contextual matching using NLP and domain knowledge
        
        Args:
            text: Text to analyze
            
        Returns:
            List of contextual skill matches
        """
        matches = []
        doc = self.nlp(text.lower())
        
        # Extract noun phrases and technical terms
        technical_phrases = []
        for chunk in doc.noun_chunks:
            technical_phrases.append(chunk.text)
        
        # Also look for specific patterns
        patterns = [
            r"experience with (.+?)(?:,|\.|and|$)",
            r"proficient in (.+?)(?:,|\.|and|$)",
            r"knowledge of (.+?)(?:,|\.|and|$)",
            r"skilled in (.+?)(?:,|\.|and|$)",
            r"expertise in (.+?)(?:,|\.|and|$)",
            r"working with (.+?)(?:,|\.|and|$)",
            r"familiar with (.+?)(?:,|\.|and|$)",
            r"(\w+) developer",
            r"(\w+) engineer",
            r"(\w+) programmer"
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text.lower()):
                technical_phrases.append(match.group(1) if match.lastindex else match.group())
        
        # Match phrases against skills
        for phrase in technical_phrases:
            normalized_phrase = self.processor.normalize_text(phrase)
            
            # Check if phrase contains or matches any skill
            for skill in self.processor.canonical_skills:
                if skill in normalized_phrase or normalized_phrase in skill:
                    matches.append(SkillMatch(
                        skill=skill,
                        confidence=0.7,  # Moderate confidence for contextual matches
                        method="contextual",
                        context=phrase,
                        category=self.processor.get_skill_category(skill)
                    ))
        
        # Deduplicate
        unique_matches = {}
        for match in matches:
            if match.skill not in unique_matches or match.confidence > unique_matches[match.skill].confidence:
                unique_matches[match.skill] = match
        
        return list(unique_matches.values())
    
    def hybrid_match(self, text: str, strategy_weights: Optional[Dict[str, float]] = None) -> List[SkillMatch]:
        """
        Perform hybrid matching combining all strategies
        
        Args:
            text: Text to analyze
            strategy_weights: Optional weights for each strategy
            
        Returns:
            Combined list of skill matches with weighted confidence
        """
        if strategy_weights is None:
            strategy_weights = {
                'exact': 1.0,
                'fuzzy': 0.7,
                'semantic': 0.8,
                'contextual': 0.6
            }
        
        all_matches = {}
        
        # Run all matching strategies
        strategies = [
            ('exact', self.exact_match),
            ('fuzzy', self.fuzzy_match),
            ('semantic', self.semantic_match),
            ('contextual', self.contextual_match)
        ]
        
        for strategy_name, strategy_func in strategies:
            weight = strategy_weights.get(strategy_name, 1.0)
            matches = strategy_func(text)
            
            for match in matches:
                if match.skill not in all_matches:
                    all_matches[match.skill] = {
                        'skill': match.skill,
                        'confidence': 0,
                        'methods': [],
                        'category': match.category,
                        'contexts': []
                    }
                
                # Weighted confidence aggregation
                all_matches[match.skill]['confidence'] += match.confidence * weight
                all_matches[match.skill]['methods'].append(match.method)
                if match.context:
                    all_matches[match.skill]['contexts'].append(match.context)
        
        # Normalize confidence scores and create final matches
        final_matches = []
        max_possible_score = sum(strategy_weights.values())
        
        for skill_data in all_matches.values():
            # Normalize confidence to 0-1 range
            normalized_confidence = min(1.0, skill_data['confidence'] / max_possible_score)
            
            if normalized_confidence >= self.config['min_confidence']:
                final_matches.append(SkillMatch(
                    skill=skill_data['skill'],
                    confidence=normalized_confidence,
                    method='+'.join(set(skill_data['methods'])),
                    context='; '.join(skill_data['contexts'][:2]) if skill_data['contexts'] else None,
                    category=skill_data['category']
                ))
        
        # Sort by confidence
        final_matches.sort(key=lambda x: x.confidence, reverse=True)
        
        return final_matches
    
    def match_skills(self, text: str, strategy: MatchingStrategy = MatchingStrategy.HYBRID) -> List[str]:
        """
        Main method to match skills from text
        
        Args:
            text: Text to extract skills from
            strategy: Matching strategy to use
            
        Returns:
            List of matched skill names
        """
        if strategy == MatchingStrategy.EXACT:
            matches = self.exact_match(text)
        elif strategy == MatchingStrategy.FUZZY:
            matches = self.fuzzy_match(text)
        elif strategy == MatchingStrategy.SEMANTIC:
            matches = self.semantic_match(text)
        elif strategy == MatchingStrategy.CONTEXTUAL:
            matches = self.contextual_match(text)
        else:  # HYBRID
            matches = self.hybrid_match(text)
        
        # Extract unique skill names
        skills = list(set(match.skill for match in matches))
        return sorted(skills)
    
    def match_skills_detailed(self, text: str, strategy: MatchingStrategy = MatchingStrategy.HYBRID) -> List[SkillMatch]:
        """
        Match skills and return detailed information
        
        Args:
            text: Text to extract skills from
            strategy: Matching strategy to use
            
        Returns:
            List of SkillMatch objects with detailed information
        """
        if strategy == MatchingStrategy.EXACT:
            matches = self.exact_match(text)
        elif strategy == MatchingStrategy.FUZZY:
            matches = self.fuzzy_match(text)
        elif strategy == MatchingStrategy.SEMANTIC:
            matches = self.semantic_match(text)
        elif strategy == MatchingStrategy.CONTEXTUAL:
            matches = self.contextual_match(text)
        else:  # HYBRID
            matches = self.hybrid_match(text)
        
        return matches
    
    def analyze_skill_gap(self, resume_text: str, job_text: str, detailed: bool = False) -> Dict:
        """
        Analyze skill gap between resume and job description
        
        Args:
            resume_text: Resume text
            job_text: Job description text
            detailed: Whether to return detailed match information
            
        Returns:
            Dictionary with gap analysis results
        """
        # Extract skills from both texts
        if detailed:
            resume_matches = self.match_skills_detailed(resume_text)
            job_matches = self.match_skills_detailed(job_text)
            
            resume_skills = {m.skill: m for m in resume_matches}
            job_skills = {m.skill: m for m in job_matches}
        else:
            resume_skills = set(self.match_skills(resume_text))
            job_skills = set(self.match_skills(job_text))
        
        if detailed:
            # Detailed analysis with confidence scores
            matched = {}
            missing = {}
            additional = {}
            
            for skill in job_skills:
                if skill in resume_skills:
                    matched[skill] = {
                        'resume_confidence': resume_skills[skill].confidence,
                        'job_confidence': job_skills[skill].confidence,
                        'category': job_skills[skill].category
                    }
                else:
                    missing[skill] = {
                        'confidence': job_skills[skill].confidence,
                        'category': job_skills[skill].category,
                        'recommendations': self.processor.recommendations.get(skill, {})
                    }
            
            for skill in resume_skills:
                if skill not in job_skills:
                    additional[skill] = {
                        'confidence': resume_skills[skill].confidence,
                        'category': resume_skills[skill].category
                    }
            
            match_percent = round(len(matched) / len(job_skills) * 100, 2) if job_skills else 0
            
            return {
                'matched_skills': matched,
                'missing_skills': missing,
                'additional_skills': additional,
                'match_percentage': match_percent,
                'total_job_skills': len(job_skills),
                'total_resume_skills': len(resume_skills)
            }
        else:
            # Simple analysis
            matched = resume_skills & job_skills
            missing = job_skills - resume_skills
            additional = resume_skills - job_skills
            
            match_percent = round(len(matched) / len(job_skills) * 100, 2) if job_skills else 0
            
            return {
                'matched_skills': sorted(list(matched)),
                'missing_skills': sorted(list(missing)),
                'additional_skills': sorted(list(additional)),
                'match_percentage': match_percent,
                'total_job_skills': len(job_skills),
                'total_resume_skills': len(resume_skills)
            }
    
    def get_skill_recommendations(self, missing_skills: List[str]) -> Dict[str, Dict]:
        """
        Get learning recommendations for missing skills
        
        Args:
            missing_skills: List of skills to get recommendations for
            
        Returns:
            Dictionary of skill to recommendation info
        """
        recommendations = {}
        
        for skill in missing_skills:
            if skill in self.processor.recommendations:
                recommendations[skill] = self.processor.recommendations[skill]
            else:
                # Provide generic recommendation
                recommendations[skill] = {
                    'courses': [
                        f"Search for '{skill}' tutorials online",
                        f"Check official {skill} documentation",
                        "Look for courses on Coursera, Udemy, or YouTube"
                    ],
                    'difficulty': 'varies',
                    'time_estimate': '1-3 months'
                }
            
            # Add related skills for learning path
            related = self.processor.get_related_skills(skill, limit=3)
            if related:
                recommendations[skill]['related_skills'] = related
        
        return recommendations
    
    def update_config(self, **kwargs):
        """
        Update matcher configuration
        
        Args:
            **kwargs: Configuration parameters to update
        """
        self.config.update(kwargs)
        logger.info(f"Updated configuration: {kwargs}")


# Example usage and testing
if __name__ == "_main_":
    from data_processor import DataProcessor
    
    # Initialize components
    data_processor = DataProcessor()
    matcher = SkillMatcher(data_processor)
    
    # Test text
    test_resume = """
    Senior Software Engineer with 8 years of experience in full-stack development.
    
    Technical Skills:
    - Languages: Python, JavaScript, TypeScript, Java
    - Frontend: React.js, Angular, HTML5, CSS3, Redux
    - Backend: Node.js, Django, Express, FastAPI
    - Databases: PostgreSQL, MongoDB, Redis
    - Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
    - Tools: Git, Jenkins, JIRA, VS Code
    
    Experience with microservices architecture, REST APIs, and agile methodologies.
    Strong problem-solving skills and leadership experience.
    """
    
    test_job = """
    We are looking for a Full Stack Developer with:
    - Strong experience in React and Node.js
    - Python or Java programming skills
    - Knowledge of cloud platforms (AWS or Azure)
    - Experience with Docker and Kubernetes
    - Understanding of machine learning concepts
    - GraphQL API development
    - PostgreSQL and NoSQL databases
    - Agile/Scrum experience
    """
    
    # Test different matching strategies
    print("Testing Exact Matching:")
    exact_matches = matcher.match_skills(test_resume, MatchingStrategy.EXACT)
    print(f"Found {len(exact_matches)} skills: {exact_matches[:5]}...")
    
    print("\nTesting Semantic Matching:")
    semantic_matches = matcher.match_skills(test_resume, MatchingStrategy.SEMANTIC)
    print(f"Found {len(semantic_matches)} skills: {semantic_matches[:5]}...")
    
    print("\nTesting Hybrid Matching:")
    hybrid_matches = matcher.match_skills(test_resume, MatchingStrategy.HYBRID)
    print(f"Found {len(hybrid_matches)} skills: {hybrid_matches[:5]}...")
    
    # Test skill gap analysis
    print("\n" + "="*50)
    print("Skill Gap Analysis:")
    gap_analysis = matcher.analyze_skill_gap(test_resume, test_job, detailed=False)
    
    print(f"\nMatch Percentage: {gap_analysis['match_percentage']}%")
    print(f"Matched Skills ({len(gap_analysis['matched_skills'])}): {gap_analysis['matched_skills']}")
    print(f"Missing Skills ({len(gap_analysis['missing_skills'])}): {gap_analysis['missing_skills']}")
    print(f"Additional Skills ({len(gap_analysis['additional_skills'])}): {gap_analysis['additional_skills'][:5]}...")
    
    # Get recommendations
    if gap_analysis['missing_skills']:
        print("\nRecommendations for missing skills:")
        recommendations = matcher.get_skill_recommendations(gap_analysis['missing_skills'][:3])
        for skill, info in recommendations.items():
            print(f"\n{skill}:")
            print(f"  - Difficulty: {info.get('difficulty')}")
            print(f"  - Time: {info.get('time_estimate')}")
            print(f"  - Courses: {info.get('courses', [])[0]}")