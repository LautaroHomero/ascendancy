# Technical Solution

To solve this exercise, we modeled the network as a graph of people, where each node represents a person and edges represent relationships inferred from shared attributes. The core idea was to avoid treating the dataset as a simple list of profiles, and instead build a relational structure capable of revealing groups, bridges, and densely connected zones.

## Graph Construction

We first parsed and cleaned the data to normalize the noisiest fields, particularly academic titles and locations. We then built the network across several dimensions of similarity:

- current company or shared work experience
- university
- position / title
- location
- academic degree
- major

Each of these dimensions generates connections between people who share the same value. For example, if two profiles have the same job title or worked at the same company, an edge is created between them. This lets us capture different kinds of professional affinity without collapsing the network into a single signal.

## Why We Chose Louvain

We used **Louvain**, a modularity-based community detection algorithm, to detect communities. We chose this method because the goal wasn't to form rigid groups based on exact attribute equality, but to find real clustering structures within the network.

Louvain is well suited to this problem because it:

- maximizes internal density within communities
- separates loosely connected zones more effectively
- can detect communities even when nodes don't share the exact same value
- is more robust on large, heterogeneous networks

This mattered because in a real professional network, many people don't share an identical attribute, yet they're still linked through indirect paths of similarity. For instance, one person might connect to another through a shared title, and that second person might connect to a third through a shared company or a related role. Louvain captures this kind of structure better than a strictly literal segmentation would.

## What a Community Represents

A community does not mean "all these profiles have the exact same attribute." It means that, within the graph's structure, they form a denser and more coherent block than the rest of the network.

That's why a community labeled, say, "Software Engineer," can still contain people who aren't software engineers themselves. The community's name is assigned based on its dominant or most representative attribute, but membership in the group comes from the structure of connections, not from an exact filter.

In other words:

- the **name** describes
- the **network** determines

## Location: Country → City Hierarchy

For locations, we made a specific improvement: instead of grouping by the full `current_location` string, we split it into a hierarchy of:

- country
- city

This solved an important problem: the full location string tends to be too granular, fragmenting the network without adding useful structure. Grouping first by country and then by city produces a cleaner, more natural reading.

As a result, a geographic network ends up organized in two levels: first, communities by country; then, within each country, subgroups by city. This makes the visualization more interpretable and prevents cities with very few records from being isolated due to excessive granularity.

## Why We Show Two Views

We chose to display the network in two different ways because they answer different questions.

### 1. Community View

This is the primary view for analysis. It shows the graph as it actually emerges from real connection structure and the communities detected by Louvain.

It helps answer questions like:

- how connected is the network?
- what groups emerge naturally?
- which nodes act as bridges between communities?
- where are the dense zones or the cut points?

This view is the most faithful to the network's structural analysis, and the most useful for the exercise's main objective.

### 2. Clique View

The second view is a complete representation of the selected group. In this mode, every node in the cluster is connected to every other node in that same cluster.

This isn't meant for structural inference — it's meant for visual inspection. Its purpose is to show:

- maximum density
- full interaction between group members
- legibility of internal relationships
- a visual comparison against the real community

The clique view doesn't replace the community view; it complements it. The community tells us which groups exist structurally. The clique lets us see what that group would look like if every possible connection were present.

## Community vs. Clique

It's important to distinguish between the two:

- **Community**: a group detected from the graph's real structure.
- **Clique**: a visually completed group, where everyone is connected to everyone.

The community is analytical.
The clique is exploratory.

That's why a person can appear in a community without being directly connected to every other member. That's not a bug — it's exactly the effect of a relational network. Group membership is often the result of indirect paths of connection, not direct relationships with every single member.

### Interpretive Example

Suppose there's a cluster labeled "Software Engineer." Within that group, you might find a person whose actual title is "Social Media Investigator." That happens because this person is connected to other members of the group through other shared attributes, and Louvain places them in that community based on structural closeness.

This doesn't mean the group's label is a literal truth about every person in it — it means it's the most representative label for the resulting community.

## Visualization

The interface was designed to be minimalist, on a dark background, so the network itself stays the visual focus. Groups are represented as circular nodes, and node size reflects cluster size. Larger groups carry more visual weight, and the spatial layout aims for a sense of orbit or floating, especially in the overview.

When entering a group, the network expands to show its connected members, preserving the distinction between the community view and the clique view.

## Limitations and Assumptions

The solution rests on a few assumptions:

- a shared attribute implies a potential relationship
- a community's name is a descriptive label, not an exact definition
- the network reflects relational similarity, not pure semantic hierarchy

There are also limitations:

- some fields may be incomplete or inconsistent
- textual location data can be ambiguous
- Louvain detects useful communities, but not "absolute truths"
- the clique view can get visually dense in larger groups

## Conclusion

This solution combines:

- relational modeling
- community detection with Louvain
- location hierarchization
- two complementary views
- a minimalist, exploration-focused interface

With this approach, the network can be analyzed structurally and also inspected visually. The community view answers the exercise's main question — what groups emerge in the network. The clique view answers a second need — seeing the inside of a group as if it were a fully connected network.