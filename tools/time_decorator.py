from time import time, sleep

class Timer:

    nb_call = {}
    time_in = {}

    def __init__(self, key):
        self.key = key
        if self.nb_call.get(key) is None:
            self.nb_call[key] = 1
            self.time_in[key] = 0.
        else:
            self.nb_call[key] += 1


    def __enter__(self):
        #Timer.nb_call += 1
        self.start = time()

    def __exit__(self, exc_type, exc, tb):
        Timer.time_in[self.key] += time() - self.start

    @classmethod
    def elapsed_time(cls, key):
        return cls.time_in[key]/cls.nb_call[key]
    
    @classmethod
    def summary(cls):
        return {key: {
            "nb_call": cls.nb_call[key],
            "total_time": cls.time_in[key],
            "mean_time": cls.time_in[key]/cls.nb_call[key]
            }
                for key in cls.nb_call}
    
    @classmethod
    def str_summary(cls):
        dico = Timer.summary()
        res = ""
        for k in dico:
            res += f"Operation {k}:\n  - called: {dico[k]['nb_call']} time(s),\n  - mean time {round(dico[k]['mean_time'],4)}s.\n"

        return res

if __name__ == "__main__":

    with Timer("test1"):
        sleep(1)

    with Timer("test1"):
        sleep(2)

    with Timer("test2"):
        sleep(1)

    print(Timer.str_summary())
    

