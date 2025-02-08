class JsonRepository:
    def _get(self, data: dict, *keys: str) -> any:
        try:
            for key in keys:
                data = data[key]
            return data
        except KeyError:
            return None
        
    def _set(self, data: dict, *keys: str, value: any) -> None:
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]

        data[keys[-1]] = value

    def _remove(self, data: dict, *keys) -> None:
        for key in keys[:-1]:
            if key in data:
                data = data[key]
            else:
                pass
        
        if keys[-1] in data:
            del data[keys[-1]]