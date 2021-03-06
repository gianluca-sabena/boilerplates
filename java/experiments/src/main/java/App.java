/*
 * This Java source file was generated by the Gradle 'init' task.
 */
import java.util.function.Function;
import java.util.function.BinaryOperator;
 
public class App {
    public static Function<Integer, Integer> adder(Integer x) {
        return y -> x + y;
     }
    public void none(Function<Integer, Integer> f) {
        
    }

    public String getGreeting() {
        return "Hello world.";
    }

    public static void main(String[] args) {
        System.out.println(new App().getGreeting());
        Function<Integer,Integer> add1 = x -> x + 1;
        Function<String,String> concat = x -> x + 1;
        //<T> Function<T> test = x -> x + x;
        //String a = test.apply("a");
        //Integer b = test.apply(1);

        Integer two = add1.apply(1); //yields 2
        System.out.println(two);
        String answer = concat.apply("0 + 1 = "); //yields "0 + 1 = 1"
        System.out.println(answer);
        
        BinaryOperator<Integer> sum = (a,b) -> a + b;
        Integer res = sum.apply(1,2); // yields 3
        System.out.println(res);
    }
}
