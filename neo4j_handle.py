from py2neo import Graph
import pydot
import re

# 连接Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "lpj123456"))
'''
    解析AST代码，把结构转换成neo4j的cypher命令，存储到知识图谱
'''


def clean_chapter_number(text):
    return re.sub(r'[0-9一二三四五六七八九十.]+ s*', '', text)


def get_command_by_node(graphs, cypher_commands, node_ids):
    for graph in graphs:
        for node in graph.get_nodes():
            print('-----', node)
            # 解析复合标签结构
            label_content = node.get_attributes().get('label', '')
            main_node, *sub_nodes = re.split(r'[\|{}]', label_content)
            sub_nodes = [s.strip() for s in sub_nodes if len(s.strip()) >= 2]
            main_node = main_node.strip()

            # 创建主节点
            node_name = clean_chapter_number(main_node)
            if node_name not in node_ids:
                node_ids.add(node_name)
                cypher_commands.append({
                    'statement': "CREATE (:Entity {name: $name, type: $type})",
                    'parameters': {'name': node_name, 'type': 'ChapterSection'}
                })

            # 创建子节点及关系
            for sub_node in filter(None, [s.strip() for s in sub_nodes]):
                sub_name = clean_chapter_number(sub_node)
                if sub_name not in node_ids:
                    node_ids.add(sub_name)
                    cypher_commands.append({
                        'statement': "CREATE (:Entity {name: $name, type: $type})",
                        'parameters': {'name': sub_name, 'type': 'Feature'}
                    })
                cypher_commands.append({
                    'statement': "MATCH (a:Entity {name: $parent}), (b:Entity {name: $child}) CREATE (a)-[:HAS_FEATURE]->(b)",
                    'parameters': {'parent': node_name, 'child': sub_name}
                })


def dot_to_cypher(dot_data):
    """
    DOT转Cypher核心逻辑
    """
    graphs = pydot.graph_from_dot_data(dot_data)
    cypher_commands = []

    # 生成节点CYPHER
    node_ids = set()
    # 递归处理所有子图和主图节点
    get_command_by_node(graphs, cypher_commands, node_ids)
    # 生成关系CYPHER
    # 递归处理所有子图和主图边
    for node in graph.get_subgraphs():
        get_command_by_node([node], cypher_commands, node_ids)
        for edge in node.get_edges():
            print(edge)
            rel_label = edge.get_label() or 'Related_to'
            rel_type = re.sub(r'[^a-zA-Z0-9_]', '', rel_label.upper().replace(' ', '_').replace('-', '_')) or 'RELATED'
            cypher_commands.append({
                'statement': "MATCH (a:Entity {name: $src}), (b:Entity {name: $dst}) CREATE (a)-[:%s]->(b)" % rel_type,
                'parameters': {'src': clean_chapter_number(edge.get_source()),
                               'dst': clean_chapter_number(edge.get_destination())}
            })
    return cypher_commands


def import_kg_to_neo4j(cypher_commands):
    """
    批量执行Cypher语句
    """
    try:
        tx = graph.begin()
        for cmd in cypher_commands:
            tx.run(cmd['statement'], parameters=cmd['parameters'])
        tx.commit()
    except Exception as e:
        tx.rollback()
        print(f'导入失败: {str(e)}')


def create_kg_from_dot(dot_file):
    with open(dot_file, 'r', encoding='utf-8') as f:
        dot_data = f.read()
    cypher = dot_to_cypher(dot_data)
    import_kg_to_neo4j(cypher)


dot_file = "./AST_windows_deepseek_all.dot"
create_kg_from_dot(dot_file)
