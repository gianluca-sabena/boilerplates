package boilerplates;

import java.util.function.Function;
import java.util.Objects;

/**
 * Java monad from https://dzone.com/articles/functor-and-monad-examples-in-plain-java
 */

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

  /**
   * Required in order to test Monad laws <https://gist.github.com/ms-tg/7420496#file-jdk8_optional_monad_laws-java>
   * From java.util.Optional
   **/
  @Override
  public boolean equals(Object obj) {
      if (this == obj) {
          return true;
      }

      if (!(obj instanceof MOptional)) {
          return false;
      }

      MOptional<?> other = (MOptional<?>) obj;
      return Objects.equals(valueOrNull, other.valueOrNull);
  }




}