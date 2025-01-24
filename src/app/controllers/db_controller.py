import os
import sqlite3
import threading
from typing import List, Dict, Any, Tuple
from app.utils.configreader import ConfigReader
from app.utils.logger import console_logger
from app.models.internal import Args, LLMConfig, Measurement, PromptInput, Request, LLM_Response, LLM_Response_Full

class DatabaseController:
    __thread_local = threading.local()
    __lock = threading.Lock()

    @classmethod
    def get_instance(cls, db_name: str):
        """
        Gibt eine thread-lokale Instanz des DatabaseController zurück.
        :param db_name: Name der SQLite-Datenbankdatei
        :return: Thread-lokale Instanz des DatabaseController
        """
        if not hasattr(cls.__thread_local, "instance"):
            with cls.__lock:
                if not hasattr(cls.__thread_local, "instance"):
                    cls.__thread_local.instance = cls(db_name)
        return cls.__thread_local.instance

    def __init__(self, db_name: str):
        """Initialisiert den DatabaseController mit einer SQLite-Verbindung."""
        if hasattr(self, "_initialized") and self._initialized:
            return  # Verhindere doppelte Initialisierung
        self._initialized = True
        self.db_path = db_name
        self.connection = sqlite3.connect(db_name, check_same_thread=False)  # Thread-Check deaktivieren

    def close(self):
        """Schließt die Verbindung für den aktuellen Thread."""
        if hasattr(self, "_initialized") and self._initialized:
            self.connection.close()
            del self.__thread_local.instance

    def create_table(self, table_name: str, columns: List[Tuple[str, str]]):
        """Create a table with the specified name and columns.

        Args:
            table_name (str): The name of the table.
            columns (List[Tuple[str, str]]): A list of column definitions, where each tuple contains the column name and type.
        """
        with self.connection:
            cursor = self.connection.cursor()
            columns_definition = ", ".join([f"{name} {type}" for name, type in columns])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})"
            cursor.execute(query)
            self.connection.commit()

    def insert_data(self, table_name: str, data: List[Tuple[Any, ...]], columns: List[str] = None):
        """Insert multiple rows of data into a table.

        Args:
            table_name (str): The name of the table.
            data (List[Tuple[Any, ...]]): A list of tuples, where each tuple contains the values for one row.
            columns (List[str]): Optional list of column names to insert into. Defaults to all columns.
        """
        if columns:
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["?" for _ in columns])
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        else:
            placeholders = ", ".join(["?" for _ in data[0]])
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        inserted_objects = []
        
        with self.connection:
            cursor = self.connection.cursor()
            inserted_ids = []
            for row in data:
                # Execute query
                cursor.execute(query, row)

                # Retrieve ID: lastrowid for autoincrement, manual ID otherwise
                row_id = cursor.lastrowid if "id" not in columns or isinstance(row[columns.index("id")], int) else row[columns.index("id")]

                # Fetch the inserted object using the ID
                fetched_object = self.search(table_name, "id", row_id)
                if fetched_object:
                    inserted_objects.append(fetched_object[0])

        self.connection.commit()
        return inserted_objects
        
            
        
    def update_data(self, table_name: str, column: str, value: Any, condition_column: str, condition_value: Any):
        """Update data in a table.

        Args:
            table_name (str): The name of the table.
            column (str): The column to update.
            value (Any): The new value.
            condition_column (str): The column to use for the condition.
            condition_value (Any): The value to match in the condition column.
        """
        query = f"UPDATE {table_name} SET {column} = ? WHERE {condition_column} = ?"
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, (value, condition_value))
            self.connection.commit()
    
    def update_multiple(self, table_name: str, columns: List[Tuple[str, Any]], conditions: List[Tuple[str, Any]]):
        """Update data in a table.

        Args:
            table_name (str): The name of the table.
            columns (List[Tuple[str, Any]]): A list of tuples, where each tuple contains the column name and new value.
            conditions (List[Tuple[str, Any]]): A list of tuples, where each tuple contains the column name and value to match.
        """
        query = f"UPDATE {table_name} SET {', '.join([f'{column} = ?' for column, _ in columns])} WHERE {' AND '.join([f'{column} = ?' for column, _ in conditions])}"
        #remove the last AND
        query  = query.replace("WHERE AND", "WHERE")
        
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, [value for _, value in columns] + [value for _, value in conditions])
            self.connection.commit()

    def fetch_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Fetch all rows from a table.

        Args:
            table_name (str): The name of the table.

        Returns:
            List[Dict[str, Any]]: A list of rows, where each row is represented as a dictionary.
        """
        query = f"SELECT * FROM {table_name}"
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


    def search(self, table_name: str, column: str, value: Any) -> List[Dict[str, Any]]:
        """Search for rows in a table where a specific column matches a value.

        Args:
            table_name (str): The name of the table.
            column (str): The column to search in.
            value (Any): The value to search for.

        Returns:
            List[Dict[str, Any]]: A list of rows, where each row is represented as a dictionary.
        """
        query = f"SELECT * FROM {table_name} WHERE {column} = ?"
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, (value,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def search_multiple(self, table_name: str, conditions: List[Tuple[str, Any]]) -> List[Dict[str, Any]]:
        """Search for rows in a table where multiple columns match specific values.

        Args:
            table_name (str): The name of the table.
            conditions (List[Tuple[str, Any]]): A list of tuples, where each tuple contains the column name and value to search for.

        Returns:
            List[Dict[str, Any]]: A list of rows, where each row is represented as a dictionary.
        """
        query = f"SELECT * FROM {table_name} WHERE {' AND '.join([f'{column} = ?' for column, _ in conditions])}"
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, [value for _, value in conditions])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def return_custom_query(self, query: str) -> List[Dict[str, Any]]:
        """Return the result of a custom query.

        Args:
            query (str): The query to execute.

        Returns:
            List[Dict[str, Any]]: A list of rows, where each row is represented as a dictionary.
        """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    def reset_database(self):
        """
        Löscht die SQLite-Datenbankdatei und erstellt eine neue leere Datei.
        :param db_path: Pfad zur SQLite-Datenbankdatei
        """
        self.connection.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            console_logger.info(f"Datenbankdatei {self.db_path} wurde gelöscht.")
        else:
            console_logger.info(f"Datenbankdatei {self.db_path} existiert nicht.")

        # Neue leere Datenbank erstellen (optional, falls Struktur neu aufgesetzt werden muss)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
    
    def close(self):
        """Close the database connection."""
        self.connection.close()

class PromptingServiceDbController:
    __instance = None
    __lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            with cls.__lock:
                if cls.__instance is None:  # Doppelprüfung
                    cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return  # Verhindert doppelte Initialisierung
        self._initialized = True

        console_logger.info("Initializing LLM Registry Database Controller...")
        config_reader = ConfigReader.get_instance()
        db_name = config_reader.get("database", "db_name")
        console_logger.info(f"Using database: {db_name}")
        self.db_controller = DatabaseController.get_instance(db_name)
        self.__create_tables__()

        
    def __create_tables__(self):
        self.db_controller.create_table("prompt_inputs", [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("prompt", "TEXT"),
            ("prompttype", "TEXT"),
            ("measurementId", "INTEGER")
        ])
        self.db_controller.create_table("llm_response", [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("llm_config", "TEXT"),
            ("idPromptInput", "INTEGER"),
            ("response", "TEXT"),
            ("sci_score", "REAL"),
            ("answer_time_seconds", "REAL"),
            ("request_id", "TEXT")
        ])
        self.db_controller.create_table("llm_request", [
            ("id", "TEXT PRIMARY KEY"),
            ("llm_config", "TEXT"),
            ("status", "TEXT"),
            ("measurementId", "INTEGER"),
            ("address", "TEXT")
        ])
        self.db_controller.create_table("measurements", [
            ("id", "INTEGER PRIMARY KEY"),
            ("status", "TEXT")
        ])

    @classmethod
    def get_instance(cls):
        return cls()

    def close(self):
        if self.db_controller:
            self.db_controller.close()
        PromptingServiceDbController.__instance = None

    def __del__(self):
        self.close()
        
    def insert_llm_response(self, llm_response: LLM_Response):
        self.db_controller.insert_data("llm_response", [(llm_response.llm_config.model_dump_json(), llm_response.idPromptInput, llm_response.response, llm_response.sci_score, llm_response.answer_time_seconds, llm_response.request_id)], ["llm_config", "idPromptInput", "response", "sci_score", "answer_time_seconds", "request_id"])
        
    def insert_llm_request(self, request: Request):
        self.db_controller.insert_data("llm_request", [(request.id, request.llm_config.model_dump_json(), request.status, request.measurementId, request.address)], ["id", "llm_config", "status", "measurementId", "address"])
        
    def insert_prompt_input(self, prompt_input: PromptInput):
        self.db_controller.insert_data("prompt_inputs", [(prompt_input.prompt, prompt_input.prompttype, prompt_input.measurementId)], ["prompt", "prompttype", "measurementId"])
    
    def create_measurement(self):
        insert_objects = self.db_controller.insert_data("measurements", [("deployments_pending",)], ["status"])
        measurement = Measurement(**insert_objects[0])
        return measurement
    
    def update_llm_request(self, request: Request):
        self.db_controller.update_multiple("llm_request", [("llm_config", request.llm_config.model_dump_json()), ("status", request.status), ("address", request.address)], [("id", request.id)])
    
    def update_measurement(self, measurement : Measurement):
        self.db_controller.update_data("measurements", "status", measurement.status, "id", measurement.id)
        
    def get_llm_responses(self, request_id: str) -> List[LLM_Response]:
        responses = self.db_controller.search("llm_response", "request_id", request_id)
        for response in responses:
            response["llm_config"] = LLMConfig.model_validate_json(response["llm_config"])
        return [LLM_Response(**response) for response in responses]
    
    def get_llm_request(self, request_id: str) -> Request:
        request = self.db_controller.search("llm_request", "id", request_id)
        request["llm_config"] = LLMConfig.model_validate_json(request["llm_config"])
    
    def get_measurements(self) -> List[Measurement]:
        measurements = self.db_controller.fetch_all("measurements")
        return [Measurement(**measurement) for measurement in measurements]
    
    def get_measurements_by_status(self, status: str) -> List[Measurement]:
        measurements = self.db_controller.search("measurements", "status", status)
        return [Measurement(**measurement) for measurement in measurements]
    
    def get_requests(self) -> List[Request]:
        requests = self.db_controller.fetch_all("llm_request")
        for request in requests:
            request["llm_config"] = LLMConfig.model_validate_json(request["llm_config"])
        return [Request(**request) for request in requests]
    
    def get_responses(self) -> List[LLM_Response]:
        responses = self.db_controller.fetch_all("llm_response")
        for response in responses:
            response["llm_config"] = LLMConfig.model_validate_json(response["llm_config"])
        return [LLM_Response(**response) for response in responses]
    
    def get_requests_by_status(self, status: str) -> List[Request]:
        requests = self.db_controller.search("llm_request", "status", status)
        for request in requests:
            request["llm_config"] = LLMConfig.model_validate_json(request["llm_config"])
        return [Request(**request) for request in requests]
    
    def get_responses_by_request_id(self, request_id: str) -> List[LLM_Response]:
        responses = self.db_controller.search("llm_response", "request_id", request_id)
        for response in responses:
            response["llm_config"] = LLMConfig.model_validate_json(response["llm_config"])
        return [LLM_Response(**response) for response in responses]
    
    def get_requests_by_measurement_id(self, measurement_id: int) -> List[Request]:
        requests = self.db_controller.search("llm_request", "measurementId", measurement_id)
        for request in requests:
            request["llm_config"] = LLMConfig.model_validate_json(request["llm_config"])
        return [Request(**request) for request in requests]
    
    def get_responses_by_measurement_id(self, measurement_id: int) -> List[LLM_Response]:
        requests = self.db_controller.search("llm_request", "measurementId", measurement_id)
        request_ids = [request["id"] for request in requests]
        responses = []
        for request_id in request_ids:
            responses.extend(self.get_responses_by_request_id(request_id))
        return responses
    
    def get_measurement(self, measurement_id: int) -> Measurement:
        measurements = self.db_controller.search("measurements", "id", measurement_id)
        return Measurement(**measurements[0])
    
    def get_full_responses(self) -> List[LLM_Response_Full]:
        responses = self.db_controller.fetch_all("llm_response")
        llm_responses = []
        for response in responses:
            response["llm_config"] = LLMConfig.model_validate_json(response["llm_config"])
            promptInnputs = self.db_controller.search("prompt_inputs", "id", response["idPromptInput"])
            response["prompt"] = promptInnputs[0]["prompt"]
            response["prompttype"] = promptInnputs[0]["prompttype"]
            llm_responses.append(response)
            
        return [LLM_Response_Full(**response) for response in responses]
    
    def get_full_responses_by_request_id(self, request_id: str) -> List[LLM_Response_Full]:
        responses = self.db_controller.search("llm_response", "request_id", request_id)
        llm_responses = []
        for response in responses:
            response["llm_config"] = LLMConfig.model_validate_json(response["llm_config"])
            promptInnputs = self.db_controller.search("prompt_inputs", "id", response["idPromptInput"])
            response["prompt"] = promptInnputs[0]["prompt"]
            response["prompttype"] = promptInnputs[0]["prompttype"]
            llm_responses.append(response)
            
        return [LLM_Response_Full(**response) for response in responses]
    
    def get_full_responses_by_measurement_id(self, measurement_id: int) -> List[LLM_Response_Full]:
        requests = self.db_controller.search("llm_request", "measurementId", measurement_id)
        request_ids = [request["id"] for request in requests]
        responses = []
        for request_id in request_ids:
            responses.extend(self.get_full_responses_by_request_id(request_id))
        return responses
    
    def get_prompt_inputs_by_measurement_id(self, measurement_id: int) -> List[PromptInput]:
        prompt_inputs = self.db_controller.search("prompt_inputs", "measurementId", measurement_id)
        return [PromptInput(**prompt_input) for prompt_input in prompt_inputs]
        
    
    
    

        
        
    def clear_all(self):
        self.db_controller.reset_database()
        self.__create_tables__()                                                        
        
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
