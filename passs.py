class A():
    def a(self):
        print('a')

class C():
    def c(self):
        print('c')

class D(A,C):
    def d(self):
        print('d')

d = D()

d.a()
d.c()
d.d()