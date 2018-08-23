package boilerplates;

import java.util.function.Function;
import java.util.ArrayList;

import com.google.common.collect.ImmutableList;

/**
 * 
 * But mere syntax is not enough to understand what a functor is. The only
 * operation that functor provides is map() that takes a function f. This
 * function receives whatever is inside a box, transforms it and wraps the
 * result as-is into a second functor. Please read that carefully. Functor<T> is
 * always an immutable container, thus map never mutates the original object it
 * was executed on. Instead, it returns the result (or results - be patient)
 * wrapped in a brand new functor, possibly of different type R. Additionally
 * functors should not perform any actions when identity function is applied,
 * that is map(x -> x). Such a pattern should always return either the same
 * functor or an equal instance. Often Functor<T> is compared to a box holding
 * instance of T where the only way of interacting with this value is by
 * transforming it. However, there is no idiomatic way of unwrapping or escaping
 * from the functor. The value(s) always stay within the context of a functor.
 */
interface Functor<T, F extends Functor<?, ?>> {
    <R> F map(Function<T, R> f);
    //F flatMap(Function<T, F> f);
}

class Identity<T> implements Functor<T, Identity<?>> {
    private final T value;

    Identity(T value) {
        this.value = value;
    }

    public <R> Identity<R> map(Function<T, R> f) {
        final R result = f.apply(value);
        return new Identity<>(result);
    }

}

/**
 * It turns out you can model several other concepts using this raw functor
 * abstraction. For example starting from Java 8 Optional is a functor with the
 * map() method.
 * 
 * An FOptional<T> functor may hold a value, but just as well it might be empty.
 * It's a type-safe way of encoding null. There are two ways of constructing
 * FOptional - by supplying a value or creating an empty() instance. In both
 * cases, just like with Identity,FOptional is immutable and we can only
 * interact with the value from inside. What differsFOptional is that the
 * transformation function f may not be applied to any value if it is empty.
 * This means functor may not necessarily encapsulate exactly one value of type
 * T. It can just as well wrap an arbitrary number of values,
 */
class FOptional<T> implements Functor<T, FOptional<?>> {
    private final T valueOrNull;

    private FOptional(T valueOrNull) {
        this.valueOrNull = valueOrNull;
    }

    public <R> FOptional<R> map(Function<T, R> f) {
        if (valueOrNull == null)
            return empty();
        else
            return of(f.apply(valueOrNull));
    }

    public static <T> FOptional<T> of(T a) {
        return new FOptional<T>(a);
    }

    public static <T> FOptional<T> empty() {
        return new FOptional<T>(null);
    }
}

class FList<T> implements Functor<T, FList<?>> {
    private final ImmutableList<T> list;

    FList(Iterable<T> value) {
        this.list = ImmutableList.copyOf(value);
    }

    //@Override
    public <R> FList<R> map(Function<T, R> f) {
        ArrayList<R> result = new ArrayList<R>(list.size());
        for (T t : list) {
            result.add(f.apply(t));
        }
        return new FList<>(result);
    }
}