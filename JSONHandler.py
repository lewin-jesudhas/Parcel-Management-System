import json

class JSONHandler:
    # Singleton instance variable
    _instance = None

    def __new__(cls):
        # Ensure only one instance of the class is created
        if cls._instance is None:
            cls._instance = super(JSONHandler, cls).__new__(cls)
        return cls._instance

    def dumps(self, obj) -> str:
        """Serialize Python object to a JSON-formatted string.

        Args:
            obj: Python object to be serialized.

        Returns:
            str: JSON-formatted string.
        """
        return json.dumps(obj, indent=2)

    def dump(self, obj, fp) -> bool:
        """Serialize Python object and write it to a file-like object.

        Args:
            obj: Python object to be serialized.
            fp: File-like object to write the JSON data.

        Returns:
            bool: True if successful.
        """
        json.dump(obj, fp, indent=2)
        return True

    def loads(self, data) -> dict:
        """Deserialize a JSON-formatted string to a Python dictionary.

        Args:
            data (str): JSON-formatted string.

        Returns:
            dict: Deserialized Python dictionary.
        """
        return json.loads(data)

    def load(self, fp) -> dict:
        """Deserialize JSON data from a file-like object to a Python dictionary.

        Args:
            fp: File-like object containing JSON data.

        Returns:
            dict: Deserialized Python dictionary.
        """
        return json.load(fp)

    def close(self):
        """Close the singleton instance.

        Note: The close method is left empty, as there is no specific cleanup logic.
        """
        JSONHandler._instance = None
        del self
        