x = ["a", "b", "c", "d"]
del(x[3])
print(x)


str = 'Hello Python!'
print (str[2:4])

y = ["this", "is", "a", True, "test"]

print(y[3])

x = 5
y = 2
result = x / y
print(f"{result:.2f}")

L = [5,6,3]

#print(L[3])



class Person: 
    def __init__(self, id): 
        self.id = id 
        
sam = Person(100) 
sam.__dict__['age'] = 49 
print(sam.age + len(sam.__dict__))

str = "testing"
print(len(str))

print(9//2)


x = [1, 2, 3, 4, 5]
squared = (num * num for num in x)
print(list(squared))

list = [ 'Sonata', 786 , 2.23, 'john', 70.2 ] 

print(list)


x = (1, 2, 3)
y = (4, 5, 6)
z = zip(x, y)
#print(list(z))

class Test: 
    def __init__(self, id): 
        self.id = id 

id = 100 
val = Test(123) 
print (val.id)

x = ["a", "b", "c"]
x = x + ["d"]
print(x)


def func(x):
    return x * x

values = [1, 2, 3, 4, 5]
squares = map(func, values)
#print(list(squares))

str = 'Hello Sonata!'
print(str[0])


tuple = ( 'Sonata', 786 , 2.23, 'john', 70.2 )
print(tuple[0])

tinylist = [123, 'Sonata']
print(tinylist * 2)

def func(x):
    return x > 0

values = [10, -5, 8, -3, 0]
positives = filter(func, values)
#print(list(positives))

x = ["a", "b", "b"]
x[2] = "c"
print(x)

xy = [4, 5, 6, 7]

print(xy[2:2])

print(type(xy))


list = [ 'abcd', 786 , 2.23, 'john', 70.2 ]

print(list[1:3])