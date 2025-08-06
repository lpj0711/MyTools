from py2neo import Graph
import pydot
import re
from common import neo4j_local_ip, neo4j_username, neo4j_password

# 连接Neo4j
graph = Graph(neo4j_local_ip, auth=(neo4j_username, neo4j_password))
'''
    解析AST代码，把结构转换成neo4j的cypher命令，存储到知识图谱
'''

node_ids = set()
node_id_names = {}


def clean_chapter_number(text):
    text = text.replace('"', '')
    return re.sub(r'[0-9一二三四五六七八九十.]+ s*', '', text)


def get_command_by_node(graphs, cypher_commands):
    nodes_in_graph = graphs.get_nodes()
    for graph in nodes_in_graph:
        # 节点的名称是其唯一标识符
        node_id = graph.get_name()
        # 节点的标签通常是其显示文本
        node_label = graph.get_label()
        if node_label is not None:
            # 解析复合标签结构
            main_node, *sub_nodes = re.split(r'[\|{}]', node_label)
            sub_nodes = [s.strip() for s in sub_nodes if len(s.strip()) >= 2]
            main_node = main_node.strip()
            node_name = create_neo4j_node(main_node, sub_nodes, cypher_commands)
            node_id_names[node_id] = node_name
            node_ids.add(node_name)
    all_edges = graphs.get_edges()
    for i, edge in enumerate(all_edges):
        parent_id = edge.get_source()
        destination = edge.get_destination()
        if type(destination) != str:
            child_ids = list(destination["nodes"].keys())
        else:
            continue
        if parent_id in node_id_names:
            parent_name = node_id_names[parent_id]
        else:
            print(parent_id)
            continue
        child_names = []
        for child_id in child_ids:
            child_name = node_id_names[child_id]
            child_names.append(child_name)
        if len(child_names) > 0:
            create_neo4j_node(parent_name, child_names, cypher_commands)


def create_neo4j_node(main_node, sub_nodes, cypher_commands):
    # 创建主节点
    node_name = clean_chapter_number(main_node)
    if node_name not in node_ids:
        node_ids.add(node_name)
        cypher_commands.append({
            'statement': "CREATE (:Entity {name: $name, type: $type})",
            'parameters': {'name': node_name, 'type': 'ChapterSection'}
        })
    print(main_node, sub_nodes)
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
    return node_name


def dot_to_cypher(dot_data):
    """
    DOT转Cypher核心逻辑
    """
    (graphs,) = pydot.graph_from_dot_data(dot_data)
    cypher_commands = []

    # 递归处理所有子图和主图节点
    get_command_by_node(graphs, cypher_commands)
    # 生成关系CYPHER
    # 递归处理所有子图和主图边

    for node in graphs.get_subgraphs():
        get_command_by_node(node, cypher_commands)
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
    print(node_id_names)
    import_kg_to_neo4j(cypher)


dot_file = "./AST_windows_deepseek_1.5.dot"
create_kg_from_dot(dot_file)
