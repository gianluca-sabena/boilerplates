package boilerplates;

import java.util.function.Function;

class Optional<T> {
  //private static final Optional<?> EMPTY = new Optional<>(null);

  public static <T> Optional<T> empty() {
    return new Optional<T>(null);
  }

  public static <T> Optional<T> of(T a) {
    return new Optional<T>(a);
  }

  private final T value;

  private Optional(T value) {
    this.value = value;
  }

  public <U> Optional<U> map(Function<? super T, ? extends U> f) {
    return value == null ? empty() : of(f.apply(value));
  }

  public <U> Optional<U> flatMap(Function<? super T, Optional<U>> f) {
    return value == null ? empty() : f.apply(value);
  }
}