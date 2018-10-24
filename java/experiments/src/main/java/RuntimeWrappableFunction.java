
@FunctionalInterface
public interface RuntimeWrappableFunction<T, R> {
  R apply(T t) throws Exception;
}