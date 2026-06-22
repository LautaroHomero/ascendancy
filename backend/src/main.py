from load_data import load_profiles
from similarity_graph import build_similarity_graph
from community_detection import detect_communities
from exporter import export_graph


INPUT_PATH = "../data/X Connections.json"
OUTPUT_PATH = "../../frontend/public/graph.json"
 
 
def main():
 
    print("Loading profiles...")
    profiles = load_profiles(INPUT_PATH)
    print(f"Loaded {len(profiles)} profiles")
 
    print("Building similarity graph...")
    similarity_graph = build_similarity_graph(profiles)
 
    print("Detecting communities...")
    community_data = detect_communities(similarity_graph)
 
    print("Exporting graph...")
    export_graph(similarity_graph, community_data, OUTPUT_PATH)
 
 
if __name__ == "__main__":
    main()