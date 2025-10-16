#TODO 

#Recebe os eventos de cada "Bob_State" e transforma em estados Globais 
#"FIELD DIGERIDA"
import py_trees


class Blackboard_Manager:
    _instance = None

    def __init__(self):
        if Blackboard_Manager._instance is not None:
            raise Exception("Use BlackboardManager.get() para acessar a instância.")
        self._bb = py_trees.blackboard.Blackboard()
    @staticmethod
    def get_instance():
        if Blackboard_Manager._instance is None:
            Blackboard_Manager._instance = Blackboard_Manager()
        return Blackboard_Manager._instance

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

    def dump(self) -> None:
        """
        Mostra todas as chaves e valores armazenados no blackboard global.
        Útil para depuração e inspeção durante execução.
        """
        print("======= BLACKBOARD DUMP =======")
        try:
            storage = getattr(self._bb, "storage", getattr(self._bb, "_storage", {}))
            if not storage:
                print("(vazio)")
                return
            for k, v in storage.items():
                print(f"{k} = {v}")
        except Exception as e:
            print(f"erro ao acessar storage do blackboard: {e}")



if __name__ == "__main__":
    bb=Blackboard_Manager.get_instance()
    print(bb.get("dsdsd"))
