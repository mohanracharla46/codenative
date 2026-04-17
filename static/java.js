const topics = document.querySelectorAll(".topic");
const content = document.getElementById("topicContent");
const pageTitle = document.getElementById("pageTitle");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");

const topicData = {
    home: `
        <h2>Welcome to Java Tutorial</h2>
        <p>Java is a high-level, class-based, object-oriented programming language that is designed to have as few implementation dependencies as possible.</p>
        <p>In this tutorial, you will learn:</p>
        <ol>
        <li>Java Home</li>
        <li>Java Introduction</li>
        <li>Java Syntax</li>
        <li>Java Variables</li>
        <li>Java Data Types</li>
        <li>Java Operators</li>
        <li>Java Strings</li>
        <li>Java Math</li>
        <li>Java If...Else</li>
        <li>Java Switch</li>
        <li>Java Loops</li>
        <li>Java Arrays</li>
        <li>Java Methods</li>
        <li>Java OOP</li>
        <li>Java Classes</li>
        <li>Java Inheritance</li>
        <li>Java Polimorphism</li>
        <li>Java Encapsulation</li>
        <li>Java Abstrsction</li>
    </ol>
        <p>Select a topic from the left sidebar to start learning.</p>
    `,

    intro: `
        <div class="intro">
        <h1>Java Introduction</h1>
        <p>
            Java oka powerful mariyu popular <b>programming language</b>.
            Ee language ni mainly large-scale applications,
            web applications, mobile apps mariyu enterprise systems
            develop cheyadaniki use chestaru.
        </p>
        <p>
            Java beginner-friendly kabatti students mariyu
            professionals rendu categories ki suitable ga untundi.
            Java nerchukunte manchi career opportunities untayi.
        </p>
    </div>

    <!-- What is Java -->
    <div class="intro">
        <h2>Java ante enti?</h2>
        <p>
            Java oka <b>high-level, object-oriented programming language</b>.
            Java ni <b>Sun Microsystems</b> develop chesindi,
            ippudu <b>Oracle Corporation</b> maintain chestundi.
        </p>
        <p>
            Java chala secure, portable mariyu powerful language kabatti
            web applications, mobile apps, desktop software mariyu
            enterprise systems lo wide ga use chestaru.
        </p>
    </div>

    <!-- Why Java -->
    <div class="intro">
        <h2>Java enduku popular?</h2>
        <ul>
            <li><b>Easy to Learn:</b> Java syntax simple ga untundi.</li>
            <li><b>Platform Independent:</b> Write Once, Run Anywhere.</li>
            <li><b>Object-Oriented:</b> Classes and Objects use chestundi.</li>
            <li><b>Secure:</b> Direct memory access ledu.</li>
            <li><b>Robust:</b> Strong exception handling untundi.</li>
            <li><b>Multithreaded:</b> Multiple tasks okesari run cheyochu.</li>
        </ul>
    </div>

    <!-- Working of Java -->
    <div class="intro">
        <h2>Java ela work avtundi?</h2>
        <ol>
            <li>Manam Java source code (.java file) rasthamu</li>
            <li>Java Compiler (javac) bytecode ga convert chestundi</li>
            <li>JVM (Java Virtual Machine) ee bytecode ni execute chestundi</li>
        </ol>
    </div>

    <!-- First Program -->
    <div class="intro">
        <h2>First Java Program</h2>
        <div class="code-box">
class Main { <br>
&nbsp;&nbsp;public static void main(String[] args) { <br>
&nbsp;&nbsp;&nbsp;&nbsp;System.out.println("Hello Java"); <br>
&nbsp;&nbsp;} <br>
}
        </div>
    </div>

    <!-- Career -->
    <div class="intro">
        <h2>Java nerchukunte em opportunities untayi?</h2>
        <p>
            Java nerchukunte <strong>Software Developer</strong>, <strong>Backend Developer</strong>,
            <strong>Android Developer</strong>, <strong>Full Stack Developer</strong> laga
            chala career opportunities untayi.
        </p>
    </div>
    <div class="intro">
        <h2>Practice:</h2>
        <ol>
        <li>Write a Java Program to Print Hello World.</li>
        <li>Write a Java program to print Your Name.</li>
        <li>Write a Java program to Print Your Address.</li>
        </ol>
    </div>

    `,

    syntax: `
        <div class="intro">
        <h1>Java Syntax</h1>
        <p>
            Java Syntax ante Java program ela rayali ane rules ni cheptundi.
            Java program correct ga run avvalante syntax correct ga undali.
        </p>
        <p>
            Java syntax simple ga untundi kabatti beginners easy ga
            Java programs write cheyagalru.
        </p>
    </div>

    <!-- Basic Structure -->
    <div class="intro">
        <h2>Java Program Basic Structure</h2>
        <p>
            Oka Java program lo mandatory ga
            <b>class</b> mariyu <b>main method</b> undali.
        </p>

        <div class="code-box">
class MyProgram { <br>
&nbsp;&nbsp;public static void main(String[] args) { <br>
&nbsp;&nbsp;&nbsp;&nbsp;// Code execution start avuthundi ikkada <br>
&nbsp;&nbsp;} <br>
}
        </div>
    </div>

    <!-- Class Explanation -->
    <div class="intro">
        <h2>Class</h2>
        <p>
            Java lo anni programs <b>class</b> lopale rayali.
            Class anedi objects create cheyadaniki blueprint laga untundi.
        </p>
    </div>

    <!-- Main Method -->
    <div class="intro">
        <h2>Main Method</h2>
        <p>
            <b>main()</b> method anedi program execution start ayye entry point.
            JVM first ga main method ni search chestundi.
        </p>
        <p>
            Syntax:
        </p>

        <div class="code-box">
public static void main(String[] args)
        </div>

        <ul>
            <li><b>public</b> – JVM ki accessible ga untundi</li>
            <li><b>static</b> – object create cheyakunda run avvadaniki</li>
            <li><b>void</b> – return value ledu</li>
            <li><b>String[] args</b> – command line arguments kosam</li>
        </ul>
    </div>

    <!-- Statements -->
    <div class="intro">
        <h2>Java Statements</h2>
        <p>
            Java lo prathi statement <b>semicolon (;)</b> tho end avvali.
            Semicolon lekapothe compile-time error vastundi.
        </p>

        <div class="code-box">
System.out.println("Hello Java");
        </div>
    </div>

    <!-- Case Sensitivity -->
    <div class="intro">
        <h2>Case Sensitivity</h2>
        <p>
            Java <b>case-sensitive</b> language.
            Ante capital letters mariyu small letters different.
        </p>
        <p>
            Example: <b>main</b> and <b>Main</b> same kadu.
        </p>
    </div>

    <!-- Comments -->
    <div class="intro">
        <h2>Java Comments</h2>
        <p>
            Comments anedi code explain cheyadaniki use chestaru.
            JVM comments ni ignore chestundi.
        </p>

        <div class="code-box">
// Single-line comment <br>
/* Multi-line <br>
&nbsp;&nbsp;comment */
        </div>
    </div>
    `,

    variables: `
        <h2>Java Variables</h2>
        <p>Variables are containers for storing data values.</p>
        <h3>Types of Variables:</h3>
        <ul>
            <li><strong>Local Variables:</strong> Declared inside methods</li>
            <li><strong>Instance Variables:</strong> Declared inside class but outside methods</li>
            <li><strong>Static Variables:</strong> Declared with static keyword</li>
        </ul>
        <h3>Variable Declaration:</h3>
        <pre><code>int age = 25;
String name = "John";
double salary = 50000.50;
boolean isActive = true;</code></pre>
        <h3>Rules for Naming Variables:</h3>
        <ul>
            <li>Must start with a letter, $ or _</li>
            <li>Cannot contain whitespace</li>
            <li>Case sensitive</li>
            <li>Cannot use Java keywords</li>
        </ul>
    `,

    datatypes: `
        <div class="intro">
    <h1>Java Data Types</h1>
    <p>
        Java lo data ni store cheyadaniki <b>Data Types</b> use chestaru.
        Prathi variable ki oka specific data type untundi.
    </p>
    <p>
        Java lo mainly <b>two categories of data types</b> unnayi.
    </p>
</div>

<!-- Primitive Data Types -->
<div class="intro">
    <h2>1. Primitive Data Types</h2>
    <p>
        Primitive data types anedi basic values ni store cheyadaniki use chestaru.
        Java lo total <b>8 primitive data types</b> unnayi.
    </p>

    <table style="width:100%; border-collapse: collapse;">
        <tr>
            <th>Type</th>
            <th>Size</th>
            <th>Description</th>
            <th>Example</th>
        </tr>
        <tr>
            <td>byte</td>
            <td>1 byte</td>
            <td>-128 to 127</td>
            <td>byte b = 100;</td>
        </tr>
        <tr>
            <td>short</td>
            <td>2 bytes</td>
            <td>-32,768 to 32,767</td>
            <td>short s = 5000;</td>
        </tr>
        <tr>
            <td>int</td>
            <td>4 bytes</td>
            <td>-2³¹ to 2³¹-1</td>
            <td>int i = 100000;</td>
        </tr>
        <tr>
            <td>long</td>
            <td>8 bytes</td>
            <td>-2⁶³ to 2⁶³-1</td>
            <td>long l = 15000000000L;</td>
        </tr>
        <tr>
            <td>float</td>
            <td>4 bytes</td>
            <td>Decimal numbers</td>
            <td>float f = 5.75f;</td>
        </tr>
        <tr>
            <td>double</td>
            <td>8 bytes</td>
            <td>Decimal numbers</td>
            <td>double d = 19.99d;</td>
        </tr>
        <tr>
            <td>boolean</td>
            <td>1 bit</td>
            <td>true or false</td>
            <td>boolean flag = true;</td>
        </tr>
        <tr>
            <td>char</td>
            <td>2 bytes</td>
            <td>Single character</td>
            <td>char c = 'A';</td>
        </tr>
    </table>
</div>

<!-- Reference Data Types -->
<div class="intro">
    <h2>2. Reference Data Types</h2>
    <p>
        Reference data types anedi objects ni store cheyadaniki use chestaru.
        Ee data types memory lo <b>reference address</b> ni store chestayi.
    </p>

    <ul>
        <li><b>String</b> – Text data store cheyadaniki</li>
        <li><b>Arrays</b> – Multiple values store cheyadaniki</li>
        <li><b>Classes</b> – User-defined data types</li>
        <li><b>Interfaces</b> – Abstraction achieve cheyadaniki</li>
    </ul>
    <b>Vitini anamu mundhu chandvkundhamu</b>
    <div class="intro">
    <h1>Java Variables</h1>
    <p>
        Java lo data ni store cheyadaniki <b>Variables</b> use chestaru.
        Variable anedi memory lo oka location, daniki oka value assign chestamu.
    </p>
    <p>
        Prathi variable ki <b>data type</b>, <b>name</b>, mariyu <b>value</b> untayi.
    </p>
</div>

<!-- Variable Declaration -->
<div class="intro">
    <h2>Variable Declaration</h2>
    <p>
        Java lo variable declare cheyadaniki first
        <b>data type</b> taruvata <b>variable name</b> rayali.
    </p>

    <pre class="code-box">
int age;
    </pre>

    <p>
        Value assign cheyadaniki:
    </p>

    <pre class="code-box">
age = 20;
    </pre>

    <p>
        Declaration mariyu initialization okesari kuda cheyochu:
    </p>

    <pre class="code-box">
int age = 20;
    </pre>
</div>

<!-- Types of Variables -->
<div class="intro">
    <h2>Types of Variables in Java</h2>
    <p>
        Java lo mainly <b>3 types of variables</b> unnayi.
    </p>

    <ul>
        <li><b>Local Variables</b></li>
        <li><b>Instance Variables</b></li>
        <li><b>Static Variables</b></li>
    </ul>
</div>

<!-- Local Variables -->
<div class="intro">
    <h2>1. Local Variables</h2>
    <p>
        Local variables anedi method lopala declare chestaru.
        Ee variables scope method lopale untundi.
    </p>

    <pre class="code-box">
void show() {
    int x = 10;   // local variable
}
    </pre>
</div>

<!-- Instance Variables -->
<div class="intro">
    <h2>2. Instance Variables</h2>
    <p>
        Instance variables anedi class lopala,
        kani method bayata declare chestaru.
        Prathi object ki separate copy untundi.
    </p>

    <pre class="code-box">
class Student {
    int id;       // instance variable
    String name;
}
    </pre>
</div>

<!-- Static Variables -->
<div class="intro">
    <h2>3. Static Variables</h2>
    <p>
        Static variables anedi <b>static</b> keyword tho declare chestaru.
        Ee variables class ki common ga untayi.
    </p>

    <pre class="code-box">
class College {
    static String collegeName = "ABC College";
}
    </pre>
</div>

<!-- Rules for Variables -->
<div class="intro">
    <h2>Rules for Naming Variables</h2>
    <ul>
        <li>Variable name letter tho start avvali</li>
        <li>Spaces allow kadu</li>
        <li>Keywords (int, class, public) use cheyakudadu</li>
        <li>Case-sensitive (age and Age different)</li>
    </ul>
</div>

<!-- Summary -->
<div class="intro">
    <h2>Summary</h2>
    <p>
        Java lo variables correct ga use cheyadam chala important.
        Variables data ni store cheyadaniki mariyu manipulate cheyadaniki use chestaru.
    </p>
</div>
<div class="intro">
    <h2>Practice</h2>
    <div class="intro">
    <h3>Problem 1: Print Student Details</h3>
    <p>
        Oka Java program rayandi.
        Student <b>name</b>, <b>roll number</b>, mariyu <b>age</b>
        ni variables lo store chesi print cheyyali.
    </p>
    <p><b>Hint:</b> String, int use cheyyandi.</p>
</div>

<!-- Problem 2 -->
<div class="intro">
    <h3>Problem 2: Add Two Numbers</h3>
    <p>
        Rendu integer numbers ni variables lo store chesi,
        vaati <b>sum</b> calculate chesi output print cheyyandi.
    </p>
    <p>
        <b>Example:</b><br>
        a = 10, b = 20 <br>
        Output: Sum = 30
    </p>
</div>

<!-- Problem 3 -->
<div class="intro">
    <h3>Problem 3: Area of a Rectangle</h3>
    <p>
        Rectangle <b>length</b> mariyu <b>breadth</b>
        ni variables lo store chesi area calculate cheyyandi.
    </p>
    <p>
        <b>Formula:</b><br>
        area = length × breadth
    </p>
</div>

<!-- Problem 4 -->
<div class="intro">
    <h3>Problem 4: Celsius to Fahrenheit</h3>
    <p>
        Oka temperature ni <b>Celsius</b> lo store chesi,
        adhi <b>Fahrenheit</b> lo convert cheyyandi.
    </p>
    <p>
        <b>Formula:</b><br>
        F = (C × 9/5) + 32
    </p>
</div>

<!-- Problem 5 -->
<div class="intro">
    <h3>Problem 5: Simple Interest</h2>
    <p>
        <b>Principal</b>, <b>Time</b>, mariyu <b>Rate</b>
        ni variables lo store chesi
        <b>Simple Interest</b> calculate cheyyandi.
    </p>
    <p>
        <b>Formula:</b><br>
        SI = (P × T × R) / 100
    </p>
</div>

</div>

`,

    operators: `
        <h2>Java Operators</h2>
        <p>Operators are used to perform operations on variables and values.</p>
        <h3>1. Arithmetic Operators:</h3>
        <pre><code>+ (Addition)
- (Subtraction)
* (Multiplication)
/ (Division)
% (Modulus)
++ (Increment)
-- (Decrement)</code></pre>
        
        <h3>2. Comparison Operators:</h3>
        <pre><code>== (Equal to)
!= (Not equal)
> (Greater than)
< (Less than)
>= (Greater than or equal to)
<= (Less than or equal to)</code></pre>
        
        <h3>3. Logical Operators:</h3>
        <pre><code>&& (Logical AND)
|| (Logical OR)
! (Logical NOT)</code></pre>
        
        <h3>4. Assignment Operators:</h3>
        <pre><code>= (Simple assignment)
+= (Add and assign)
-= (Subtract and assign)
*= (Multiply and assign)
/= (Divide and assign)</code></pre>
    `,

    strings: `
        <h2>Java Strings</h2>
        <p>Strings are used for storing text. A String in Java is an object.</p>
        <h3>String Creation:</h3>
        <pre><code>String greeting = "Hello World";
String name = new String("John");</code></pre>
        
        <h3>Common String Methods:</h3>
        <pre><code>length() - Returns the length of string
toUpperCase() - Converts to uppercase
toLowerCase() - Converts to lowercase
indexOf() - Returns position of first occurrence
substring() - Extracts substring
concat() - Concatenates strings
equals() - Compares two strings
charAt() - Returns character at index</code></pre>
        
        <h3>Example:</h3>
        <pre><code>String txt = "Hello World";
System.out.println(txt.length());        // 11
System.out.println(txt.toUpperCase());   // HELLO WORLD
System.out.println(txt.indexOf("World")); // 6</code></pre>
    `,

    math: `
        <h2>Java Math</h2>
        <p>The Math class allows you to perform mathematical tasks.</p>
        <h3>Common Math Methods:</h3>
        <pre><code>Math.max(x, y) - Returns the highest value
Math.min(x, y) - Returns the lowest value
Math.sqrt(x) - Returns square root
Math.abs(x) - Returns absolute value
Math.pow(x, y) - Returns x to the power of y
Math.random() - Returns random number (0 to 1)
Math.round(x) - Rounds to nearest integer
Math.floor(x) - Rounds down
Math.ceil(x) - Rounds up</code></pre>
        
        <h3>Example:</h3>
        <pre><code>System.out.println(Math.max(5, 10));    // 10
System.out.println(Math.sqrt(64));      // 8.0
System.out.println(Math.random());      // Random number
System.out.println(Math.pow(2, 3));     // 8.0</code></pre>
    `,

    conditions: `
        <h2>Java If...Else</h2>
        <p>Use if to specify a block of code to be executed if a condition is true.</p>
        <h3>Syntax:</h3>
        <pre><code>if (condition) {
    // block of code
} else if (condition) {
    // block of code
} else {
    // block of code
}</code></pre>
        
        <h3>Example:</h3>
        <pre><code>int age = 20;

if (age < 18) {
    System.out.println("Minor");
} else if (age >= 18 && age < 60) {
    System.out.println("Adult");
} else {
    System.out.println("Senior");
}</code></pre>
        
        <h3>Ternary Operator:</h3>
        <pre><code>int result = (age >= 18) ? 100 : 80;
System.out.println(result);</code></pre>
    `,

    switch: `
        <h2>Java Switch</h2>
        <p>The switch statement selects one of many code blocks to execute.</p>
        <h3>Syntax:</h3>
        <pre><code>switch(expression) {
    case x:
        // code block
        break;
    case y:
        // code block
        break;
    default:
        // code block
}</code></pre>
        
        <h3>Example:</h3>
        <pre><code>int day = 4;
switch (day) {
    case 1:
        System.out.println("Monday");
        break;
    case 2:
        System.out.println("Tuesday");
        break;
    case 3:
        System.out.println("Wednesday");
        break;
    case 4:
        System.out.println("Thursday");
        break;
    case 5:
        System.out.println("Friday");
        break;
    case 6:
        System.out.println("Saturday");
        break;
    case 7:
        System.out.println("Sunday");
        break;
    default:
        System.out.println("Invalid day");
}</code></pre>
    `,

    loops: `
        <h2>Java Loops</h2>
        <p>Loops can execute a block of code multiple times.</p>
        <h3>1. For Loop:</h3>
        <pre><code>for (int i = 0; i < 5; i++) {
    System.out.println(i);
}</code></pre>
        
        <h3>2. While Loop:</h3>
        <pre><code>int i = 0;
while (i < 5) {
    System.out.println(i);
    i++;
}</code></pre>
        
        <h3>3. Do-While Loop:</h3>
        <pre><code>int i = 0;
do {
    System.out.println(i);
    i++;
} while (i < 5);</code></pre>
        
        <h3>4. For-Each Loop:</h3>
        <pre><code>String[] cars = {"Volvo", "BMW", "Ford"};
for (String car : cars) {
    System.out.println(car);
}</code></pre>
        
        <h3>Loop Control:</h3>
        <ul>
            <li><code>break</code> - Exits the loop</li>
            <li><code>continue</code> - Skips current iteration</li>
        </ul>
    `,

    arrays: `
        <h2>Java Arrays</h2>
        <p>Arrays are used to store multiple values in a single variable.</p>
        <h3>Array Declaration:</h3>
        <pre><code>// Method 1
String[] cars = {"Volvo", "BMW", "Ford"};

// Method 2
int[] numbers = new int[5];
numbers[0] = 10;
numbers[1] = 20;</code></pre>
        
        <h3>Accessing Array Elements:</h3>
        <pre><code>String[] cars = {"Volvo", "BMW", "Ford"};
System.out.println(cars[0]);  // Volvo</code></pre>
        
        <h3>Array Length:</h3>
        <pre><code>String[] cars = {"Volvo", "BMW", "Ford"};
System.out.println(cars.length);  // 3</code></pre>
        
        <h3>Loop Through Array:</h3>
        <pre><code>String[] cars = {"Volvo", "BMW", "Ford"};
for (int i = 0; i < cars.length; i++) {
    System.out.println(cars[i]);
}</code></pre>
        
        <h3>Multidimensional Arrays:</h3>
        <pre><code>int[][] numbers = {
    {1, 2, 3, 4},
    {5, 6, 7}
};
System.out.println(numbers[0][2]);  // 3</code></pre>
    `,

    methods: `
        <h2>Java Methods</h2>
        <p>A method is a block of code which only runs when it is called.</p>
        <h3>Method Declaration:</h3>
        <pre><code>public static void myMethod() {
    System.out.println("I just got executed!");
}</code></pre>
        
        <h3>Calling a Method:</h3>
        <pre><code>public class Main {
    static void myMethod() {
        System.out.println("I just got executed!");
    }
    
    public static void main(String[] args) {
        myMethod();
    }
}</code></pre>
        
        <h3>Method with Parameters:</h3>
        <pre><code>static void greet(String name) {
    System.out.println("Hello " + name);
}

public static void main(String[] args) {
    greet("John");
    greet("Jane");
}</code></pre>
        
        <h3>Return Values:</h3>
        <pre><code>static int add(int x, int y) {
    return x + y;
}

public static void main(String[] args) {
    int result = add(5, 3);
    System.out.println(result);  // 8
}</code></pre>
        
        <h3>Method Overloading:</h3>
        <pre><code>static int add(int x, int y) {
    return x + y;
}

static double add(double x, double y) {
    return x + y;
}</code></pre>
    `,

    oop: `
        <h2>Java OOP (Object-Oriented Programming)</h2>
        <p>OOP is about creating objects that contain both data and methods.</p>
        <h3>Main Principles of OOP:</h3>
        <ul>
            <li><strong>Encapsulation:</strong> Bundling data and methods together</li>
            <li><strong>Inheritance:</strong> Creating new classes from existing ones</li>
            <li><strong>Polymorphism:</strong> Many forms of a single entity</li>
            <li><strong>Abstraction:</strong> Hiding complex implementation details</li>
        </ul>
        
        <h3>Advantages of OOP:</h3>
        <ul>
            <li>Code reusability</li>
            <li>Easier maintenance</li>
            <li>Better organization</li>
            <li>Modularity</li>
            <li>Security through data hiding</li>
        </ul>
        
        <h3>Basic Example:</h3>
        <pre><code>class Car {
    String color;
    int year;
    
    void drive() {
        System.out.println("The car is driving");
    }
}

public class Main {
    public static void main(String[] args) {
        Car myCar = new Car();
        myCar.color = "Red";
        myCar.year = 2020;
        myCar.drive();
    }
}</code></pre>
    `,

    classes: `
        <h2>Java Classes and Objects</h2>
        <p>A class is a template for objects, and an object is an instance of a class.</p>
        <h3>Creating a Class:</h3>
        <pre><code>public class Car {
    // Attributes (fields)
    String brand;
    String model;
    int year;
    
    // Constructor
    public Car(String brand, String model, int year) {
        this.brand = brand;
        this.model = model;
        this.year = year;
    }
    
    // Method
    public void displayInfo() {
        System.out.println(year + " " + brand + " " + model);
    }
}</code></pre>
        
        <h3>Creating Objects:</h3>
        <pre><code>public class Main {
    public static void main(String[] args) {
        Car car1 = new Car("Toyota", "Camry", 2020);
        Car car2 = new Car("Honda", "Civic", 2021);
        
        car1.displayInfo();  // 2020 Toyota Camry
        car2.displayInfo();  // 2021 Honda Civic
    }
}</code></pre>
        
        <h3>Access Modifiers:</h3>
        <ul>
            <li><code>public</code> - Accessible from anywhere</li>
            <li><code>private</code> - Only accessible within the class</li>
            <li><code>protected</code> - Accessible within package and subclasses</li>
            <li><code>default</code> - Accessible within package only</li>
        </ul>
    `,

    inheritance: `
        <h2>Java Inheritance</h2>
        <p>Inheritance allows a class to inherit attributes and methods from another class.</p>
        <h3>Syntax:</h3>
        <pre><code>class Vehicle {
    protected String brand = "Ford";
    
    public void honk() {
        System.out.println("Tuut, tuut!");
    }
}

class Car extends Vehicle {
    private String modelName = "Mustang";
    
    public void display() {
        System.out.println(brand + " " + modelName);
    }
}</code></pre>
        
        <h3>Using Inheritance:</h3>
        <pre><code>public class Main {
    public static void main(String[] args) {
        Car myCar = new Car();
        myCar.honk();      // From Vehicle class
        myCar.display();   // From Car class
    }
}</code></pre>
        
        <h3>Types of Inheritance:</h3>
        <ul>
            <li><strong>Single Inheritance:</strong> One class inherits from another</li>
            <li><strong>Multilevel Inheritance:</strong> Chain of inheritance</li>
            <li><strong>Hierarchical Inheritance:</strong> Multiple classes inherit from one class</li>
        </ul>
        
        <h3>The super Keyword:</h3>
        <pre><code>class Animal {
    void eat() {
        System.out.println("Eating...");
    }
}

class Dog extends Animal {
    void eat() {
        super.eat();  // Calls parent method
        System.out.println("Eating bones...");
    }
}</code></pre>
    `,

    polymorphism: `
        <h2>Java Polymorphism</h2>
        <p>Polymorphism means "many forms", allowing us to perform a single action in different ways.</p>
        <h3>1. Method Overriding (Runtime Polymorphism):</h3>
        <pre><code>class Animal {
    public void sound() {
        System.out.println("Animal makes a sound");
    }
}

class Dog extends Animal {
    public void sound() {
        System.out.println("Dog barks");
    }
}

class Cat extends Animal {
    public void sound() {
        System.out.println("Cat meows");
    }
}

public class Main {
    public static void main(String[] args) {
        Animal myAnimal = new Animal();
        Animal myDog = new Dog();
        Animal myCat = new Cat();
        
        myAnimal.sound();  // Animal makes a sound
        myDog.sound();     // Dog barks
        myCat.sound();     // Cat meows
    }
}</code></pre>
        
        <h3>2. Method Overloading (Compile-time Polymorphism):</h3>
        <pre><code>class Calculator {
    int add(int a, int b) {
        return a + b;
    }
    
    int add(int a, int b, int c) {
        return a + b + c;
    }
    
    double add(double a, double b) {
        return a + b;
    }
}</code></pre>
    `,

    encapsulation: `
        <h2>Java Encapsulation</h2>
        <p>Encapsulation is the bundling of data and methods that operate on that data within a single unit.</p>
        <h3>Why Encapsulation?</h3>
        <ul>
            <li>Better control of class attributes and methods</li>
            <li>Flexible: can make attributes read-only or write-only</li>
            <li>Increased security of data</li>
        </ul>
        
        <h3>Example:</h3>
        <pre><code>public class Person {
    private String name;  // private = restricted access
    private int age;
    
    // Getter
    public String getName() {
        return name;
    }
    
    // Setter
    public void setName(String newName) {
        this.name = newName;
    }
    
    // Getter
    public int getAge() {
        return age;
    }
    
    // Setter with validation
    public void setAge(int newAge) {
        if (newAge > 0) {
            this.age = newAge;
        }
    }
}</code></pre>
        
        <h3>Using Getters and Setters:</h3>
        <pre><code>public class Main {
    public static void main(String[] args) {
        Person person = new Person();
        person.setName("John");
        person.setAge(25);
        
        System.out.println(person.getName());  // John
        System.out.println(person.getAge());   // 25
    }
}</code></pre>
    `,

    abstraction: `
        <h2>Java Abstraction</h2>
        <p>Abstraction is hiding implementation details and showing only functionality to the user.</p>
        <h3>Abstract Classes:</h3>
        <pre><code>abstract class Animal {
    // Abstract method (does not have a body)
    public abstract void sound();
    
    // Regular method
    public void sleep() {
        System.out.println("Zzz");
    }
}

class Dog extends Animal {
    public void sound() {
        System.out.println("Dog barks");
    }
}

class Cat extends Animal {
    public void sound() {
        System.out.println("Cat meows");
    }
}</code></pre>
        
        <h3>Using Abstract Classes:</h3>
        <pre><code>public class Main {
    public static void main(String[] args) {
        Dog myDog = new Dog();
        Cat myCat = new Cat();
        
        myDog.sound();  // Dog barks
        myDog.sleep();  // Zzz
        myCat.sound();  // Cat meows
    }
}</code></pre>
        
        <h3>Key Points:</h3>
        <ul>
            <li>Cannot create objects of abstract class</li>
            <li>Can have both abstract and regular methods</li>
            <li>Abstract methods must be implemented by subclass</li>
            <li>Can have constructors and static methods</li>
        </ul>
    `,

    interface: `
        <h2>Java Interface</h2>
        <p>An interface is a completely "abstract class" used to group related methods with empty bodies.</p>
        <h3>Creating an Interface:</h3>
        <pre><code>interface Animal {
    void sound();  // interface method (no body)
    void sleep();  // interface method (no body)
}</code></pre>
        
        <h3>Implementing an Interface:</h3>
        <pre><code>class Dog implements Animal {
    public void sound() {
        System.out.println("Dog barks");
    }
    
    public void sleep() {
        System.out.println("Zzz");
    }
}

public class Main {
    public static void main(String[] args) {
        Dog myDog = new Dog();
        myDog.sound();
        myDog.sleep();
    }
}</code></pre>
        
        <h3>Multiple Interfaces:</h3>
        <pre><code>interface FirstInterface {
    void myMethod();
}

interface SecondInterface {
    void myOtherMethod();
}

class DemoClass implements FirstInterface, SecondInterface {
    public void myMethod() {
        System.out.println("Some text..");
    }
    
    public void myOtherMethod() {
        System.out.println("Some other text...");
    }
}</code></pre>
        
        <h3>Interface vs Abstract Class:</h3>
        <ul>
            <li>Interface: All methods are abstract by default</li>
            <li>Interface: Supports multiple inheritance</li>
            <li>Interface: Cannot have instance variables</li>
            <li>Abstract Class: Can have both abstract and concrete methods</li>
            <li>Abstract Class: Can have constructors and instance variables</li>
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
