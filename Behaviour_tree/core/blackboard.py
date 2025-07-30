#TODO 

#Recebe os eventos de cada "Bob_State" e transforma em estados Globais 
#"FIELD DIGERIDA"
import py_trees


class BlackboardManager:
    _instance = None

    def __init__(self):
        if BlackboardManager._instance is not None:
            raise Exception("Use BlackboardManager.get() para acessar a instância.")
        self._bb = py_trees.blackboard.Blackboard()
    @staticmethod
    def get_instance():
        if BlackboardManager._instance is None:
            BlackboardManager._instance = BlackboardManager()
        return BlackboardManager._instance

    def set(self, key: str, value):
        self._bb.set(key, value)

    def get(self, key: str):
        try:
            return self._bb.get(key)
        except KeyError:
            print(f"chave {key} nao existe no blackboard")
            return None


    def clear(self, key: str = ""):
        if key:
            try:
                self._bb.unset(key)
            except KeyError:
                print(f"chave {key} nao existe no blackboard")
                pass
        else:
            for k in list(self._bb.storage.keys()):
                try:
                    self._bb.unset(k)
                except KeyError:
                    pass


if __name__ == "__main__":
    bb=BlackboardManager.get_instance()
    print(bb.get("dsdsd"))
