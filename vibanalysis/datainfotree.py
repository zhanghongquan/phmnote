'''
整个数据集的规划如下，
首先是整个数据集规划为一棵树，如下图

ROOT
 |--XJTU
      |--collection1
           |---bearing1_1
                |---data_node
'''

from .utils import InvalidParameter
from .db import Database, DATA_CATEGORY_BEARING, DATA_CATEGORY_FOLDER, DATA_CATEGORY_GEAR


class TreeNode:
    def __init__(self, tree, db_node) -> None:
        self.tree = tree
        self.db_node = db_node
        self.id2child = {}
        self.name2children = {}
        self._fullpath = None
    
    @property
    def name(self):
        return self.db_node.name
    
    @property
    def category(self):
        return self.db_node.category
    
    @property
    def id(self):
        return self.db_node.id
    
    @property
    def is_root(self):
        return self.db_node.parent == 0
    
    @property
    def is_folder(self):
        return self.db_node.category == DATA_CATEGORY_FOLDER
    
    @property
    def is_bearing(self):
        return self.db_node.category == DATA_CATEGORY_BEARING
    
    @property
    def is_gear(self):
        return self.db_node.category == DATA_CATEGORY_GEAR
    
    @property
    def parent(self):
        assert not self.is_root
        return self.tree._find_node(self.db_node.parent_id)
    
    def child(self, name):
        assert name in self.name2children
        return self.name2children[name]
    
    @property
    def fullpath(self):
        if self._fullpath is not None:
            return self._fullpath
        names = []
        node = self
        while True:
            names.insert(0, node.name)
            if node.is_root:
                break
            node = node.parent
        names = names[::-1]
        self._fullpath = "/".join(names)
        return self._fullpath

    def add_child(self, node):
        if node.id in self.id2child:
            raise InvalidParameter(f"node[{node.id}] already exist under[{self.fullpath}]")
        if node.name in self.name2child:
            raise InvalidParameter(f"node[{node.name}] already exist under[{self.fullpath}]")
        self.id2child[node.id] = node
        self.name2children[node.name] = node


class DataInfoTree(Database):
    def __init__(self, db_url=None) -> None:
        super().__init__(db_url=db_url)
        self.root_node = None
        self.id2node = {}
        self.current_node = None

    @property
    def root(self):
        return self.root_node
    
    def _register_treenode(self, node):
        if node.id in self.id2node:
            raise InvalidParameter(f"node[{node.id}] already exist")
        self.id2node[node.id] = node
    
    def _find_node(self, id):
        if id not in self.id2node:
            raise InvalidParameter(f"node[{id}] not exist")
        return self.id2node[id]
    
    def _build_tree(self, db_nodes):
        for db_node in db_nodes:
            node = TreeNode(db_node=db_node)
            self._register_treenode(node)
            if not node.is_root:
                parent_node = self._find_node(db_node.parent_id)
                parent_node.add_child(node)
            else:
                if self.root_node is not None:
                    raise InvalidParameter("more than 1 root node found")
                self.root_node = node
        if len(db_nodes) != len(self.id2node):
            raise InvalidParameter(f"tree node data error, orphan node found")
    
    def cd(self, name):
        if name is None or not isinstance(name, str):
            raise InvalidParameter(f"can only change directory by pass in string")
        from_root = name.startswith("/")
        folder_names =  name.split("/")
        folders = []
        for folder_name in folder_names:
            if len(folder_name) != 0:
                folders.append(folder_name)
        node = self.root_node if from_root else self.current_node
        for name in folders:
            if not node:
                raise InvalidParameter(f"invalid path [{name}]")
            node = node.child(name)
        self.current_node = node
        return node
    
    def mkdir(self, name, category, description=None):
        db_node = self.make_treenode(self.current_node, name, category, description)
        info_node = TreeNode(db_node)
        self._register_treenode(info_node)
        if not self.root_node:
            self.root_node = info_node
        else:
            self.current_node.add_child(info_node)
