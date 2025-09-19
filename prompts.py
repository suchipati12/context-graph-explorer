"""
Prompt templates for OpenAI GPT-4o concept extraction
"""

CONCEPT_EXTRACTION_PROMPT = """
You are an expert at analyzing documents and extracting key concepts, relationships, and hierarchical structures.

Given the following document text, please:

1. **Identify Key Concepts**: Extract the main concepts, entities, ideas, and important terms
2. **Define Relationships**: Determine how concepts relate to each other (dependencies, hierarchies, associations)
3. **Create Hierarchy**: Organize concepts into logical groups or levels where applicable

Document Text:
```
{document_text}
```

Please return your analysis in the following JSON format:

{{
    "concepts": [
        {{
            "id": "unique_concept_id",
            "name": "Concept Name",
            "description": "Brief description of the concept",
            "type": "category|entity|process|definition|other",
            "importance": 1-10,
            "keywords": ["keyword1", "keyword2"]
        }}
    ],
    "relationships": [
        {{
            "source": "concept_id_1",
            "target": "concept_id_2",
            "relationship_type": "depends_on|part_of|related_to|defines|includes|causes|enables",
            "strength": 1-10,
            "description": "Brief description of the relationship"
        }}
    ],
    "hierarchy": [
        {{
            "parent": "parent_concept_id",
            "children": ["child_concept_id_1", "child_concept_id_2"],
            "level": 1
        }}
    ],
    "summary": "Brief summary of the document's main themes and structure"
}}

Guidelines:
- Use descriptive, consistent concept IDs (lowercase, underscores)
- Focus on the most important concepts (aim for 10-30 concepts depending on document length)
- Relationship types should be meaningful and consistent
- Importance and strength scores should reflect actual significance
- Include both explicit and implicit relationships
- Consider temporal, causal, and hierarchical relationships
"""

RELATIONSHIP_REFINEMENT_PROMPT = """
Given the extracted concepts and their initial relationships, please refine and enhance the relationship network by:

1. **Adding Missing Relationships**: Identify implicit connections between concepts
2. **Improving Relationship Types**: Ensure relationship types are accurate and specific
3. **Adjusting Strengths**: Fine-tune relationship strength scores based on context
4. **Removing Weak Connections**: Filter out relationships that aren't meaningful

Current Concepts and Relationships:
```json
{current_data}
```

Please return the refined relationship network in the same JSON format, focusing on:
- More accurate relationship types
- Better strength scoring
- Additional meaningful connections
- Removal of weak or irrelevant relationships

Return only the "relationships" array in JSON format.
"""

CONCEPT_GROUPING_PROMPT = """
Given the following concepts from a document, please organize them into logical groups or clusters that represent different themes, topics, or functional areas.

Concepts:
```json
{concepts}
```

Please return a JSON structure that groups related concepts:

{{
    "groups": [
        {{
            "group_id": "unique_group_id",
            "group_name": "Descriptive Group Name",
            "description": "Brief description of what this group represents",
            "concepts": ["concept_id_1", "concept_id_2"],
            "color": "#hex_color_code",
            "priority": 1-5
        }}
    ]
}}

Guidelines:
- Create 3-8 meaningful groups
- Each concept should belong to exactly one primary group
- Group names should be descriptive and concise
- Use distinct colors for visualization
- Priority indicates importance (1=highest, 5=lowest)
"""

GRAPH_VALIDATION_PROMPT = """
Please validate and optimize this concept graph for visualization:

Graph Data:
```json
{graph_data}
```

Check for:
1. **Orphaned Nodes**: Concepts with no relationships
2. **Circular Dependencies**: Loops that might cause visualization issues
3. **Over-connected Nodes**: Concepts with too many relationships (>10)
4. **Weak Relationships**: Connections with very low strength scores (<3)

Suggest improvements to make the graph more readable and meaningful for visualization.

Return recommendations in JSON format:
{{
    "issues": [
        {{
            "type": "orphaned_node|circular_dependency|over_connected|weak_relationship",
            "description": "Description of the issue",
            "affected_concepts": ["concept_ids"],
            "suggestion": "How to fix this issue"
        }}
    ],
    "optimized_graph": {{
        "concepts": [...],
        "relationships": [...],
        "groups": [...]
    }}
}}
"""

def create_extraction_prompt(document_text: str, max_concepts: int = 25) -> str:
    """Create a customized concept extraction prompt"""
    prompt = CONCEPT_EXTRACTION_PROMPT.format(document_text=document_text)
    
    if max_concepts != 25:
        prompt += f"\n\nNote: Focus on the top {max_concepts} most important concepts."
    
    return prompt

def create_refinement_prompt(current_data: dict) -> str:
    """Create a relationship refinement prompt"""
    import json
    return RELATIONSHIP_REFINEMENT_PROMPT.format(
        current_data=json.dumps(current_data, indent=2)
    )

def create_grouping_prompt(concepts: list) -> str:
    """Create a concept grouping prompt"""
    import json
    return CONCEPT_GROUPING_PROMPT.format(
        concepts=json.dumps(concepts, indent=2)
    )

def create_validation_prompt(graph_data: dict) -> str:
    """Create a graph validation prompt"""
    import json
    return GRAPH_VALIDATION_PROMPT.format(
        graph_data=json.dumps(graph_data, indent=2)
    )