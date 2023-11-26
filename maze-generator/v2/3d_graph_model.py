import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx

# Create a sample multi-layered graph
G = nx.Graph()

# Nodes in layer 1
G.add_nodes_from([(1, {'layer': 1}), (2, {'layer': 1}), (3, {'layer': 1})])

# Nodes in layer 2
G.add_nodes_from([(4, {'layer': 2}), (5, {'layer': 2})])

# Edges between layers
G.add_edges_from([(1, 4), (2, 5), (3, 4)])

# Get node positions
pos = nx.spring_layout(G, seed=42, dim=3)  # Set dim=3 to get 3D positions

# Create 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Extract x, y, and z coordinates for each node
x = [pos[node][0] for node in G.nodes()]
y = [pos[node][1] for node in G.nodes()]
z = [pos[node][2] for node in G.nodes()]

# Plot nodes
ax.scatter(x, y, z, c=[G.nodes[node]['layer'] for node in G.nodes()], marker='o', s=100)

# Plot edges
for edge in G.edges():
    ax.plot([pos[edge[0]][0], pos[edge[1]][0]],
            [pos[edge[0]][1], pos[edge[1]][1]],
            [pos[edge[0]][2], pos[edge[1]][2]], color='black')

# Label nodes
for node in G.nodes():
    ax.text(pos[node][0], pos[node][1], pos[node][2] + 0.1, str(node), color='black', fontsize=8)

# Set axis labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.title('3D Structure of Multi-Layered Graph Nodes')
plt.show()
