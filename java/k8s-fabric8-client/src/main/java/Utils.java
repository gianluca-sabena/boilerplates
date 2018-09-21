import java.util.function.*;
import java.util.concurrent.*;
public final class Utils {
  private Utils() {
  }

  public static <T> Supplier<T> wrap(Callable<T> callable) {
      return () -> {
          try {
              return callable.call();
          }
          catch (RuntimeException e) {
              throw e;
          }
          catch (Exception e) {
              throw new RuntimeException(e);
          }
      };
  }
}