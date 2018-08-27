package boilerplates;

import static java.util.Arrays.asList;
import java.util.function.Function;

/**
 * Hello world!
 *
 */
public class App {
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

    public static void main(String[] args) {
        // Mario Fusco Simple Optional Monad
        Optional<String> str = Optional.of("42");
        Optional<Optional<Integer>> num = str.map(App::tryParse);
        Optional<Integer> answer = str.flatMap(App::tryParse);

        // Monads in Java
        System.out.println("Hello World!");
        Identity<String> idString = new Identity<>("Hello World!");
        Identity<Integer> idInt = idString.map(String::length);
        Identity<Object> idNull = idInt.map(e -> {
            System.out.println("String length is: "+e.toString());
            return e;
        });
        FOptional<String> fopString = FOptional.of("FOptional Hello World!");
        fopString.map(e -> {
            System.out.println(e.toString());
            return e;
        });

        // Transform list type with map
        FList<String> flString = new FList<>(asList("FList", "Hello", "World", "!"));
        FList<Integer> flSizes = flString.map(e -> e.length());

        MOptional<String> str2 = MOptional.of("42");
        MOptional<MOptional<Integer>> num2 = str2.map(App::MtryParse);
        MOptional<Integer> answer2 = str2.flatMap(App::MtryParse);

        /**
         * Test Monad laws from
         * [1] https://gist.github.com/ms-tg/7420496#file-jdk8_optional_monad_laws-java
         *  
         */
        final int value = 42;
        final MOptional<Integer> monadicValue = MOptional.of(value);
        final Function<Integer, MOptional<Integer>> f = (n) -> MOptional.of(n * 2);
        final Function<Integer, MOptional<Integer>> g = (n) -> MOptional.of(n * 5);
        final Function<Integer, MOptional<Integer>> f_flatMap_g = (n) -> f.apply(n).flatMap(g);
        
        /**
         * Monad law 1, Left Identity
         *
         * The first monad law states that if we take a value,
         * put it in a default context with return and then feed it to a function by
         * using >>=, it’s the same as just taking the value and applying the function
         * to it
         */
        Boolean firstLaw = MOptional.of(value).flatMap(f).equals(f.apply(value));
        System.out.println("Monadic law 1: " + firstLaw.toString());
        /**
         * Monad law 2, Right Identity
         *
         *   The second law states that if we have a monadic value and we use >>= to feed 
         *   it to return, the result is our original monadic value.
         */
        Boolean law2RightIdentity = monadicValue.flatMap(n -> MOptional.of(n)).equals(monadicValue);
        System.out.println("Monadic law 2: " + law2RightIdentity.toString());
        /**
         * Monad law 3, Associativity
         *
         * The final monad law says that when we have a chain of
         * monadic function applications with >>=, it shouldn’t matter how they’re
         * nested.
         */
        Boolean law3Associativity = monadicValue.flatMap(f).flatMap(g).equals(monadicValue.flatMap(f_flatMap_g));
        System.out.println("Monadic law 3: " + law3Associativity.toString());
    }
}
