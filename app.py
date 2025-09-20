"""
Context Graph Explorer - Main Streamlit Application
Upload documents and visualize concept relationships as interactive graphs
"""

import streamlit as st
import json
import tempfile
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Import our custom modules
from parsing_utils import DocumentParser, validate_file_upload
from graph_utils import ConceptExtractor, GraphBuilder
from pyvis.network import Network
import networkx as nx

# Check if running on Hugging Face Spaces
IS_HUGGINGFACE = os.getenv("SPACE_ID") is not None


def generate_comprehensive_html_report(doc_info, stats, ai_summary, sorted_concepts, 
                                     relationships, relationship_types, export_data):
    """Generate a comprehensive HTML report with embedded interactive graph"""
    
    # Create a new graph for the HTML report
    report_net = Network(
        height="600px",
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
        directed=True
    )
    
    # Configure the graph
    report_net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "stabilization": {"iterations": 100},
        "barnesHut": {"gravitationalConstant": -8000, "springConstant": 0.001}
      },
      "interaction": {
        "dragNodes": true,
        "dragView": true,
        "zoomView": true
      },
      "nodes": {
        "font": {"size": 14}
      },
      "edges": {
        "font": {"size": 12}
      }
    }
    """)
    
    # Add nodes to report graph
    for node in export_data['nodes']:
        type_colors = {
            'category': '#ff9999',
            'entity': '#66b3ff',
            'process': '#99ff99',
            'definition': '#ffcc99',
            'other': '#ff99cc'
        }
        color = type_colors.get(node['type'], '#cccccc')
        
        report_net.add_node(
            node['id'],
            label=node['label'],
            title=f"{node['title']}\\nType: {node['type']}\\nImportance: {node['importance']}",
            size=int(node['size'] * 1.5),
            color=color,
            font={'size': 14, 'color': 'black'}
        )
    
    # Add edges to report graph
    for edge in export_data['edges']:
        report_net.add_edge(
            edge['from'],
            edge['to'],
            label=edge['label'],
            title=f"{edge['label']}: {edge['title']}",
            width=edge['width'],
            arrows="to"
        )
    
    # Generate graph HTML
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as graph_tmp:
        report_net.save_graph(graph_tmp.name)
        with open(graph_tmp.name, 'r', encoding='utf-8') as f:
            graph_html_content = f.read()
        os.unlink(graph_tmp.name)
    
    # Extract just the graph div and script from the generated HTML
    import re
    graph_div_match = re.search(r'<div id="mynetworkid".*?</div>', graph_html_content, re.DOTALL)
    script_match = re.search(r'<script type="text/javascript">.*?</script>', graph_html_content, re.DOTALL)
    
    graph_div = graph_div_match.group(0) if graph_div_match else '<div>Graph could not be generated</div>'
    graph_script = script_match.group(0) if script_match else ''
    
    # Create comprehensive HTML report
    html_report = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Context Graph Explorer - Analysis Report</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; font-weight: 300; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 1.1em; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: #e8f5e8; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; color: #2e7d32; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .graph-container {{ border: 1px solid #ddd; border-radius: 8px; margin: 20px 0; background: white; }}
        #mynetworkid {{ height: 600px !important; width: 100% !important; }}
        .ai-summary {{ background: #fff3e0; padding: 20px; border-radius: 8px; border-left: 4px solid #ff9800; font-style: italic; }}
        .concept-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }}
        .concept-item {{ background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; }}
        .concept-item h4 {{ margin: 0 0 10px 0; color: #333; }}
        .concept-importance {{ background: #667eea; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; display: inline-block; }}
        .footer {{ background: #333; color: white; text-align: center; padding: 20px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Context Graph Explorer</h1>
            <p>Document Analysis Report</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📄 Document Information</h2>
                <p><strong>Filename:</strong> {doc_info.get('filename', 'Unknown')}</p>
                <p><strong>Type:</strong> {doc_info.get('file_type', 'Unknown')}</p>
                <p><strong>Processed:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Graph Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('nodes', 0)}</div>
                        <div class="stat-label">Concepts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('edges', 0)}</div>
                        <div class="stat-label">Relationships</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats.get('density', 0):.3f}</div>
                        <div class="stat-label">Density</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🌐 Interactive Concept Graph</h2>
                <p><em>Drag nodes to move them, use mouse wheel to zoom, and click and drag to pan around the graph.</em></p>
                <div class="graph-container">
                    {graph_div}
                </div>
            </div>
            
            <div class="section">
                <h2>🤖 AI-Generated Summary</h2>
                <div class="ai-summary">
                    {ai_summary.replace(chr(10), '<br>')}
                </div>
            </div>
            
            <div class="section">
                <h2>🎯 Key Concepts</h2>
                <div class="concept-list">"""
    
    # Add top concepts
    for i, concept in enumerate(sorted_concepts[:15], 1):
        concept_type = concept.get('type', 'other')
        html_report += f"""
                    <div class="concept-item">
                        <h4>{concept.get('name', 'Unknown')} <span class="concept-importance">{concept.get('importance', 0)}</span></h4>
                        <p><strong>Type:</strong> {concept_type.title()}</p>
                        <p>{concept.get('description', 'No description available')}</p>
                    </div>"""
    
    html_report += """
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by Context Graph Explorer | Powered by OpenAI GPT-4o</p>
        </div>
    </div>
    
    """ + graph_script + """
</body>
</html>"""
    
    return html_report

