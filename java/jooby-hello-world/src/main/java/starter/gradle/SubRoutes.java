package starter.gradle;

import org.jooby.Jooby;

public class SubRoutes extends Jooby {
  {
    get("/async", deferred(() -> {
      return "Hello";
    }));
  }
}
