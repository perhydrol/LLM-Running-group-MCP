# DND Map MCP 实施计划

## 目标
创建一个 MCP 服务器，提供 DND 战役的地图导航和地点信息查询功能。

## 功能
1.  **获取地点列表 (list_locations)**: 获取所有主要地点的名称和地点特点摘要。
2.  **获取地点详情 (get_location_info)**: 输入地点名称，获取地点的详细信息（Markdown 格式）。
3.  **路径规划 (get_shortest_path)**: 输入出发点和目标点，返回距离最短的路线。

## 架构

### 目录结构
```
dnd_map_mcp/
├── map_data/               # 存储 Markdown 文件的文件夹
│   └── 城市名称/
│       └── graph.json              # 图结构的持久化存储
│       └── 地点名称/
│           └── info.md     # 详细信息文件
├── server.py               # MCP 服务器主入口
├── graph_manager.py        # 图结构管理逻辑
└── requirements.txt        # 依赖文件
```

### 数据结构

#### 1. 图结构持久化 (`graph.json`)
存储地点的连接关系和基本元数据。
```json
{
  "nodes": [
    {
      "id": "loc_1",
      "name": "跃马旅店",
      "city": "布理",
      "summary": "一家著名的旅店。",
      "type": "旅店"
    }
  ],
  "edges": [
    {
      "source": "loc_1",
      "target": "loc_2",
      "weight": 10  // 距离
    }
  ]
}
```

#### 2. 地点详情 (`map_data/`)
层级结构：`城市名称` -> `地点名称` -> `info.md`。
`info.md` 文件包含详细描述、NPC、秘密等信息。

### 工具定义

#### 1. `list_locations`
-   **描述**: 获取指定城市所有主要地点的列表。
-   **输入**: `city_name` (城市名称)。
-   **输出**: 包含地点名称、摘要的列表。

#### 2. `get_location_info`
-   **描述**: 获取特定地点的详细信息。
-   **输入**: `city_name` (城市名称), `location_name` (地点名称)。
-   **输出**: 对应 Markdown 文件的内容。如果地点存在别名或模糊匹配，应尝试智能解析。

#### 3. `get_shortest_path`
-   **描述**: 计算两个地点之间的最短路径。
-   **输入**: `city_name` (城市名称), `start_location` (出发点名称), `target_location` (目标点名称)。
-   **输出**: 路径上的地点列表及总距离。

## 实施步骤

1.  **环境设置**:
    -   创建 `requirements.txt`，包含 `mcp`, `networkx` (用于图算法)。
    -   初始化 `graph.json` 和 `map_data` 目录。

2.  **核心逻辑实现**:
    -   **GraphManager**: 负责根据城市名称加载 `graph.json`，构建 `networkx` 图对象，并实现最短路径算法。
    -   **DataManager**: 负责根据地点名称查找并读取 `map_data` 中的 Markdown 文件。

3.  **MCP 服务器实现**:
    -   使用 `mcp.server.fastmcp` 暴露上述三个工具。
    -   集成 `GraphManager` 和 `DataManager`。

4.  **测试与验证**:
    -   验证路径规划算法的准确性。
    -   验证文件读取功能的鲁棒性（处理文件不存在的情况）。

## 依赖库
-   `mcp`
-   `networkx`
