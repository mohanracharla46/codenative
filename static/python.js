const topics = document.querySelectorAll(".topic");
const content = document.getElementById("topicContent");
const pageTitle = document.getElementById("pageTitle");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");

const topicData = {
    home: `
        <h2>Welcome to Python Tutorial</h2>
        <p>Python is a popular programming language. It was created by Guido van Rossum, and released in 1991.</p>
        <p>In this tutorial, you will learn:</p>
        <ul>
            <li>Python Basics and Syntax</li>
            <li>Data Structures (Lists, Tuples, Sets, Dictionaries)</li>
            <li>Functions and Modules</li>
            <li>Object-Oriented Programming</li>
            <li>Exception Handling</li>
            <li>And much more!</li>
        </ul>
        <p>Select a topic from the left sidebar to start learning.</p>
    `,

    intro: `
        <h2>Python Introduction</h2>
        <p>Python is a high-level, interpreted, interactive and object-oriented scripting language.</p>
        <h3>Why Learn Python?</h3>
        <ul>
            <li><strong>Easy to Learn:</strong> Simple and readable syntax</li>
            <li><strong>Versatile:</strong> Web development, data science, AI, automation</li>
            <li><strong>Large Community:</strong> Extensive libraries and frameworks</li>
            <li><strong>Cross-platform:</strong> Works on Windows, Mac, Linux</li>
            <li><strong>Open Source:</strong> Free to use and distribute</li>
        </ul>
        <h3>Applications of Python:</h3>
        <ul>
            <li>Web Development (Django, Flask)</li>
            <li>Data Science and Machine Learning</li>
            <li>Automation and Scripting</li>
            <li>Desktop GUI Applications</li>
            <li>Game Development</li>
            <li>Scientific Computing</li>
        </ul>
    `,

    syntax: `
        <h2>Python Syntax</h2>
        <p>Python syntax is designed to be readable and straightforward.</p>
        <h3>Hello World Program:</h3>
        <pre><code>print("Hello, World!")</code></pre>
        
        <h3>Key Features:</h3>
        <ul>
            <li><strong>Indentation:</strong> Python uses indentation to define code blocks</li>
            <li><strong>No Semicolons:</strong> Line endings don't need semicolons</li>
            <li><strong>Case Sensitive:</strong> Variables and function names are case-sensitive</li>
            <li><strong>Comments:</strong> Use # for single-line comments</li>
        </ul>
        
        <h3>Example:</h3>
        <pre><code># This is a comment
if 5 > 2:
    print("Five is greater than two!")  # Indentation is important</code></pre>
    `,

    variables: `
        <h2>Python Variables</h2>
        <p>Variables are containers for storing data values. Python has no command for declaring a variable.</p>
        <h3>Creating Variables:</h3>
        <pre><code>x = 5           # Integer
y = "Hello"     # String
z = 3.14        # Float
is_valid = True # Boolean</code></pre>
        
        <h3>Variable Names:</h3>
        <ul>
            <li>Must start with a letter or underscore</li>
            <li>Can only contain alpha-numeric characters and underscores</li>
            <li>Case-sensitive (age, Age, and AGE are different)</li>
        </ul>
        
        <h3>Multiple Assignment:</h3>
        <pre><code>x, y, z = "Orange", "Banana", "Cherry"
print(x)  # Orange
print(y)  # Banana
print(z)  # Cherry

# Same value to multiple variables
a = b = c = "Apple"</code></pre>
        
        <h3>Variable Types:</h3>
        <pre><code>x = 5
print(type(x))  # &lt;class 'int'&gt;

y = "Hello"
print(type(y))  # &lt;class 'str'&gt;</code></pre>
    `,

    datatypes: `
        <h2>Python Data Types</h2>
        <p>Python has various data types built-in by default.</p>
        <h3>Common Data Types:</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>Type</th>
                <th>Example</th>
                <th>Description</th>
            </tr>
            <tr>
                <td>str</td>
                <td>"Hello"</td>
                <td>Text/String</td>
            </tr>
            <tr>
                <td>int</td>
                <td>20</td>
                <td>Integer number</td>
            </tr>
            <tr>
                <td>float</td>
                <td>20.5</td>
                <td>Decimal number</td>
            </tr>
            <tr>
                <td>bool</td>
                <td>True</td>
                <td>Boolean</td>
            </tr>
            <tr>
                <td>list</td>
                <td>["apple", "banana"]</td>
                <td>Ordered, mutable collection</td>
            </tr>
            <tr>
                <td>tuple</td>
                <td>("apple", "banana")</td>
                <td>Ordered, immutable collection</td>
            </tr>
            <tr>
                <td>set</td>
                <td>{"apple", "banana"}</td>
                <td>Unordered, unique elements</td>
            </tr>
            <tr>
                <td>dict</td>
                <td>{"name": "John", "age": 36}</td>
                <td>Key-value pairs</td>
            </tr>
        </table>
        
        <h3>Type Conversion:</h3>
        <pre><code>x = 1    # int
y = 2.8  # float
z = "3"  # str

a = float(x)  # Convert to float
b = int(y)    # Convert to int
c = str(x)    # Convert to string</code></pre>
    `,

    numbers: `
        <h2>Python Numbers</h2>
        <p>There are three numeric types in Python: int, float, and complex.</p>
        <h3>Integer (int):</h3>
        <pre><code>x = 1
y = 35656222554887711
z = -3255522</code></pre>
        
        <h3>Float:</h3>
        <pre><code>x = 1.10
y = 1.0
z = -35.59</code></pre>
        
        <h3>Complex:</h3>
        <pre><code>x = 3+5j
y = 5j
z = -5j</code></pre>
        
        <h3>Type Conversion:</h3>
        <pre><code>x = 1    # int
y = 2.8  # float
z = 1j   # complex

# Convert from int to float
a = float(x)

# Convert from float to int
b = int(y)

# Convert from int to complex
c = complex(x)</code></pre>
        
        <h3>Random Number:</h3>
        <pre><code>import random
print(random.randrange(1, 10))  # Random number between 1 and 10</code></pre>
    `,

    strings: `
        <h2>Python Strings</h2>
        <p>Strings in Python are surrounded by either single or double quotation marks.</p>
        <h3>String Creation:</h3>
        <pre><code>a = "Hello"
b = 'Hello'
# Multiline strings
c = """Lorem ipsum dolor sit amet,
consectetur adipiscing elit"""</code></pre>
        
        <h3>String Operations:</h3>
        <pre><code># Length
a = "Hello, World!"
print(len(a))  # 13

# Check if character exists
print("free" in a)  # False
print("World" in a)  # True

# Slicing
print(a[2:5])  # llo

# Upper/Lower case
print(a.upper())  # HELLO, WORLD!
print(a.lower())  # hello, world!

# Replace
print(a.replace("H", "J"))  # Jello, World!

# Split
print(a.split(","))  # ['Hello', ' World!']</code></pre>
        
        <h3>String Concatenation:</h3>
        <pre><code>a = "Hello"
b = "World"
c = a + " " + b
print(c)  # Hello World</code></pre>
        
        <h3>String Formatting:</h3>
        <pre><code># f-strings (Python 3.6+)
name = "John"
age = 36
txt = f"My name is {name} and I am {age}"
print(txt)</code></pre>
    `,

    operators: `
        <h2>Python Operators</h2>
        <p>Operators are used to perform operations on variables and values.</p>
        <h3>1. Arithmetic Operators:</h3>
        <pre><code>+ (Addition)        5 + 3 = 8
- (Subtraction)     5 - 3 = 2
* (Multiplication)  5 * 3 = 15
/ (Division)        5 / 3 = 1.666...
% (Modulus)         5 % 3 = 2
** (Exponentiation) 5 ** 3 = 125
// (Floor division) 5 // 3 = 1</code></pre>
        
        <h3>2. Comparison Operators:</h3>
        <pre><code>== (Equal)                  x == y
!= (Not equal)              x != y
> (Greater than)            x > y
< (Less than)               x < y
>= (Greater than or equal)  x >= y
<= (Less than or equal)     x <= y</code></pre>
        
        <h3>3. Logical Operators:</h3>
        <pre><code>and (Returns True if both are true)    x > 3 and x < 10
or  (Returns True if one is true)      x < 5 or x > 10
not (Reverse the result)               not(x > 3 and x < 10)</code></pre>
        
        <h3>4. Assignment Operators:</h3>
        <pre><code>=   (Assign)            x = 5
+=  (Add and assign)    x += 3  # x = x + 3
-=  (Subtract)          x -= 3
*=  (Multiply)          x *= 3
/=  (Divide)            x /= 3</code></pre>
    `,

    lists: `
        <h2>Python Lists</h2>
        <p>Lists are used to store multiple items in a single variable. Lists are ordered, changeable, and allow duplicates.</p>
        <h3>Creating Lists:</h3>
        <pre><code>mylist = ["apple", "banana", "cherry"]
print(mylist)

# List with different types
list1 = ["abc", 34, True, 40, "male"]</code></pre>
        
        <h3>Accessing Items:</h3>
        <pre><code>thislist = ["apple", "banana", "cherry"]
print(thislist[1])   # banana
print(thislist[-1])  # cherry (last item)
print(thislist[1:3]) # ['banana', 'cherry']</code></pre>
        
        <h3>Modifying Lists:</h3>
        <pre><code>thislist = ["apple", "banana", "cherry"]
thislist[1] = "blackcurrant"  # Change item
thislist.append("orange")     # Add item
thislist.insert(1, "lemon")   # Insert at position
thislist.remove("banana")     # Remove specific item
thislist.pop(1)               # Remove by index
del thislist[0]               # Delete by index
thislist.clear()              # Empty the list</code></pre>
        
        <h3>List Methods:</h3>
        <pre><code>append()  # Add element at the end
extend()  # Add elements from another list
insert()  # Add element at specified position
remove()  # Remove specified item
pop()     # Remove element at specified position
clear()   # Remove all elements
sort()    # Sort the list
reverse() # Reverse the list order
copy()    # Return a copy of the list</code></pre>
    `,

    tuples: `
        <h2>Python Tuples</h2>
        <p>Tuples are used to store multiple items in a single variable. Tuples are ordered and unchangeable.</p>
        <h3>Creating Tuples:</h3>
        <pre><code>mytuple = ("apple", "banana", "cherry")
print(mytuple)

# Tuple with one item (need comma)
thistuple = ("apple",)</code></pre>
        
        <h3>Accessing Items:</h3>
        <pre><code>thistuple = ("apple", "banana", "cherry")
print(thistuple[1])   # banana
print(thistuple[-1])  # cherry
print(thistuple[1:3]) # ('banana', 'cherry')</code></pre>
        
        <h3>Updating Tuples:</h3>
        <pre><code># Tuples are unchangeable, but you can convert to list
x = ("apple", "banana", "cherry")
y = list(x)
y[1] = "kiwi"
x = tuple(y)
print(x)  # ('apple', 'kiwi', 'cherry')</code></pre>
        
        <h3>Unpacking Tuples:</h3>
        <pre><code>fruits = ("apple", "banana", "cherry")
(green, yellow, red) = fruits
print(green)   # apple
print(yellow)  # banana
print(red)     # cherry</code></pre>
        
        <h3>Tuple Methods:</h3>
        <pre><code>count()  # Returns the number of times a value occurs
index()  # Searches for a value and returns its position</code></pre>
    `,

    sets: `
        <h2>Python Sets</h2>
        <p>Sets are used to store multiple items in a single variable. Sets are unordered, unindexed, and do not allow duplicates.</p>
        <h3>Creating Sets:</h3>
        <pre><code>myset = {"apple", "banana", "cherry"}
print(myset)

# Duplicates are ignored
myset = {"apple", "banana", "cherry", "apple"}
print(myset)  # {'banana', 'cherry', 'apple'}</code></pre>
        
        <h3>Accessing Items:</h3>
        <pre><code># You cannot access items by index, but you can loop
thisset = {"apple", "banana", "cherry"}
for x in thisset:
    print(x)

# Check if exists
print("banana" in thisset)  # True</code></pre>
        
        <h3>Adding Items:</h3>
        <pre><code>thisset = {"apple", "banana", "cherry"}
thisset.add("orange")
print(thisset)

# Add multiple items
thisset.update(["mango", "grapes"])</code></pre>
        
        <h3>Removing Items:</h3>
        <pre><code>thisset = {"apple", "banana", "cherry"}
thisset.remove("banana")  # Error if not exists
thisset.discard("apple")  # No error if not exists
thisset.pop()             # Remove random item
thisset.clear()           # Empty the set</code></pre>
        
        <h3>Set Operations:</h3>
        <pre><code>set1 = {"a", "b", "c"}
set2 = {"c", "d", "e"}

# Union
set3 = set1.union(set2)  # {'a', 'b', 'c', 'd', 'e'}

# Intersection
set3 = set1.intersection(set2)  # {'c'}

# Difference
set3 = set1.difference(set2)  # {'a', 'b'}</code></pre>
    `,

    dictionaries: `
        <h2>Python Dictionaries</h2>
        <p>Dictionaries are used to store data values in key:value pairs. Dictionaries are ordered, changeable, and do not allow duplicates.</p>
        <h3>Creating Dictionaries:</h3>
        <pre><code>thisdict = {
    "brand": "Ford",
    "model": "Mustang",
    "year": 1964
}
print(thisdict)</code></pre>
        
        <h3>Accessing Items:</h3>
        <pre><code>thisdict = {
    "brand": "Ford",
    "model": "Mustang",
    "year": 1964
}

x = thisdict["model"]  # Mustang
x = thisdict.get("model")  # Mustang

# Get all keys
x = thisdict.keys()

# Get all values
x = thisdict.values()

# Get all items
x = thisdict.items()</code></pre>
        
        <h3>Modifying Dictionaries:</h3>
        <pre><code>thisdict = {
    "brand": "Ford",
    "model": "Mustang",
    "year": 1964
}

# Update value
thisdict["year"] = 2020

# Add new item
thisdict["color"] = "red"

# Remove item
thisdict.pop("model")
del thisdict["year"]</code></pre>
        
        <h3>Looping Through Dictionary:</h3>
        <pre><code># Print all keys
for x in thisdict:
    print(x)

# Print all values
for x in thisdict:
    print(thisdict[x])

# Print keys and values
for x, y in thisdict.items():
    print(x, y)</code></pre>
    `,

    conditions: `
        <h2>Python If...Else</h2>
        <p>Python supports the usual logical conditions from mathematics.</p>
        <h3>If Statement:</h3>
        <pre><code>a = 33
b = 200
if b > a:
    print("b is greater than a")</code></pre>
        
        <h3>Elif:</h3>
        <pre><code>a = 33
b = 33
if b > a:
    print("b is greater than a")
elif a == b:
    print("a and b are equal")</code></pre>
        
        <h3>Else:</h3>
        <pre><code>a = 200
b = 33
if b > a:
    print("b is greater than a")
elif a == b:
    print("a and b are equal")
else:
    print("a is greater than b")</code></pre>
        
        <h3>Short Hand If:</h3>
        <pre><code>if a > b: print("a is greater than b")</code></pre>
        
        <h3>Ternary Operator:</h3>
        <pre><code>a = 2
b = 330
print("A") if a > b else print("B")</code></pre>
        
        <h3>Logical Operators:</h3>
        <pre><code>a = 200
b = 33
c = 500

# And
if a > b and c > a:
    print("Both conditions are True")

# Or
if a > b or a > c:
    print("At least one condition is True")

# Not
if not a > b:
    print("a is NOT greater than b")</code></pre>
    `,

    loops: `
        <h2>Python Loops</h2>
        <p>Python has two primitive loop commands: while loops and for loops.</p>
        <h3>While Loop:</h3>
        <pre><code>i = 1
while i < 6:
    print(i)
    i += 1</code></pre>
        
        <h3>While with Break:</h3>
        <pre><code>i = 1
while i < 6:
    print(i)
    if i == 3:
        break
    i += 1</code></pre>
        
        <h3>While with Continue:</h3>
        <pre><code>i = 0
while i < 6:
    i += 1
    if i == 3:
        continue
    print(i)</code></pre>
        
        <h3>For Loop:</h3>
        <pre><code># Loop through a list
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    print(x)

# Loop through a string
for x in "banana":
    print(x)

# Range
for x in range(6):
    print(x)  # 0 to 5

for x in range(2, 6):
    print(x)  # 2 to 5

for x in range(2, 30, 3):
    print(x)  # 2, 5, 8, 11, 14, 17, 20, 23, 26, 29</code></pre>
        
        <h3>Nested Loops:</h3>
        <pre><code>adj = ["red", "big", "tasty"]
fruits = ["apple", "banana", "cherry"]

for x in adj:
    for y in fruits:
        print(x, y)</code></pre>
    `,

    functions: `
        <h2>Python Functions</h2>
        <p>A function is a block of code which only runs when it is called.</p>
        <h3>Creating a Function:</h3>
        <pre><code>def my_function():
    print("Hello from a function")

# Call the function
my_function()</code></pre>
        
        <h3>Arguments:</h3>
        <pre><code>def my_function(fname):
    print(fname + " Refsnes")

my_function("Emil")
my_function("Tobias")
my_function("Linus")</code></pre>
        
        <h3>Multiple Arguments:</h3>
        <pre><code>def my_function(fname, lname):
    print(fname + " " + lname)

my_function("Emil", "Refsnes")</code></pre>
        
        <h3>Default Parameter:</h3>
        <pre><code>def my_function(country = "Norway"):
    print("I am from " + country)

my_function("Sweden")
my_function()  # Uses default value</code></pre>
        
        <h3>Return Values:</h3>
        <pre><code>def my_function(x):
    return 5 * x

print(my_function(3))  # 15
print(my_function(5))  # 25</code></pre>
        
        <h3>Keyword Arguments:</h3>
        <pre><code>def my_function(child3, child2, child1):
    print("The youngest child is " + child3)

my_function(child1 = "Emil", child2 = "Tobias", child3 = "Linus")</code></pre>
        
        <h3>Arbitrary Arguments (*args):</h3>
        <pre><code>def my_function(*kids):
    print("The youngest child is " + kids[2])

my_function("Emil", "Tobias", "Linus")</code></pre>
    `,

    lambda: `
        <h2>Python Lambda</h2>
        <p>A lambda function is a small anonymous function. It can take any number of arguments but can only have one expression.</p>
        <h3>Syntax:</h3>
        <pre><code>lambda arguments : expression</code></pre>
        
        <h3>Basic Example:</h3>
        <pre><code>x = lambda a : a + 10
print(x(5))  # 15

# Multiple arguments
x = lambda a, b : a * b
print(x(5, 6))  # 30

x = lambda a, b, c : a + b + c
print(x(5, 6, 2))  # 13</code></pre>
        
        <h3>Why Use Lambda?</h3>
        <pre><code>def myfunc(n):
    return lambda a : a * n

mydoubler = myfunc(2)
mytripler = myfunc(3)

print(mydoubler(11))  # 22
print(mytripler(11))  # 33</code></pre>
        
        <h3>Lambda with map():</h3>
        <pre><code>numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
print(squared)  # [1, 4, 9, 16, 25]</code></pre>
        
        <h3>Lambda with filter():</h3>
        <pre><code>numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)  # [2, 4, 6, 8, 10]</code></pre>
    `,

    modules: `
        <h2>Python Modules</h2>
        <p>A module is a file containing Python code. It can define functions, classes, and variables.</p>
        <h3>Creating a Module:</h3>
        <pre><code># Save this as mymodule.py
def greeting(name):
    print("Hello, " + name)</code></pre>
        
        <h3>Using a Module:</h3>
        <pre><code>import mymodule

mymodule.greeting("Jonathan")</code></pre>
        
        <h3>Module with Variables:</h3>
        <pre><code># mymodule.py
person1 = {
    "name": "John",
    "age": 36,
    "country": "Norway"
}

# Use the module
import mymodule
a = mymodule.person1["age"]
print(a)  # 36</code></pre>
        
        <h3>Renaming a Module:</h3>
        <pre><code>import mymodule as mx
a = mx.person1["age"]</code></pre>
        
        <h3>Import Specific Parts:</h3>
        <pre><code>from mymodule import person1
print(person1["age"])</code></pre>
        
        <h3>Built-in Modules:</h3>
        <pre><code># Platform module
import platform
x = platform.system()
print(x)

# Math module
import math
print(math.pi)
print(math.sqrt(64))

# Random module
import random
print(random.randint(1, 10))

# Datetime module
import datetime
x = datetime.datetime.now()
print(x)</code></pre>
    `,

    classes: `
        <h2>Python Classes and Objects</h2>
        <p>Python is an object-oriented programming language. A class is like a blueprint for creating objects.</p>
        <h3>Creating a Class:</h3>
        <pre><code>class MyClass:
    x = 5

# Create object
p1 = MyClass()
print(p1.x)  # 5</code></pre>
        
        <h3>The __init__() Function:</h3>
        <pre><code>class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

p1 = Person("John", 36)
print(p1.name)  # John
print(p1.age)   # 36</code></pre>
        
        <h3>Object Methods:</h3>
        <pre><code>class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def myfunc(self):
        print("Hello my name is " + self.name)

p1 = Person("John", 36)
p1.myfunc()  # Hello my name is John</code></pre>
        
        <h3>The self Parameter:</h3>
        <pre><code># self refers to the current instance of the class
# It doesn't have to be named "self"
class Person:
    def __init__(mysillyobject, name, age):
        mysillyobject.name = name
        mysillyobject.age = age
    
    def myfunc(abc):
        print("Hello my name is " + abc.name)</code></pre>
        
        <h3>Modify Object Properties:</h3>
        <pre><code>p1 = Person("John", 36)
p1.age = 40
print(p1.age)  # 40

# Delete property
del p1.age

# Delete object
del p1</code></pre>
    `,

    inheritance: `
        <h2>Python Inheritance</h2>
        <p>Inheritance allows us to define a class that inherits all methods and properties from another class.</p>
        <h3>Parent Class:</h3>
        <pre><code>class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname
    
    def printname(self):
        print(self.firstname, self.lastname)</code></pre>
        
        <h3>Child Class:</h3>
        <pre><code>class Student(Person):
    pass

# Use the child class
x = Student("Mike", "Olsen")
x.printname()  # Mike Olsen</code></pre>
        
        <h3>Child Class with __init__():</h3>
        <pre><code>class Student(Person):
    def __init__(self, fname, lname):
        Person.__init__(self, fname, lname)</code></pre>
        
        <h3>Using super():</h3>
        <pre><code>class Student(Person):
    def __init__(self, fname, lname):
        super().__init__(fname, lname)</code></pre>
        
        <h3>Add Properties:</h3>
        <pre><code>class Student(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)
        self.graduationyear = year

x = Student("Mike", "Olsen", 2019)
print(x.graduationyear)  # 2019</code></pre>
        
        <h3>Add Methods:</h3>
        <pre><code>class Student(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)
        self.graduationyear = year
    
    def welcome(self):
        print("Welcome", self.firstname, self.lastname, 
              "to the class of", self.graduationyear)

x = Student("Mike", "Olsen", 2019)
x.welcome()</code></pre>
    `,

    exceptions: `
        <h2>Python Exception Handling</h2>
        <p>The try block lets you test a block of code for errors. The except block lets you handle the error.</p>
        <h3>Try...Except:</h3>
        <pre><code>try:
    print(x)
except:
    print("An exception occurred")</code></pre>
        
        <h3>Multiple Exceptions:</h3>
        <pre><code>try:
    print(x)
except NameError:
    print("Variable x is not defined")
except:
    print("Something else went wrong")</code></pre>
        
        <h3>Else:</h3>
        <pre><code>try:
    print("Hello")
except:
    print("Something went wrong")
else:
    print("Nothing went wrong")</code></pre>
        
        <h3>Finally:</h3>
        <pre><code>try:
    print(x)
except:
    print("Something went wrong")
finally:
    print("The 'try except' is finished")</code></pre>
        
        <h3>Raise an Exception:</h3>
        <pre><code>x = -1
if x < 0:
    raise Exception("Sorry, no numbers below zero")

# Raise specific error type
x = "hello"
if not type(x) is int:
    raise TypeError("Only integers are allowed")</code></pre>
        
        <h3>Common Exceptions:</h3>
        <ul>
            <li><code>NameError</code> - Variable not defined</li>
            <li><code>TypeError</code> - Wrong data type</li>
            <li><code>ValueError</code> - Wrong value</li>
            <li><code>IndexError</code> - Index out of range</li>
            <li><code>KeyError</code> - Key not found in dictionary</li>
            <li><code>FileNotFoundError</code> - File doesn't exist</li>
            <li><code>ZeroDivisionError</code> - Division by zero</li>
        </ul>
    `
};

