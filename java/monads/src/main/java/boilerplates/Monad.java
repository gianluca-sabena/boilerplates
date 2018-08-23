package boilerplates;

import java.util.function.Function;

// interface Monad<T,M extends Monad<?,?>> extends Functor<T,M> {
//   M flatMap(Function<T,M> f);
// }

interface Monad<T, M extends Monad<?, ?>> {
  <R> M map(Function<T, R> f);
  <R> M flatMap(Function<T, MOptional<R>> f);
}

class MOptional<T> implements Monad<T, MOptional<?>> {
  private final T valueOrNull;
  @Override
  public <R> MOptional<R> flatMap(Function<T, MOptional<R>> f) {
    if (valueOrNull == null)
      return empty();
    else
      return f.apply(valueOrNull);
  }
  @Override
  public <R> MOptional<R> map(Function<T, R> f) {
    if (valueOrNull == null)
      return empty();
    else
      return of(f.apply(valueOrNull));
  }
  private MOptional(T valueOrNull) {
    this.valueOrNull = valueOrNull;
  }

  public static <T> MOptional<T> of(T a) {
    return new MOptional<T>(a);
  }

  public static <T> MOptional<T> empty() {
    return new MOptional<T>(null);
  }




}