# Configure Streamlit page
st.set_page_config(
    page_title="Context Graph Explorer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'document_data' not in st.session_state:
    st.session_state.document_data = None
if 'graph_data' not in st.session_state:
    st.session_state.graph_data = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

def main():
    """Main application function"""
    
    # Header
    st.title("🔍 Context Graph Explorer")
    st.markdown("Upload a document and explore its concepts as an interactive graph")
    
    # Add Hugging Face specific info
    if IS_HUGGINGFACE:
        st.info("🤗 Running on Hugging Face Spaces! Add your OpenAI API key in the sidebar to get started.")
    
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # OpenAI API Key
        # Check for environment variable first (for Hugging Face Spaces)
        default_api_key = os.getenv("OPENAI_API_KEY", st.session_state.api_key)
        
        api_key = st.text_input(
            "OpenAI API Key:",
            type="password",
            value=default_api_key,
            help="Enter your OpenAI API key to enable AI-powered concept extraction"
        )
        
        if IS_HUGGINGFACE and not api_key:
            st.warning("⚠️ Please add your OpenAI API key to use the AI features. You can also set it as a Hugging Face Space secret.")
        
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
        
        st.markdown("---")
        
        # Processing options
        st.subheader("Processing Options")
        max_concepts = st.slider(
            "Max concepts to extract:",
            min_value=5,
            max_value=50,
            value=25,
            help="Maximum number of concepts to extract from the document"
        )
        
        # Graph visualization options
        st.subheader("Visualization Options")
        
        physics_enabled = st.checkbox(
            "Enable physics simulation",
            value=True,
            help="Enable interactive physics for the graph"
        )
        
        show_labels = st.checkbox(
            "Show relationship labels",
            value=True,
            help="Display relationship types on edges"
        )
        
        node_size_factor = st.slider(
            "Node size factor:",
            min_value=1.0,
            max_value=3.0,
            value=1.5,
            step=0.1,
            help="Adjust the size of nodes in the graph"
        )
        
        # Font size
        font_size = st.slider(
            "Font size:",
            min_value=8,
            max_value=24,
            value=14,
            help="Adjust the font size of node labels"
        )
        
        # Node label display
        show_node_labels = st.checkbox(
            "Show node labels",
            value=True,
            help="Display concept names on nodes"
        )
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📄 Document Upload")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=['pdf', 'docx', 'txt', 'md'],
            help="Upload PDF, DOCX, TXT, or Markdown files"
        )
        
        if uploaded_file:
            # Validate file
            validation_error = validate_file_upload(uploaded_file)
            if validation_error:
                st.error(validation_error)
                return
            
            # Parse document button
            if st.button("📖 Parse Document", type="primary"):
                with st.spinner("Parsing document..."):
                    parser = DocumentParser()
                    document_data = parser.parse_document(uploaded_file)
                    
                    if "error" in document_data:
                        st.error(f"Error parsing document: {document_data['error']}")
                    else:
                        st.session_state.document_data = document_data
                        st.success("✅ Document parsed successfully!")
        
        # Show document info
        if st.session_state.document_data:
            st.subheader("📋 Document Info")
            doc_data = st.session_state.document_data
            
            st.write(f"**Filename:** {doc_data['filename']}")
            st.write(f"**Type:** {doc_data['file_type']}")
            
            # Show metadata based on file type
            metadata = doc_data.get('metadata', {})
            if 'pages' in metadata:
                st.write(f"**Pages:** {metadata['pages']}")
            elif 'paragraphs' in metadata:
                st.write(f"**Paragraphs:** {metadata['paragraphs']}")
            elif 'lines' in metadata:
                st.write(f"**Lines:** {metadata['lines']}")
            
            # Text preview
            with st.expander("📝 Text Preview"):
                parser = DocumentParser()
                preview = parser.get_text_preview(doc_data['text_content'], 1000)
                st.text_area("Document content preview:", preview, height=200, disabled=True)
            
            # Extract concepts button
            if st.session_state.api_key:
                if st.button("🧠 Extract Concepts", type="primary"):
                    with st.spinner("Extracting concepts using AI..."):
                        extractor = ConceptExtractor(st.session_state.api_key)
                        extraction_result = extractor.extract_concepts(
                            doc_data['text_content'], 
                            max_concepts
                        )
                        
                        if "error" in extraction_result:
                            st.error(f"Error extracting concepts: {extraction_result['error']}")
                        else:
                            # Build graph
                            graph_builder = GraphBuilder()
                            graph_builder.build_graph(
                                extraction_result['concepts'],
                                extraction_result['relationships']
                            )
                            
                            # Store graph data
                            st.session_state.graph_data = {
                                'extraction_result': extraction_result,
                                'graph_builder': graph_builder,
                                'export_data': graph_builder.export_graph_data()
                            }
                            
                            st.success("✅ Concepts extracted and graph built!")
            else:
                st.warning("⚠️ Please enter your OpenAI API key to extract concepts")
    
    with col2:
        st.header("🌐 Concept Graph")
        
        if st.session_state.graph_data:
            graph_data = st.session_state.graph_data
            export_data = graph_data['export_data']
            
            # Graph statistics
            stats = export_data['statistics']
            if 'error' not in stats:
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Concepts", stats['nodes'])
                with col_stat2:
                    st.metric("Relationships", stats['edges'])
                with col_stat3:
                    st.metric("Density", f"{stats['density']:.3f}")
            
            # Graph display options
            graph_height = st.selectbox(
                "Graph height:",
                options=["600px", "800px", "1000px", "1200px"],
                index=1,
                help="Select the height of the graph visualization"
            )
            
            # Create and display the graph
            try:
                net = Network(
                    height=graph_height,
                    width="100%",
                    bgcolor="#ffffff",
                    font_color="black",
                    directed=True
                )
                
                # Configure physics and interaction
                if physics_enabled:
                    net.set_options(f"""
                    var options = {{
                      "physics": {{
                        "enabled": true,
                        "stabilization": {{"iterations": 100}},
                        "barnesHut": {{"gravitationalConstant": -8000, "springConstant": 0.001}}
                      }},
                      "interaction": {{
                        "dragNodes": true,
                        "dragView": true,
                        "zoomView": true
                      }},
                      "nodes": {{
                        "font": {{"size": {font_size}}}
                      }},
                      "edges": {{
                        "font": {{"size": {max(8, font_size - 2)}}}
                      }}
                    }}
                    """)
                else:
                    net.set_options(f"""
                    var options = {{
                      "physics": {{"enabled": false}},
                      "interaction": {{
                        "dragNodes": true,
                        "dragView": true,
                        "zoomView": true
                      }},
                      "nodes": {{
                        "font": {{"size": {font_size}}}
                      }},
                      "edges": {{
                        "font": {{"size": {max(8, font_size - 2)}}}
                      }}
                    }}
                    """)
                
                # Add nodes
                for node in export_data['nodes']:
                    # Color nodes by type
                    type_colors = {
                        'category': '#ff9999',
                        'entity': '#66b3ff',
                        'process': '#99ff99',
                        'definition': '#ffcc99',
                        'other': '#ff99cc'
                    }
                    color = type_colors.get(node['type'], '#cccccc')
                    
                    # Configure node label
                    node_label = node['label'] if show_node_labels else ""
                    
                    net.add_node(
                        node['id'],
                        label=node_label,
                        title=f"{node['title']}\nType: {node['type']}\nImportance: {node['importance']}",
                        size=int(node['size'] * node_size_factor),
                        color=color,
                        font={'size': font_size, 'color': 'black'}
                    )
                
                # Add edges
                for edge in export_data['edges']:
                    label = edge['label'] if show_labels else ""
                    net.add_edge(
                        edge['from'],
                        edge['to'],
                        label=label,
                        title=f"{edge['label']}: {edge['title']}",
                        width=edge['width'],
                        arrows="to"
                    )
                
                # Generate and display the graph
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
                    net.save_graph(tmp_file.name)
                    
                    with open(tmp_file.name, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Display in expandable container
                    with st.container():
                        st.markdown("### 🌐 Interactive Graph")
                        st.markdown("*Drag nodes, zoom, and pan to explore. Hover over nodes for details.*")
                        
                        # Convert height string to integer for st.components
                        height_px = int(graph_height.replace('px', ''))
                        st.components.v1.html(html_content, height=height_px, scrolling=True)
                    
                    # Add graph controls
                    col_tip, col_download = st.columns([2, 1])
                    with col_tip:
                        st.info("💡 **Tip**: Use browser's fullscreen mode (F11) for better graph exploration!")
                    with col_download:
                        # Download graph as HTML
                        st.download_button(
                            label="📱 Download Graph HTML",
                            data=html_content,
                            file_name="concept_graph.html",
                            mime="text/html",
                            help="Download the graph as a standalone HTML file for full-screen viewing"
                        )
                    
                    # Clean up temporary file
                    os.unlink(tmp_file.name)
                    
            except Exception as e:
                st.error(f"Error creating graph visualization: {str(e)}")
            
            # Concept details
            with st.expander("📊 Concept Details"):
                extraction_result = graph_data['extraction_result']
                
                st.subheader("Key Concepts")
                concepts_df_data = []
                for concept in extraction_result['concepts']:
                    concepts_df_data.append({
                        'Name': concept['name'],
                        'Type': concept['type'],
                        'Importance': concept['importance'],
                        'Description': concept['description'][:100] + '...' if len(concept['description']) > 100 else concept['description']
                    })
                
                if concepts_df_data:
                    st.dataframe(concepts_df_data, use_container_width=True)
                
                st.subheader("Relationships")
                relationships_df_data = []
                for rel in extraction_result['relationships']:
                    relationships_df_data.append({
                        'Source': rel['source'],
                        'Target': rel['target'],
                        'Type': rel['relationship_type'],
                        'Strength': rel['strength'],
                        'Description': rel['description'][:100] + '...' if len(rel['description']) > 100 else rel['description']
                    })
                
                if relationships_df_data:
                    st.dataframe(relationships_df_data, use_container_width=True)
            
            # Export options
            with st.expander("💾 Export Options"):
                st.subheader("Download Graph Data")
                
                # JSON export
                json_data = json.dumps(graph_data['extraction_result'], indent=2)
                st.download_button(
                    label="📄 Download as JSON",
                    data=json_data,
                    file_name="concept_graph.json",
                    mime="application/json"
                )
                
                # Enhanced Summary export
                ai_summary = extraction_result.get('summary', 'No AI summary available')
                
                # Create comprehensive summary
                doc_info = st.session_state.document_data
                stats = graph_data['export_data']['statistics']
                concepts = extraction_result.get('concepts', [])
                relationships = extraction_result.get('relationships', [])
                sorted_concepts = sorted(concepts, key=lambda x: x.get('importance', 0), reverse=True)
                
                # Create text summary for simple download
                text_summary = f"""CONTEXT GRAPH EXPLORER - DOCUMENT ANALYSIS SUMMARY
================================================================

Document Information:
- Filename: {doc_info.get('filename', 'Unknown')}
- File Type: {doc_info.get('file_type', 'Unknown')}
- Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Graph Statistics:
- Total Concepts: {stats.get('nodes', 0)}
- Total Relationships: {stats.get('edges', 0)}
- Graph Density: {stats.get('density', 0):.3f}
- Connected Components: {'Yes' if stats.get('is_connected', False) else 'No'}

AI-Generated Summary:
{ai_summary}

Key Concepts Identified:
"""
                
                for i, concept in enumerate(sorted_concepts[:10], 1):
                    text_summary += f"{i}. {concept.get('name', 'Unknown')} (Importance: {concept.get('importance', 0)})\n"
                    if concept.get('description'):
                        text_summary += f"   Description: {concept.get('description', '')}\n"
                    text_summary += "\n"
                
                # Add relationship types summary
                relationship_types = {}
                for rel in relationships:
                    rel_type = rel.get('relationship_type', 'unknown')
                    relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
                
                if relationship_types:
                    text_summary += "\nRelationship Types Found:\n"
                    for rel_type, count in sorted(relationship_types.items(), key=lambda x: x[1], reverse=True):
                        text_summary += f"- {rel_type}: {count} relationships\n"
                
                text_summary += f"\n\nGenerated by Context Graph Explorer\nPowered by OpenAI GPT-4o"
                
                # Create HTML report function
                def create_html_report():
                    return generate_comprehensive_html_report(
                        doc_info, stats, ai_summary, sorted_concepts, 
                        relationships, relationship_types, export_data
                    )
                
                # Generate HTML report
                html_report_content = create_html_report()
                
                # Create three columns for download buttons
                col_summary1, col_summary2, col_summary3 = st.columns(3)
                
                with col_summary1:
                    st.download_button(
                        label="📊 HTML Report",
                        data=html_report_content,
                        file_name=f"{doc_info.get('filename', 'document').split('.')[0]}_analysis_report.html",
                        mime="text/html",
                        help="Download interactive HTML report with embedded graph",
                        use_container_width=True
                    )
                
                with col_summary2:
                    st.download_button(
                        label="📝 Text Analysis",
                        data=text_summary,
                        file_name=f"{doc_info.get('filename', 'document').split('.')[0]}_analysis_summary.txt",
                        mime="text/plain",
                        help="Download text-based analysis summary",
                        use_container_width=True
                    )
                
                with col_summary3:
                    st.download_button(
                        label="🤖 AI Summary Only",
                        data=ai_summary,
                        file_name=f"{doc_info.get('filename', 'document').split('.')[0]}_ai_summary.txt",
                        mime="text/plain",
                        help="Download just the AI-generated summary",
                        use_container_width=True
                    )
        
        else:
            st.info("👆 Upload a document and extract concepts to see the graph visualization")
            
            # Show example/demo
            st.subheader("🎯 How it works:")
            st.markdown("""
            1. **Upload** a document (PDF, DOCX, TXT, or Markdown)
            2. **Parse** the document to extract text content
            3. **Extract** key concepts using AI (GPT-4o)
            4. **Visualize** concepts and relationships as an interactive graph
            5. **Explore** the graph to understand document structure
            6. **Export** results for further analysis
            
            **Supported formats:**
            - 📄 PDF documents
            - 📝 Word documents (DOCX)
            - 📋 Text files (TXT)
            - 📖 Markdown files (MD)
            """)

if __name__ == "__main__":
    main()