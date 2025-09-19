"""
Context Graph Explorer - Main Streamlit Application
Upload documents and visualize concept relationships as interactive graphs
"""

import streamlit as st
import json
import tempfile
import os
from typing import Dict, Any, Optional

# Import our custom modules
from parsing_utils import DocumentParser, validate_file_upload
from graph_utils import ConceptExtractor, GraphBuilder
from pyvis.network import Network
import networkx as nx

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
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # OpenAI API Key
        api_key = st.text_input(
            "OpenAI API Key:",
            type="password",
            value=st.session_state.api_key,
            help="Enter your OpenAI API key to enable AI-powered concept extraction"
        )
        
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
            
            # Create and display the graph
            try:
                net = Network(
                    height="600px",
                    width="100%",
                    bgcolor="#ffffff",
                    font_color="black",
                    directed=True
                )
                
                # Configure physics
                if physics_enabled:
                    net.set_options("""
                    var options = {
                      "physics": {
                        "enabled": true,
                        "stabilization": {"iterations": 100},
                        "barnesHut": {"gravitationalConstant": -8000, "springConstant": 0.001}
                      }
                    }
                    """)
                else:
                    net.set_options("""
                    var options = {
                      "physics": {"enabled": false}
                    }
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
                    
                    net.add_node(
                        node['id'],
                        label=node['label'],
                        title=f"{node['title']}\nType: {node['type']}\nImportance: {node['importance']}",
                        size=int(node['size'] * node_size_factor),
                        color=color
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
                    
                    st.components.v1.html(html_content, height=600)
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
                
                # Summary export
                summary = extraction_result.get('summary', 'No summary available')
                st.download_button(
                    label="📝 Download Summary",
                    data=summary,
                    file_name="document_summary.txt",
                    mime="text/plain"
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