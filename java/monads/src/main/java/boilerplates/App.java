package boilerplates;

import static java.util.Arrays.asList;

/**
 * Hello world!
 *
 */
public class App 
{
    private static Optional<Integer> tryParse(String s) {
        try {
            final int i = Integer.parseInt(s);
            return Optional.of(i);
        } catch (NumberFormatException e) {
            return Optional.empty();
        }
    }
    private static MOptional<Integer> MtryParse(String s) {
        try {
            final int i = Integer.parseInt(s);
            return MOptional.of(i);
        } catch (NumberFormatException e) {
            return MOptional.empty();
        }
    }    
    public static void main( String[] args )
    {
        System.out.println( "Hello World!" );
        Identity<String> idString = new Identity<>("Hello World!");
        Identity<Integer> idInt = idString.map(String::length);
        Identity<Object> idNull = idInt.map( e -> { 
            System.out.print(e.toString()); 
            return e;
         } );
        FOptional<String> fopString = FOptional.of("FOptional Hello World!");
        fopString.map( e -> {
            System.out.print(e.toString()); 
            return e;
        });

        // Transform list type with map
        FList<String> flString = new FList<>(asList("FList", "Hello", "World", "!"));
        FList<Integer> flSizes = flString.map(e -> e.length());


        Optional<String> str = Optional.of("42");
        Optional<Optional<Integer>> num = str.map(App::tryParse);
        Optional<Integer> answer = str.flatMap(App::tryParse);

        MOptional<String> str2 = MOptional.of("42");
        MOptional<MOptional<Integer>> num2 = str2.map(App::MtryParse);
        MOptional<Integer> answer2 = str2.flatMap(App::MtryParse);
    } 
}
