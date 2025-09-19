"""
Graph utilities for Context Graph Explorer
Handles concept extraction, relationship building, and graph generation
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st
import networkx as nx

# OpenAI integration
try:
    import openai
    from openai import OpenAI
except ImportError:
    st.error("OpenAI library not installed. Please install it using: pip install openai")

from prompts import (
    create_extraction_prompt,
    create_refinement_prompt,
    create_grouping_prompt,
    create_validation_prompt
)


class ConceptExtractor:
    """Extract concepts and relationships from documents using OpenAI GPT-4o"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the concept extractor with OpenAI API key"""
        self.client = None
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                st.error(f"Error initializing OpenAI client: {str(e)}")
    
    def extract_concepts(self, document_text: str, max_concepts: int = 25) -> Dict[str, Any]:
        """Extract concepts and relationships from document text"""
        if not self.client:
            return {"error": "OpenAI client not initialized. Please provide a valid API key."}
        
        try:
            prompt = create_extraction_prompt(document_text, max_concepts)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert document analyzer specializing in concept extraction and relationship mapping."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                result = self._validate_extraction_result(result)
                return result
            else:
                return {"error": "Could not parse JSON response from OpenAI"}
                
        except json.JSONDecodeError as e:
            return {"error": f"JSON parsing error: {str(e)}"}
        except Exception as e:
            return {"error": f"Error extracting concepts: {str(e)}"}
    
    def _validate_extraction_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the extraction result"""
        if 'concepts' not in result:
            result['concepts'] = []
        if 'relationships' not in result:
            result['relationships'] = []
        if 'hierarchy' not in result:
            result['hierarchy'] = []
        
        # Validate concepts
        valid_concepts = []
        concept_ids = set()
        
        for concept in result['concepts']:
            if isinstance(concept, dict) and 'id' in concept and 'name' in concept:
                concept.setdefault('description', '')
                concept.setdefault('type', 'other')
                concept.setdefault('importance', 5)
                concept.setdefault('keywords', [])
                
                concept['id'] = self._clean_id(concept['id'])
                if concept['id'] not in concept_ids:
                    concept_ids.add(concept['id'])
                    valid_concepts.append(concept)
        
        result['concepts'] = valid_concepts
        
        # Validate relationships
        valid_relationships = []
        for rel in result['relationships']:
            if (isinstance(rel, dict) and 
                'source' in rel and 'target' in rel and
                rel['source'] in concept_ids and rel['target'] in concept_ids):
                
                rel.setdefault('relationship_type', 'related_to')
                rel.setdefault('strength', 5)
                rel.setdefault('description', '')
                valid_relationships.append(rel)
        
        result['relationships'] = valid_relationships
        return result
    
    def _clean_id(self, concept_id: str) -> str:
        """Clean and normalize concept IDs"""
        cleaned = re.sub(r'[^\w\s-]', '', str(concept_id).lower())
        cleaned = re.sub(r'[\s-]+', '_', cleaned)
        return cleaned.strip('_')


class GraphBuilder:
    """Build and manage the concept graph structure"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.concept_groups = {}
    
    def build_graph(self, concepts: List[Dict], relationships: List[Dict]) -> nx.DiGraph:
        """Build NetworkX graph from concepts and relationships"""
        self.graph.clear()
        
        # Add nodes (concepts)
        for concept in concepts:
            self.graph.add_node(
                concept['id'],
                name=concept['name'],
                description=concept.get('description', ''),
                type=concept.get('type', 'other'),
                importance=concept.get('importance', 5),
                keywords=concept.get('keywords', [])
            )
        
        # Add edges (relationships)
        for rel in relationships:
            if (rel['source'] in self.graph.nodes and 
                rel['target'] in self.graph.nodes):
                self.graph.add_edge(
                    rel['source'],
                    rel['target'],
                    relationship_type=rel.get('relationship_type', 'related_to'),
                    strength=rel.get('strength', 5),
                    description=rel.get('description', '')
                )
        
        return self.graph
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the graph"""
        if self.graph.number_of_nodes() == 0:
            return {"error": "No graph data available"}
        
        try:
            return {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
                "density": nx.density(self.graph),
                "is_connected": nx.is_weakly_connected(self.graph),
                "strongly_connected_components": nx.number_strongly_connected_components(self.graph)
            }
        except Exception as e:
            return {"error": f"Error calculating graph statistics: {str(e)}"}
    
    def export_graph_data(self) -> Dict[str, Any]:
        """Export graph data for visualization"""
        nodes = []
        edges = []
        
        # Export nodes
        for node_id, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": data.get('name', node_id),
                "title": data.get('description', ''),
                "type": data.get('type', 'other'),
                "importance": data.get('importance', 5),
                "size": max(15, data.get('importance', 5) * 4)
            })
        
        # Export edges
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                "from": source,
                "to": target,
                "label": data.get('relationship_type', ''),
                "title": data.get('description', ''),
                "strength": data.get('strength', 5),
                "width": max(1, data.get('strength', 5) / 2)
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": self.get_graph_statistics()
        }
