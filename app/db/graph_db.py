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

    def get_person_relationships(self, person_id: int):
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

    def get_person_details(self, person_id: int):
        query = """
        MATCH (p:Person {id: $personId})
        RETURN p
        """
        with self.driver.session() as session:
            result = session.run(query, personId=person_id)
            record = result.single()
            return record.data()['p'] if record else None # Accedemos a 'p' porque retornamos el nodo 'p'
