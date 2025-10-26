"""
Simple web viewer for ChromaDB templates
Access at: http://localhost:8000/chromadb-viewer/
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from apps.ai_engine.rag.chroma_manager import ChromaManager
from apps.ai_engine.rag.retriever import RAGRetriever
import json


@require_http_methods(["GET"])
def chroma_stats(request):
    """Get ChromaDB statistics"""
    chroma = ChromaManager()

    stats = {
        'total_templates': chroma.count_templates(),
        'collection_name': chroma.collection_name,
        'persist_directory': str(chroma.collection._client.get_settings().persist_directory) if hasattr(chroma.collection._client, 'get_settings') else 'N/A'
    }

    return JsonResponse(stats)


@require_http_methods(["GET"])
def list_templates(request):
    """List all templates"""
    chroma = ChromaManager()
    templates = chroma.list_all_templates()

    return JsonResponse({
        'count': len(templates),
        'templates': templates
    })


@require_http_methods(["GET"])
def get_template(request, template_id):
    """Get specific template with full code"""
    chroma = ChromaManager()
    template = chroma.get_template_by_id(template_id)

    if template:
        return JsonResponse({
            'success': True,
            'template': template
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Template not found'
        }, status=404)


@require_http_methods(["GET"])
def search_templates(request):
    """Search templates by query"""
    query = request.GET.get('q', '')
    n_results = int(request.GET.get('limit', 5))

    if not query:
        return JsonResponse({
            'success': False,
            'error': 'Query parameter "q" is required'
        }, status=400)

    retriever = RAGRetriever()
    results = retriever.retrieve_relevant_templates(query, n_results=n_results)

    # Add similarity percentage
    for r in results:
        if 'distance' in r and r['distance'] is not None:
            r['similarity_percent'] = round((1 - r['distance']) * 100, 2)

    return JsonResponse({
        'success': True,
        'query': query,
        'count': len(results),
        'results': results
    })


@require_http_methods(["GET"])
def viewer_html(request):
    """Simple HTML viewer for ChromaDB"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ChromaDB Viewer</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .stat-value {
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
            }
            .search-box {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            input[type="text"] {
                width: 70%;
                padding: 12px;
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            button {
                padding: 12px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-left: 10px;
            }
            button:hover {
                background: #5568d3;
            }
            .templates-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
            }
            .template-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .template-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .template-title {
                font-size: 20px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
            .template-type {
                display: inline-block;
                padding: 5px 15px;
                background: #667eea;
                color: white;
                border-radius: 20px;
                font-size: 12px;
                margin-bottom: 10px;
            }
            .template-tags {
                color: #666;
                font-size: 14px;
                margin: 10px 0;
            }
            .template-code-size {
                color: #999;
                font-size: 12px;
            }
            .similarity {
                background: #10b981;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            .code-preview {
                background: #f8f8f8;
                padding: 15px;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                overflow-x: auto;
                margin-top: 10px;
                max-height: 200px;
                overflow-y: auto;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
                font-size: 18px;
            }
            .view-code-btn {
                background: #10b981;
                padding: 8px 20px;
                margin-top: 10px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🗄️ ChromaDB Template Viewer</h1>
            <p>View and search PixiJS game templates stored in ChromaDB</p>
        </div>

        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-value" id="totalTemplates">-</div>
                <div>Total Templates</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="collectionName">-</div>
                <div>Collection Name</div>
            </div>
        </div>

        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search templates (e.g., 'quiz about math', 'platformer game', 'puzzle')">
            <button onclick="searchTemplates()">🔍 Search</button>
            <button onclick="loadAllTemplates()">📋 Show All</button>
        </div>

        <div id="results" class="loading">Loading templates...</div>

        <script>
            async function loadStats() {
                try {
                    const response = await fetch('/chromadb-viewer/stats/');
                    const data = await response.json();
                    document.getElementById('totalTemplates').textContent = data.total_templates;
                    document.getElementById('collectionName').textContent = data.collection_name;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            async function loadAllTemplates() {
                document.getElementById('results').innerHTML = '<div class="loading">Loading templates...</div>';
                try {
                    const response = await fetch('/chromadb-viewer/templates/');
                    const data = await response.json();
                    displayTemplates(data.templates);
                } catch (error) {
                    document.getElementById('results').innerHTML = '<div class="loading">Error loading templates</div>';
                }
            }

            async function searchTemplates() {
                const query = document.getElementById('searchInput').value;
                if (!query) {
                    loadAllTemplates();
                    return;
                }

                document.getElementById('results').innerHTML = '<div class="loading">Searching...</div>';
                try {
                    const response = await fetch(`/chromadb-viewer/search/?q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    if (data.success) {
                        displayTemplates(data.results, true);
                    }
                } catch (error) {
                    document.getElementById('results').innerHTML = '<div class="loading">Error searching</div>';
                }
            }

            async function viewCode(templateId) {
                try {
                    const response = await fetch(`/chromadb-viewer/template/${templateId}/`);
                    const data = await response.json();
                    if (data.success) {
                        const codeDiv = document.getElementById(`code-${templateId}`);
                        if (codeDiv.style.display === 'none') {
                            codeDiv.innerHTML = `<div class="code-preview">${escapeHtml(data.template.code)}</div>`;
                            codeDiv.style.display = 'block';
                        } else {
                            codeDiv.style.display = 'none';
                        }
                    }
                } catch (error) {
                    console.error('Error loading code:', error);
                }
            }

            function displayTemplates(templates, showSimilarity = false) {
                if (templates.length === 0) {
                    document.getElementById('results').innerHTML = '<div class="loading">No templates found</div>';
                    return;
                }

                const html = templates.map(t => `
                    <div class="template-card">
                        <div class="template-title">${t.name}</div>
                        <span class="template-type">${t.game_type}</span>
                        ${showSimilarity && t.similarity_percent ? `<span class="similarity">${t.similarity_percent}% match</span>` : ''}
                        <div class="template-tags">🏷️ ${t.tags.join(', ')}</div>
                        <div class="template-code-size">📝 ${t.code_length || 'N/A'} characters</div>
                        <div style="margin-top: 10px;">
                            <strong>ID:</strong> <code>${t.id}</code>
                        </div>
                        <button class="view-code-btn" onclick="viewCode('${t.id}')">👁️ View Code</button>
                        <div id="code-${t.id}" style="display: none;"></div>
                    </div>
                `).join('');

                document.getElementById('results').innerHTML = `<div class="templates-grid">${html}</div>`;
            }

            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            // Search on Enter key
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchTemplates();
                }
            });

            // Load initial data
            loadStats();
            loadAllTemplates();
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)
