# Topic-Based Document Splitting

## 🎯 What This Does

Instead of creating ONE big markdown file per PDF, this feature:
- ✅ **Analyzes** your PDF using AI to detect distinct topics
- ✅ **Splits** the document into separate markdown files (one per topic)
- ✅ **Creates semantic backlinks** between related topic files
- ✅ **Builds a knowledge network** like Obsidian/Zettelkasten

## 🌟 Perfect For

- **Research papers** → Split into: Introduction, Methods, Results, Discussion
- **Annual reports** → Split into: Financial Performance, Market Trends, Outlook, Team
- **Technical documentation** → Split into: Setup, Configuration, Troubleshooting, API Reference
- **Books/Manuals** → Split into chapters or sections with cross-references

## 📊 Example Output

### Input:
```
annual_report_2024.pdf (50 pages)
```

### Output:
```
data/topics/
├── executive_summary.md        ← Links to: financial_performance, future_outlook
├── financial_performance.md    ← Links to: market_trends, executive_summary
├── market_trends.md            ← Links to: financial_performance, future_outlook
├── team_overview.md            ← Links to: executive_summary
├── future_outlook.md           ← Links to: market_trends, financial_performance
└── annual_report_2024_index.md ← Overview of all topics
```

### What Each File Looks Like:

**financial_performance.md:**
```markdown
---
topic: financial_performance
description: Q4 revenue and profit analysis
keywords: revenue, profit, growth, performance
source: annual_report_2024.pdf
---

# Q4 Revenue and Profit Analysis

[Content about financial performance...]

---

## Related Topics

- [[market_trends]] (similarity: 85%)
- [[executive_summary]] (similarity: 72%)
- [[future_outlook]] (similarity: 68%)

---

*This is part of the [[annual_report_2024]] document network*
```

## 🚀 How To Use

### Method 1: Command Line

```bash
# Basic usage
python3 split_by_topics.py document.pdf

# Custom output directory
python3 split_by_topics.py document.pdf -o my_topics/

# Control number of topics
python3 split_by_topics.py document.pdf --min-topics 5 --max-topics 15

# Example with all options
python3 split_by_topics.py annual_report.pdf \
    -o topics/2024_report \
    --min-topics 4 \
    --max-topics 8
```

### Method 2: Python API

```python
from core.topic_splitter import TopicSplitter
from markitdown import MarkItDown
from pathlib import Path
import os

# Load Azure credentials
from dotenv import load_dotenv
load_dotenv()

azure_endpoint = os.getenv("AZURE_ENDPOINT")
azure_api_key = os.getenv("AZURE_API_KEY")

# Initialize
markitdown = MarkItDown()
splitter = TopicSplitter(azure_endpoint, azure_api_key)

# Convert PDF
result = markitdown.convert("document.pdf")
markdown = result.text_content

# Split by topics
files = splitter.split_by_topics(
    markdown,
    "document.pdf",
    Path("output/topics"),
    min_topics=3,
    max_topics=10
)

print(f"Created {len(files)} topic files!")
```

## 🎨 How It Works

### Step 1: Topic Detection
Uses Azure AI (GPT-4) to analyze the document and identify distinct topics:

```
Document Analysis
      ↓
AI identifies 5 main topics:
  1. Executive Summary
  2. Financial Performance  
  3. Market Trends
  4. Team Overview
  5. Future Outlook
```

### Step 2: Content Segmentation
Splits the document based on detected topics:

```
Full Document (50 pages)
      ↓
Segment 1: Executive Summary (lines 1-150)
Segment 2: Financial Performance (lines 151-300)
Segment 3: Market Trends (lines 301-450)
...
```

### Step 3: Semantic Link Generation
Calculates similarity between topics using embeddings:

```
Financial Performance ←→ Market Trends (85% similar)
Financial Performance ←→ Future Outlook (72% similar)
Executive Summary ←→ Financial Performance (68% similar)
```

### Step 4: Create Interconnected Files
Each topic becomes a separate markdown file with:
- ✅ Topic metadata
- ✅ Original content
- ✅ Wiki-style links to related topics
- ✅ Similarity scores

## 🔍 Topic Detection Methods

### Primary: AI-Based (Semantic)
- Uses GPT-4 to understand document themes
- Groups related content together semantically
- Works even if document structure is poor
- **Best for:** Complex documents, research papers

### Fallback: Structure-Based (Headers)
- Uses document headers (H1, H2) as topics
- Faster but less intelligent
- Requires good document structure
- **Best for:** Well-structured documents

## 💡 Use Cases

### 1. Knowledge Base Creation
```bash
# Convert company docs into interconnected knowledge base
python3 split_by_topics.py employee_handbook.pdf -o kb/handbook/
python3 split_by_topics.py policies.pdf -o kb/policies/
python3 split_by_topics.py procedures.pdf -o kb/procedures/
```

### 2. Research Paper Analysis
```bash
# Split paper into sections with cross-references
python3 split_by_topics.py research_paper.pdf -o papers/2024_study/
# Creates: introduction.md, methodology.md, results.md, discussion.md
```

