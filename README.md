# SuolinZhang-Maya-tools
A custom Maya toolkit for evaluating applicant's proficiency in computer technology by faculty at the targeted master's degree program.
## Description
This is a toolkit specifically for Maya rigging, but also suited for other modules in maya, written in object-oriented programming.  It leverages the Maya API and cmds library, restructuring functionalities into new classes to reduce code duplication and to make coding look neat and clean.

An example of a pre-programmed character case is also provided to illustrate the usage of this library.
## The problem
Many users, while programming in Python within Maya, often create multiple modules by invoking the CMDS module and subsequently call these distinct modules separately. This approach frequently results in code that is not concise and lacks proper organization, leading to disorder and making code navigation and reference extremely inconvenient. Furthermore, this programming method not only overlooks the advantages of object-oriented programming but also fails to delve into the deep usage of the Maya API. This series of potential issues has led to redundant code, with much meaningless labor being repeated, significantly reducing overall efficiency.

The codebase I provide is specifically designed to address the aforementioned challenges in traditional programming. Its goal is to minimize redundancy, streamline the code, and consequently enhance work efficiency.
## Design
The entire codebase revolves around Maya's Dependency Node and DAG (Directed Acyclic Graph) Node as entry points. It begins by creating a DepNode class and a DagNode class, where DepNode serves as the base class for DagNode. Leveraging the functionalities of the Dependency and DAG function sets in the Maya API, the names and fullpaths of all nodes in the Maya scene can be translated into DepNode and DagNode. All DepNode and DagNode instances share properties and methods defined in the class, allowing direct actions such as deleting a node with Dag('node').delete(), renaming a node with Dag('node').rename(), and retrieving a node's parent with Dag('node').parent, and so on.

Additionally, by relying on the naming conventions of Maya attributes, we can easily access node attributes through DepNode and DagNode by redefining __getattr__ and __getitem__ dunder method in attributes class and return attribute class. Within my codebase, not only can we effortlessly get and set attributes using methods in the attribute class, but we can also achieve rapid attribute connections using Python's dunder methods. By overloading methods such as __lshift__ (<<) and __rshift__ (>>), quick attribute connections can be made, and mathematical operations like +-*/ directly create PlusMinusAverage nodes and MultiplyDivide nodes.

With the introduction of DAG nodes, it's possible to further extend the functionality by creating new node classes based on inheriting from the Dag class. For example, one can create classes for mesh nodes, curve nodes, and so on. By continuously expanding features and developing new nodes during the binding process, our toolkit has the capability to reduce at least half of the code workload.
## Classes
### Dep Node
Dep Node class allows the transformation of existing nodes into Dep nodes or the creation of new Dep nodes of specific types. It includes common node attributes such as name and type, along with frequently used functionalities like delete and rename.
### Dag Node
The Dag node can retrieve the full path of a node, query attributes like shape, parent, and children. It encompasses functionalities such as creating constraints, moveto, setting colors, and creating offset groups.
### Attributes & Attribute
The Attribute class, associated with both DepNode and DagNode classes, retrieves the attributes of Maya nodes. In addition to setting and getting attributes, it enables the quick creation of connections, conditional nodes, and arithmetic nodes through Python's dunder methods.
### Dag Dimension
Dag Dimension class mainly involves utilizing the xform command from the cmds module to retrieve node's three-dimensional spatial attributes and functionalities related to pivot transformations.
### Mesh
Mesh class primarily involves functionalities related to model weight processing.
### Curve, Joint
Only related properties were added, more functionalities are waiting to be developed.
## Bugs and Future Development
BUGS:

When using `>>` or `<<` to connect attributes, some unexpected connection error may occur when the destination attribute has multi-indices.

When using load weights method, if the proxy model has excessive subdivisions, it may result in inaccurate weight distribution, leading to subtle distortions in the topology of the model.

Future Development：

The controller library will be rewritten into the Curve class, creating controllers by calling external CV point coordinates.

The weight handling toolbox will be enhanced to achieve precise weight copying and weight transferring functionalities.

## Configuration
To minimize unnecessary trouble, please create a directory on the C drive named "Coding/rigging_tools/" and place the extracted folder inside it.

After creating the directory, please place the userSetup.py file into `C:\Users\User\Documents\maya\2023\prefs\scripts`.

You can also choose to place the extracted files into a new root directory based on your preferences, please replace the new path in userSetup.py.
## Example
A pre-written rigging script and related project files have been placed in `projects\biped\troll`. After configuring the toolkit, you can directly drag the `main.py` from `projects\biped\troll\scripts` into the Maya Script Editor and run it to generate a complete rigging setup.

If you place the files in new directory, please make sure the projectPath in `build.py` has been modified.
## Tests
