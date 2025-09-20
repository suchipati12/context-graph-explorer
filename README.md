---
title: Context Graph Explorer
emoji: 🔍
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: false
license: mit
---

# 🔍 Context Graph Explorer

An AI-powered tool that transforms documents into interactive concept graphs, helping you visualize and understand complex relationships within your content.

## 🎯 Features

- **📄 Multi-format Support**: Upload PDF, DOCX, TXT, or Markdown files
- **🧠 AI-Powered Analysis**: Uses OpenAI GPT-4o for intelligent concept extraction
- **🌐 Interactive Visualization**: Explore concepts through dynamic network graphs
- **🔗 Relationship Mapping**: Discover connections and dependencies between ideas
- **📊 Graph Analytics**: Get insights with statistics and centrality measures
- **💾 Export Options**: Download results as JSON or text summaries

## 🚀 How to Use

1. **Enter your OpenAI API Key** in the sidebar (required for AI analysis)
2. **Upload a document** (PDF, DOCX, TXT, or MD format)
3. **Parse the document** to extract text content
4. **Extract concepts** using AI-powered analysis
5. **Explore the interactive graph** with physics simulation
6. **Export your results** for further analysis

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI**: OpenAI GPT-4o
- **Graph Processing**: NetworkX
- **Visualization**: Pyvis
- **Document Parsing**: pypdf, python-docx

## 📋 Requirements

- OpenAI API key for concept extraction
- Supported file formats: PDF, DOCX, TXT, MD
- Maximum file size: 10MB

## 🎮 Try It Out

Upload the included `sample_document.md` to see the Context Graph Explorer in action!

## 📖 Example Use Cases

- **Research**: Analyze academic papers and research documents
- **Business**: Understand complex reports and documentation
- **Education**: Visualize learning materials and textbooks
- **Content Analysis**: Break down articles and blog posts

---

*Built with ❤️ using Streamlit and OpenAI*