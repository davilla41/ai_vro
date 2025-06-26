from neo4j import GraphDatabase
from app.core.config import settings

class GraphDB:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def get_person_relationships_by_name(self, person_name: str):
        query = """
        MATCH (p:Person {first_name: $person_name})-[r]->(related:Person)
        RETURN
        type(r) AS relationship_type, related.first_name AS related_name, related.last_name AS related_apellido, related.nickname AS related_apodo
        """
        with self.driver.session() as session:
            result = session.run(query, person_name=person_name)
            return [record.data() for record in result]
    def get_person_details_by_name(self, person_name: str):
        query = """
        MATCH (p:Person {first_name: $person_name})
        RETURN p.first_name AS nombre, p.middle_name AS segundo_nombre, p.last_name AS apellido, p.mother_surname AS segundo_apellido, p.nickname AS apodo, p.date_of_birth AS fecha_nacimiento, p.date_of_death AS fecha_fallecimiento, p.profession AS profesion, p.sex AS sexo, p.email AS email, p.mobile_phone AS numero_de_movil, p.is_main_user AS es_usuario_principal
        """
        with self.driver.session() as session:
            result = session.run(query, person_name=person_name)
            record = result.single()
            return record.data() if record else None

    def get_person_relationships_by_id(self, person_id: int):
        query = """
        MATCH (p:Person {id: $personId})-[r]-(related:Person)
        RETURN DISTINCT
            type(r) AS relationship_type,
            related.first_name AS related_first_name,
            related.last_name AS related_last_name,
            related.nickname AS related_nickname,
            CASE
                WHEN startNode(r) = p THEN 'outgoing'
                ELSE 'incoming'
            END AS direction_from_personId
        """
        with self.driver.session() as session:
            result = session.run(query, personId=person_id)
            return [record.data() for record in result]

    def get_person_details_by_id(self, person_id: int):
        query = """
        MATCH (p:Person {id: $personId})
        RETURN p.first_name AS nombre, p.middle_name AS segundo_nombre, p.last_name AS apellido, p.mother_surname AS segundo_apellido, p.nickname AS apodo, p.date_of_birth AS fecha_nacimiento, p.date_of_death AS fecha_fallecimiento, p.profession AS profesion, p.sex AS sexo, p.email AS email, p.mobile_phone AS numero_de_movil, p.is_main_user AS es_usuario_principal
        """
        with self.driver.session() as session:
            result = session.run(query, personId=person_id)
            record = result.single()
            return record.data()['p'] if record else None # Accedemos a 'p' porque retornamos el nodo 'p'
    
    def execute_cypher_query(self, cypher_query: str):
        """
        Ejecuta una consulta Cypher arbitraria en Neo4j y devuelve los resultados.
        """
        with self.driver.session() as session:
            try:
                result = session.run(cypher_query)
                # Convertir los resultados a una lista de diccionarios para facilitar el manejo
                return [record.data() for record in result]
            except Exception as e:
                print(f"Error al ejecutar la consulta Cypher: {e}")
                return [] 

    def get_graph_schema(self) -> str:
        """
        Devuelve una representación del esquema del grafo (nodos y relaciones) en un formato legible para el LLM.
        """
        schema_info = []
        with self.driver.session() as session:
            # Obtener todos los labels de nodos y sus propiedades
            node_properties_query = """
            CALL db.schema.nodeTypeProperties()
            YIELD nodeType, propertyName, propertyTypes, mandatory
            RETURN nodeType AS label, collect({property: propertyName, type: propertyTypes, required: mandatory}) AS properties
            """
            node_results = session.run(node_properties_query)
            for record in node_results:
                props = ", ".join([
                    f"{p['property']}:"
                    f"{p['type'][0] if p['type'] and len(p['type']) > 0 else 'UNKNOWN_TYPE'} "
                    f"{'(required)' if p['required'] else ''}"
                    for p in record['properties']
                ])
                schema_info.append(f"Node '{record['label']}' with properties: {props}")

            # Obtener todos los tipos de relaciones y sus propiedades, y los tipos de nodos conectados
            relationship_properties_query = """
            CALL db.schema.relTypeProperties()
            YIELD relType, propertyName, propertyTypes, mandatory
            RETURN relType AS relationshipType, collect({property: propertyName, type: propertyTypes, required: mandatory}) AS properties
            """
            rel_results = session.run(relationship_properties_query)
            for record in rel_results:
                props = ", ".join([
                    f"{p['property']}:"
                    f"{p['type'][0] if p['type'] and len(p['type']) > 0 else 'UNKNOWN_TYPE'}"
                    for p in record['properties']
                ])
                schema_info.append(f"Relationship '{record['relationshipType']}' with properties: {props}")
            
            # También podemos listar ejemplos de relaciones entre tipos de nodos
            # Esto puede ser muy útil para el LLM
            relationship_examples_query = """
            MATCH (a)-[r]->(b)
            WITH type(r) AS relType, labels(a) AS fromLabels, labels(b) AS toLabels
            RETURN DISTINCT relType, fromLabels, toLabels
            """
            example_rel_results = session.run(relationship_examples_query)
            for record in example_rel_results:
                schema_info.append(f"Example: ({record['fromLabels'][0]})-[{record['relType']}]->({record['toLabels'][0]})")

        return "\n".join(schema_info)