// Navigation functionality
let currentTopicIndex = 0;
const topicKeys = Array.from(topics).map(t => t.getAttribute("data-topic"));

function loadTopic(index) {
    if (index < 0 || index >= topicKeys.length) return;
    currentTopicIndex = index;

    // Update active class
    topics.forEach((t, i) => {
        if (i === index) t.classList.add("active");
        else t.classList.remove("active");
    });

    // Update Content
    const key = topicKeys[index];
    pageTitle.textContent = topics[index].textContent;
    content.innerHTML = topicData[key];

    // Update Buttons State
    if (prevBtn) {
        prevBtn.disabled = index === 0;
        prevBtn.style.opacity = index === 0 ? "0.5" : "1";
        prevBtn.style.cursor = index === 0 ? "not-allowed" : "pointer";
    }

    if (nextBtn) {
        nextBtn.disabled = index === topicKeys.length - 1;
        nextBtn.style.opacity = index === topicKeys.length - 1 ? "0.5" : "1";
        nextBtn.style.cursor = index === topicKeys.length - 1 ? "not-allowed" : "pointer";
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Event Listeners
if (prevBtn) {
    prevBtn.addEventListener("click", () => {
        loadTopic(currentTopicIndex - 1);
    });
}

if (nextBtn) {
    nextBtn.addEventListener("click", () => {
        loadTopic(currentTopicIndex + 1);
    });
}

topics.forEach((item, index) => {
    item.addEventListener("click", () => {
        loadTopic(index);
    });
});

// Mobile Menu Toggle
const menuToggle = document.getElementById("menuToggle");
const sidebar = document.querySelector(".tutorial-sidebar");

if (menuToggle && sidebar) {
    menuToggle.addEventListener("click", () => {
        sidebar.classList.toggle("active");
        menuToggle.innerText = sidebar.classList.contains("active") ? "✕" : "☰";
    });

    // Close sidebar when clicking a topic on mobile
    topics.forEach(item => {
        item.addEventListener("click", () => {
            if (window.innerWidth <= 1024) {
                sidebar.classList.remove("active");
                menuToggle.innerText = "☰";
            }
        });
    });
}

// Load first topic
loadTopic(0);
