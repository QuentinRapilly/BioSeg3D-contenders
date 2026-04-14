from time import time, sleep


class Timer:

    nb_call = 0
    time_in = 0.

    def __enter__(self):
        Timer.nb_call += 1
        Timer.start = time()

    def __exit__(self, exc_type, exc, tb):
        Timer.time_in += time() - Timer.start

    @classmethod
    def elapsed_time(cls):

        print(cls.nb_call)
        print(cls.time_in)
        return cls.time_in/cls.nb_call
    


if __name__ == "__main__":


    with Timer():
        sleep(1)

    with Timer():
        sleep(2)

    print(Timer.elapsed_time())
    