### 3. Book/Manual to Zettelkasten
```bash
# Convert book into interconnected notes
python3 split_by_topics.py programming_book.pdf \
    -o zettelkasten/programming/ \
    --min-topics 10 \
    --max-topics 20
```

### 4. Report Decomposition
```bash
# Break down annual report for easier analysis
python3 split_by_topics.py annual_report.pdf -o reports/2024/
# Navigate between: financials.md, market_analysis.md, outlook.md
```

## 🔗 Using With Obsidian

The output is **100% compatible** with Obsidian!

### Setup:
1. Process your PDF:
   ```bash
   python3 split_by_topics.py document.pdf -o ~/Obsidian/MyVault/Documents/
   ```

2. Open in Obsidian:
   - Files appear in your vault immediately
   - `[[wiki-links]]` work automatically
   - Graph view shows topic connections
   - Backlinks panel shows related topics

3. Navigate:
   - Start with `*_index.md` for overview
   - Click any `[[topic_name]]` to jump to that topic
   - View graph to see topic network
   - Use backlinks to explore relationships

## ⚙️ Configuration

### Number of Topics

```bash
# Fewer topics (broader categories)
--min-topics 2 --max-topics 5

# More topics (detailed splitting)  
--min-topics 10 --max-topics 20

# Let AI decide optimal number
# (default: 3-10 topics)
```

### Similarity Threshold

In the Python API, you can adjust link sensitivity:

```python
# More links (lower threshold)
splitter.generate_semantic_links(topics, contents, similarity_threshold=0.2)

# Fewer links (higher threshold)
splitter.generate_semantic_links(topics, contents, similarity_threshold=0.5)

# Default: 0.3 (balanced)
```

## 📊 Comparison

### Single File Mode (Current Default)
```
document.pdf → document.md (1 file, all content)
```
✅ Simple, easy to read  
❌ Large files, hard to navigate  
❌ No semantic organization  

### Topic Split Mode (New Feature)
```
document.pdf → topic1.md, topic2.md, topic3.md... (multiple files)
              Each with semantic backlinks!
```
✅ Organized by topic  
✅ Semantic connections  
✅ Easy navigation  
✅ Perfect for knowledge management  
❌ Requires Azure AI  

## 🎯 Requirements

- ✅ Azure OpenAI configured (`./configure_azure.sh`)
- ✅ Python packages installed
- ✅ GPT-4 deployment (for best results)

## 💻 Sample Session

```bash
$ python3 split_by_topics.py whitepaper.pdf

======================================================================
PDF TO TOPIC-BASED MARKDOWN CONVERTER
======================================================================

✓ Azure AI configured
  Input: whitepaper.pdf
  Output: data/topics
  Target topics: 3-10

Initializing...

Step 1: Converting PDF to Markdown...
✓ Converted (42,158 characters)

Step 2: Analyzing and splitting by topics...
======================================================================
Starting topic-based document splitting
======================================================================
Detecting topics in document (target: 3-10 topics)...
✓ Detected 6 topics
  - introduction: Overview and background
  - technical_architecture: System design and components
  - implementation: Deployment and configuration
  - performance_analysis: Benchmark results and optimization
  - security_considerations: Security model and best practices
  - future_work: Roadmap and planned enhancements

Extracting content for each topic...
  - introduction: 3,842 characters
  - technical_architecture: 8,127 characters
  - implementation: 6,534 characters
  - performance_analysis: 9,211 characters
  - security_considerations: 7,443 characters
  - future_work: 4,201 characters

Generating semantic links between topics...
  - introduction: 3 related topics
  - technical_architecture: 4 related topics
  - implementation: 4 related topics
  - performance_analysis: 3 related topics
  - security_considerations: 4 related topics
  - future_work: 3 related topics

Creating topic markdown files...
  ✓ Created: introduction.md
  ✓ Created: technical_architecture.md
  ✓ Created: implementation.md
  ✓ Created: performance_analysis.md
  ✓ Created: security_considerations.md
  ✓ Created: future_work.md

Creating index file...
======================================================================
✓ Document split complete: 7 files created
======================================================================

COMPLETE!
Created 7 files:
  - introduction.md (4,532 bytes)
  - technical_architecture.md (9,847 bytes)
  - implementation.md (7,891 bytes)
  - performance_analysis.md (10,543 bytes)
  - security_considerations.md (8,765 bytes)
  - future_work.md (5,234 bytes)
  - whitepaper_index.md (2,104 bytes)

All files saved to: data/topics

You can now:
  1. Open the files in Obsidian or any markdown editor
  2. Use [[wiki-links]] to navigate between topics  
  3. Start with the *_index.md file for an overview
```

## 🎉 Summary

**You asked:** Can I get one MD file per topic with semantic backlinks?

**Answer:** YES! Use the new `split_by_topics.py` script!

```bash
# Convert your PDF into a topic-based knowledge network
python3 split_by_topics.py your_document.pdf
```

This creates an interconnected web of topic files, perfect for Obsidian, Zettelkasten, or any knowledge management system!
