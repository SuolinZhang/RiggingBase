# SuolinZhang-Maya-tools
## Description
## The problem
Many users, while programming in Python within Maya, often create multiple modules by invoking the CMDS module and subsequently call these distinct modules separately. This approach frequently results in code that is not concise and lacks proper organization, leading to disorder and making code navigation and reference extremely inconvenient. Furthermore, this programming method not only overlooks the advantages of object-oriented programming but also fails to delve into the deep usage of the Maya API. This series of potential issues has led to redundant code, with much meaningless labor being repeated, significantly reducing overall efficiency.


The codebase I provide is specifically designed to address the aforementioned challenges in traditional programming. Its goal is to minimize redundancy, streamline the code, and consequently enhance work efficiency.
## Design
The entire codebase revolves around Maya's Dependency Node and DAG (Directed Acyclic Graph) Node as entry points. It begins by creating a DepNode class and a DagNode class, where DepNode serves as the base class for DagNode. Leveraging the functionalities of the Dependency and DAG function sets in the Maya API, the names and fullpaths of all nodes in the Maya scene can be translated into DepNode and DagNode. All DepNode and DagNode instances share properties and methods defined in the class, allowing direct actions such as deleting a node with Dag('node').delete(), renaming a node with Dag('node').rename(), and retrieving a node's parent with Dag('node').parent, and so on.

Additionally, by relying on the naming conventions of Maya attributes, we can easily access node attributes through DepNode and DagNode by redefining __getattr__ and __getitem__ dunder method in attributes class and return attribute class. Within my codebase, not only can we effortlessly get and set attributes using methods in the attribute class, but we can also achieve rapid attribute connections using Python's dunder methods. By overloading methods such as __lshift__ (<<) and __rshift__ (>>), quick attribute connections can be made, and mathematical operations like +-*/ directly create PlusMinusAverage nodes and MultiplyDivide nodes.

With the introduction of DAG nodes, it's possible to further extend the functionality by creating new node classes based on inheriting from the Dag class. For example, one can create classes for mesh nodes, curve nodes, and so on. By continuously expanding features and developing new nodes during the binding process, our toolkit has the capability to reduce at least half of the code workload.
## Classes
## Bugs and Future Development
BUGS:

When using `>>` or `<<` to connect attributes, some unexpected connection error may occur when the destination attribute has multi-indices.

When using load weights method, if the proxy model has excessive subdivisions, it may result in inaccurate weight distribution, leading to subtle distortions in the topology of the model.

Future Development：

The controller library will be rewritten into the Curve class, creating controllers by calling external CV point coordinates.

The weight handling toolbox will be enhanced to achieve precise weight copying and weight transferring functionalities.

## Example
## Tests
