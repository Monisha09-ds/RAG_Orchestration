import logging
import random
from pyvis.network import Network
import tempfile
import os

logger = logging.getLogger("graph_rag.visualizer")

class GraphVisualizer:
    def __init__(self, graph_driver):
        self.driver = graph_driver

    def create_graph_view(self, limit=50, filters=None):
        """
        Generates an interactive HTML graph with hierarchical layout.
        Fully responsive and dynamically adjusts to viewport size.
        """
        logger.info(f"Generating graph view with limit {limit}")
        
        # Use remote CDN and dynamic viewport height
        net = Network(
            height="85vh", 
            width="100%", 
            bgcolor="#121212", 
            font_color="#e0e0e0", 
            cdn_resources="remote"
        )
        
        # Hierarchical layout options with responsive scaling
        physics_options = """
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "levelSeparation": 150,
              "nodeSpacing": 200,
              "treeSpacing": 200,
              "blockShifting": true,
              "edgeMinimization": true,
              "parentCentralization": true,
              "direction": "UD",
              "sortMethod": "directed"
            }
          },
          "physics": {
            "enabled": false
          },
          "nodes": {
            "font": { "size": 16, "face": "Inter, sans-serif" },
            "shadow": { "enabled": true, "color": "rgba(0,0,0,0.5)" },
            "borderWidth": 2
          },
          "edges": {
            "color": { "inherit": "from", "opacity": 0.3 },
            "smooth": { "enabled": true, "type": "cubicBezier", "roundness": 0.5 },
            "width": 1,
            "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } }
          },
          "groups": {
            "Person": { "color": { "background": "#00d4ff", "border": "#00b8e6" }, "shape": "diamond", "size": 40 },
            "Project": { "color": { "background": "#ff007f", "border": "#e60073" }, "shape": "dot", "size": 30 },
            "Skill": { "color": { "background": "#7cfc00", "border": "#6edb00" }, "shape": "dot", "size": 20 },
            "Organization": { "color": { "background": "#ffd700", "border": "#e6c200" }, "shape": "square", "size": 25 },
            "Tool": { "color": { "background": "#a855f7", "border": "#9333ea" }, "shape": "triangle", "size": 20 },
            "Domain": { "color": { "background": "#f97316", "border": "#ea580c" }, "shape": "hexagon", "size": 22 },
            "Website": { "color": { "background": "#6366f1", "border": "#4f46e5" }, "shape": "star", "size": 25 },
            "Education": { "color": { "background": "#2dd4bf", "border": "#0d9488" }, "shape": "dot", "size": 22 },
            "Experience": { "color": { "background": "#fbbf24", "border": "#d97706" }, "shape": "square", "size": 25 }
          },
          "interaction": {
            "zoomView": true,
            "dragView": true,
            "navigationButtons": true,
            "keyboard": true
          }
        }
        """
        net.set_options(physics_options)
        
        # Level mapping for hierarchical structure
        LEVEL_MAP = {
            "Person": 0,
            "Experience": 1,
            "Education": 1,
            "Website": 1,
            "Organization": 2,
            "Award": 2,
            "Project": 2,
            "Skill": 3,
            "Tool": 3,
            "Domain": 3
        }
        
        query = """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT $limit
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, limit=limit)
                
                for record in result:
                    src = record['n']
                    src_id = src.element_id
                    src_labels = list(src.labels)
                    src_label = src_labels[0] if src_labels else "Unknown"
                    src_title = src.get('name', src.get('id', src_label))
                    src_level = LEVEL_MAP.get(src_label, 1)
                    
                    dst = record['m']
                    dst_id = dst.element_id
                    dst_labels = list(dst.labels)
                    dst_label = dst_labels[0] if dst_labels else "Unknown"
                    dst_title = dst.get('name', dst.get('id', dst_label))
                    dst_level = LEVEL_MAP.get(dst_label, 2)
                    
                    rel = record['r']
                    rel_type = rel.type
                    
                    # Clean up relation label for graph view
                    display_rel_label = "" if rel_type == "MENTIONS" else rel_type
                    
                    # Add nodes with hierarchical levels
                    net.add_node(src_id, label=src_title, title=f"{src_label}: {src_title}", group=src_label, level=src_level)
                    net.add_node(dst_id, label=dst_title, title=f"{dst_label}: {dst_title}", group=dst_label, level=dst_level)
                    net.add_edge(src_id, dst_id, title=rel_type, label=display_rel_label)

            # Generate HTML
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w+') as tmp:
                net.save_graph(tmp.name)
                tmp.seek(0)
                html_content = tmp.read()
                
            # Inject Custom Responsive UI
            custom_ui = """
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
                
                /* Full viewport responsive layout */
                body, html { 
                    margin: 0; 
                    padding: 0; 
                    width: 100vw; 
                    height: 100vh; 
                    overflow: hidden; 
                    background-color: #121212; 
                    font-family: 'Inter', sans-serif; 
                }
                
                #mynetwork { 
                    width: 100%; 
                    height: 85vh; 
                    display: block; 
                    z-index: 1; 
                }
                
                /* Responsive overlay */
                .graph-overlay {
                    position: fixed;
                    top: 1.5rem;
                    left: 1.5rem;
                    z-index: 1000;
                    background: rgba(18, 18, 18, 0.9);
                    backdrop-filter: blur(12px);
                    -webkit-backdrop-filter: blur(12px);
                    color: #ffffff;
                    padding: 1.25rem;
                    border-radius: 16px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.6);
                    border: 1px solid rgba(255,255,255,0.1);
                    min-width: 180px;
                    max-width: 250px;
                    pointer-events: none;
                }
                
                .graph-overlay h4 { 
                    margin: 0 0 0.75rem 0; 
                    font-weight: 600; 
                    color: #00d4ff; 
                    text-transform: uppercase; 
                    letter-spacing: 1.5px; 
                    font-size: 0.85em; 
                    border-bottom: 1px solid rgba(255,255,255,0.1); 
                    padding-bottom: 0.5rem; 
                }
                
                .stat-item { 
                    display: flex; 
                    justify-content: space-between; 
                    margin-bottom: 0.5rem; 
                    font-size: 0.9em; 
                }
                
                .stat-label { color: #888; }
                .stat-value { font-weight: 600; color: #fff; }
                
                /* Responsive node details */
                .node-details {
                    position: fixed;
                    bottom: 1.5rem;
                    right: 1.5rem;
                    background: rgba(24, 24, 24, 0.95);
                    backdrop-filter: blur(16px);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 20px;
                    display: none;
                    width: min(340px, 90vw);
                    max-height: 40vh;
                    overflow-y: auto;
                    box-shadow: 0 16px 64px rgba(0,0,0,0.8);
                    border: 1px solid rgba(255,255,255,0.15);
                    z-index: 1001;
                    animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                @keyframes slideUp { 
                    from { transform: translateY(20px); opacity: 0; } 
                    to { transform: translateY(0); opacity: 1; } 
                }
                
                .node-details h3 { 
                    margin: 0 0 0.5rem 0; 
                    color: #00d4ff; 
                    font-weight: 600; 
                    font-size: 1.3em; 
                }
                
                .node-badge { 
                    display: inline-block; 
                    padding: 4px 10px; 
                    border-radius: 20px; 
                    font-size: 0.7em; 
                    font-weight: 700; 
                    margin-bottom: 1rem; 
                    letter-spacing: 0.8px; 
                    text-transform: uppercase; 
                    color: #000; 
                }
                
                .nd-info-box { 
                    background: rgba(255,255,255,0.06); 
                    padding: 1rem; 
                    border-radius: 12px; 
                    font-size: 0.95em; 
                    line-height: 1.6; 
                    color: #d1d1d1; 
                }
                
                .graph-hint { 
                    margin-top: 1rem; 
                    font-size: 0.75em; 
                    color: #555; 
                    display: flex; 
                    align-items: center; 
                    gap: 0.5rem; 
                }
                
                .hint-dot { 
                    width: 6px; 
                    height: 6px; 
                    border-radius: 50%; 
                    background: #00d4ff; 
                }
                
                /* Mobile responsive adjustments */
                @media (max-width: 768px) {
                    .graph-overlay {
                        top: 1rem;
                        left: 1rem;
                        padding: 1rem;
                        min-width: 150px;
                    }
                    
                    .node-details {
                        bottom: 1rem;
                        right: 1rem;
                        padding: 1rem;
                        max-height: 50vh;
                    }
                    
                    #mynetwork {
                        height: 90vh;
                    }
                }
            </style>
            
            <div class="graph-overlay">
                <h4>Hierarchical Portfolio</h4>
                <div class="stat-item"><span class="stat-label">Nodes</span> <span class="stat-value">{NODE_COUNT}</span></div>
                <div class="stat-item"><span class="stat-label">Connections</span> <span class="stat-value">{EDGE_COUNT}</span></div>
                <div class="graph-hint">
                    <div class="hint-dot"></div>
                    <i>Responsive View</i>
                </div>
            </div>
            
            <div id="node-details" class="node-details">
                <div id="nd-badge" class="node-badge"></div>
                <h3 id="nd-title"></h3>
                <div id="nd-info" class="nd-info-box"></div>
            </div>

            <script type="text/javascript">
                var checkNet = setInterval(function() {
                    if (typeof network !== 'undefined' && typeof nodes !== 'undefined') {
                        clearInterval(checkNet);
                        
                        network.on("click", function (params) {
                            if (params.nodes.length > 0) {
                                var nodeId = params.nodes[0];
                                var node = nodes.get(nodeId);
                                
                                var badge = document.getElementById('nd-badge');
                                badge.innerText = node.group;
                                var colors = {
                                    'Person': '#00d4ff',
                                    'Project': '#ff007f',
                                    'Skill': '#7cfc00',
                                    'Organization': '#ffd700',
                                    'Tool': '#a855f7',
                                    'Domain': '#f97316',
                                    'Website': '#6366f1',
                                    'Education': '#2dd4bf',
                                    'Experience': '#fbbf24'
                                };
                                badge.style.backgroundColor = colors[node.group] || '#444';
                                
                                document.getElementById('nd-title').innerText = node.label;
                                
                                var rawInfo = (node.title || "").replace(node.group + ": ", "");
                                var formattedInfo = rawInfo.split('\\n').join('<br>');
                                document.getElementById('nd-info').innerHTML = formattedInfo || "No additional details available.";
                                
                                var details = document.getElementById('node-details');
                                details.style.display = 'block';
                            } else {
                                document.getElementById('node-details').style.display = 'none';
                            }
                        });
                        
                        // Auto-fit with responsive scaling
                        setTimeout(function() { 
                            network.fit({ 
                                animation: { duration: 500, easingFunction: 'easeInOutQuad' } 
                            }); 
                        }, 500);
                        
                        // Re-fit on window resize
                        window.addEventListener('resize', function() {
                            network.fit();
                        });
                    }
                }, 100);
            </script>
            """
            
            final_ui = custom_ui.replace("{NODE_COUNT}", str(len(net.nodes))).replace("{EDGE_COUNT}", str(len(net.edges)))
            html_content = html_content.replace("</body>", f"{final_ui}</body>")
                
            return html_content

        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            return f"<div style='color: white; padding: 20px;'>Error generating graph view: {str(e)}</div>"

    def highlight_query_path(self, cypher_query):
        pass
