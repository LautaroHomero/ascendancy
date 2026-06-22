import json  # <- No te olvides de importar json arriba si no lo tienes
from load_data import load_profiles
from similarity_graph import build_similarity_graph
from community_detection import detect_communities
from exporter import export_graph
from createdb import create_database, save_people

INPUT_PATH = "../data/X Connections.json"
OUTPUT_PATH = "../../frontend/public/graph.json"
 
def main():
 
     #print("Loading profiles...")
    profiles = load_profiles(INPUT_PATH)
     #print(f"Loaded {len(profiles)} profiles")
 
     #print("Building similarity graph...")
    similarity_graph = build_similarity_graph(profiles)
 
     #print("Detecting communities...")
    community_data = detect_communities(similarity_graph)

    # 1. Aseguramos que la base de datos y la tabla existan
     #print("Preparing database...")
    create_database()
    
    # 2. Exportas el grafo al archivo JSON como siempre
     #print("Exporting graph...")
    export_graph(similarity_graph, community_data, OUTPUT_PATH)
 
    # 3. LEER EL JSON GENERADO Y GUARDAR EN LA BASE DE DATOS
     #print("Reading exported graph to save people...")
    try:
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            graph_data = json.load(f)
        
        # Extraemos la lista de personas usando la estructura de tu JSON
        people_list = graph_data["company"]["people"]
        print("PRIMER REGISTRO EN MEMORIA:", people_list[0])
        # Guardamos en la base de datos
        print(f"Saving {len(people_list)} people to the database...")
        save_people(people_list)
        
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo en {OUTPUT_PATH}")
    except KeyError:
        print("Error: El JSON exportado no tiene la estructura 'company' -> 'people'")
 
if __name__ == "__main__":
    main()