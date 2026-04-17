const topics = document.querySelectorAll(".topic");
const content = document.getElementById("topicContent");
const pageTitle = document.getElementById("pageTitle");

const topicData = {
    home: `
        <h2>Welcome to C Tutorial</h2>
        </p>
    `,

    intro: `
    <div class="intro"><h2>C Introduction</h2>
       
        C Language gurinchi telusukune mundu, asalu computer lo data aneedi ela memory lo save avuthundo telusukovali. Computer lo manam ye key 
        
        press chesina (or) yedaina song (leda) video (leda) yedaina data (data) ni vesthe, adi computer lo unde memory lo save avuthundi. Save ayina appudu prati data (computer lo vese prati danini data antaru) ki oka number ni istundi. Ee number ne memory location address ani antaru.

        Ee number valla upayogam emiti ante, tvaraga data ni access cheyavachu. Ante ippudu computer lo ye pani chesina adi memory location lo save avuthundi. Kabatti daniki oka number istundi. A number ne memory location address antam.
    </div>

      <div class="intro"> <h3>Computer paranga chooste Languages anevi 3 rakalu :</h3>

        1. Low Level Language ( Machine Level Language / Binary Level Language )  <br>
        2. Middle Level Language ( Assembly Language )<br>  
        3. High Level Language ( C, C++, Java, Python ... )<br>
    </div>

    <div class="intro">   <h4>Low Level Language:</h4>  Computer ki danantata adi emi cheyaledu. Daniki ardham ayyede 0 (sunna), 1 (okati) maathrame. 
        
        Ila 0, 1 unnaa language ni Low Level Language antaru. Ee language computer ki ardham ayyé basha. Manam computer tho emi cheyali anna computer ki sunna, okati lone cheppali. Ila cheppite ne computer ki ardham avtundi. Kaani pratidi ila 0, 1 latho computer ki cheppali ante chala kashtam.

        Example: Rend-u ankalu ni koodali ante ee language lo ela vrastamo chuddham — 0001 0111 0100

        Kaani ee Low Level Language codes anevi computer nunchi computer ki maaripotai. Veetini gurthupettukovatam chala kashtam.
        
    </div>

    <div class="intro">
        <h4>Middle Level Language :</h4> Middle level languages ante manam computer lo programs ni konni mnemonic codes upayoginchi vrastam. Ante MOV, ADD, SUB, DIV ani konni mnemonic codes untayi. Vatini upayoginchi programs anevi direct ga computer yokka memory, registers mida vrastam.

Ee mnemonic codes kuda computer ki ardham kaadu. Computer ki okka Machine level language lo unte ne ardham avtundi. Kabatti ee middle level lo vrase programs computer ki ardham avvali ante, computer veetini kuda low level language lo ki marchali. Appude computer ardham chesukuntundi. Veetini kuda gurthupettukovatam chala kashtam.
        
    </div>

    <div class="intro">
        <h4>High level language :</h4> Manam maatlaade bashani / manam computer lo vrase programs (C, C++, Java ...) ni High level language antaru. Ee language ni computer ardham chesukoledhu. Ante manam computer lo general ga type chese matter ni computer ardham chesukoledhu.

Computer manam type chesedi ardham chesukovali ante, adi computer ki ardham ayyé bashalo ki marchukovali. Computer programming languages lo High nundi Low ki marchali ante Compiler / Interpreter anevi untayi.

Computer ki ardham ayyé bashani Machine Level (Machine Level Language / Low Level Language / Binary Level Language) antaru.
</div>

<div class="intro">
<h4>Compiler / Interpreter :</h4> Manam computer lo ye programming language lo program ni vrasthe, adi compiler / interpreter latho computer ki ardham ayyé bashalo ki marchali. Ee process ni compilation (leda) interpretation antaru.
Compiler / Interpreter valla manam vrase programming language lo unné programs ni computer ki ardham ayyé bashalo ki marchadam jarugutundi. Appude computer adi ardham chesukuntundi.
</div>

<div class="intro">
<h4>What is C Language ?</h4>
C Language aneedi oka High Level Programming Language. Ee C Language ni 1972 lo Dennis Ritchie ane vyakti Bell Labs lo develop chesaru. C Language ni mainly system programming kosam design chesaru. Kaani ipudu C Language ni general purpose programming language ga use chesthunaru.

C Language ni manam different platforms (Windows, Linux, Mac OS) mida use cheyavachu. C Language ni use chesi manam system software (Operating Systems, Compilers), application software (Databases, Graphics), embedded systems (Microcontrollers), games development lanti chala rakala applications ni develop cheyavachu.
</div>

<div class="intro"> 
<h4>C Language Features :</h4>
<strong>1. Simple and Efficient:</strong><br> C Language chala simple ga undi. Adi efficient ga run avutundi, kabatti system programming kosam perfect ga untundi.<br>
<strong>2. Portability:</strong><br> C Language lo vrase programs ni different platforms mida easy ga port cheyavachu.<br>
<strong>3. Low-Level Access:</strong><br> C Language lo manam low-level memory access ni chesukovachu, kabatti system programming kosam use cheyadam easy avutundi.<br>
<strong>4. Rich Library:</strong> <br>C Language ki chala rich standard library undi, idi manaki different functionalities ni provide chestundi.<br>
<strong>5. Structured Programming:</strong><br> C Language lo manam structured programming techniques ni use chesukovachu, idi code readability and maintainability ni improve chestundi.
</div>
<div class="intro">
<h4>Why Learn C Language ?</h4>
<strong>1. Foundation for Other Languages:</strong><br> C Language ni nerchukunte, adi manaki C++, Java, Python lanti vere programming languages ni nerchukovadaniki strong foundation istundi.<br>
<strong>2. System Programming:</strong><br> C Language system programming kosam widely use avutundi, kabatti system-level programming lo career start cheyadaniki C Language ni nerchukovadam important.<br>
<strong>3. Performance:</strong><br> C Language chala efficient ga run avutundi, kabatti performance-critical applications develop cheyadaniki C Language ni use chestharu.<br>
<strong>4. Job Opportunities:</strong><br> C Language lo skilled programmers ki IT industry lo chala demand undi, kabatti C Language ni nerchukovadam manaki better job opportunities istundi.
</div>
<div class="intro"><center><h2>Try it Yourself !</h2>
<p>Below is a simple C program that prints "Hello, World!" to the console:</p>
</center>
</div>
    `,

    syntax: `
        <h2>C Syntax</h2>
        <div class="intro">
                A simple C program looks like this:

                     <pre> #include &lt;stdio.h>
                     int main() {
                        printf("Hello, World!");
                        return 0;
                    }</pre>
        </div>
        <div class="intro">
                <h4>Preprocessor Directive — #include</h4>

                    Ivi # tho start avtayi.

                    Compiler ki “ee file ni mundu include cheyyi” ani cheptayi.

                    Example:

                    <pre>#include &lt;stdio.h></pre>

                    <mark>stdio ante standard input-output library</mark>


                    stdio.h lo printf() lantivi untayi.
        </div>
        <div class="intro">
                <h4>int main() :</h4>

                    int main()  Dinini ne Main Function Antamu.<br>

                    Example:

                    <pre>int main() {
                        printf("Hello, World!");
                        return 0;
                    }</pre>
                    <ul>
                    <li>C Program  lo program ki entry point idhe . </li>

                    <li>return 0 anedhi exit point.</li>

                    <li>Main function madylo rasevatini Statements antaru.</li>

                    <li>C program lo { }(Curly Braces) Rase statements ni Block of Code antaru</li>

                    <li>Manam E code rayalanukunna Curly Braces Madylano rayali.</li>

                    <li>printf() anedhi Oka Pre-Defined Function Stdio.h Header File lo untundi. Dinini Output Print cheyyadaniki Use chestam.</li>

                    </ul>
        </div>
        <div class="intro">
                <h4>Practice:</h4>
                <h5>1. Write a C program to print "Hello, World!" to the console.</h5>
                <h5>2. Write a C program to print Your Name and Roll Number.</h5>
                <h5>3. Write a C program to print Your Address in Multiple Lines.</h5>
                <p><mark>Ikkada Main Point Enti ante , Okavela Multiple printf statements rasthe Oke line lo print avtundi,
                 Multiple lines print avvali ante <strong>" \\n "</strong> use cheyyali.</mark></p>
        </div>
    `,
    tokens: `<h2> C Tokens</h2>
    <div class='intro'>
      <p> Tokens ante oka smallest unit of a programm, ante oka chinna word aina ledha oka chinna part ni tokens antaru.
      <h3>Tokens lo 5 Types:</h3>
      <ol>
        <li>Keywords</li>
        <li>Identifiers</li>
        <li>Constants</li>
        <li>Operators</li>
        <li>Separators</li>
      </ol>
      </div>
      <div class='intro'>
      <h4>1. Keywords:</h4>
       <p>Key word ante Reserved keyword. Means Prathi Programming Language lo Vatiki sambandhinchina konni keywords pre defined ga cheyavundini.
       vatini use cheskuntu manam programe rayali, Mundhu classes lo manamu keywords chala use chestham.
       C language lo manaku 32 keywords unnai.
       </p>
       <h4>2.Identifiers:</h4>
       <p> Manamu C Programe rase time lo konni names use chestamu , Like name, rollno, age, etc.</p>
       <p> Vitine manamu Identifiers antamu. Identifiers are two type:</p>
       <h5>Pre Defined Identifiers</h5>
       <p>Pre Defined Identifiers ante C Language lo pre defined ga Unnavi.<b>Ex:Main,clrscr,printf,etc....</b></p>
       <h5>User Defined Identifiers</h5>
       <p>User Defined Identifiers ante Manam C Programe lo konni names use chestamu.<b>Ex:name,rollno,age,etc....</b></p>
       <h4>3.Constants:</h4>
       <p>Program Exicution Time to Change kani vatini Constants antaru. Ante Program intial stage
        lo ela undo exicution aipoyaka kuda alane untundi . Andhuke vatini Constants antaru.</p>
        <h4>4.Operators:</h4>
        <p>Values madyalo konni operations cheyyadaniki Operator use chesthamu. 
        The Operation edaina kavchu like arthemetic or logical operation. </p>
        <h4>5.Separators:</h4>
        <p>Separators nti ante Brackets, Semicolons, Commas, etc. Vitini manam endhuku use chestamu 
        separate cheyyadniki use chestamu</p>
        
    </div>`,

    variables: `
        <h2>C Variables</h2>
        
    `,

    datatypes: `
    <div class='intro'>
        <h2>C Data Types</h2>
        <p>Data type ante oka variable lo ye type data store cheyyalo computer ki cheppadam.<br>
      
        <mark>Syntax: Datatype variablename=values;<mark></p>
        <h4>Datatypes:</h4>
        <ol>
         <li>Int</li>
         <li>Float</li>
         <li>Char</li>
         <li>Void</li>
        </ol>
    </div>
    <div class='intro'>
        <h4>1.Int:</h4>
        <p>Numbers kosam int ane Keyword ni use chestam
        <pre>int a = 10;</pre></p>
    </div>
    <div class='intro'>
        <h4>2.Float:</h4>
        <p>Decimal values kosam float ane Keyword ni use chestam
        <pre>float a = 10.67;</pre></p>
    </div>
    <div class='intro'>
        <h4>3.Char:</h4>
        <p>Alphabetic letters  kosam char ane Keyword ni use chestam
        <pre>char a = 'x';</pre></p>
    </div>
    <div class='intro'>
        <h4>4.Void:</h4>
        <p>Okavela manamu oka function nundi eh value return cheyyakapothe void datatype use cheyyali.<br>
        
    </div>
    <div class='intro'>
    <h3> Variables :</h3>
    <p> Manamu Oka value use cheskovali ante daniki oka place allocate cheyyali. Ah Place ne Manamu Memory Allocation antamu .</p>
    <p> So Ah value anedhi ah place lo store avtundi</p>
    <p> Ah place ne manamu <b>Variable</b> antamu.
    <b>Example</b>
     <pre> int a =10;</pre>
     <p> Paina datlo 'a' Anedhi oka Variable. '10' ane value ni 'a' ane variable lo store chestunnam. </p>
    </div>

    <div class='intro'>
        <h3>Format Specifiers:</h3>
        <p> C language lo Manam eh Value print cheyyalanna kuda format specifiers use cheyyali.
        ippudu manaki unna datatypes ki vatiki specific ga format specifiers anevi untai.</p>
        <ul>
           
          <li>int --->%d</li>
          <li>float --->%f</li>
          <li>char --->%c</li>
          <li>string --->%s</li>

        </ul>

       
    </div>
    
    <div class='intro'>
        <b>Syntax</b>
        <pre>printf("format specifier",variable);</pre>
        <b>Example</b>
        <pre>
        int a=10;
        printf("%d",a);
        float b=10.5;
        printf("%f",b);
        char c='a';
        printf("%c",c);</pre>
    </div>
    <div class='intro'>
        <b>Practice</b>
        <ol>
         <li>Write a C Programe to print value on output screen</li>
         <li>Write a C Programe to print add of two numbers. </li>
        <li>Write a C Programe to print Sub of two numbers. </li>
        <li>Write a C Programe to print Multiplication of two numbers. </li>
        <li>Write a C Programe to print Division of two numbers. </li>
        <li>Write a C Programe to print Modulus of two numbers. </li>
        <li>Write a C Programe to print area of square  </li>
        <li>Write a C Programe to print area of Rectangle  </li>
        <li>Write a C Programe to print area of Traingle   </li>



        </ol>
    </div>
        
        
    `,
    typeconversion: `
        <h2>C Type Conversion</h2>
        <p>Type conversion ante oka data type ni inko data type ki marchadam.</p>
        <p> Ante Ippudu 'int' datatype ni 'float' datatype ki change chesamu anukondi danine Type Conversion antamu.</p>
        <b>Type Conversion enduku avasaram?</b>
        <p>Different data types tho operations chesthe, C automatic ga leda maname manual ga type marchali.
        Types of Type Conversion in C:<br>
           1.Implicit Type Conversion (Automatic):<br>
                    <p>Compiler automatic ga type change chestundi.</p>
                    <pre>
                    int a = 10;
                    float b = a;</pre>
                        <p>Explain:
                        a int type,
                        b float type,
                        int value automatic ga float ki convert ayindi.No data loss usually</p>

              2.Explicit Type Conversion (Manual):<br>
              <p>Maname force chesi type marchadam.<br>
              <b>Syntax</b><br>
               <pre>(type) value</pre>
               <b>Example:</b>
                <pre>
                float a = 10.5;
                int b = (int)a;
                </pre>
                   </p>
        <div class='intro' >
           <b>Practice</b>
           <ol>
           <li>Write a C program where an int value is assigned to a float variable and print the result.</li>
           <li>Write a C program to divide two integers and get the correct decimal result using type casting.</li>
           </ol>
        <div>
            
    `,
    operators: `
        <h2>C Operators</h2>
        <h3>Operator ante enti?</h3>
        <p>Operator ante C language lo variables mariyu values mida operations perform 
        cheyadaniki use chese symbols.</p>
        <b>Types of Operators in C:</b>
        <ol>
        <li>Arithmetic Operators</li>
        <li>Assignment Operators</li>
        <li>Comparison Operators</li>
        <li>Logical Operators</li>
        <li>Bitwise Operators</li>
        <li>Increment/Decrement Operators</li>
        </ol>   
        <div class="intro">
        <h2>1. Arithmetic Operators</h2>
        <p>Ee operators math calculations kosam use chestaru.</p>
        <p>+ (addition), - (subtraction), * (multiplication), / (division), % (modulus)</p>
        <code>
int a = 10, b = 3;<br>
printf("%d", a % b); // remainder
        </code>
    </div>

    <div class="intro">
        <h2>2. Relational Operators</h2>
        <p>Rendu values ni compare cheyadaniki use chestaru. Result true (1) leda false (0).</p>
        <p>==, !=, >, <, >=, <=</p>
        <code>
int a = 10, b = 5;<br>
printf("%d", a > b); // 1
        </code>
    </div>

    <div class="intro">
        <h2>3. Logical Operators</h2>
        <p>Conditions ni combine cheyadaniki logical operators use chestaru.</p>
        <p>&& (AND), || (OR), ! (NOT)</p>
        <code>
int a = 10;<br>
printf("%d", a > 5 && a < 20);
        </code>
    </div>

    <div class="intro">
        <h2>4. Assignment Operators</h2>
        <p>Variable ki value assign cheyadaniki use chestaru.</p>
        <p>=, +=, -=, *=, /=</p>
        <code>
int a = 10;<br>
a += 5; // a = 15
        </code>
    </div>

    <div class="intro">
        <h2>5. Increment & Decrement</h2>
        <p>Value ni 1 penchadam leda 1 tagginchadam kosam use chestaru.</p>
        <p>++ , --</p>
        <code>
int a = 5;<br>
a++; // 6<br>
a--; // 5
        </code>
    </div>

    <div class="intro">
        <h2>6. Conditional Operator</h2>
        <p>Idi if-else ki short form.</p>
        <code>
int a = 10, b = 5;<br>
int max = (a > b) ? a : b;
        </code>
    </div>
    <div class="intro">
        <h2>6. Bitwise Operators</h2>
        <p>Ee operators binary (bits) level lo work chestayi.</p>
        <ul>
            <li>&amp; → Bitwise AND</li>
            <li>| → Bitwise OR</li>
            <li>^ → Bitwise XOR</li>
            <li>~ → Bitwise NOT</li>
            <li>&lt;&lt; → Left Shift</li>
            <li>&gt;&gt; → Right Shift</li>
        </ul>
        <code>
int a = 5, b = 3;<br>
printf("%d", a & b);  // AND operation
        </code>
        <p><b>Explanation:</b>  
        5 = 0101<br>
        3 = 0011<br>
        Result = 0001 (1)
        </p>
    </div>

    <p><b>Summary:</b> Operators C language lo calculations, comparisons mariyu decisions kosam chala important.</p>
    <div class="intro">
        <b>Practice</b>
        <ol>
        <li>Write a C program to perform addition, subtraction, multiplication, and division of two numbers.</li>
        <li>Write a C program to find the maximum of two numbers using the ternary operator.</li>

        
        </ol>
    </div>
 `
    ,
    controlstructures: `
        <h1>Control Flow in C</h1>

<p>
<b>Control Flow</b> ante C program lo statements execute ayye order ni control cheyadam.
Normal ga statements top to bottom execute avtayi, kani control flow statements valla decision,
repetition mariyu jumping possible avtundi.
</p>

---

<div class="intro">
    <h2>Types of Control Flow in C</h2>
    <ol>
        <li>Decision Making Statements</li>
        <li>Looping Statements</li>
        <li>Jump Statements</li>
    </ol>
</div>

---

<div class="intro">
    <h2>1. Decision Making Statements</h2>
    <p>
    Conditions based ga different code execute cheyadaniki decision making statements use chestaru.
    </p>

    <h3>a) if Statement</h3>
    <p>
    Condition true ayithe block execute avtundi.
    </p>
    <pre>
if (condition) {
    // statements
}
    </pre>

    <pre>
int age = 20;
if (age >= 18) {
    printf("Eligible to vote");
}
    </pre>

    <h3>b) if-else Statement</h3>
    <p>
    Condition true ayithe if block, false ayithe else block execute avtundi.
    </p>
    <pre>
if (condition) {
    // true block
} else {
    // false block
}
    </pre>

    <pre>
int num = 5;
if (num % 2 == 0) {
    printf("Even number");
} else {
    printf("Odd number");
}
    </pre>

    <h3>c) else-if Ladder</h3>
    <p>
    Multiple conditions check cheyadaniki else-if ladder use chestaru.
    </p>
    <pre>
if (condition1) {
    // block
} else if (condition2) {
    // block
} else {
    // default
}
    </pre>

    <pre>
int marks = 85;
if (marks >= 90) {
    printf("Grade A");
} else if (marks >= 75) {
    printf("Grade B");
} else {
    printf("Grade C");
}
    </pre>

    <h3>d) switch Statement</h3>
    <p>
    Multiple choices lo oka choice select cheyadaniki switch use chestaru.
    </p>
    <pre>
switch(expression) {
    case value1:
        // statements
        break;
    case value2:
        // statements
        break;
    default:
        // statements
}
    </pre>

    <pre>
int day = 3;
switch (day) {
    case 1: printf("Monday"); break;
    case 2: printf("Tuesday"); break;
    case 3: printf("Wednesday"); break;
    default: printf("Invalid day");
}
    </pre>
</div>

---

<div class="intro">
    <h2>2. Looping Statements</h2>
    <p>
    Same code ni multiple times execute cheyali ante loops use chestaru.
    </p>

    <h3>a) for Loop</h3>
    <p>
    Fixed number of times repeat cheyadaniki use chestaru.
    </p>
    <pre>
for (initialization; condition; increment/decrement) {
    // statements
}
    </pre>

    <pre>
for (int i = 1; i <= 5; i++) {
    printf("%d ", i);
}
    </pre>

    <h3>b) while Loop</h3>
    <p>
    Condition true unna varaku loop run avtundi.
    </p>
    <pre>
while (condition) {
    // statements
}
    </pre>

    <pre>
int i = 1;
while (i <= 5) {
    printf("%d ", i);
    i++;
}
    </pre>

    <h3>c) do-while Loop</h3>
    <p>
    Minimum okasari loop execute avtundi.
    </p>
    <pre>
do {
    // statements
} while (condition);
    </pre>

    <pre>
int i = 1;
do {
    printf("%d ", i);
    i++;
} while (i <= 5);
    </pre>
</div>

---

<div class="intro">
    <h2>3. Jump Statements</h2>
    <p>
    Program control ni sudden ga change cheyadaniki jump statements use chestaru.
    </p>

    <h3>a) break</h3>
    <p>
    Loop or switch nundi bayatiki ravadaniki use chestaru.
    </p>
    <pre>
for (int i = 1; i <= 10; i++) {
    if (i == 5)
        break;
    printf("%d ", i);
}
    </pre>

    <h3>b) continue</h3>
    <p>
    Current iteration skip chesi next iteration ki velladaniki use chestaru.
    </p>
    <pre>
for (int i = 1; i <= 5; i++) {
    if (i == 3)
        continue;
    printf("%d ", i);
}
    </pre>

    <h3>c) goto</h3>
    <p>
    Direct ga program lo oka label ki jump cheyadaniki use chestaru.
    (General ga avoid cheyadam better)
    </p>
    <pre>
goto label;

label:
    // statements
    </pre>

    <pre>
int i = 1;
start:
printf("%d ", i);
i++;
if (i <= 5)
    goto start;
    </pre>
</div>

---

<div class="intro">
    <h2>Summary</h2>
    <ul>
        <li>Control flow program execution order ni control chestundi</li>
        <li>Decision making → if, if-else, switch</li>
        <li>Loops → for, while, do-while</li>
        <li>Jump statements → break, continue, goto</li>
    </ul>
</div>

---

`,
    functions: `
        <h1>Functions in C</h1>

<p>
<b>Function</b> ante oka specific task perform cheyadaniki use chese block of code.
Functions valla program ni easy ga understand cheyochu, reuse cheyochu mariyu manage cheyochu.
</p>

<div class="intro">
    <h2>Why Functions are Used?</h2>
    <ul>
        <li>Code reusability</li>
        <li>Program readability improve avtundi</li>
        <li>Large programs ni small parts ga divide cheyochu</li>
        <li>Debugging easy avtundi</li>
    </ul>
</div>

<div class="intro">
    <h2>Types of Functions in C</h2>
    <ol>
        <li>Library Functions</li>
        <li>User-Defined Functions</li>
    </ol>
</div>

<div class="intro">
    <h2>Library Functions</h2>
    <p>C language lo predefined ga unna functions.</p>
    <ul>
        <li>printf(), scanf()</li>
        <li>strlen(), strcpy()</li>
        <li>sqrt(), pow()</li>
    </ul>
</div>

<div class="intro">
    <h2>User-Defined Functions</h2>
    <pre>
int add(int a, int b) {
    return a + b;
}
    </pre>
</div>

<div class="intro">
    <h2>Function Declaration</h2>
    <pre>
int add(int, int);
    </pre>
</div>

<div class="intro">
    <h2>Function Call</h2>
    <pre>
int sum = add(10, 20);
printf("%d", sum);
    </pre>
</div>

<div class="intro">
    <h2>Call by Value</h2>
    <pre>
void change(int x) {
    x = 10;
}
    </pre>
</div>

<div class="intro">
    <h2>Call by Reference</h2>
    <pre>
void change(int *x) {
    *x = 10;
}
    </pre>
</div>

<div class="intro">
    <h2>Recursion</h2>
    <pre>
int factorial(int n) {
    if (n == 0)
        return 1;
    return n * factorial(n - 1);
}
    </pre>
</div>

<div class="intro">
    <h2>Summary</h2>
    <ul>
        <li>Functions make code reusable</li>
        <li>User-defined & library functions untayi</li>
        <li>Call by value & reference important</li>
        <li>Recursion powerful concept</li>
    </ul>
</div>
`,
    pointers: `
    < h2 > C Pointers</h2 >
        <p>Pointers are variables that store the memory address of another variable.</p>
`,
    arrays: `
    <h1>Arrays in C</h1>

<p>
<b>Array</b> ante same data type values ni oka single variable name lo store cheyadam.
Array use chesthe multiple values ni easy ga manage cheyochu.
</p>

<div class="intro">
    <h2>Why Arrays are Used?</h2>
    <ul>
        <li>Multiple values ni store cheyadaniki</li>
        <li>Memory management easy avtundi</li>
        <li>Loops tho easy ga access cheyochu</li>
        <li>Code length reduce avtundi</li>
    </ul>
</div>

<div class="intro">
    <h2>Array Declaration</h2>
    <pre>
data_type array_name[size];

int marks[5];
    </pre>
</div>

<div class="intro">
    <h2>Array Initialization</h2>
    <pre>
int marks[5] = {10, 20, 30, 40, 50};

int marks[] = {10, 20, 30};
    </pre>
</div>

<div class="intro">
    <h2>Accessing Array Elements</h2>
    <p>
    Array elements ni index value dwara access chestaru.
    Index always <b>0 nundi start</b> avtundi.
    </p>
    <pre>
int a[3] = {5, 10, 15};
printf("%d", a[0]); // Output: 5
    </pre>
</div>

<div class="intro">
    <h2>Using Loop with Array</h2>
    <pre>
int a[5] = {1, 2, 3, 4, 5};

for (int i = 0; i < 5; i++) {
    printf("%d ", a[i]);
}
    </pre>
</div>

<div class="intro">
    <h2>Types of Arrays</h2>
    <ol>
        <li>One Dimensional Array</li>
        <li>Two Dimensional Array</li>
    </ol>
</div>

<div class="intro">
    <h2>One Dimensional Array</h2>
    <pre>
int numbers[4] = {10, 20, 30, 40};
    </pre>
</div>

<div class="intro">
    <h2>Two Dimensional Array</h2>
    <p>Rows and columns format lo data store chestaru (matrix).</p>
    <pre>
int matrix[2][3] = {
    {1, 2, 3},
    {4, 5, 6}
};

printf("%d", matrix[1][2]); // Output: 6
    </pre>
</div>

<div class="intro">
    <h2>Array Input using Loop</h2>
    <pre>
int a[5];

for (int i = 0; i < 5; i++) {
    scanf("%d", &a[i]);
}
    </pre>
</div>

<div class="intro">
    <h2>Passing Array to Function</h2>
    <pre>
void display(int a[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", a[i]);
    }
}
    </pre>
</div>

<div class="intro">
    <h2>Advantages of Arrays</h2>
    <ul>
        <li>Fast access using index</li>
        <li>Less variables needed</li>
        <li>Easy sorting & searching</li>
    </ul>
</div>

<div class="intro">
    <h2>Disadvantages of Arrays</h2>
    <ul>
        <li>Fixed size (cannot change dynamically)</li>
        <li>Memory wastage possible</li>
        <li>Same data type only</li>
    </ul>
</div>

<div class="intro">
    <h2>Summary</h2>
    <ul>
        <li>Array stores multiple values of same data type</li>
        <li>Index starts from 0</li>
        <li>1D and 2D arrays commonly used</li>
        <li>Loops and functions work well with arrays</li>
    </ul>
</div>
`,
    pointers: `
 <h1>Pointers in C</h1>

<div class="intro">
    <p>
    <b>Pointer</b> ante oka variable, idi inkoka variable yokka
    <b>address</b> ni store chestundi.
    </p>
</div>

<div class="intro">
    <h2>Why Pointers are Used?</h2>
    <ul>
        <li>Memory ni efficient ga use cheyadaniki</li>
        <li>Call by reference implement cheyadaniki</li>
        <li>Arrays & strings ni handle cheyadaniki</li>
        <li>Dynamic memory allocation kosam</li>
    </ul>
</div>

<div class="intro">
    <h2>Pointer Declaration</h2>
    <pre>
data_type *pointer_name;

int *p;
    </pre>
</div>

<div class="intro">
    <h2>Pointer Initialization</h2>
    <pre>
int a = 10;
int *p = &a;
    </pre>
</div>

<div class="intro">
    <h2>Address Operator (&)</h2>
    <p>
    Variable yokka memory address tiskovadaniki
    <b>&</b> operator use chestaru.
    </p>
    <pre>
int a = 10;
printf("%p", &a);
    </pre>
</div>

<div class="intro">
    <h2>Dereference Operator (*)</h2>
    <p>
    Pointer lo unna address lo value ni access cheyadaniki
    <b>*</b> operator use chestaru.
    </p>
    <pre>
int a = 10;
int *p = &a;

printf("%d", *p); // Output: 10
    </pre>
</div>

<div class="intro">
    <h2>Example: Pointer Working</h2>
    <pre>
int a = 5;
int *p;

p = &a;

printf("a = %d\n", a);
printf("address of a = %p\n", &a);
printf("p = %p\n", p);
printf("*p = %d\n", *p);
    </pre>
</div>

<div class="intro">
    <h2>Pointer and Functions (Call by Reference)</h2>
    <p>
    Pointer use chesi original value ni change cheyochu.
    </p>
    <pre>
void change(int *x) {
    *x = 20;
}

int main() {
    int a = 10;
    change(&a);
    printf("%d", a); // Output: 20
}
    </pre>
</div>

<div class="intro">
    <h2>Pointer with Arrays</h2>
    <p>
    Array name itself oka pointer laga behave chestundi.
    </p>
    <pre>
int a[3] = {10, 20, 30};
int *p = a;

printf("%d", *p);      // 10
printf("%d", *(p+1));  // 20
printf("%d", *(p+2));  // 30
    </pre>
</div>

<div class="intro">
    <h2>Null Pointer</h2>
    <p>
    Pointer ni NULL ki assign cheyadam safe practice.
    </p>
    <pre>
int *p = NULL;
    </pre>
</div>

<div class="intro">
    <h2>Pointer to Pointer</h2>
    <p>
    Pointer yokka address ni store chese pointer ni
    <b>pointer to pointer</b> antaru.
    </p>
    <pre>
int a = 10;
int *p = &a;
int **q = &p;

printf("%d", **q); // Output: 10
    </pre>
</div>

<div class="intro">
    <h2>Advantages of Pointers</h2>
    <ul>
        <li>Fast execution</li>
        <li>Dynamic memory handling</li>
        <li>Efficient array & string handling</li>
    </ul>
</div>

<div class="intro">
    <h2>Disadvantages of Pointers</h2>
    <ul>
        <li>Wrong usage leads to runtime errors</li>
        <li>Memory leaks possible</li>
        <li>Complex to understand for beginners</li>
    </ul>
</div>

<div class="intro">
    <h2>Summary</h2>
    <ul>
        <li>Pointer stores address of another variable</li>
        <li>& is used to get address</li>
        <li>* is used to access value</li>
        <li>Pointers are very powerful but risky</li>
    </ul>
</div>
 `,
    strings: `
    <h1>Strings in C</h1>

<div class="intro">
    <p>
    <b>String</b> ante characters yokka collection.
    C language lo string ante <b>character array</b>
    with <b>NULL character ('\0')</b> at the end.
    </p>
</div>

<div class="intro">
    <h2>String Declaration</h2>
    <pre>
char str[10];
    </pre>
</div>

<div class="intro">
    <h2>String Initialization</h2>
    <pre>
char name[10] = "C Language";

char name[] = "Hello";
    </pre>
</div>

<div class="intro">
    <h2>NULL Character ('\0')</h2>
    <p>
    String end ni indicate cheyadaniki
    <b>'\0'</b> use chestaru.
    </p>
    <pre>
char name[] = {'H','e','l','l','o','\0'};
    </pre>
</div>

<div class="intro">
    <h2>String Input & Output</h2>
    <pre>
char name[20];

scanf("%s", name);
printf("%s", name);
    </pre>
    <p>
    Note: <b>scanf()</b> space varaku matrame input tiskuntundi.
    </p>
</div>

<div class="intro">
    <h2>Using gets() and puts()</h2>
    <pre>
char name[50];

gets(name);
puts(name);
    </pre>
    <p>
    ⚠️ <b>gets()</b> unsafe, general ga avoid cheyali.
    </p>
</div>

<div class="intro">
    <h2>String Functions (string.h)</h2>
    <p>Common ga use chese string functions:</p>
    <ul>
        <li><b>strlen()</b> – string length</li>
        <li><b>strcpy()</b> – copy string</li>
        <li><b>strcat()</b> – join strings</li>
        <li><b>strcmp()</b> – compare strings</li>
    </ul>
</div>

<div class="intro">
    <h2>strlen()</h2>
    <pre>
#include <string.h>

char s[] = "Hello";
printf("%d", strlen(s)); // 5
    </pre>
</div>

<div class="intro">
    <h2>strcpy()</h2>
    <pre>
char s1[20] = "C";
char s2[20];

strcpy(s2, s1);
    </pre>
</div>

<div class="intro">
    <h2>strcat()</h2>
    <pre>
char s1[20] = "Hello";
char s2[20] = "World";

strcat(s1, s2); // HelloWorld
    </pre>
</div>

<div class="intro">
    <h2>strcmp()</h2>
    <pre>
char s1[] = "abc";
char s2[] = "abc";

if (strcmp(s1, s2) == 0)
    printf("Equal");
else
    printf("Not Equal");
    </pre>
</div>

<div class="intro">
    <h2>String using Pointer</h2>
    <pre>
char *str = "Hello";
printf("%s", str);
    </pre>
</div>

<div class="intro">
    <h2>Array of Strings</h2>
    <pre>
char names[3][10] = {
    "Ram",
    "Sita",
    "Lakshman"
};
    </pre>
</div>

<div class="intro">
    <h2>Advantages of Strings</h2>
    <ul>
        <li>Easy text handling</li>
        <li>Supports many built-in functions</li>
        <li>Used in file handling & user input</li>
    </ul>
</div>

<div class="intro">
    <h2>Disadvantages of Strings</h2>
    <ul>
        <li>Fixed size</li>
        <li>Buffer overflow risk</li>
        <li>Manual memory handling</li>
    </ul>
</div>

<div class="intro">
    <h2>Summary</h2>
    <ul>
        <li>String is a character array ending with '\0'</li>
        <li>string.h provides useful functions</li>
        <li>Be careful with input functions</li>
        <li>Strings are very important in C</li>
    </ul>
</div>

`,
    structures: `
   <h1>Structures in C</h1>

<div class="intro">
    <p>
    <b>Structure</b> ante different data types ni
    oka single name kindha group cheyadam.
    Structure use chesi real-world entities ni represent cheyochu.
    </p>
</div>

<div class="intro">
    <h2>Why Structures are Used?</h2>
    <ul>
        <li>Different data types ni okasari store cheyadaniki</li>
        <li>Complex data ni organize cheyadaniki</li>
        <li>Real-world entities represent cheyadaniki</li>
        <li>Code readability improve cheyadaniki</li>
    </ul>
</div>

<div class="intro">
    <h2>Structure Declaration</h2>
    <pre>
struct structure_name {
    data_type member1;
    data_type member2;
};
    </pre>

    <pre>
struct student {
    int id;
    char name[20];
    float marks;
};
    </pre>
</div>

<div class="intro">
    <h2>Structure Variable Declaration</h2>
    <pre>
struct student s1;
    </pre>
</div>

<div class="intro">
    <h2>Accessing Structure Members</h2>
    <p>
    Structure members ni access cheyadaniki
    <b>dot (.) operator</b> use chestaru.
    </p>
    <pre>
s1.id = 101;
strcpy(s1.name, "Ravi");
s1.marks = 85.5;
    </pre>
</div>

<div class="intro">
    <h2>Structure Initialization</h2>
    <pre>
struct student s1 = {101, "Ravi", 85.5};
    </pre>
</div>

<div class="intro">
    <h2>Array of Structures</h2>
    <p>
    Multiple structure objects ni array lo store cheyochu.
    </p>
    <pre>
struct student s[3];

s[0].id = 1;
s[1].id = 2;
    </pre>
</div>

<div class="intro">
    <h2>Structure and Function</h2>
    <p>
    Structure ni function ki pass cheyochu.
    </p>
    <pre>
void display(struct student s) {
    printf("%d %s %f", s.id, s.name, s.marks);
}
    </pre>
</div>

<div class="intro">
    <h2>Pointer to Structure</h2>
    <p>
    Structure yokka address ni store chese pointer.
    </p>
    <pre>
struct student s1;
struct student *p;

p = &s1;
p->id = 101;
    </pre>
</div>

<div class="intro">
    <h2>Arrow Operator (->)</h2>
    <p>
    Pointer to structure lo members ni access cheyadaniki
    <b>-></b> operator use chestaru.
    </p>
    <pre>
p->marks = 90.5;
    </pre>
</div>

<div class="intro">
    <h2>Nested Structure</h2>
    <pre>
struct address {
    char city[20];
    int pin;
};

struct student {
    int id;
    struct address addr;
};
    </pre>
</div>

<div class="intro">
    <h2>Advantages of Structures</h2>
    <ul>
        <li>Multiple data types in one unit</li>
        <li>Better data organization</li>
        <li>Useful for large programs</li>
    </ul>
</div>

<div class="intro">
    <h2>Disadvantages of Structures</h2>
    <ul>
        <li>More memory usage</li>
        <li>No built-in data protection</li>
        <li>Complex syntax for beginners</li>
    </ul>
</div>

<div class="intro">
    <h2>Structure vs Array</h2>
    <ul>
        <li>Array → same data type</li>
        <li>Structure → different data types</li>
    </ul>
</div>

<div class="intro">
    <h2>Summary</h2>
    <ul>
        <li>Structure groups different data types</li>
        <li>Dot (.) and Arrow (->) operators are important</li>
        <li>Structures are widely used in real applications</li>
    </ul>
</div>

`

};

// Navigation Logic
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const topicKeys = Array.from(topics).map(t => t.getAttribute("data-topic"));
let currentTopicIndex = 0;

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

// Button Event Listeners
if (prevBtn) prevBtn.addEventListener("click", () => loadTopic(currentTopicIndex - 1));
if (nextBtn) nextBtn.addEventListener("click", () => loadTopic(currentTopicIndex + 1));

// Sidebar Click Listeners
topics.forEach((item, index) => {
    item.addEventListener("click", () => {
        loadTopic(index);
    });
});

// Initialize first topic state
loadTopic(0);
